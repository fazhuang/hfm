"""Unified search service (P1-08 — ADR-02, PostgreSQL-native).

Search predicates are server-side and mandatory (ADR-02 Guard-01):
  - public search hard-injects the publication predicate: only passages
    referenced by Evidence bound to a PUBLISHED ContentArtifact are returned;
  - research search requires an authenticated principal;
  - admin search additionally requires content:review.
P1-03/P1-04 integration (frontier-3): person-domain records (Entity
person) and Works are searchable — public person/Work hits are restricted
by the canonical PUBLISHED artifact binding (subject_entity_id), so
unpublished A/B content is excluded from public search; research visibility
obeys RBAC (authenticated only). No second search subsystem.

Matching uses portable ILIKE (Chinese substring works on PostgreSQL and the
SQLite test path); production has pg_trgm GIN indexes (migration 0010,
PostgreSQL-only). No Elasticsearch / external search; no clinical ranking
(ADR-02 Guard-02). Visibility predicates are always server-side.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from hfm.models.content_artifact import ContentArtifact
from hfm.models.entity import Entity, EntityType
from hfm.models.evidence import Evidence
from hfm.models.passage import Passage
from hfm.models.publication import PublicationRecord, PublicationStatus
from hfm.models.work import Work
from hfm.phase1.auth import Principal


@dataclass(frozen=True)
class SearchHit:
    """One search result with source/version context (ADR-02 §4)."""

    kind: str
    id: str
    title: str
    snippet: str
    version_id: str | None
    publication_status: str


@dataclass(frozen=True)
class SearchResult:
    hits: tuple[SearchHit, ...]
    total: int
    page: int
    page_size: int


def _clip(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[:limit] + "…"


def _count_result(result: Any) -> int:
    try:
        return int(str(result.scalar_one()))
    except (ValueError, TypeError, AttributeError):
        return 0


class SearchService:
    """Cross-domain-ready canonical search with mandatory visibility predicates."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def public_search(
        self, *, query: str, page: int = 1, page_size: int = 20
    ) -> SearchResult:
        """Public search: only PUBLISHED content (publication predicate injected)."""
        self._validate_paging(page, page_size)
        pattern = f"%{query}%"
        published = PublicationStatus.PUBLISHED.value
        published_ids = select(PublicationRecord.artifact_id).where(
            PublicationRecord.publication_status == published
        )
        public_passage_ids = select(Evidence.source_passage_id).where(
            Evidence.source_passage_id.is_not(None),
            Evidence.artifact_id.is_not(None),
            Evidence.artifact_id.in_(published_ids),
        )
        base = select(Passage.id).where(
            Passage.content_text.ilike(pattern), Passage.id.in_(public_passage_ids)
        )
        total = _count_result(
            await self.session.execute(select(func.count()).select_from(base.subquery()))
        )
        pub_passages = (
            await self.session.execute(
                base.with_only_columns(Passage.id, Passage.content_text, Passage.version_id)
                .limit(page_size)
                .offset((page - 1) * page_size)
            )
        ).all()
        hits = [
            SearchHit(
                kind="passage",
                id=str(p.id),
                title="（片段）",
                snippet=_clip(str(p.content_text), 120),
                version_id=str(p.version_id) if p.version_id else None,
                publication_status=published,
            )
            for p in pub_passages
        ]
        # P1-04: public Works — only those with a PUBLISHED artifact binding
        published_subjects = select(ContentArtifact.subject_entity_id).where(
            ContentArtifact.subject_entity_id.is_not(None),
            ContentArtifact.id.in_(published_ids),
        )
        works = (
            await self.session.execute(
                select(Work.id, Work.title)
                .where(Work.title.ilike(pattern), Work.entity_id.in_(published_subjects))
                .limit(10)
            )
        ).all()
        hits += [
            SearchHit(
                kind="work",
                id=str(w.id),
                title=str(w.title),
                snippet="",
                version_id=None,
                publication_status=published,
            )
            for w in works
        ]
        # P1-03: public Persons — PUBLISHED artifact binding on the Entity
        person_ids = select(Entity.id).where(
            Entity.entity_type == EntityType.person.value,
            or_(Entity.name.ilike(pattern), Entity.name_zh.ilike(pattern)),
            Entity.id.in_(published_subjects),
        )
        persons = (
            await self.session.execute(
                select(Entity.id, Entity.name, Entity.name_zh)
                .where(Entity.id.in_(person_ids))
                .limit(10)
            )
        ).all()
        hits += [
            SearchHit(
                kind="person",
                id=str(p.id),
                title=str(p.name_zh or p.name),
                snippet="",
                version_id=None,
                publication_status=published,
            )
            for p in persons
        ]
        return SearchResult(hits=tuple(hits), total=total, page=page, page_size=page_size)

    async def research_search(
        self, *, query: str, principal: Principal, page: int = 1, page_size: int = 20
    ) -> SearchResult:
        """Research search: requires an authenticated principal (drafts visible
        to researchers; never to anonymous public)."""
        if not principal.is_authenticated:
            raise PermissionError("research search requires authentication")
        self._validate_paging(page, page_size)
        pattern = f"%{query}%"
        base = select(Passage.id).where(Passage.content_text.ilike(pattern))
        total = _count_result(
            await self.session.execute(select(func.count()).select_from(base.subquery()))
        )
        passages = (
            await self.session.execute(
                base.with_only_columns(Passage.id, Passage.content_text, Passage.version_id)
                .limit(page_size)
                .offset((page - 1) * page_size)
            )
        ).all()
        hits = [
            SearchHit(
                kind="passage",
                id=str(p.id),
                title="（研究片段）",
                snippet=_clip(str(p.content_text), 120),
                version_id=str(p.version_id) if p.version_id else None,
                publication_status="RESEARCH",
            )
            for p in passages
        ]
        # P1-03: research person search — authenticated; no publication filter
        person_ids = select(Entity.id).where(
            Entity.entity_type == EntityType.person.value,
            or_(Entity.name.ilike(pattern), Entity.name_zh.ilike(pattern)),
        )
        persons = (
            await self.session.execute(
                select(Entity.id, Entity.name, Entity.name_zh)
                .where(Entity.id.in_(person_ids))
                .limit(10)
            )
        ).all()
        hits += [
            SearchHit(
                kind="person",
                id=str(p.id),
                title=str(p.name_zh or p.name),
                snippet="",
                version_id=None,
                publication_status="RESEARCH",
            )
            for p in persons
        ]
        return SearchResult(hits=tuple(hits), total=total, page=page, page_size=page_size)

    async def admin_search(self, *, query: str, principal: Principal) -> SearchResult:
        """Admin search: privileged access across all content."""
        if not principal.has_permission("content:review"):
            raise PermissionError("admin search requires content:review")
        return await self.research_search(query=query, principal=principal)

    def _validate_paging(self, page: int, page_size: int) -> None:
        if page < 1 or page_size < 1 or page_size > 100:
            raise ValueError("invalid pagination")
