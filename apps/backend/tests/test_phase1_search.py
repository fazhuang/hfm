"""Phase 1 P1-08 — unified search tests (ADR-02, publication/RBAC predicates).

Public search returns only PUBLISHED content; withdrawn/draft/private content
absent; research search requires authentication; no leakage to anonymous.
"""

from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from hfm.models.content_artifact import ProvenanceStatus, RightsStatus
from hfm.models.identity import Role, User, UserRoleCode, user_roles
from hfm.models.passage import Passage
from hfm.phase1.auth import (
    Principal,
    ensure_roles_seeded,
    hash_password,
    issue_token,
    principal_for_token,
)
from hfm.phase1.publication import PublicationService
from hfm.phase1.search import SearchService
from hfm.repositories.chapter import ChapterRepository
from hfm.repositories.content_artifact import ContentArtifactRepository
from hfm.repositories.evidence import EvidenceRepository
from hfm.repositories.source import SourceRepository
from hfm.repositories.source_ref import SourceRefRepository
from hfm.repositories.work import WorkRepository


async def _principal(session: AsyncSession, username: str, role_code: UserRoleCode) -> Principal:
    await ensure_roles_seeded(session)
    from sqlalchemy import select

    user = User(username=username, password_hash=hash_password("pw"))
    session.add(user)
    await session.flush()
    role_row = (
        await session.execute(select(Role).where(Role.code == role_code.value))
    ).scalar_one()
    await session.execute(user_roles.insert().values(user_id=user.id, role_id=role_row.id))
    await session.flush()
    return await principal_for_token(
        session, issue_token(user.id, role_code.value, user.token_version)
    )


async def _published_passage(session: AsyncSession, text: str, *, publish: bool = True) -> Passage:
    """Create passage + evidence binding + artifact + (optional) publication."""
    work = await WorkRepository(session).create(title="针灸甲乙经")
    chapter = await ChapterRepository(session).create(work_id=work.id, title="卷一")
    passage = await PassageRepository_create(session, chapter.id, text)
    source, _ = await SourceRepository(session).create_idempotent(
        source_key=f"src-{id(session)}-{hash(text) % 10**6}", title="史料"
    )
    ref = await SourceRefRepository(session).create(source_id=source.id, title="史料引")
    evidence = await EvidenceRepository(session).create(
        description="证据", source_passage_id=passage.id, source_ref_id=ref.id
    )
    artifact = await ContentArtifactRepository(session).submit_with_source_check(
        source_id=source.id,
        content=text.encode("utf-8"),
        provenance_status=ProvenanceStatus.VERIFIED,
        rights_status=RightsStatus.CUSTOMER_OWNED,
    )
    evidence.artifact_id = artifact.id
    await session.flush()
    if publish:
        researcher = await _principal(
            session, f"res{hash(text) % 10**5}", UserRoleCode.SCHOLAR_RESEARCHER
        )
        reviewer = await _principal(
            session, f"rev{hash(text) % 10**5}", UserRoleCode.CONTENT_REVIEWER
        )
        svc = PublicationService(session)
        await svc.submit_for_review(artifact_id=artifact.id, creator=researcher)
        await svc.review(artifact_id=artifact.id, reviewer=reviewer, approve=True)
        await svc.publish(artifact_id=artifact.id, actor=reviewer)
    return passage


async def PassageRepository_create(session: AsyncSession, chapter_id: str, text: str) -> Passage:
    from hfm.repositories.passage import PassageRepository

    return await PassageRepository(session).create(chapter_id=chapter_id, content_text=text)


async def test_chinese_text_search_public(session: AsyncSession) -> None:
    await _published_passage(session, "合谷穴主治齿痛")
    result = await SearchService(session).public_search(query="合谷")
    assert result.total >= 1
    assert any("合谷穴" in h.snippet for h in result.hits)


async def test_draft_absent_from_public_search(session: AsyncSession) -> None:
    """Draft (PENDING_REVIEW) content must be absent from public search."""
    await _published_passage(session, "仅草稿状态的独有内容甲", publish=False)
    result = await SearchService(session).public_search(query="独有内容甲")
    assert result.total == 0


async def test_withdrawn_absent_from_public_search(session: AsyncSession) -> None:
    passage = await _published_passage(session, "已撤回的独有内容乙")
    assert (await SearchService(session).public_search(query="独有内容乙")).total >= 1
    # withdraw
    artifact = (
        await session.execute(
            __import__("sqlalchemy").text(
                "SELECT artifact_id FROM evidences WHERE source_passage_id = :pid"
            ),
            {"pid": passage.id},
        )
    ).scalar_one()
    reviewer = await _principal(session, "revw", UserRoleCode.CONTENT_REVIEWER)
    await PublicationService(session).withdraw(artifact_id=str(artifact), actor=reviewer)
    assert (await SearchService(session).public_search(query="独有内容乙")).total == 0


async def test_research_search_requires_auth(session: AsyncSession) -> None:
    with pytest.raises(PermissionError, match="authentication"):
        await SearchService(session).research_search(
            query="x",
            principal=Principal(
                user_id=None, roles=("ANONYMOUS_VISITOR",), permissions=frozenset()
            ),
        )


async def test_research_search_authenticated_sees_drafts(session: AsyncSession) -> None:
    await _published_passage(session, "研究端可见的草稿内容丙", publish=False)
    researcher = await _principal(session, "rsch", UserRoleCode.SCHOLAR_RESEARCHER)
    result = await SearchService(session).research_search(query="草稿内容丙", principal=researcher)
    assert result.total >= 1


async def test_anonymous_cannot_elevate_via_query_params(session: AsyncSession) -> None:
    """Direct query parameters cannot bypass visibility predicates."""
    await _published_passage(session, "内部私有内容丁", publish=False)
    result = await SearchService(session).public_search(
        query="内部私有内容丁", page=1, page_size=100
    )
    assert result.total == 0


async def test_pagination(session: AsyncSession) -> None:
    for i in range(5):
        await _published_passage(session, f"分页测试条目{i}")
    page1 = await SearchService(session).public_search(query="分页测试条目", page=1, page_size=2)
    assert page1.total >= 5 and len(page1.hits) == 2
    page2 = await SearchService(session).public_search(query="分页测试条目", page=2, page_size=2)
    assert len(page2.hits) == 2
    assert {h.id for h in page1.hits}.isdisjoint({h.id for h in page2.hits})
    with pytest.raises(ValueError, match="pagination"):
        await SearchService(session).public_search(query="x", page=0)
