"""C-domain service (P1-05 — 《针灸甲乙经》历史知识体系, E-05).

Implements the frozen P1-05 acceptance criterion: historical
disease/point/meridian/technique retrieval returns source/version/citation;
no diagnosis, treatment, ranking or prescription (AB-14).

  - CDomainTerm records with typed-Entity identity (I5), anchored to the
    versioned literature (canonical_passage_id — P1-04 reuse);
  - structured historical relations among terms with evidence binding
    (evidence_id → evidences.id, P1-02 reuse);
  - retrieval returns: term + related structured historical records +
    original text/source (passage) + Citation/Evidence/Version context;
  - public projection: a term is public iff an admitted ContentArtifact
    bound to its Entity identity is PUBLISHED (P1-09 canonical truth — no
    parallel publication store); relations are public only when evidenced;
  - no implicit publication; mutation requires P1-10 authorization.

No clinical advice semantics are implemented (AB-14 / ADR-02 Guard-02) —
there is no diagnosis/treatment/prescription surface anywhere.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from hfm.core.hashing import canonical_json
from hfm.models.c_domain import (
    CDomainRelation,
    CDomainRelationType,
    CDomainTerm,
    CDomainTermType,
)
from hfm.models.content_artifact import (
    ContentArtifact,
    ProvenanceStatus,
    RightsStatus,
)
from hfm.models.entity import Entity, EntityType
from hfm.models.passage import Passage
from hfm.models.publication import PublicationRecord, PublicationStatus
from hfm.phase1.auth import Principal
from hfm.phase1.version_audit import AuditService, VersionLineageService
from hfm.repositories.c_domain import CDomainRelationRepository, CDomainTermRepository
from hfm.repositories.content_artifact import ContentArtifactRepository

PERMISSION_ASSERTION_CREATE = "assertion:create"


@dataclass(frozen=True)
class CDomainTermView:
    """Serializable C-domain term projection."""

    entity_id: str
    term_type: str
    term_name: str
    publication_status: str
    canonical_passage_id: str | None
    relations: tuple[dict[str, Any], ...]


class CDomainService:
    """Canonical C-domain records with source/version/citation retrieval."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # ------------------------------------------------------------- mutations
    async def create_term(
        self,
        *,
        principal: Principal,
        term_type: str,
        term_name: str,
        canonical_passage_id: str | None = None,
        description: str | None = None,
    ) -> CDomainTerm:
        """Create a canonical C-domain term (typed-Entity identity).

        Requires assertion:create; never creates a publication record
        (no implicit publication — P1-09 boundary).
        """
        self._require_permission(principal, PERMISSION_ASSERTION_CREATE)
        if not term_name:
            raise ValueError("c-domain term_name is required")
        term_type_enum = CDomainTermType(term_type)
        entity_type = (
            EntityType.acupoint.value
            if term_type_enum == CDomainTermType.acupoint
            else EntityType.concept.value
        )
        entity = Entity(
            entity_type=entity_type,
            name=term_name,
            name_zh=term_name,
            description=description,
        )
        self.session.add(entity)
        await self.session.flush()
        if canonical_passage_id is not None:
            passage = await self.session.get(Passage, canonical_passage_id)
            if passage is None:
                raise ValueError("canonical passage does not exist")
        term = await CDomainTermRepository(self.session).create(
            entity_id=entity.id,
            term_type=term_type_enum.value,
            term_name=term_name,
            canonical_passage_id=canonical_passage_id,
            description=description,
            created_by=principal.user_id,
        )
        await AuditService(self.session).record(
            actor_id=principal.user_id,
            action="c_domain_term.create",
            target_type="c_domain_term",
            target_id=term.entity_id,
            detail=canonical_json({"term_type": term_type, "term_name": term_name}),
        )
        return term

    async def create_relation(
        self,
        *,
        principal: Principal,
        source_term_entity_id: str,
        target_term_entity_id: str,
        relation_type: str,
        evidence_id: str | None = None,
        description: str | None = None,
    ) -> CDomainRelation:
        """Create a structured historical relation between two C terms.

        Requires assertion:create; relation bindings are immutable (I4);
        evidence anchoring follows P1-02.
        """
        self._require_permission(principal, PERMISSION_ASSERTION_CREATE)
        relation = await CDomainRelationRepository(self.session).create(
            source_term_entity_id=source_term_entity_id,
            target_term_entity_id=target_term_entity_id,
            relation_type=CDomainRelationType(relation_type).value,
            evidence_id=evidence_id,
            description=description,
            created_by=principal.user_id,
        )
        await AuditService(self.session).record(
            actor_id=principal.user_id,
            action="c_domain_relation.create",
            target_type="c_domain_relation",
            target_id=relation.id,
            detail=canonical_json(
                {
                    "source_term_entity_id": source_term_entity_id,
                    "target_term_entity_id": target_term_entity_id,
                    "relation_type": relation.relation_type,
                    "evidence_id": evidence_id,
                }
            ),
        )
        return relation

    async def admit_term_artifact(
        self,
        *,
        principal: Principal,
        term_entity_id: str,
        source_id: str,
        content: bytes,
        rights_status: RightsStatus,
        provenance_status: ProvenanceStatus = ProvenanceStatus.PENDING,
        format: str | None = None,
        version_id: str | None = None,
    ) -> ContentArtifact:
        """Admit a canonical representation of the term (P1-01 gate).

        The artifact is bound to the term's Entity identity so the P1-09
        publication state projects onto the term record.
        """
        self._require_permission(principal, PERMISSION_ASSERTION_CREATE)
        term = await CDomainTermRepository(self.session).get_by_entity_id(term_entity_id)
        if term is None:
            raise ValueError("c-domain term does not exist")
        artifact = await ContentArtifactRepository(self.session).submit_with_source_check(
            source_id=source_id,
            content=content,
            format=format,
            provenance_status=provenance_status,
            rights_status=rights_status,
            version_id=version_id,
            subject_entity_id=term.entity_id,
            created_by=principal.user_id,
        )
        await AuditService(self.session).record(
            actor_id=principal.user_id,
            action="artifact.submit",
            target_type="content_artifact",
            target_id=artifact.id,
            detail=canonical_json({"term_entity_id": term.entity_id}),
        )
        return artifact

    # ------------------------------------------------------------ visibility
    async def public_visibility(self, term_entity_id: str) -> bool:
        """Term is public iff a PUBLISHED artifact is bound to its Entity."""
        return await self._published_subject_entity(term_entity_id) is not None

    async def get_public_term(self, term_entity_id: str) -> dict[str, Any] | None:
        """Public projection: term + evidenced historical relations + source.

        Returns the term record, its canonical passage (source text with
        version lineage), and every evidenced historical relation. Absent
        publication → None (404 at the API layer).
        """
        term = await CDomainTermRepository(self.session).get_by_entity_id(term_entity_id)
        if term is None:
            return None
        if not await self.public_visibility(term_entity_id):
            return None
        view = await self._view(term, public_only=True)
        return await self._serialize_with_passage(view)

    async def get_research_term(self, term_entity_id: str) -> dict[str, Any]:
        """Research projection: full term record incl. all relations + state."""
        term = await CDomainTermRepository(self.session).get_by_entity_id(term_entity_id)
        if term is None:
            raise ValueError("c-domain term does not exist")
        view = await self._view(term, public_only=False)
        return await self._serialize_with_passage(view)

    async def list_public_terms(self, query: str | None = None) -> list[dict[str, Any]]:
        """Published C-domain terms (P1-08 search integration, public predicate)."""
        published = PublicationStatus.PUBLISHED.value
        published_subjects = select(ContentArtifact.subject_entity_id).where(
            ContentArtifact.subject_entity_id.is_not(None),
            ContentArtifact.id.in_(
                select(PublicationRecord.artifact_id).where(
                    PublicationRecord.publication_status == published
                )
            ),
        )
        base = select(CDomainTerm).where(CDomainTerm.entity_id.in_(published_subjects))
        if query:
            pattern = f"%{query}%"
            base = base.where(CDomainTerm.term_name.ilike(pattern))
        terms = (await self.session.execute(base.order_by(CDomainTerm.term_name))).scalars().all()
        result: list[dict[str, Any]] = []
        for term in terms:
            view = await self._view(term, public_only=True)
            result.append(
                {
                    "entity_id": view.entity_id,
                    "term_type": view.term_type,
                    "term_name": view.term_name,
                    "publication_status": view.publication_status,
                }
            )
        return result

    # -------------------------------------------------------------- internals
    async def _view(self, term: CDomainTerm, *, public_only: bool) -> CDomainTermView:
        status = await self._publication_status(term.entity_id)
        relations = await CDomainRelationRepository(self.session).by_term(term.entity_id)
        relation_views: list[dict[str, Any]] = []
        for relation in relations:
            if public_only and relation.evidence_id is None:
                continue  # public relations must be evidenced (E-05)
            other_id = (
                relation.target_term_entity_id
                if relation.source_term_entity_id == term.entity_id
                else relation.source_term_entity_id
            )
            other = await CDomainTermRepository(self.session).get_by_entity_id(other_id)
            relation_views.append(
                {
                    "relation_id": relation.id,
                    "relation_type": relation.relation_type,
                    "source_term_entity_id": relation.source_term_entity_id,
                    "target_term_entity_id": relation.target_term_entity_id,
                    "other_term_entity_id": other_id,
                    "other_term_name": other.term_name if other is not None else None,
                    "evidence_id": relation.evidence_id,
                }
            )
        return CDomainTermView(
            entity_id=term.entity_id,
            term_type=term.term_type,
            term_name=term.term_name,
            publication_status=status,
            canonical_passage_id=term.canonical_passage_id,
            relations=tuple(relation_views),
        )

    async def _serialize_with_passage(self, view: CDomainTermView) -> dict[str, Any]:
        """Serialize a term view resolving the async passage/version context."""
        data: dict[str, Any] = {
            "entity_id": view.entity_id,
            "term_type": view.term_type,
            "term_name": view.term_name,
            "publication_status": view.publication_status,
            "relations": list(view.relations),
        }
        if view.canonical_passage_id is not None:
            data["canonical_passage"] = await self._passage_context(view.canonical_passage_id)
        return data

    async def _passage_context(self, passage_id: str) -> dict[str, Any]:
        passage = await self.session.get(Passage, passage_id)
        if passage is None:
            return {}
        context: dict[str, Any] = {
            "passage_id": passage.id,
            "chapter_id": passage.chapter_id,
            "version_id": passage.version_id,
        }
        if passage.version_id is not None:
            try:
                context["lineage_hash"] = await VersionLineageService(self.session).lineage_hash(
                    passage.version_id
                )
            except ValueError:
                context["lineage_hash"] = None
        return context

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


async def published_c_term_entities(session: AsyncSession) -> set[str]:
    """Entity ids of published C-domain terms (search predicate input)."""
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
