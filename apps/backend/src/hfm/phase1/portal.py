"""Public approved-content portal service (P1-11 — P1-PORTAL, E-11).

Anonymous portal over the approved publication projection (AB-02/05/07,
ADR-01/05): an anonymous visitor sees published content only.

  - ``home``: aggregate published projection — published Works (with
    edition counts) plus published counts per domain (Work/Person/
    Heritage/C-domain term);
  - ``works``: deterministic paginated list of published Works;
  - ``work_editions``: editions of a published Work (``None`` when the
    Work is not published — no leak of unpublished lineages).

Fail-closed rules (frozen P1-11 acceptance): DRAFT, PRIVATE/unauthorized,
WITHDRAWN and missing-publication content is never returned; withdrawal
removes the public projection immediately. The public predicate is the
canonical one — a PUBLISHED ``PublicationRecord`` bound to a
``ContentArtifact`` whose ``subject_entity_id`` is the record's entity
(P1-04/P1-05/P1-06/P1-09 projections), matching the accepted reader and
search predicates.

Responses are strict whitelist projections: no internal entity ids, no
provenance/rights/hash fields, no research state, no relation traversal,
no clinical recommendation semantics (AB-14). Only accepted canonical
truth stores are consumed — no duplicate Source/SourceRef/Artifact/
Version/Citation/Evidence/Publication/RBAC store is created.

No schema change is required (read-only projection; Alembic stays at
0012). No HFB runtime dependency; no production import.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from hfm.models.c_domain import CDomainTerm
from hfm.models.content_artifact import ContentArtifact
from hfm.models.edition import Edition
from hfm.models.heritage import HeritageProject
from hfm.models.person import Person
from hfm.models.publication import PublicationRecord, PublicationStatus
from hfm.models.work import Work

_PAGE_SIZE_MAX = 100


def _count_result(result: Any) -> int:
    """Coerce a scalar count; malformed/absent results fail closed to 0."""
    try:
        return int(result.scalar() or 0)
    except (TypeError, ValueError):
        return 0


class PortalService:
    """Anonymous public portal projection (approved content only)."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # -------------------------------------------------------------- helpers
    @staticmethod
    def _validate_paging(page: int, page_size: int) -> None:
        if page < 1 or page_size < 1 or page_size > _PAGE_SIZE_MAX:
            raise ValueError("invalid pagination")

    async def _published_subject_entities(self) -> set[str]:
        """Entity ids of records inside the approved publication projection."""
        published = PublicationStatus.PUBLISHED.value
        rows = await self.session.execute(
            select(ContentArtifact.subject_entity_id)
            .join(PublicationRecord, PublicationRecord.artifact_id == ContentArtifact.id)
            .where(
                ContentArtifact.subject_entity_id.is_not(None),
                PublicationRecord.publication_status == published,
            )
        )
        return {str(r) for r in rows.scalars().all()}

    async def _edition_counts(self, work_ids: tuple[str, ...]) -> dict[str, int]:
        """Edition count per Work (accepted lineage — P1-04)."""
        if not work_ids:
            return {}
        rows = (
            await self.session.execute(
                select(Edition.work_id, func.count(Edition.id))
                .where(Edition.work_id.in_(work_ids))
                .group_by(Edition.work_id)
            )
        ).all()
        counts: dict[str, int] = {}
        for work_id, count in rows:
            try:
                counts[str(work_id)] = int(count)
            except (TypeError, ValueError):
                counts[str(work_id)] = 0
        return counts

    async def _count_subjects(self, model: type[Any], subjects: set[str]) -> int:
        """Published count for one domain (entity-id bound projection)."""
        result = await self.session.execute(
            select(func.count(model.id)).where(model.entity_id.in_(subjects))
        )
        return _count_result(result)

    @staticmethod
    def _serialize_work(work: Work, edition_count: int) -> dict[str, Any]:
        """Strict public whitelist — no entity_id, no internal provenance."""
        return {
            "work_id": work.id,
            "title": work.title,
            "dynasty": work.dynasty,
            "category": work.category,
            "edition_count": edition_count,
            "publication_status": PublicationStatus.PUBLISHED.value,
        }

    # ------------------------------------------------------------- surfaces
    async def home(self) -> dict[str, Any]:
        """Portal home: published Works + published counts per domain."""
        subjects = await self._published_subject_entities()
        if not subjects:
            return {
                "works": [],
                "counts": {
                    "works": 0,
                    "persons": 0,
                    "heritage_projects": 0,
                    "c_terms": 0,
                },
            }
        work_rows = (
            (
                await self.session.execute(
                    select(Work)
                    .where(Work.entity_id.in_(subjects))
                    .order_by(Work.created_at.desc(), Work.id)
                    .limit(10)
                )
            )
            .scalars()
            .all()
        )
        counts = await self._edition_counts(tuple(w.id for w in work_rows))
        works = [self._serialize_work(w, counts.get(w.id, 0)) for w in work_rows]
        return {
            "works": works,
            "counts": {
                "works": await self._count_subjects(Work, subjects),
                "persons": await self._count_subjects(Person, subjects),
                "heritage_projects": await self._count_subjects(HeritageProject, subjects),
                "c_terms": await self._count_subjects(CDomainTerm, subjects),
            },
        }

    async def works(self, *, page: int = 1, page_size: int = 20) -> dict[str, Any]:
        """Deterministic paginated list of published Works."""
        self._validate_paging(page, page_size)
        subjects = await self._published_subject_entities()
        if not subjects:
            return {"works": [], "total": 0, "page": page}
        base = select(Work).where(Work.entity_id.in_(subjects))
        total_result = await self.session.execute(select(func.count()).select_from(base.subquery()))
        total = _count_result(total_result)
        rows = (
            (
                await self.session.execute(
                    base.order_by(Work.created_at.desc(), Work.id)
                    .limit(page_size)
                    .offset((page - 1) * page_size)
                )
            )
            .scalars()
            .all()
        )
        counts = await self._edition_counts(tuple(w.id for w in rows))
        works = [self._serialize_work(w, counts.get(w.id, 0)) for w in rows]
        return {"works": works, "total": total, "page": page}

    @staticmethod
    def _serialize_person(person: Person) -> dict[str, Any]:
        """Strict public whitelist for the persons list."""
        return {
            "entity_id": person.entity_id,
            "name_zh": person.name_zh,
            "name_pinyin": person.name_pinyin,
            "dynasty": person.dynasty,
            "publication_status": PublicationStatus.PUBLISHED.value,
        }

    async def persons(self, *, page: int = 1, page_size: int = 20) -> dict[str, Any]:
        """Deterministic paginated list of published Persons (pre-acceptance demo)."""
        self._validate_paging(page, page_size)
        subjects = await self._published_subject_entities()
        if not subjects:
            return {"persons": [], "total": 0, "page": page}
        base = select(Person).where(Person.entity_id.in_(subjects))
        total = _count_result(
            await self.session.execute(select(func.count()).select_from(base.subquery()))
        )
        rows = (
            (
                await self.session.execute(
                    base.order_by(Person.created_at.desc(), Person.id)
                    .limit(page_size)
                    .offset((page - 1) * page_size)
                )
            )
            .scalars()
            .all()
        )
        return {
            "persons": [self._serialize_person(p) for p in rows],
            "total": total,
            "page": page,
        }

    async def work_editions(self, work_id: str) -> list[dict[str, Any]] | None:
        """Editions of a published Work; None when the Work is not published."""
        work = await self.session.get(Work, work_id)
        if work is None or work.entity_id is None:
            return None
        subjects = await self._published_subject_entities()
        if str(work.entity_id) not in subjects:
            return None
        editions = (
            (
                await self.session.execute(
                    select(Edition)
                    .where(Edition.work_id == work.id)
                    .order_by(Edition.edition_name, Edition.id)
                )
            )
            .scalars()
            .all()
        )
        return [
            {
                "edition_id": e.id,
                "edition_name": e.edition_name,
                "era": e.era,
                "publisher_block": e.publisher_block,
            }
            for e in editions
        ]
