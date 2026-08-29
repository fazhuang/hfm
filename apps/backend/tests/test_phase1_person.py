"""Phase 1 P1-03 — A-domain (皇甫谧人物体系) tests (E-03).

Valid canonical person-domain records; invalid relationship rejection;
evidence/citation linkage integrity; provenance/version linkage;
update/version behavior (immutability); no implicit publication; public
visibility obeys the canonical P1-09 publication state; unauthorized
mutation rejected (P1-10); search integration (P1-08).
"""

from __future__ import annotations

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from hfm.models.content_artifact import ProvenanceStatus, RightsStatus
from hfm.models.entity import Entity, EntityType
from hfm.models.identity import Role, User, UserRoleCode, user_roles
from hfm.models.person import Person
from hfm.phase1.auth import (
    Principal,
    ensure_roles_seeded,
    hash_password,
    issue_token,
    principal_for_token,
)
from hfm.phase1.person import PersonService
from hfm.phase1.publication import PublicationService
from hfm.phase1.search import SearchService
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


async def _evidence(session: AsyncSession, text: str = "史料") -> str:
    source, _ = await SourceRepository(session).create_idempotent(
        source_key=f"p1-03-src-{id(session)}-{hash(text) % 10**6}", title=text
    )
    ref = await SourceRefRepository(session).create(source_id=source.id, title="史料引")
    from hfm.models.evidence import Evidence

    evidence: Evidence = await EvidenceRepository(session).create(
        description="证据", source_ref_id=ref.id
    )
    return str(evidence.id)


async def _published_person(
    session: AsyncSession, name_zh: str = "皇甫谧"
) -> tuple[Principal, Principal, str]:
    """Create person + evidenced assertion + publish via canonical workflow."""
    researcher = await _principal(
        session, f"res-{hash(name_zh) % 10**6}", UserRoleCode.SCHOLAR_RESEARCHER
    )
    reviewer = await _principal(
        session, f"rev-{hash(name_zh) % 10**6}", UserRoleCode.CONTENT_REVIEWER
    )
    svc = PersonService(session)
    person = await svc.create_person(principal=researcher, name_zh=name_zh, dynasty="西晋")
    ev_id = await _evidence(session, name_zh)
    await svc.add_biographical_assertion(
        principal=researcher,
        person_entity_id=person.entity_id,
        predicate="born_in",
        value="安定朝那",
        evidence_ids=(ev_id,),
    )
    source, _ = await SourceRepository(session).create_idempotent(
        source_key=f"p1-03-pub-src-{hash(name_zh) % 10**6}", title="史料"
    )
    artifact = await svc.admit_person_artifact(
        principal=researcher,
        person_entity_id=person.entity_id,
        source_id=source.id,
        content=f"person:{name_zh}".encode(),
        provenance_status=ProvenanceStatus.VERIFIED,
        rights_status=RightsStatus.CUSTOMER_OWNED,
    )
    pub = PublicationService(session)
    await pub.submit_for_review(artifact_id=artifact.id, creator=researcher)
    await pub.review(artifact_id=artifact.id, reviewer=reviewer, approve=True)
    await pub.publish(artifact_id=artifact.id, actor=reviewer)
    return researcher, reviewer, person.entity_id


async def test_valid_person_record_creation(session: AsyncSession) -> None:
    researcher = await _principal(session, "p1", UserRoleCode.SCHOLAR_RESEARCHER)
    person = await PersonService(session).create_person(
        principal=researcher, name_zh="皇甫谧", name_pinyin="Huangfu Mi", dynasty="西晋"
    )
    entity = await session.get(Entity, person.entity_id)
    assert entity is not None
    assert entity.entity_type == EntityType.person.value
    assert person.name_zh == "皇甫谧"
    # no publication record is created by person creation (no implicit publish)
    assert not await PersonService(session).public_visibility(person.entity_id)


async def test_invalid_relationship_rejected(session: AsyncSession) -> None:
    researcher = await _principal(session, "p2", UserRoleCode.SCHOLAR_RESEARCHER)
    svc = PersonService(session)
    person = await svc.create_person(principal=researcher, name_zh="皇甫谧")
    other = await svc.create_person(principal=researcher, name_zh="张仲景")
    # assertion without value/object rejected
    with pytest.raises(ValueError, match="literal value or an object"):
        await svc.add_biographical_assertion(
            principal=researcher, person_entity_id=person.entity_id, predicate="born_in"
        )
    # event self-relation rejected (entity_id == event_id impossible via repo)
    with pytest.raises(ValueError, match="relation event does not exist"):
        await svc.relate_event(
            principal=researcher,
            person_entity_id=person.entity_id,
            event_entity_id="",
            role="actor",
        )
    # missing evidence linkage rejected (fail-closed)
    with pytest.raises(ValueError, match="evidence does not exist"):
        await svc.add_biographical_assertion(
            principal=researcher,
            person_entity_id=person.entity_id,
            predicate="died_in",
            value="太康三年",
            evidence_ids=("00000000-0000-7000-8000-000000000000",),
        )
    # unknown person rejected
    with pytest.raises(ValueError, match="person does not exist"):
        await svc.add_biographical_assertion(
            principal=researcher,
            person_entity_id="00000000-0000-7000-8000-000000000000",
            predicate="born_in",
            value="安定",
        )
    assert other.entity_id != person.entity_id


async def test_invalid_subject_entity_binding_rejected(session: AsyncSession) -> None:
    """P1-01 gate integration: an unresolvable subject binding is rejected."""
    source, _ = await SourceRepository(session).create_idempotent(
        source_key=f"p1-03-bind-{id(session)}", title="史料"
    )
    from hfm.repositories.content_artifact import ContentArtifactRepository

    artifact = await ContentArtifactRepository(session).submit_with_source_check(
        source_id=source.id,
        content=b"bound content",
        provenance_status=ProvenanceStatus.VERIFIED,
        rights_status=RightsStatus.CUSTOMER_OWNED,
        subject_entity_id="00000000-0000-7000-8000-000000000000",
    )
    assert artifact.admission_state == "rejected"
    assert artifact.rejection_reason == "invalid_subject_entity_binding"


async def test_evidence_citation_linkage_integrity(session: AsyncSession) -> None:
    researcher = await _principal(session, "p3", UserRoleCode.SCHOLAR_RESEARCHER)
    svc = PersonService(session)
    person = await svc.create_person(principal=researcher, name_zh="皇甫谧")
    ev_id = await _evidence(session)
    assertion = await svc.add_biographical_assertion(
        principal=researcher,
        person_entity_id=person.entity_id,
        predicate="born_in",
        value="安定朝那",
        evidence_ids=(ev_id,),
        confidence="high",
    )
    assert assertion.subject_entity_id == person.entity_id
    from hfm.repositories.assertion import AssertionRepository

    assert ev_id in await AssertionRepository(session).get_evidence_ids(assertion.id)


async def test_provenance_and_version_linking(session: AsyncSession) -> None:
    researcher = await _principal(session, "p4", UserRoleCode.SCHOLAR_RESEARCHER)
    svc = PersonService(session)
    person = await svc.create_person(principal=researcher, name_zh="皇甫谧")
    assertion = await svc.add_biographical_assertion(
        principal=researcher,
        person_entity_id=person.entity_id,
        predicate="composed",
        value="《针灸甲乙经》",
    )
    assert assertion.created_by == researcher.user_id  # provenance linkage
    # revision is a new assertion, never a silent overwrite (I4)
    second = await svc.add_biographical_assertion(
        principal=researcher,
        person_entity_id=person.entity_id,
        predicate="composed",
        value="《针灸甲乙经》十二卷",
    )
    assert second.id != assertion.id
    with pytest.raises(ValueError, match="immutable"):
        assertion.value = "篡改"
        await session.flush()


async def test_no_implicit_publication(session: AsyncSession) -> None:
    researcher = await _principal(session, "p5", UserRoleCode.SCHOLAR_RESEARCHER)
    svc = PersonService(session)
    person = await svc.create_person(principal=researcher, name_zh="皇甫谧")
    assert not await svc.public_visibility(person.entity_id)
    # admission alone does not publish
    source, _ = await SourceRepository(session).create_idempotent(
        source_key=f"p1-03-noimp-{id(session)}", title="史料"
    )
    artifact = await svc.admit_person_artifact(
        principal=researcher,
        person_entity_id=person.entity_id,
        source_id=source.id,
        content=b"person record",
        provenance_status=ProvenanceStatus.VERIFIED,
        rights_status=RightsStatus.CUSTOMER_OWNED,
    )
    assert artifact.admission_state == "admitted"
    assert not await svc.public_visibility(person.entity_id)  # still unpublished


async def test_public_visibility_obeys_publication_state(session: AsyncSession) -> None:
    _, _, entity_id = await _published_person(session, "皇甫谧")
    svc = PersonService(session)
    assert await svc.public_visibility(entity_id)
    public = await svc.get_public_person(entity_id)
    assert public is not None
    assert public["publication_status"] == "PUBLISHED"
    assert public["name_zh"] == "皇甫谧"
    assert len(public["assertions"]) == 1  # evidenced assertion projected
    # withdraw → public projection disappears (immediate)
    reviewer = await _principal(session, "p6-rev", UserRoleCode.CONTENT_REVIEWER)
    from hfm.repositories.content_artifact import ContentArtifactRepository

    artifacts = await ContentArtifactRepository(session).get_by_subject_entity(entity_id)
    await PublicationService(session).withdraw(artifact_id=artifacts[0].id, actor=reviewer)
    assert not await svc.public_visibility(entity_id)
    assert await svc.get_public_person(entity_id) is None


async def test_unpublished_person_not_public(session: AsyncSession) -> None:
    researcher = await _principal(session, "p7", UserRoleCode.SCHOLAR_RESEARCHER)
    svc = PersonService(session)
    person = await svc.create_person(principal=researcher, name_zh="未发布人物")
    assert await svc.get_public_person(person.entity_id) is None


async def test_unauthorized_mutation_rejected(session: AsyncSession) -> None:
    anonymous = Principal(user_id=None, roles=("ANONYMOUS_VISITOR",), permissions=frozenset())
    researcher = await _principal(session, "p8", UserRoleCode.SCHOLAR_RESEARCHER)
    svc = PersonService(session)
    with pytest.raises(PermissionError, match="assertion:create"):
        await svc.create_person(principal=anonymous, name_zh="匿名")
    person = await svc.create_person(principal=researcher, name_zh="皇甫谧")
    with pytest.raises(PermissionError, match="assertion:create"):
        await svc.add_biographical_assertion(
            principal=anonymous, person_entity_id=person.entity_id, predicate="born_in", value="x"
        )


async def test_person_search_integration_public_and_research(session: AsyncSession) -> None:
    """P1-08 integration: published persons discoverable publicly; drafts
    excluded publicly; research sees drafts with auth."""
    await _published_person(session, "皇甫谧")
    # draft-only person must NOT appear in public search
    researcher = await _principal(session, "p9", UserRoleCode.SCHOLAR_RESEARCHER)
    draft = await PersonService(session).create_person(
        principal=researcher, name_zh="草稿人物甲", name_pinyin="CaoGao"
    )
    _ = draft
    public = await SearchService(session).public_search(query="皇甫谧")
    assert any(h.kind == "person" and h.title == "皇甫谧" for h in public.hits)
    draft_public = await SearchService(session).public_search(query="草稿人物甲")
    assert not any(h.kind == "person" for h in draft_public.hits)
    # research search (authenticated) sees the draft person
    research = await SearchService(session).research_search(
        query="草稿人物甲", principal=researcher
    )
    assert any(h.kind == "person" and h.title == "草稿人物甲" for h in research.hits)


async def test_person_row_bound_to_entity(session: AsyncSession) -> None:
    researcher = await _principal(session, "p10", UserRoleCode.SCHOLAR_RESEARCHER)
    person = await PersonService(session).create_person(
        principal=researcher, name_zh="皇甫谧", dynasty="西晋"
    )
    row = (
        await session.execute(select(Person).where(Person.entity_id == person.entity_id))
    ).scalar_one()
    assert row.dynasty == "西晋"
