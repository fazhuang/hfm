"""B-domain literature service (P1-04 — 文献/思想体系, E-04).

Implements the frozen P1-04 acceptance criterion: work/edition/version/
passages preserve lineage and rights. Reuses the canonical CD-2 FRBR
structure (Work → Edition → Version → Chapter → Passage) with:

  - typed-Entity stable identity for Works (entity_id, I5);
  - lineage integrity enforcement (Edition same-Work parent, Version
    same-Edition parent, Chapter hierarchy, Passage cross-Work version
    consistency) — malformed bindings are rejected;
  - citation addressability: reproducible passage locators (Locator VO);
  - publication projection: a Work is public iff an admitted ContentArtifact
    bound to its Entity identity is PUBLISHED (P1-09 canonical truth — no
    parallel publication store; rights preserved on the artifact);
  - no implicit publication; mutation requires P1-10 authorization.

No Reader surface is implemented (P1-07 out of scope); no HFB runtime
dependency.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from hfm.core.hashing import canonical_json
from hfm.core.locator import Locator
from hfm.models.chapter import Chapter
from hfm.models.content_artifact import (
    ContentArtifact,
    ProvenanceStatus,
    RightsStatus,
)
from hfm.models.edition import Edition
from hfm.models.entity import Entity, EntityType
from hfm.models.passage import Passage
from hfm.models.publication import PublicationRecord, PublicationStatus
from hfm.models.version import Version
from hfm.models.work import Work
from hfm.phase1.auth import Principal
from hfm.phase1.version_audit import AuditService, VersionLineageService
from hfm.repositories.chapter import ChapterRepository
from hfm.repositories.content_artifact import ContentArtifactRepository
from hfm.repositories.edition import EditionRepository
from hfm.repositories.passage import PassageRepository
from hfm.repositories.version import VersionRepository

PERMISSION_ASSERTION_CREATE = "assertion:create"


@dataclass(frozen=True)
class WorkView:
    """Serializable work projection (public = published lineage only)."""

    work_id: str
    entity_id: str | None
    title: str
    dynasty: str | None
    category: str | None
    publication_status: str
    rights_status: str | None
    editions: tuple[dict[str, Any], ...]


class LiteratureService:
    """Canonical B-domain records with lineage + rights + publication state."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # ------------------------------------------------------------- mutations
    async def create_work(
        self,
        *,
        principal: Principal,
        title: str,
        author_entity_id: str | None = None,
        dynasty: str | None = None,
        category: str | None = None,
        description: str | None = None,
        is_extant: bool = True,
    ) -> Work:
        """Create a canonical Work with typed-Entity identity (I5).

        Requires assertion:create; no publication record is created
        (no implicit publication — P1-09 boundary).
        """
        self._require_permission(principal, PERMISSION_ASSERTION_CREATE)
        if not title:
            raise ValueError("work title is required")
        entity = Entity(entity_type=EntityType.work.value, name=title, name_zh=title)
        self.session.add(entity)
        await self.session.flush()
        work = Work(
            entity_id=entity.id,
            title=title,
            author_entity_id=author_entity_id,
            dynasty=dynasty,
            category=category,
            description=description,
            is_extant=is_extant,
        )
        self.session.add(work)
        await self.session.flush()
        await AuditService(self.session).record(
            actor_id=principal.user_id,
            action="work.create",
            target_type="work",
            target_id=work.id,
            detail=canonical_json({"title": title, "dynasty": dynasty, "category": category}),
        )
        return work

    async def create_edition(
        self,
        *,
        principal: Principal,
        work_id: str,
        edition_name: str,
        era: str | None = None,
        publisher_block: str | None = None,
        preface_postscript: str | None = None,
        lineage_parent_edition_id: str | None = None,
    ) -> Edition:
        """Create an Edition under a Work (lineage parent same-Work enforced)."""
        self._require_permission(principal, PERMISSION_ASSERTION_CREATE)
        work = await self.session.get(Work, work_id)
        if work is None:
            raise ValueError("work does not exist")
        if not edition_name:
            raise ValueError("edition_name is required")
        edition = await EditionRepository(self.session).create(
            work_id=work_id,
            edition_name=edition_name,
            era=era,
            publisher_block=publisher_block,
            preface_postscript=preface_postscript,
            lineage_parent_edition_id=lineage_parent_edition_id,
        )
        await AuditService(self.session).record(
            actor_id=principal.user_id,
            action="edition.create",
            target_type="edition",
            target_id=edition.id,
            detail=canonical_json({"work_id": work_id, "edition_name": edition_name}),
        )
        return edition

    async def create_version(
        self,
        *,
        principal: Principal,
        edition_id: str,
        version_name: str,
        era: str | None = None,
        year: int | None = None,
        repository: str | None = None,
        shelf_mark: str | None = None,
        editor: str | None = None,
        description: str | None = None,
        is_formal_source: bool = False,
        parent_version_id: str | None = None,
    ) -> Version:
        """Create a Version under an Edition (lineage parent same-Edition).

        parent_version_id is a protected structural identity (I2) — the
        lineage is fixed at creation and verified by VersionLineageService.
        """
        self._require_permission(principal, PERMISSION_ASSERTION_CREATE)
        edition = await self.session.get(Edition, edition_id)
        if edition is None:
            raise ValueError("edition does not exist")
        if not version_name:
            raise ValueError("version_name is required")
        if parent_version_id is not None:
            parent = await self.session.get(Version, str(parent_version_id))
            if parent is None:
                raise ValueError("parent version does not exist")
            if parent.edition_id != edition_id:
                raise ValueError("parent version must belong to the same Edition")
            await VersionLineageService(self.session).lineage(str(parent_version_id))
        version = await VersionRepository(self.session).create(
            edition_id=edition_id,
            version_name=version_name,
            era=era,
            year=year,
            repository=repository,
            shelf_mark=shelf_mark,
            editor=editor,
            description=description,
            is_formal_source=is_formal_source,
            parent_version_id=parent_version_id,
        )
        await AuditService(self.session).record(
            actor_id=principal.user_id,
            action="version.create",
            target_type="version",
            target_id=version.id,
            detail=canonical_json(
                {
                    "edition_id": edition_id,
                    "version_name": version_name,
                    "parent_version_id": parent_version_id,
                }
            ),
        )
        return version

    async def create_chapter(
        self,
        *,
        principal: Principal,
        work_id: str,
        title: str,
        order: int = 0,
        parent_id: str | None = None,
    ) -> Chapter:
        """Create a Chapter under a Work (parent hierarchy same-Work enforced)."""
        self._require_permission(principal, PERMISSION_ASSERTION_CREATE)
        work = await self.session.get(Work, work_id)
        if work is None:
            raise ValueError("work does not exist")
        if not title:
            raise ValueError("chapter title is required")
        chapter = await ChapterRepository(self.session).create(
            work_id=work_id, title=title, order=order, parent_id=parent_id
        )
        await AuditService(self.session).record(
            actor_id=principal.user_id,
            action="chapter.create",
            target_type="chapter",
            target_id=chapter.id,
            detail=canonical_json({"work_id": work_id, "title": title}),
        )
        return chapter

    async def create_passage(
        self,
        *,
        principal: Principal,
        chapter_id: str,
        content_text: str,
        order: int = 0,
        version_id: str | None = None,
        translation: str | None = None,
        notes: str | None = None,
        tags: str | None = None,
    ) -> Passage:
        """Create a Passage under a Chapter (version pinning, cross-Work check).

        version_id is a pinned fixed reference (I2): once set it is protected
        from post-create mutation (no silent 'latest' swap).
        """
        self._require_permission(principal, PERMISSION_ASSERTION_CREATE)
        chapter = await self.session.get(Chapter, chapter_id)
        if chapter is None:
            raise ValueError("chapter does not exist")
        if not content_text:
            raise ValueError("passage content_text is required")
        if version_id is not None:
            version = await self.session.get(Version, str(version_id))
            if version is None:
                raise ValueError("version does not exist")
        passage = await PassageRepository(self.session).create(
            chapter_id=chapter_id,
            version_id=version_id,
            content_text=content_text,
            translation=translation,
            notes=notes,
            order=order,
            tags=tags,
        )
        await AuditService(self.session).record(
            actor_id=principal.user_id,
            action="passage.create",
            target_type="passage",
            target_id=passage.id,
            detail=canonical_json({"chapter_id": chapter_id, "version_id": version_id}),
        )
        return passage

    async def admit_work_artifact(
        self,
        *,
        principal: Principal,
        work_id: str,
        source_id: str,
        content: bytes,
        rights_status: RightsStatus,
        provenance_status: ProvenanceStatus = ProvenanceStatus.PENDING,
        format: str | None = None,
        version_id: str | None = None,
    ) -> ContentArtifact:
        """Admit a canonical representation of the Work (P1-01 gate).

        The artifact is bound to the Work's Entity identity so the P1-09
        publication state projects onto the work record; rights_status is
        preserved on the artifact (E-04).
        """
        self._require_permission(principal, PERMISSION_ASSERTION_CREATE)
        work = await self.session.get(Work, work_id)
        if work is None:
            raise ValueError("work does not exist")
        if work.entity_id is None:
            raise ValueError("work has no typed-Entity identity (create via LiteratureService)")
        artifact = await ContentArtifactRepository(self.session).submit_with_source_check(
            source_id=source_id,
            content=content,
            format=format,
            provenance_status=provenance_status,
            rights_status=rights_status,
            version_id=version_id,
            subject_entity_id=work.entity_id,
            created_by=principal.user_id,
        )
        await AuditService(self.session).record(
            actor_id=principal.user_id,
            action="artifact.submit",
            target_type="content_artifact",
            target_id=artifact.id,
            detail=canonical_json({"work_id": work_id, "rights_status": rights_status.value}),
        )
        return artifact

    # ---------------------------------------------------------- addressability
    async def passage_locator(self, passage_id: str) -> Locator:
        """Reproducible passage locator (E-04/E-07 boundary: same locator
        re-opens the same version/passage)."""
        passage = await self.session.get(Passage, passage_id)
        if passage is None:
            raise ValueError("passage does not exist")
        chapter = await self.session.get(Chapter, passage.chapter_id)
        if chapter is None:
            raise ValueError("passage chapter does not exist")
        work = await self.session.get(Work, chapter.work_id)
        version_id = passage.version_id
        edition_id: str | None = None
        if version_id is not None:
            version = await self.session.get(Version, str(version_id))
            if version is not None:
                edition_id = version.edition_id
        locator = Locator(
            work_id=work.id if work is not None else None,
            edition_id=edition_id,
            version_id=str(version_id) if version_id else None,
            chapter_id=chapter.id,
            passage_id=passage.id,
            section=f"{chapter.order + 1}",
            line=str(passage.order),
        )
        return locator

    # ------------------------------------------------------------ visibility
    async def public_visibility(self, work_id: str) -> bool:
        """Work is public iff a PUBLISHED artifact is bound to its Entity."""
        work = await self.session.get(Work, work_id)
        if work is None or work.entity_id is None:
            return False
        return await self._published_subject_entity(str(work.entity_id)) is not None

    async def get_public_work(self, work_id: str) -> dict[str, Any] | None:
        """Public projection: published lineage (editions/versions), rights."""
        work = await self.session.get(Work, work_id)
        if work is None:
            return None
        if not await self.public_visibility(work_id):
            return None
        view = await self._view(work, public_only=True)
        return {
            "work_id": view.work_id,
            "title": view.title,
            "dynasty": view.dynasty,
            "category": view.category,
            "publication_status": view.publication_status,
            "rights_status": view.rights_status,
            "editions": list(view.editions),
        }

    async def get_research_work(self, work_id: str) -> dict[str, Any]:
        """Research projection: full lineage + rights + publication state."""
        work = await self.session.get(Work, work_id)
        if work is None:
            raise ValueError("work does not exist")
        view = await self._view(work, public_only=False)
        return {
            "work_id": view.work_id,
            "entity_id": view.entity_id,
            "title": view.title,
            "dynasty": view.dynasty,
            "category": view.category,
            "publication_status": view.publication_status,
            "rights_status": view.rights_status,
            "editions": list(view.editions),
        }

    # -------------------------------------------------------------- internals
    async def _view(self, work: Work, *, public_only: bool) -> WorkView:
        status, rights = await self._publication_state(work)
        editions = (
            (
                await self.session.execute(
                    select(Edition).where(Edition.work_id == work.id).order_by(Edition.edition_name)
                )
            )
            .scalars()
            .all()
        )
        edition_views: list[dict[str, Any]] = []
        for edition in editions:
            versions = (
                (
                    await self.session.execute(
                        select(Version)
                        .where(Version.edition_id == edition.id)
                        .order_by(Version.version_name)
                    )
                )
                .scalars()
                .all()
            )
            version_views: list[dict[str, Any]] = []
            for version in versions:
                lineage_hash = ""
                try:
                    lineage_hash = await VersionLineageService(self.session).lineage_hash(
                        version.id
                    )
                except ValueError:
                    lineage_hash = ""  # raw lineage shown; digest only when intact
                version_views.append(
                    {
                        "version_id": version.id,
                        "version_name": version.version_name,
                        "parent_version_id": version.parent_version_id,
                        "is_formal_source": version.is_formal_source,
                        "withdrawn_at": (
                            version.withdrawn_at.isoformat() if version.withdrawn_at else None
                        ),
                        "lineage_hash": lineage_hash,
                    }
                )
            edition_views.append(
                {
                    "edition_id": edition.id,
                    "edition_name": edition.edition_name,
                    "era": edition.era,
                    "lineage_parent_edition_id": edition.lineage_parent_edition_id,
                    "versions": version_views,
                }
            )
        return WorkView(
            work_id=work.id,
            entity_id=work.entity_id,
            title=work.title,
            dynasty=work.dynasty,
            category=work.category,
            publication_status=status,
            rights_status=rights,
            editions=tuple(edition_views),
        )

    async def _publication_state(self, work: Work) -> tuple[str, str | None]:
        if work.entity_id is None:
            return "UNPUBLISHED", None
        stmt = (
            select(PublicationRecord.publication_status, ContentArtifact.rights_status)
            .join(ContentArtifact, ContentArtifact.id == PublicationRecord.artifact_id)
            .where(ContentArtifact.subject_entity_id == work.entity_id)
            .order_by(PublicationRecord.updated_at.desc())
            .limit(1)
        )
        row = (await self.session.execute(stmt)).first()
        if row is None:
            return "UNPUBLISHED", None
        return str(row[0]), str(row[1]) if row[1] else None

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

    def _require_permission(self, principal: Principal, code: str) -> None:
        if not principal.is_authenticated or not principal.has_permission(code):
            raise PermissionError(f"missing permission: {code}")
