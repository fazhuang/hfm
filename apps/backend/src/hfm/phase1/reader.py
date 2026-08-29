"""Versioned source reader service (P1-07 — P1-READER, E-07).

Implements the frozen P1-07 acceptance criterion: a passage locator
reproducibly opens source context and citation; no reader access to
unauthorized draft (AB-09).

  - resolve a Locator string (or a passage id) to a reader view carrying:
    quotation (passage text + translation/notes), source context
    (Work/Edition/Version lineage with the deterministic lineage digest),
    citation context (Citations referencing the passage), rights display,
    and publication state;
  - deterministic resolution: the returned ``locator`` is the canonical
    locator derived from the passage's FK ancestry (P1-04
    ``LiteratureService.passage_locator``), so the same locator always
    re-opens the same version/passage (E-07); entity ids supplied in the
    input locator are cross-validated against that ancestry and rejected
    on mismatch (fail-closed malformed binding);
  - public reader: fail-closed — a passage is publicly readable only when
    it belongs to an approved published projection (a PUBLISHED artifact
    bound to the Work lineage, a PUBLISHED artifact bound through
    Evidence, or the canonical passage of a PUBLISHED C-domain term —
    P1-02/04/05/09 projections) and its pinned Version is not withdrawn;
    any other case resolves to ``None`` (404 at the API layer) so draft
    content never leaks;
  - research reader: requires an authenticated principal (P1-10 RBAC);
    exposes the richer evidence chain context
    (Source→SourceRef→Evidence + Citation targets);
  - no relation traversal and no clinical recommendation surface (AB-14):
    the reader returns the passage and its source/citation context only.

No schema change is required: the reader is a read-only projection over
the accepted canonical tables. No HFB runtime dependency; no production
import.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from hfm.core.locator import Locator
from hfm.models.c_domain import CDomainTerm
from hfm.models.chapter import Chapter
from hfm.models.citation import Citation
from hfm.models.content_artifact import ContentArtifact
from hfm.models.edition import Edition
from hfm.models.evidence import Evidence
from hfm.models.passage import Passage
from hfm.models.publication import PublicationRecord, PublicationStatus
from hfm.models.source import Source
from hfm.models.source_ref import SourceRef
from hfm.models.version import Version
from hfm.models.work import Work
from hfm.phase1.auth import Principal
from hfm.phase1.literature import LiteratureService
from hfm.phase1.version_audit import VersionLineageService


@dataclass(frozen=True)
class ReaderCitation:
    """One Citation referencing the passage (citation context)."""

    citation_id: str
    quote_text: str | None
    target_assertion_id: str | None = None
    note: str | None = None


@dataclass(frozen=True)
class ReaderEvidence:
    """One Evidence bound to the passage (evidence context)."""

    evidence_id: str
    description: str
    evidence_level: str
    taint_status: str
    source_ref_id: str | None
    source_ref_title: str | None
    source_id: str | None
    source_title: str | None


@dataclass(frozen=True)
class ReaderView:
    """Serializable versioned source reader projection (AB-09)."""

    locator: str
    passage_id: str
    quotation: str
    translation: str | None
    notes: str | None
    work: dict[str, Any]
    edition: dict[str, Any] | None
    version: dict[str, Any] | None
    chapter: dict[str, Any]
    citations: tuple[ReaderCitation, ...]
    evidence: tuple[ReaderEvidence, ...]
    rights: dict[str, Any] | None
    publication_status: str


class ReaderService:
    """Versioned source reader — reproducible locator → source + citation."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # ------------------------------------------------------------ public
    async def resolve_public(
        self, *, locator: str = "", passage_id: str = ""
    ) -> dict[str, Any] | None:
        """Public reader: PUBLISHED projection only; fail closed to None.

        Malformed locators, missing passages, unpublished/draft content,
        and withdrawn versions all resolve to ``None`` (404 at the API
        layer) — no information about unpublished material is leaked.
        """
        try:
            passage, canonical = await self._anchor(locator=locator, passage_id=passage_id)
        except ValueError:
            return None
        if not await self._passage_public(passage.id):
            return None
        view = await self._view(passage, canonical, public_only=True)
        return self._serialize(view)

    # ---------------------------------------------------------- research
    async def resolve_research(
        self, *, principal: Principal, locator: str = "", passage_id: str = ""
    ) -> dict[str, Any]:
        """Research reader: authenticated; richer evidence chain context."""
        if not principal.is_authenticated:
            raise PermissionError("reader requires authentication")
        passage, canonical = await self._anchor(locator=locator, passage_id=passage_id)
        view = await self._view(passage, canonical, public_only=False)
        return self._serialize(view)

    # ------------------------------------------------------------ anchors
    async def _anchor(self, *, locator: str = "", passage_id: str = "") -> tuple[Passage, Locator]:
        """Resolve the anchor passage + canonical locator; fail closed.

        The canonical locator is always derived from the passage's FK
        ancestry (LiteratureService.passage_locator) so resolution is
        deterministic (E-07): client-supplied entity ids are validated
        against that ancestry, never trusted blindly.
        """
        if locator:
            parsed = Locator.from_locator_string(locator)
            if parsed.passage_id is None:
                raise ValueError("locator must carry a passage anchor")
            passage = await self.session.get(Passage, parsed.passage_id)
            if passage is None:
                raise ValueError("passage does not exist")
            await self._validate_ancestry(passage, parsed)
            canonical = await LiteratureService(self.session).passage_locator(passage.id)
            return passage, canonical
        if passage_id:
            passage = await self.session.get(Passage, passage_id)
            if passage is None:
                raise ValueError("passage does not exist")
            canonical = await LiteratureService(self.session).passage_locator(passage.id)
            return passage, canonical
        raise ValueError("locator or passage_id is required")

    async def _validate_ancestry(self, passage: Passage, locator: Locator) -> None:
        """Fail closed: locator entity ids must match the passage ancestry."""
        chapter = await self.session.get(Chapter, passage.chapter_id)
        if chapter is None:
            raise ValueError("passage chapter does not exist")
        work = await self.session.get(Work, chapter.work_id)
        if locator.work_id is not None and (work is None or locator.work_id != work.id):
            raise ValueError("locator work_id does not match the passage ancestry")
        if locator.chapter_id is not None and locator.chapter_id != passage.chapter_id:
            raise ValueError("locator chapter_id does not match the passage ancestry")
        if locator.version_id is not None and locator.version_id != passage.version_id:
            raise ValueError("locator version_id does not match the passage ancestry")
        if locator.edition_id is not None:
            version = (
                await self.session.get(Version, passage.version_id)
                if passage.version_id is not None
                else None
            )
            if version is None or locator.edition_id != version.edition_id:
                raise ValueError("locator edition_id does not match the passage ancestry")

    # --------------------------------------------------------- publicity
    async def _passage_public(self, passage_id: str) -> bool:
        """Passage belongs to an approved public projection (not withdrawn)."""
        if await self._version_withdrawn(passage_id):
            return False
        published = PublicationStatus.PUBLISHED.value
        published_artifacts = select(PublicationRecord.artifact_id).where(
            PublicationRecord.publication_status == published
        )
        # (a) PUBLISHED artifact bound to the Work lineage / canonical C term
        #     (P1-04 / P1-05 public projections, subject_entity binding);
        authorizing = await self._authorizing_entities(passage_id)
        if authorizing:
            bound = select(ContentArtifact.id).where(
                ContentArtifact.subject_entity_id.in_(authorizing),
                ContentArtifact.id.in_(published_artifacts),
            )
            if (await self.session.execute(bound)).scalar_one_or_none() is not None:
                return True
        # (b) Evidence bound to a PUBLISHED artifact (P1-08 public search
        #     predicate — a passage discoverable publicly must be readable).
        ev = select(Evidence.id).where(
            Evidence.source_passage_id == passage_id,
            Evidence.artifact_id.is_not(None),
            Evidence.artifact_id.in_(published_artifacts),
        )
        return (await self.session.execute(ev)).scalar_one_or_none() is not None

    async def _authorizing_entities(self, passage_id: str) -> set[str]:
        """Entity identities whose publication projection authorizes the passage."""
        entities: set[str] = set()
        passage = await self.session.get(Passage, passage_id)
        if passage is not None:
            chapter = await self.session.get(Chapter, passage.chapter_id)
            if chapter is not None:
                work = await self.session.get(Work, chapter.work_id)
                if work is not None and work.entity_id is not None:
                    entities.add(str(work.entity_id))
        # canonical passage of C-domain terms (P1-05 public projection)
        terms = (
            (
                await self.session.execute(
                    select(CDomainTerm.entity_id).where(
                        CDomainTerm.canonical_passage_id == passage_id
                    )
                )
            )
            .scalars()
            .all()
        )
        entities.update(str(t) for t in terms)
        # artifact subjects bound to the passage through Evidence (P1-02)
        subjects = (
            (
                await self.session.execute(
                    select(ContentArtifact.subject_entity_id)
                    .join(Evidence, Evidence.artifact_id == ContentArtifact.id)
                    .where(
                        Evidence.source_passage_id == passage_id,
                        ContentArtifact.subject_entity_id.is_not(None),
                    )
                )
            )
            .scalars()
            .all()
        )
        entities.update(str(s) for s in subjects)
        return entities

    async def _version_withdrawn(self, passage_id: str) -> bool:
        """Fail closed: a withdrawn pinned Version is never readable publicly."""
        passage = await self.session.get(Passage, passage_id)
        if passage is None or passage.version_id is None:
            return False
        version = await self.session.get(Version, passage.version_id)
        if version is None:
            return True  # broken pin → fail closed
        return version.withdrawn_at is not None

    # -------------------------------------------------------------- views
    async def _view(self, passage: Passage, canonical: Locator, *, public_only: bool) -> ReaderView:
        chapter = await self.session.get(Chapter, passage.chapter_id)
        work = await self.session.get(Work, chapter.work_id) if chapter is not None else None
        version = (
            await self.session.get(Version, passage.version_id)
            if passage.version_id is not None
            else None
        )
        edition = (
            await self.session.get(Edition, version.edition_id) if version is not None else None
        )
        work_view = {
            "work_id": work.id if work is not None else None,
            "title": work.title if work is not None else None,
            "dynasty": work.dynasty if work is not None else None,
            "category": work.category if work is not None else None,
        }
        edition_view = None
        if edition is not None:
            edition_view = {
                "edition_id": edition.id,
                "edition_name": edition.edition_name,
                "era": edition.era,
                "publisher_block": edition.publisher_block,
            }
        version_view = None
        if version is not None:
            lineage_hash = ""
            try:
                lineage_hash = await VersionLineageService(self.session).lineage_hash(version.id)
            except ValueError:
                lineage_hash = ""  # raw lineage shown; digest only when intact
            version_view = {
                "version_id": version.id,
                "version_name": version.version_name,
                "era": version.era,
                "year": version.year,
                "repository": version.repository,
                "shelf_mark": version.shelf_mark,
                "editor": version.editor,
                "is_formal_source": version.is_formal_source,
                "withdrawn_at": version.withdrawn_at.isoformat() if version.withdrawn_at else None,
                "lineage_hash": lineage_hash,
            }
        chapter_view = {
            "chapter_id": chapter.id if chapter is not None else None,
            "title": chapter.title if chapter is not None else None,
            "order": chapter.order if chapter is not None else None,
        }
        citations = await self._citations(passage.id, public_only=public_only)
        evidence = await self._evidence(passage.id, public_only=public_only)
        rights = await self._rights_display(passage.id, public_only=public_only)
        return ReaderView(
            locator=canonical.to_locator_string(),
            passage_id=passage.id,
            quotation=passage.content_text,
            translation=passage.translation,
            notes=passage.notes,
            work=work_view,
            edition=edition_view,
            version=version_view,
            chapter=chapter_view,
            citations=citations,
            evidence=evidence,
            rights=rights,
            publication_status="PUBLISHED" if public_only else self._status_or(rights),
        )

    @staticmethod
    def _status_or(rights: dict[str, Any] | None) -> str:
        if rights is not None and rights.get("publication_status"):
            return str(rights["publication_status"])
        return "UNPUBLISHED"

    async def _citations(self, passage_id: str, *, public_only: bool) -> tuple[ReaderCitation, ...]:
        rows = (
            (
                await self.session.execute(
                    select(Citation)
                    .where(Citation.passage_id == passage_id)
                    .order_by(Citation.created_at)
                )
            )
            .scalars()
            .all()
        )
        result: list[ReaderCitation] = []
        for c in rows:
            result.append(
                ReaderCitation(
                    citation_id=c.id,
                    quote_text=c.quote_text,
                    target_assertion_id=None if public_only else c.target_assertion_id,
                    note=None if public_only else c.note,
                )
            )
        return tuple(result)

    async def _evidence(self, passage_id: str, *, public_only: bool) -> tuple[ReaderEvidence, ...]:
        rows = (
            (
                await self.session.execute(
                    select(Evidence)
                    .where(Evidence.source_passage_id == passage_id)
                    .order_by(Evidence.created_at)
                )
            )
            .scalars()
            .all()
        )
        result: list[ReaderEvidence] = []
        for ev in rows:
            source_ref = (
                await self.session.get(SourceRef, ev.source_ref_id)
                if ev.source_ref_id is not None
                else None
            )
            source = (
                await self.session.get(Source, source_ref.source_id)
                if source_ref is not None
                else None
            )
            result.append(
                ReaderEvidence(
                    evidence_id=ev.id,
                    description="" if public_only else ev.description,
                    evidence_level=str(ev.evidence_level.value),
                    taint_status="" if public_only else ev.taint_status,
                    source_ref_id=ev.source_ref_id,
                    source_ref_title=(
                        None if public_only else (source_ref.title if source_ref else None)
                    ),
                    source_id=source.id if source is not None else None,
                    source_title=(None if public_only else (source.title if source else None)),
                )
            )
        return tuple(result)

    async def _rights_display(self, passage_id: str, *, public_only: bool) -> dict[str, Any] | None:
        """Rights/provenance of the publication projection authorizing the passage."""
        authorizing = await self._authorizing_entities(passage_id)
        if not authorizing:
            return None
        stmt = (
            select(
                ContentArtifact.rights_status,
                ContentArtifact.provenance_status,
                PublicationRecord.publication_status,
            )
            .join(PublicationRecord, PublicationRecord.artifact_id == ContentArtifact.id)
            .where(ContentArtifact.subject_entity_id.in_(authorizing))
            .order_by(PublicationRecord.updated_at.desc())
            .limit(1)
        )
        row = (await self.session.execute(stmt)).first()
        if row is None:
            return None
        return {
            "rights_status": str(row[0]) if row[0] is not None else None,
            "provenance_status": str(row[1]) if row[1] is not None else None,
            "publication_status": str(row[2]),
        }

    # ------------------------------------------------------- serialization
    @staticmethod
    def _serialize(view: ReaderView) -> dict[str, Any]:
        return {
            "locator": view.locator,
            "passage_id": view.passage_id,
            "quotation": view.quotation,
            "translation": view.translation,
            "notes": view.notes,
            "work": view.work,
            "edition": view.edition,
            "version": view.version,
            "chapter": view.chapter,
            "citations": [
                {
                    "citation_id": c.citation_id,
                    "quote_text": c.quote_text,
                    **(
                        {}
                        if c.target_assertion_id is None and c.note is None
                        else {"target_assertion_id": c.target_assertion_id, "note": c.note}
                    ),
                }
                for c in view.citations
            ],
            "evidence": [
                {
                    "evidence_id": e.evidence_id,
                    "evidence_level": e.evidence_level,
                    **(
                        {}
                        if not e.description and not e.taint_status and not e.source_ref_title
                        else {
                            "description": e.description,
                            "taint_status": e.taint_status,
                            "source_ref_id": e.source_ref_id,
                            "source_ref_title": e.source_ref_title,
                            "source_id": e.source_id,
                            "source_title": e.source_title,
                        }
                    ),
                }
                for e in view.evidence
            ],
            "rights": view.rights,
            "publication_status": view.publication_status,
        }
