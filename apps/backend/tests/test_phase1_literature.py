"""Phase 1 P1-04 — B-domain (文献/思想体系) tests (E-04).

Valid work/edition/version/passage structure; version relationship
integrity; citation addressability (reproducible locators); malformed
binding rejected; no implicit publication; public visibility rules; rights
preservation; unauthorized mutation rejected (P1-10); search integration.
"""

from __future__ import annotations

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from hfm.core.locator import Locator
from hfm.models.content_artifact import ProvenanceStatus, RightsStatus
from hfm.models.entity import Entity, EntityType
from hfm.models.identity import Role, User, UserRoleCode, user_roles
from hfm.phase1.auth import (
    Principal,
    ensure_roles_seeded,
    hash_password,
    issue_token,
    principal_for_token,
)
from hfm.phase1.literature import LiteratureService
from hfm.phase1.publication import PublicationService
from hfm.phase1.search import SearchService
from hfm.phase1.version_audit import VersionLineageService
from hfm.repositories.content_artifact import ContentArtifactRepository
from hfm.repositories.source import SourceRepository


async def _principal(session: AsyncSession, username: str, role_code: UserRoleCode) -> Principal:
    await ensure_roles_seeded(session)
    user = User(username=username, password_hash=hash_password("pw"))
    session.add(user)
    await session.flush()
    role_row = (
        await session.execute(select(Role).where(Role.code == role_code.value))
    ).scalar_one()
    await session.execute(user_roles.insert().values(user_id=user.id, role_id=role_row.id))
    await session.flush()
    token = issue_token(user.id, role_code.value, user.token_version)
    return await principal_for_token(session, token)


async def _published_work(
    session: AsyncSession, title: str = "针灸甲乙经"
) -> tuple[Principal, Principal, str]:
    """Create work + edition + version + passage and publish via P1-09."""
    researcher = await _principal(
        session, f"lres-{hash(title) % 10**6}", UserRoleCode.SCHOLAR_RESEARCHER
    )
    reviewer = await _principal(
        session, f"lrev-{hash(title) % 10**6}", UserRoleCode.CONTENT_REVIEWER
    )
    svc = LiteratureService(session)
    work = await svc.create_work(principal=researcher, title=title, dynasty="西晋")
    edition = await svc.create_edition(principal=researcher, work_id=work.id, edition_name="宋刻本")
    version = await svc.create_version(
        principal=researcher, edition_id=edition.id, version_name="北宋本"
    )
    chapter = await svc.create_chapter(principal=researcher, work_id=work.id, title="卷一")
    await svc.create_passage(
        principal=researcher,
        chapter_id=chapter.id,
        content_text="夫医道所兴，其来久矣",
        version_id=version.id,
    )
    source, _ = await SourceRepository(session).create_idempotent(
        source_key=f"l-src-{hash(title) % 10**6}", title="史料"
    )
    artifact = await svc.admit_work_artifact(
        principal=researcher,
        work_id=work.id,
        source_id=source.id,
        content=f"work:{title}".encode(),
        provenance_status=ProvenanceStatus.VERIFIED,
        rights_status=RightsStatus.CUSTOMER_OWNED,
    )
    pub = PublicationService(session)
    await pub.submit_for_review(artifact_id=artifact.id, creator=researcher)
    await pub.review(artifact_id=artifact.id, reviewer=reviewer, approve=True)
    await pub.publish(artifact_id=artifact.id, actor=reviewer)
    return researcher, reviewer, work.id


async def test_valid_work_structure(session: AsyncSession) -> None:
    researcher = await _principal(session, "l1", UserRoleCode.SCHOLAR_RESEARCHER)
    svc = LiteratureService(session)
    work = await svc.create_work(
        principal=researcher, title="针灸甲乙经", dynasty="西晋", category="医学/针灸"
    )
    assert work.entity_id is not None
    entity = await session.get(Entity, work.entity_id)
    assert entity is not None and entity.entity_type == EntityType.work.value
    assert not await svc.public_visibility(work.id)  # no implicit publication


async def test_version_lineage_integrity(session: AsyncSession) -> None:
    researcher = await _principal(session, "l2", UserRoleCode.SCHOLAR_RESEARCHER)
    svc = LiteratureService(session)
    work = await svc.create_work(principal=researcher, title="针灸甲乙经")
    edition = await svc.create_edition(principal=researcher, work_id=work.id, edition_name="宋刻本")
    root = await svc.create_version(
        principal=researcher, edition_id=edition.id, version_name="祖本"
    )
    child = await svc.create_version(
        principal=researcher,
        edition_id=edition.id,
        version_name="覆刻本",
        parent_version_id=root.id,
    )
    chain = await VersionLineageService(session).lineage(child.id)
    assert [n.version_id for n in chain] == [child.id, root.id]  # deterministic leaf→root
    digest = await VersionLineageService(session).lineage_hash(child.id)
    assert len(digest) == 64
    assert digest == await VersionLineageService(session).lineage_hash(child.id)
    # invalid parent (different edition / nonexistent) rejected
    other_work = await svc.create_work(principal=researcher, title="玄晏春秋")
    other_edition = await svc.create_edition(
        principal=researcher, work_id=other_work.id, edition_name="明刻本"
    )
    with pytest.raises(ValueError, match="parent version must belong to the same Edition"):
        await svc.create_version(
            principal=researcher,
            edition_id=other_edition.id,
            version_name="错链",
            parent_version_id=root.id,
        )
    with pytest.raises(ValueError, match="parent version does not exist"):
        await svc.create_version(
            principal=researcher,
            edition_id=edition.id,
            version_name="孤儿",
            parent_version_id="00000000-0000-7000-8000-000000000000",
        )


async def test_edition_lineage_same_work(session: AsyncSession) -> None:
    researcher = await _principal(session, "l3", UserRoleCode.SCHOLAR_RESEARCHER)
    svc = LiteratureService(session)
    w1 = await svc.create_work(principal=researcher, title="针灸甲乙经")
    w2 = await svc.create_work(principal=researcher, title="玄晏春秋")
    e1 = await svc.create_edition(principal=researcher, work_id=w1.id, edition_name="宋刻本")
    with pytest.raises(ValueError, match="parent edition must belong to the same Work"):
        await svc.create_edition(
            principal=researcher,
            work_id=w2.id,
            edition_name="错链本",
            lineage_parent_edition_id=e1.id,
        )


async def test_malformed_binding_rejected(session: AsyncSession) -> None:
    researcher = await _principal(session, "l4", UserRoleCode.SCHOLAR_RESEARCHER)
    svc = LiteratureService(session)
    work = await svc.create_work(principal=researcher, title="针灸甲乙经")
    edition = await svc.create_edition(principal=researcher, work_id=work.id, edition_name="宋刻本")
    version = await svc.create_version(
        principal=researcher, edition_id=edition.id, version_name="北宋本"
    )
    chapter = await svc.create_chapter(principal=researcher, work_id=work.id, title="卷一")
    # passage with a version from another work rejected (cross-Work consistency)
    other_work = await svc.create_work(principal=researcher, title="玄晏春秋")
    other_edition = await svc.create_edition(
        principal=researcher, work_id=other_work.id, edition_name="明刻本"
    )
    other_version = await svc.create_version(
        principal=researcher, edition_id=other_edition.id, version_name="明本"
    )
    with pytest.raises(ValueError, match="same Work"):
        await svc.create_passage(
            principal=researcher,
            chapter_id=chapter.id,
            content_text="跨著作错绑定",
            version_id=other_version.id,
        )
    # nonexistent version binding rejected
    with pytest.raises(ValueError, match="version does not exist"):
        await svc.create_passage(
            principal=researcher,
            chapter_id=chapter.id,
            content_text="x",
            version_id="00000000-0000-7000-8000-000000000000",
        )
    # empty title rejected
    with pytest.raises(ValueError, match="title is required"):
        await svc.create_work(principal=researcher, title="")
    # empty passage text rejected
    with pytest.raises(ValueError, match="content_text is required"):
        await svc.create_passage(principal=researcher, chapter_id=chapter.id, content_text="")
    assert version.id  # sanity


async def test_citation_addressability_reproducible_locator(session: AsyncSession) -> None:
    researcher = await _principal(session, "l5", UserRoleCode.SCHOLAR_RESEARCHER)
    svc = LiteratureService(session)
    work = await svc.create_work(principal=researcher, title="针灸甲乙经")
    edition = await svc.create_edition(principal=researcher, work_id=work.id, edition_name="宋刻本")
    version = await svc.create_version(
        principal=researcher, edition_id=edition.id, version_name="北宋本"
    )
    chapter = await svc.create_chapter(principal=researcher, work_id=work.id, title="卷一", order=0)
    passage = await svc.create_passage(
        principal=researcher,
        chapter_id=chapter.id,
        content_text="夫医道所兴",
        version_id=version.id,
        order=3,
    )
    locator: Locator = await svc.passage_locator(passage.id)
    assert locator.work_id == work.id
    assert locator.edition_id == edition.id
    assert locator.version_id == version.id
    assert locator.passage_id == passage.id
    assert locator.line == "3"
    # reproducibility: same locator fields re-open the same passage
    reparsed = Locator(**locator.model_dump())
    assert reparsed.passage_id == passage.id
    assert locator.to_locator_string() == reparsed.to_locator_string()
    assert locator.to_locator_string() != "unlocated"


async def test_no_implicit_publication_and_public_visibility(session: AsyncSession) -> None:
    researcher = await _principal(session, "l6", UserRoleCode.SCHOLAR_RESEARCHER)
    svc = LiteratureService(session)
    work = await svc.create_work(principal=researcher, title="针灸甲乙经")
    assert not await svc.public_visibility(work.id)
    assert await svc.get_public_work(work.id) is None
    source, _ = await SourceRepository(session).create_idempotent(
        source_key=f"l6-src-{id(session)}", title="史料"
    )
    artifact = await svc.admit_work_artifact(
        principal=researcher,
        work_id=work.id,
        source_id=source.id,
        content=b"work record",
        provenance_status=ProvenanceStatus.VERIFIED,
        rights_status=RightsStatus.LICENSED,
    )
    assert artifact.admission_state == "admitted"
    assert not await svc.public_visibility(work.id)  # admitted ≠ published


async def test_public_work_projection_obeys_publication_and_rights(session: AsyncSession) -> None:
    _, _, work_id = await _published_work(session, "针灸甲乙经")
    svc = LiteratureService(session)
    assert await svc.public_visibility(work_id)
    public = await svc.get_public_work(work_id)
    assert public is not None
    assert public["publication_status"] == "PUBLISHED"
    assert public["title"] == "针灸甲乙经"
    assert public["rights_status"] == RightsStatus.CUSTOMER_OWNED.value
    assert len(public["editions"]) == 1
    assert public["editions"][0]["versions"][0]["version_name"] == "北宋本"


async def test_withdrawn_work_not_public(session: AsyncSession) -> None:
    researcher, reviewer, work_id = await _published_work(session, "玄晏春秋")
    svc = LiteratureService(session)
    assert await svc.public_visibility(work_id)
    from hfm.repositories.work import WorkRepository

    work = await WorkRepository(session).get_by_id(work_id)
    assert work is not None and work.entity_id is not None
    artifacts = await ContentArtifactRepository(session).get_by_subject_entity(str(work.entity_id))
    await PublicationService(session).withdraw(artifact_id=artifacts[0].id, actor=reviewer)
    assert not await svc.public_visibility(work_id)
    assert await svc.get_public_work(work_id) is None
    _ = researcher


async def test_unauthorized_mutation_rejected(session: AsyncSession) -> None:
    anonymous = Principal(user_id=None, roles=("ANONYMOUS_VISITOR",), permissions=frozenset())
    researcher = await _principal(session, "l7", UserRoleCode.SCHOLAR_RESEARCHER)
    svc = LiteratureService(session)
    with pytest.raises(PermissionError, match="assertion:create"):
        await svc.create_work(principal=anonymous, title="针灸甲乙经")
    work = await svc.create_work(principal=researcher, title="针灸甲乙经")
    with pytest.raises(PermissionError, match="assertion:create"):
        await svc.create_edition(principal=anonymous, work_id=work.id, edition_name="宋刻本")


async def test_work_search_integration_public_and_research(session: AsyncSession) -> None:
    """P1-08 integration: published works discoverable publicly; drafts excluded."""
    await _published_work(session, "针灸甲乙经")
    researcher = await _principal(session, "l8", UserRoleCode.SCHOLAR_RESEARCHER)
    draft = await LiteratureService(session).create_work(principal=researcher, title="草稿文献甲")
    _ = draft
    public = await SearchService(session).public_search(query="针灸甲乙经")
    assert any(h.kind == "work" and h.title == "针灸甲乙经" for h in public.hits)
    draft_public = await SearchService(session).public_search(query="草稿文献甲")
    assert not any(h.kind == "work" for h in draft_public.hits)
    # legacy works without a typed-Entity identity are never public (no binding)
    from hfm.repositories.work import WorkRepository

    legacy = await WorkRepository(session).create(title="无实体绑定古籍")
    assert not await LiteratureService(session).public_visibility(legacy.id)


async def test_work_entity_immutable(session: AsyncSession) -> None:
    researcher = await _principal(session, "l9", UserRoleCode.SCHOLAR_RESEARCHER)
    work = await LiteratureService(session).create_work(principal=researcher, title="针灸甲乙经")
    with pytest.raises(ValueError, match="immutable"):
        work.entity_id = None
        await session.flush()
