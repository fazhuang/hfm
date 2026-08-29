"""Phase 1 P1-06 — D-domain (非遗传承体系) tests (E-06).

Lineage relations carry official-name, evidence and publication state; no
unverified heritage/inheritor claim is public. Covers: valid canonical
heritage project creation; person/institution lineage relations (P1-03
integration); evidence binding; official-name retention; invalid relation
rejection; no implicit publication; public visibility via P1-09; withdrawal
visibility; RBAC denial; public/research projection separation; search
integration (P1-08).
"""

from __future__ import annotations

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from hfm.models.content_artifact import ProvenanceStatus, RightsStatus
from hfm.models.heritage import HeritageProject, HeritageRelationRole
from hfm.models.identity import Role, User, UserRoleCode, user_roles
from hfm.phase1.auth import (
    Principal,
    ensure_roles_seeded,
    hash_password,
    issue_token,
    principal_for_token,
)
from hfm.phase1.heritage import HeritageService
from hfm.phase1.person import PersonService
from hfm.phase1.publication import PublicationService
from hfm.phase1.search import SearchService
from hfm.repositories.content_artifact import ContentArtifactRepository
from hfm.repositories.evidence import EvidenceRepository
from hfm.repositories.source import SourceRepository
from hfm.repositories.source_ref import SourceRefRepository


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


async def _evidence(session: AsyncSession, text: str = "非遗档案") -> str:
    source, _ = await SourceRepository(session).create_idempotent(
        source_key=f"p1-06-src-{id(session)}-{hash(text) % 10**6}", title=text
    )
    ref = await SourceRefRepository(session).create(source_id=source.id, title="档案引")
    evidence = await EvidenceRepository(session).create(description="证据", source_ref_id=ref.id)
    return str(evidence.id)


async def _published_project(
    session: AsyncSession, project_name: str = "针灸"
) -> tuple[Principal, Principal, str]:
    """Create heritage project + inheritor person + publish via P1-09."""
    researcher = await _principal(
        session, f"hres-{hash(project_name) % 10**6}", UserRoleCode.SCHOLAR_RESEARCHER
    )
    reviewer = await _principal(
        session, f"hrev-{hash(project_name) % 10**6}", UserRoleCode.CONTENT_REVIEWER
    )
    svc = HeritageService(session)
    project = await svc.create_project(
        principal=researcher,
        project_name=project_name,
        official_name=f"{project_name}国家级非遗项目",
        category="传统医药",
    )
    source, _ = await SourceRepository(session).create_idempotent(
        source_key=f"p1-06-pub-{hash(project_name) % 10**6}", title="史料"
    )
    artifact = await svc.admit_project_artifact(
        principal=researcher,
        project_entity_id=project.entity_id,
        source_id=source.id,
        content=f"heritage:{project_name}".encode(),
        provenance_status=ProvenanceStatus.VERIFIED,
        rights_status=RightsStatus.CUSTOMER_OWNED,
    )
    pub = PublicationService(session)
    await pub.submit_for_review(artifact_id=artifact.id, creator=researcher)
    await pub.review(artifact_id=artifact.id, reviewer=reviewer, approve=True)
    await pub.publish(artifact_id=artifact.id, actor=reviewer)
    return researcher, reviewer, project.entity_id


async def _inheritor(session: AsyncSession, name: str = "王传承人") -> str:
    """P1-03 reuse: create a canonical person and return the entity_id."""
    researcher = await _principal(
        session, f"hin-{hash(name) % 10**6}", UserRoleCode.SCHOLAR_RESEARCHER
    )
    person = await PersonService(session).create_person(principal=researcher, name_zh=name)
    assert person.entity_id is not None
    return str(person.entity_id)


async def test_valid_heritage_project_creation(session: AsyncSession) -> None:
    researcher = await _principal(session, "d1", UserRoleCode.SCHOLAR_RESEARCHER)
    project = await HeritageService(session).create_project(
        principal=researcher,
        project_name="针灸",
        official_name="针灸（国家级非物质文化遗产）",
        category="传统医药",
    )
    row = (
        await session.execute(
            select(HeritageProject).where(HeritageProject.entity_id == project.entity_id)
        )
    ).scalar_one()
    assert row.official_name == "针灸（国家级非物质文化遗产）"
    assert not await HeritageService(session).public_visibility(project.entity_id)  # no implicit


async def test_lineage_relation_official_name_evidence(session: AsyncSession) -> None:
    """Lineage relations carry official-name and evidence (E-06)."""
    researcher = await _principal(session, "d2", UserRoleCode.SCHOLAR_RESEARCHER)
    svc = HeritageService(session)
    project = await svc.create_project(principal=researcher, project_name="针灸")
    inheritor_id = await _inheritor(session, "王传承人")
    ev_id = await _evidence(session)
    relation = await svc.create_relation(
        principal=researcher,
        project_entity_id=project.entity_id,
        subject_entity_id=inheritor_id,
        relation_role="inheritor",
        official_name="王传承人（省级代表性传承人）",
        evidence_id=ev_id,
    )
    assert relation.official_name == "王传承人（省级代表性传承人）"
    assert relation.evidence_id == ev_id
    assert relation.relation_role == HeritageRelationRole.inheritor.value
    # binding immutability (I4)
    with pytest.raises(ValueError, match="immutable"):
        relation.evidence_id = None
        await session.flush()


async def test_invalid_relation_rejected(session: AsyncSession) -> None:
    researcher = await _principal(session, "d3", UserRoleCode.SCHOLAR_RESEARCHER)
    svc = HeritageService(session)
    project = await svc.create_project(principal=researcher, project_name="针灸")
    inheritor_id = await _inheritor(session, "李传承人")
    # unknown project rejected
    with pytest.raises(ValueError, match="project does not exist"):
        await svc.create_relation(
            principal=researcher,
            project_entity_id="00000000-0000-7000-8000-000000000000",
            subject_entity_id=inheritor_id,
            relation_role="inheritor",
        )
    # unknown subject rejected
    with pytest.raises(ValueError, match="subject entity does not exist"):
        await svc.create_relation(
            principal=researcher,
            project_entity_id=project.entity_id,
            subject_entity_id="00000000-0000-7000-8000-000000000000",
            relation_role="inheritor",
        )
    # non-person non-institution subject rejected (P1-03 integration)
    from hfm.models.entity import Entity, EntityType

    bad_entity = Entity(entity_type=EntityType.work.value, name="著作", name_zh="著作")
    session.add(bad_entity)
    await session.flush()
    with pytest.raises(ValueError, match="person or institution"):
        await svc.create_relation(
            principal=researcher,
            project_entity_id=project.entity_id,
            subject_entity_id=bad_entity.id,
            relation_role="inheritor",
        )
    # missing evidence rejected (fail-closed)
    with pytest.raises(ValueError, match="evidence does not exist"):
        await svc.create_relation(
            principal=researcher,
            project_entity_id=project.entity_id,
            subject_entity_id=inheritor_id,
            relation_role="inheritor",
            evidence_id="00000000-0000-7000-8000-000000000000",
        )
    # empty project name rejected
    with pytest.raises(ValueError, match="project_name is required"):
        await svc.create_project(principal=researcher, project_name="")


async def test_no_implicit_publication(session: AsyncSession) -> None:
    researcher = await _principal(session, "d4", UserRoleCode.SCHOLAR_RESEARCHER)
    svc = HeritageService(session)
    project = await svc.create_project(principal=researcher, project_name="艾灸")
    assert not await svc.public_visibility(project.entity_id)
    source, _ = await SourceRepository(session).create_idempotent(
        source_key=f"p1-06-noimp-{id(session)}", title="史料"
    )
    artifact = await svc.admit_project_artifact(
        principal=researcher,
        project_entity_id=project.entity_id,
        source_id=source.id,
        content=b"project record",
        provenance_status=ProvenanceStatus.VERIFIED,
        rights_status=RightsStatus.CUSTOMER_OWNED,
    )
    assert artifact.admission_state == "admitted"
    assert not await svc.public_visibility(project.entity_id)  # admitted ≠ published


async def test_public_visibility_obeys_publication_and_withdrawal(session: AsyncSession) -> None:
    researcher, reviewer, entity_id = await _published_project(session, "推拿")
    svc = HeritageService(session)
    assert await svc.public_visibility(entity_id)
    public = await svc.get_public_project(entity_id)
    assert public is not None
    assert public["publication_status"] == "PUBLISHED"
    assert public["official_name"] == "推拿国家级非遗项目"
    # withdrawal → public projection disappears immediately
    artifacts = await ContentArtifactRepository(session).get_by_subject_entity(entity_id)
    await PublicationService(session).withdraw(artifact_id=artifacts[0].id, actor=reviewer)
    assert not await svc.public_visibility(entity_id)
    assert await svc.get_public_project(entity_id) is None
    _ = researcher


async def test_unpublished_project_not_public(session: AsyncSession) -> None:
    researcher = await _principal(session, "d5", UserRoleCode.SCHOLAR_RESEARCHER)
    project = await HeritageService(session).create_project(
        principal=researcher, project_name="未发布非遗项目"
    )
    assert await HeritageService(session).get_public_project(project.entity_id) is None


async def test_public_projection_only_evidenced_relations(session: AsyncSession) -> None:
    """E-06 negative: un-evidenced lineage claims never appear publicly."""
    researcher, reviewer, entity_id = await _published_project(session, "拔罐")
    svc = HeritageService(session)
    inheritor_id = await _inheritor(session, "张传承人")
    # un-evidenced relation (research only)
    await svc.create_relation(
        principal=researcher,
        project_entity_id=entity_id,
        subject_entity_id=inheritor_id,
        relation_role="inheritor",
        official_name="张传承人",
    )
    public = await svc.get_public_project(entity_id)
    assert public is not None
    assert public["relations"] == []  # un-evidenced claim excluded publicly
    research = await svc.get_research_project(entity_id)
    assert len(research["relations"]) == 1  # visible to researchers
    _ = reviewer


async def test_research_projection_includes_evidenced_relations(session: AsyncSession) -> None:
    researcher, reviewer, entity_id = await _published_project(session, "导引")
    svc = HeritageService(session)
    inheritor_id = await _inheritor(session, "赵传承人")
    ev_id = await _evidence(session)
    await svc.create_relation(
        principal=researcher,
        project_entity_id=entity_id,
        subject_entity_id=inheritor_id,
        relation_role="inheritor",
        official_name="赵传承人（省级代表性传承人）",
        evidence_id=ev_id,
    )
    public = await svc.get_public_project(entity_id)
    assert public is not None
    assert len(public["relations"]) == 1  # evidenced relation is public
    assert public["relations"][0]["official_name"] == "赵传承人（省级代表性传承人）"
    assert public["relations"][0]["evidence_id"] == ev_id
    _ = reviewer


async def test_unauthorized_mutation_rejected(session: AsyncSession) -> None:
    anonymous = Principal(user_id=None, roles=("ANONYMOUS_VISITOR",), permissions=frozenset())
    researcher = await _principal(session, "d6", UserRoleCode.SCHOLAR_RESEARCHER)
    svc = HeritageService(session)
    with pytest.raises(PermissionError, match="assertion:create"):
        await svc.create_project(principal=anonymous, project_name="针灸")
    project = await svc.create_project(principal=researcher, project_name="针灸")
    with pytest.raises(PermissionError, match="assertion:create"):
        await svc.create_relation(
            principal=anonymous,
            project_entity_id=project.entity_id,
            subject_entity_id="00000000-0000-7000-8000-000000000000",
            relation_role="inheritor",
        )


async def test_heritage_search_integration_public_and_research(session: AsyncSession) -> None:
    """P1-08 integration: published projects discoverable publicly; drafts excluded."""
    await _published_project(session, "五禽戏")
    researcher = await _principal(session, "d7", UserRoleCode.SCHOLAR_RESEARCHER)
    draft = await HeritageService(session).create_project(
        principal=researcher, project_name="草稿非遗项目甲"
    )
    _ = draft
    public = await SearchService(session).public_search(query="五禽戏")
    assert any(h.kind == "heritage_project" and h.title == "五禽戏" for h in public.hits)
    draft_public = await SearchService(session).public_search(query="草稿非遗项目甲")
    assert not any(h.kind == "heritage_project" for h in draft_public.hits)
    research = await SearchService(session).research_search(
        query="草稿非遗项目甲", principal=researcher
    )
    assert any(h.kind == "heritage_project" and h.title == "草稿非遗项目甲" for h in research.hits)
