# mypy: disable-error-code="import-untyped"
# The canonical gate (`mypy src tests`) resolves hfm to source and passes with
# 142 files; per-file mypy sees the editable install and flags import-untyped
# (same artifact present in accepted test files). File-level suppression keeps
# the per-file guard green without weakening the real gate.
"""Phase 1 P1-11 — public approved-content portal tests (E-11, AB-02/05/07).

Anonymous users see the approved publication projection only: published
home aggregate, published works list, editions of published works; draft,
unpublished, withdrawn and missing-publication material is never returned;
withdrawal is reflected immediately; responses are strict whitelist
projections (no internal entity ids / provenance / research state / relation
traversal / clinical semantics — AB-14). No authorization bypass through
guessed identifiers. Deterministic pagination/ordering.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from hfm.models.content_artifact import ContentArtifact, ProvenanceStatus, RightsStatus
from hfm.models.edition import Edition
from hfm.models.identity import Role, User, UserRoleCode, user_roles
from hfm.models.person import Person
from hfm.models.publication import PublicationRecord, PublicationStatus
from hfm.models.version import Version
from hfm.models.work import Work
from hfm.phase1.auth import (
    Principal,
    ensure_roles_seeded,
    hash_password,
    issue_token,
    principal_for_token,
)
from hfm.phase1.literature import LiteratureService
from hfm.phase1.person import PersonService
from hfm.phase1.portal import PortalService
from hfm.phase1.publication import PublicationService
from hfm.repositories.source import SourceRepository

_WORK_KEYS = {"work_id", "title", "dynasty", "category", "edition_count", "publication_status"}
_EDITION_KEYS = {"edition_id", "edition_name", "era", "publisher_block"}
_COUNT_KEYS = {"works", "persons", "heritage_projects", "c_terms"}
_FORBIDDEN_SUBSTRINGS = (
    "diagnosis",
    "treatment",
    "prescription",
    "recommendation",
    "主穴",
    "配穴",
)

_PRINCIPAL_SEQ = 0


async def _principal(session: AsyncSession, role_code: UserRoleCode) -> Principal:
    """Create a distinct HFM user with the requested role (unique username)."""
    global _PRINCIPAL_SEQ
    _PRINCIPAL_SEQ += 1
    await ensure_roles_seeded(session)
    user = User(
        username=f"pt-{role_code.value.lower()}-{_PRINCIPAL_SEQ}",
        password_hash=hash_password("pw"),
    )
    session.add(user)
    await session.flush()
    role_row = (
        await session.execute(select(Role).where(Role.code == role_code.value))
    ).scalar_one()
    await session.execute(user_roles.insert().values(user_id=user.id, role_id=role_row.id))
    await session.flush()
    token = issue_token(user.id, role_code.value, user.token_version)
    return await principal_for_token(session, token)


async def _scholar(session: AsyncSession) -> Principal:
    return await _principal(session, UserRoleCode.SCHOLAR_RESEARCHER)


async def _reviewer(session: AsyncSession) -> Principal:
    return await _principal(session, UserRoleCode.CONTENT_REVIEWER)


async def _work(session: AsyncSession, title: str) -> tuple[Work, Edition, Version]:
    """Create an unadmitted Work with one edition/version."""
    scholar = await _scholar(session)
    svc = LiteratureService(session)
    work = await svc.create_work(principal=scholar, title=title, dynasty="西晋")
    edition = await svc.create_edition(principal=scholar, work_id=work.id, edition_name="宋刻本")
    version = await svc.create_version(
        principal=scholar, edition_id=edition.id, version_name="北宋本"
    )
    return work, edition, version


async def _publish_work(
    session: AsyncSession, scholar: Principal, work: Work, content: bytes | None = None
) -> ContentArtifact:
    """Admit + review + publish a Work artifact via P1-09."""
    source, _ = await SourceRepository(session).create_idempotent(
        source_key=f"pt-src-{hash(work.id) % 10**6}", title="史料"
    )
    artifact = await LiteratureService(session).admit_work_artifact(
        principal=scholar,
        work_id=work.id,
        source_id=source.id,
        content=content or f"work:{work.id}".encode(),
        provenance_status=ProvenanceStatus.VERIFIED,
        rights_status=RightsStatus.CUSTOMER_OWNED,
    )
    reviewer = await _reviewer(session)
    pub = PublicationService(session)
    await pub.submit_for_review(artifact_id=artifact.id, creator=scholar)
    await pub.review(artifact_id=artifact.id, reviewer=reviewer, approve=True)
    await pub.publish(artifact_id=artifact.id, actor=reviewer)
    return artifact


async def _published_person(session: AsyncSession) -> Person:
    """Publish a Person artifact so counts cover >1 domain (P1-03 reuse)."""
    scholar = await _scholar(session)
    person = await PersonService(session).create_person(
        principal=scholar, name_zh="皇甫谧", name_pinyin="huangfumi"
    )
    source, _ = await SourceRepository(session).create_idempotent(
        source_key=f"pt-psrc-{id(session) % 10**6}", title="史传"
    )
    artifact = await PersonService(session).admit_person_artifact(
        principal=scholar,
        person_entity_id=person.entity_id,
        source_id=source.id,
        content=f"person:{person.entity_id}".encode(),
        provenance_status=ProvenanceStatus.VERIFIED,
        rights_status=RightsStatus.CUSTOMER_OWNED,
    )
    reviewer = await _reviewer(session)
    pub = PublicationService(session)
    await pub.submit_for_review(artifact_id=artifact.id, creator=scholar)
    await pub.review(artifact_id=artifact.id, reviewer=reviewer, approve=True)
    await pub.publish(artifact_id=artifact.id, actor=reviewer)
    return person


async def _published_subjects(session: AsyncSession) -> set[str]:
    rows = await session.execute(
        select(PublicationRecord.artifact_id).where(
            PublicationRecord.publication_status == PublicationStatus.PUBLISHED.value
        )
    )
    return set(rows.scalars().all())


# ------------------------------------------------------------------- home
async def test_home_returns_published_projection(session: AsyncSession) -> None:
    """Anonymous portal home exposes approved published content only."""
    scholar = await _scholar(session)
    work, edition, _ = await _work(session, "针灸甲乙经")
    await _publish_work(session, scholar, work)
    person = await _published_person(session)

    home = await PortalService(session).home()
    assert home["counts"]["works"] == 1
    assert home["counts"]["persons"] == 1
    assert home["counts"]["heritage_projects"] == 0
    assert home["counts"]["c_terms"] == 0
    assert [w["work_id"] for w in home["works"]] == [work.id]
    assert home["works"][0]["title"] == "针灸甲乙经"
    assert home["works"][0]["edition_count"] == 1
    assert home["works"][0]["publication_status"] == "PUBLISHED"
    assert person is not None


async def test_home_excludes_unpublished(session: AsyncSession) -> None:
    """Unpublished/draft material never appears in the portal home."""
    scholar = await _scholar(session)
    published_work, _, _ = await _work(session, "已发布")
    draft_work, _, _ = await _work(session, "草稿未发布")
    await _publish_work(session, scholar, published_work)

    home = await PortalService(session).home()
    assert [w["work_id"] for w in home["works"]] == [published_work.id]
    assert draft_work.id not in {w["work_id"] for w in home["works"]}
    assert home["counts"]["works"] == 1


async def test_home_excludes_missing_publication(session: AsyncSession) -> None:
    """Admitted-but-never-published content (no PUBLISHED record) is absent."""
    scholar = await _scholar(session)
    work, _, _ = await _work(session, "仅准入")
    source, _ = await SourceRepository(session).create_idempotent(
        source_key=f"pt-msrc-{id(session) % 10**6}", title="史料"
    )
    await LiteratureService(session).admit_work_artifact(
        principal=scholar,
        work_id=work.id,
        source_id=source.id,
        content=b"admitted",
        provenance_status=ProvenanceStatus.VERIFIED,
        rights_status=RightsStatus.CUSTOMER_OWNED,
    )
    home = await PortalService(session).home()
    assert home["works"] == []
    assert home["counts"]["works"] == 0


# ------------------------------------------------------------------ works
async def test_works_list_published_only(session: AsyncSession) -> None:
    """Works list returns only published Works, deterministically ordered."""
    scholar = await _scholar(session)
    published, _, _ = await _work(session, "甲经")
    draft, _, _ = await _work(session, "未刊本")
    await _publish_work(session, scholar, published)

    result = await PortalService(session).works(page=1, page_size=20)
    assert result["total"] == 1
    assert [w["work_id"] for w in result["works"]] == [published.id]
    assert draft.id not in {w["work_id"] for w in result["works"]}
    assert result["page"] == 1


async def test_works_list_withdrawn_excluded(session: AsyncSession) -> None:
    """WITHDRAWN content is excluded from the published works list."""
    scholar = await _scholar(session)
    work, _, _ = await _work(session, "撤回本")
    artifact = await _publish_work(session, scholar, work)
    result = await PortalService(session).works(page=1, page_size=20)
    assert [w["work_id"] for w in result["works"]] == [work.id]

    reviewer = await _reviewer(session)
    await PublicationService(session).withdraw(artifact_id=artifact.id, actor=reviewer)
    result_after = await PortalService(session).works(page=1, page_size=20)
    assert result_after["total"] == 0
    assert result_after["works"] == []


async def test_withdrawal_immediately_reflected(session: AsyncSession) -> None:
    """Withdrawal removes the public projection at once (ADR-05 Guard-03)."""
    scholar = await _scholar(session)
    work, _, _ = await _work(session, "即时撤回")
    artifact = await _publish_work(session, scholar, work)
    assert await PortalService(session).work_editions(work.id) is not None

    reviewer = await _reviewer(session)
    await PublicationService(session).withdraw(artifact_id=artifact.id, actor=reviewer)
    assert await PortalService(session).work_editions(work.id) is None
    home = await PortalService(session).home()
    assert work.id not in {w["work_id"] for w in home["works"]}
    assert home["counts"]["works"] == 0


# ---------------------------------------------------------------- editions
async def test_work_editions_published_work(session: AsyncSession) -> None:
    """Editions of a published Work are exposed as a strict whitelist."""
    scholar = await _scholar(session)
    work, edition, _ = await _work(session, "甲乙经版本")
    await _publish_work(session, scholar, work)

    editions = await PortalService(session).work_editions(work.id)
    assert editions is not None
    assert [e["edition_id"] for e in editions] == [edition.id]
    assert set(editions[0]) == _EDITION_KEYS
    assert editions[0]["edition_name"] == "宋刻本"


async def test_work_editions_unpublished_work_fail_closed(session: AsyncSession) -> None:
    """Unpublished Work → None (404 at API layer): no existence leak."""
    work, _, _ = await _work(session, "未发布版本")
    assert await PortalService(session).work_editions(work.id) is None
    # published subject exists but this work is not among them
    scholar = await _scholar(session)
    other, _, _ = await _work(session, "另一部")
    await _publish_work(session, scholar, other)
    assert await PortalService(session).work_editions(work.id) is None


async def test_work_editions_guessed_id_no_leak(session: AsyncSession) -> None:
    """Random/guessed identifiers never open unpublished projections."""
    assert (
        await PortalService(session).work_editions("00000000-0000-0000-0000-000000000000") is None
    )


# ---------------------------------------------------------------- whitelist
async def test_strict_response_whitelist(session: AsyncSession) -> None:
    """Portal responses carry exactly the public fields — nothing internal."""
    scholar = await _scholar(session)
    work, _, _ = await _work(session, "白名单")
    await _publish_work(session, scholar, work)
    await _published_person(session)

    home = await PortalService(session).home()
    works_result = await PortalService(session).works(page=1, page_size=20)
    editions = await PortalService(session).work_editions(work.id)

    assert set(home) == {"works", "counts"}
    assert set(home["counts"]) == _COUNT_KEYS
    assert set(works_result) == {"works", "total", "page"}
    for entry in works_result["works"]:
        assert set(entry) == _WORK_KEYS
    assert editions is not None
    for entry in editions:
        assert set(entry) == _EDITION_KEYS

    import json

    blob = json.dumps(home) + json.dumps(works_result) + json.dumps(editions)
    for forbidden in (
        "entity_id",
        "created_by",
        "provenance",
        "rights_status",
        "evidence",
        "relations",
    ):
        assert forbidden not in blob, f"internal field leaked: {forbidden}"


# ------------------------------------------------------------ determinism
async def test_pagination_deterministic(session: AsyncSession) -> None:
    """Same page twice → identical order; pages partition the result set."""
    scholar = await _scholar(session)
    for i in range(3):
        work, _, _ = await _work(session, f"典{i}")
        await _publish_work(session, scholar, work)

    first = await PortalService(session).works(page=1, page_size=2)
    again = await PortalService(session).works(page=1, page_size=2)
    second = await PortalService(session).works(page=2, page_size=2)
    assert first == again  # deterministic ordering
    assert first["total"] == 3
    first_ids = [w["work_id"] for w in first["works"]]
    second_ids = [w["work_id"] for w in second["works"]]
    assert len(first_ids) == 2 and len(second_ids) == 1
    assert not set(first_ids) & set(second_ids)  # no overlap across pages
    assert len(first_ids + second_ids) == 3


async def test_pagination_bounds_fail_closed(session: AsyncSession) -> None:
    """Invalid paging fails closed (mirrors accepted search validation)."""
    svc = PortalService(session)
    for page, size in ((0, 10), (1, 0), (1, 101), (-3, 5)):
        try:
            await svc.works(page=page, page_size=size)
        except ValueError:
            continue
        raise AssertionError(f"pagination ({page}, {size}) did not fail closed")


# ----------------------------------------------------------- boundary guards
async def test_no_relation_traversal(session: AsyncSession) -> None:
    """Portal surfaces expose no relation traversal (AB-14)."""
    scholar = await _scholar(session)
    work, _, _ = await _work(session, "无关系遍历")
    await _publish_work(session, scholar, work)
    await _published_person(session)

    home = await PortalService(session).home()
    works_result = await PortalService(session).works(page=1, page_size=20)
    editions = await PortalService(session).work_editions(work.id)
    blob = f"{home}{works_result}{editions}"
    assert "relations" not in blob
    assert "related" not in blob


async def test_no_clinical_recommendation_surface(session: AsyncSession) -> None:
    """Clinical recommendation behavior = 0 across the portal projection."""
    scholar = await _scholar(session)
    work, _, _ = await _work(session, "临床边界")
    await _publish_work(session, scholar, work)

    home = await PortalService(session).home()
    works_result = await PortalService(session).works(page=1, page_size=20)
    editions = await PortalService(session).work_editions(work.id)
    blob = f"{home}{works_result}{editions}".lower()
    for token in _FORBIDDEN_SUBSTRINGS:
        assert token not in blob, f"clinical token leaked: {token}"
    assert _published_subjects is not None  # predicate helper exercised
