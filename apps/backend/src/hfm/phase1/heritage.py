"""D-domain service (P1-06 — 非遗传承体系, E-06).

Implements the frozen P1-06 acceptance criterion: lineage relations carry
official-name, evidence and publication state; no unverified heritage /
inheritor claim is public.

  - HeritageProject records (非遗项目/事项) with typed-Entity identity (I5),
    official-name evidence anchor (官方名称);
  - lineage relations (传承人/传承主体/机构) binding a project to a Person
    (P1-03 reuse) or institution Entity, carrying official name + evidence;
  - public projection: a project is public iff an admitted ContentArtifact
    bound to its Entity identity is PUBLISHED (P1-09 canonical truth);
    relations are public only when evidenced — no unverified claim (E-06);
  - no implicit publication; mutation requires P1-10 authorization;
    governed mutations are recorded through P1-13 audit.

No client content is invented — tests use synthetic fixtures.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from hfm.core.hashing import canonical_json
from hfm.models.content_artifact import (
    ContentArtifact,
    ProvenanceStatus,
    RightsStatus,
)
from hfm.models.entity import Entity, EntityType
from hfm.models.heritage import (
    HeritageProject,
    HeritageRelation,
    HeritageRelationRole,
)
from hfm.models.publication import PublicationRecord, PublicationStatus
from hfm.phase1.auth import Principal
from hfm.phase1.version_audit import AuditService
from hfm.repositories.content_artifact import ContentArtifactRepository
from hfm.repositories.heritage import (
    HeritageProjectRepository,
    HeritageRelationRepository,
)

PERMISSION_ASSERTION_CREATE = "assertion:create"


@dataclass(frozen=True)
class HeritageProjectView:
    """Serializable heritage project projection."""

    entity_id: str
    project_name: str
    official_name: str | None
    category: str | None
    publication_status: str
    relations: tuple[dict[str, Any], ...]


class HeritageService:
    """Canonical D-domain records with official-name + evidence + state."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # ------------------------------------------------------------- mutations
    async def create_project(
        self,
        *,
        principal: Principal,
        project_name: str,
        official_name: str | None = None,
        category: str | None = None,
        description: str | None = None,
    ) -> HeritageProject:
        """Create a canonical heritage project (typed-Entity identity).

        Requires assertion:create; never creates a publication record
        (no implicit publication — P1-09 boundary).
        """
        self._require_permission(principal, PERMISSION_ASSERTION_CREATE)
        if not project_name:
            raise ValueError("heritage project_name is required")
        entity = Entity(
            entity_type=EntityType.concept.value,
            name=project_name,
            name_zh=project_name,
            description=description,
        )
        self.session.add(entity)
        await self.session.flush()
        project = await HeritageProjectRepository(self.session).create(
            entity_id=entity.id,
            project_name=project_name,
            official_name=official_name,
            category=category,
            description=description,
            created_by=principal.user_id,
        )
        await AuditService(self.session).record(
            actor_id=principal.user_id,
            action="heritage_project.create",
            target_type="heritage_project",
            target_id=project.entity_id,
            detail=canonical_json({"project_name": project_name, "official_name": official_name}),
        )
        return project

    async def create_relation(
        self,
        *,
        principal: Principal,
        project_entity_id: str,
        subject_entity_id: str,
        relation_role: str,
        official_name: str | None = None,
        start_year: int | None = None,
        end_year: int | None = None,
        evidence_id: str | None = None,
        description: str | None = None,
    ) -> HeritageRelation:
        """Create an evidenced lineage relation (official-name carried).

        Requires assertion:create; relation bindings + official-name +
        evidence anchor are immutable (I4).
        """
        self._require_permission(principal, PERMISSION_ASSERTION_CREATE)
        relation = await HeritageRelationRepository(self.session).create(
            project_entity_id=project_entity_id,
            subject_entity_id=subject_entity_id,
            relation_role=HeritageRelationRole(relation_role).value,
            official_name=official_name,
            start_year=start_year,
            end_year=end_year,
            evidence_id=evidence_id,
            description=description,
            created_by=principal.user_id,
        )
        await AuditService(self.session).record(
            actor_id=principal.user_id,
            action="heritage_relation.create",
            target_type="heritage_relation",
            target_id=relation.id,
            detail=canonical_json(
                {
                    "project_entity_id": project_entity_id,
                    "subject_entity_id": subject_entity_id,
                    "relation_role": relation.relation_role,
                    "official_name": official_name,
                    "evidence_id": evidence_id,
                }
            ),
        )
        return relation

    async def admit_project_artifact(
        self,
        *,
        principal: Principal,
        project_entity_id: str,
        source_id: str,
        content: bytes,
        rights_status: RightsStatus,
        provenance_status: ProvenanceStatus = ProvenanceStatus.PENDING,
        format: str | None = None,
        version_id: str | None = None,
    ) -> ContentArtifact:
        """Admit a canonical representation of the project (P1-01 gate)."""
        self._require_permission(principal, PERMISSION_ASSERTION_CREATE)
        project = await HeritageProjectRepository(self.session).get_by_entity_id(project_entity_id)
        if project is None:
            raise ValueError("heritage project does not exist")
        artifact = await ContentArtifactRepository(self.session).submit_with_source_check(
            source_id=source_id,
            content=content,
            format=format,
            provenance_status=provenance_status,
            rights_status=rights_status,
            version_id=version_id,
            subject_entity_id=project.entity_id,
            created_by=principal.user_id,
        )
        await AuditService(self.session).record(
            actor_id=principal.user_id,
            action="artifact.submit",
            target_type="content_artifact",
            target_id=artifact.id,
            detail=canonical_json({"project_entity_id": project.entity_id}),
        )
        return artifact

    # ------------------------------------------------------------ visibility
    async def public_visibility(self, project_entity_id: str) -> bool:
        """Project is public iff a PUBLISHED artifact is bound to its Entity."""
        return await self._published_subject_entity(project_entity_id) is not None

    async def get_public_project(self, project_entity_id: str) -> dict[str, Any] | None:
        """Public projection: project + evidenced lineage relations only."""
        project = await HeritageProjectRepository(self.session).get_by_entity_id(project_entity_id)
        if project is None:
            return None
        if not await self.public_visibility(project_entity_id):
            return None
        view = await self._view(project, public_only=True)
        return self._serialize(view)

    async def get_research_project(self, project_entity_id: str) -> dict[str, Any]:
        """Research projection: full project record incl. all relations."""
        project = await HeritageProjectRepository(self.session).get_by_entity_id(project_entity_id)
        if project is None:
            raise ValueError("heritage project does not exist")
        view = await self._view(project, public_only=False)
        return self._serialize(view)

    async def list_public_projects(self, query: str | None = None) -> list[dict[str, Any]]:
        """Published heritage projects (P1-08 search integration)."""
        published = PublicationStatus.PUBLISHED.value
        published_subjects = select(ContentArtifact.subject_entity_id).where(
            ContentArtifact.subject_entity_id.is_not(None),
            ContentArtifact.id.in_(
                select(PublicationRecord.artifact_id).where(
                    PublicationRecord.publication_status == published
                )
            ),
        )
        base = select(HeritageProject).where(HeritageProject.entity_id.in_(published_subjects))
        if query:
            pattern = f"%{query}%"
            base = base.where(
                (HeritageProject.project_name.ilike(pattern))
                | (
                    HeritageProject.official_name.is_not(None)
                    & HeritageProject.official_name.ilike(pattern)
                )
            )
        projects = (
            (await self.session.execute(base.order_by(HeritageProject.project_name)))
            .scalars()
            .all()
        )
        result: list[dict[str, Any]] = []
        for project in projects:
            view = await self._view(project, public_only=True)
            result.append(
                {
                    "entity_id": view.entity_id,
                    "project_name": view.project_name,
                    "official_name": view.official_name,
                    "category": view.category,
                    "publication_status": view.publication_status,
                }
            )
        return result

    # -------------------------------------------------------------- internals
    async def _view(self, project: HeritageProject, *, public_only: bool) -> HeritageProjectView:
        status = await self._publication_status(project.entity_id)
        relations = await HeritageRelationRepository(self.session).by_project(project.entity_id)
        relation_views: list[dict[str, Any]] = []
        for relation in relations:
            if public_only and relation.evidence_id is None:
                continue  # public lineage relations must be evidenced (E-06)
            subject = await self.session.get(Entity, relation.subject_entity_id)
            relation_views.append(
                {
                    "relation_id": relation.id,
                    "subject_entity_id": relation.subject_entity_id,
                    "subject_name": subject.name if subject is not None else None,
                    "relation_role": relation.relation_role,
                    "official_name": relation.official_name,
                    "start_year": relation.start_year,
                    "end_year": relation.end_year,
                    "evidence_id": relation.evidence_id,
                }
            )
        return HeritageProjectView(
            entity_id=project.entity_id,
            project_name=project.project_name,
            official_name=project.official_name,
            category=project.category,
            publication_status=status,
            relations=tuple(relation_views),
        )

    def _serialize(self, view: HeritageProjectView) -> dict[str, Any]:
        return {
            "entity_id": view.entity_id,
            "project_name": view.project_name,
            "official_name": view.official_name,
            "category": view.category,
            "publication_status": view.publication_status,
            "relations": list(view.relations),
        }

    async def _published_subject_entity(self, entity_id: str) -> str | None:
        published = PublicationStatus.PUBLISHED.value
        stmt = (
            select(ContentArtifact.id)
            .join(PublicationRecord, PublicationRecord.artifact_id == ContentArtifact.id)
            .where(
                ContentArtifact.subject_entity_id == entity_id,
                PublicationRecord.publication_status == published,
            )
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def _publication_status(self, entity_id: str) -> str:
        stmt = (
            select(PublicationRecord.publication_status)
            .join(ContentArtifact, ContentArtifact.id == PublicationRecord.artifact_id)
            .where(ContentArtifact.subject_entity_id == entity_id)
            .order_by(PublicationRecord.updated_at.desc())
            .limit(1)
        )
        status = (await self.session.execute(stmt)).scalar_one_or_none()
        return str(status) if status is not None else "UNPUBLISHED"

    def _require_permission(self, principal: Principal, code: str) -> None:
        if not principal.is_authenticated or not principal.has_permission(code):
            raise PermissionError(f"missing permission: {code}")


async def published_heritage_entities(session: AsyncSession) -> set[str]:
    """Entity ids of published heritage projects (search predicate input)."""
    published = PublicationStatus.PUBLISHED.value
    stmt = select(ContentArtifact.subject_entity_id).where(
        ContentArtifact.subject_entity_id.is_not(None),
        ContentArtifact.id.in_(
            select(PublicationRecord.artifact_id).where(
                PublicationRecord.publication_status == published
            )
        ),
    )
    result = await session.execute(stmt)
    return {str(v) for v in result.scalars().all() if v is not None}
