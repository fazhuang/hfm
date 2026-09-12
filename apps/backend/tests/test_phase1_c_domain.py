"""Phase 1 P1-05 — C-domain (《针灸甲乙经》数字知识体系) tests (E-05).

Historical disease/point/meridian/technique retrieval returns
source/version/citation; no diagnosis, treatment, ranking or prescription
(AB-14 / ADR-02 Guard-02). Covers: valid canonical term creation; invalid
relation rejection; evidence binding; versioned literature anchoring
(P1-04 reuse); no implicit publication; public visibility via P1-09;
withdrawal visibility; RBAC denial; search integration (P1-08); forbidden
clinical behavior absence.
"""

from __future__ import annotations

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import hfm.phase1.c_domain as c_domain_module
from hfm.models.c_domain import CDomainTerm, CDomainTermType
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
from hfm.phase1.c_domain import CDomainService
from hfm.phase1.literature import LiteratureService
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


async def _evidence(session: AsyncSession, text: str = "甲乙经卷三") -> str:
    source, _ = await SourceRepository(session).create_idempotent(
        source_key=f"p1-05-src-{id(session)}-{hash(text) % 10**6}", title=text
    )
    ref = await SourceRefRepository(session).create(source_id=source.id, title="甲乙经引")
    evidence = await EvidenceRepository(session).create(description="证据", source_ref_id=ref.id)
    return str(evidence.id)


async def _versioned_passage(session: AsyncSession, text: str = "合谷，手阳明脉气所过") -> str:
    """P1-04 reuse: build a Work→Edition→Version→Chapter→Passage and return the passage id."""
    researcher = await _principal(
        session, f"c-lit-{hash(text) % 10**6}", UserRoleCode.SCHOLAR_RESEARCHER
    )
    svc = LiteratureService(session)
    work = await svc.create_work(principal=researcher, title="针灸甲乙经", dynasty="西晋")
    edition = await svc.create_edition(principal=researcher, work_id=work.id, edition_name="宋刻本")
    version = await svc.create_version(
        principal=researcher, edition_id=edition.id, version_name="北宋本"
    )
    chapter = await svc.create_chapter(principal=researcher, work_id=work.id, title="卷三")
    passage = await svc.create_passage(
        principal=researcher, chapter_id=chapter.id, content_text=text, version_id=version.id
    )
    assert passage.id is not None
    return str(passage.id)


async def _published_c_term(
    session: AsyncSession, term_name: str = "合谷", term_type: str = "acupoint"
) -> tuple[Principal, Principal, str]:
    """Create a C term + versioned passage anchor and publish via P1-09."""
    researcher = await _principal(
        session, f"cres-{hash(term_name) % 10**6}", UserRoleCode.SCHOLAR_RESEARCHER
    )
    reviewer = await _principal(
        session, f"crev-{hash(term_name) % 10**6}", UserRoleCode.CONTENT_REVIEWER
    )
    svc = CDomainService(session)
    passage_id = await _versioned_passage(session)
    term = await svc.create_term(
        principal=researcher,
        term_type=term_type,
        term_name=term_name,
        canonical_passage_id=passage_id,
        description="历史术语记录",
    )
    source, _ = await SourceRepository(session).create_idempotent(
        source_key=f"p1-05-pub-{hash(term_name) % 10**6}", title="史料"
    )
    artifact = await svc.admit_term_artifact(
        principal=researcher,
        term_entity_id=term.entity_id,
        source_id=source.id,
        content=f"term:{term_name}".encode(),
        provenance_status=ProvenanceStatus.VERIFIED,
        rights_status=RightsStatus.CUSTOMER_OWNED,
    )
    pub = PublicationService(session)
    await pub.submit_for_review(artifact_id=artifact.id, creator=researcher)
    await pub.review(artifact_id=artifact.id, reviewer=reviewer, approve=True)
    await pub.publish(artifact_id=artifact.id, actor=reviewer)
    return researcher, reviewer, term.entity_id


async def test_valid_c_term_creation(session: AsyncSession) -> None:
    researcher = await _principal(session, "c1", UserRoleCode.SCHOLAR_RESEARCHER)
    term = await CDomainService(session).create_term(
        principal=researcher,
        term_type="acupoint",
        term_name="合谷",
        description="手阳明大肠经穴",
    )
    entity = await session.get(Entity, term.entity_id)
    assert entity is not None
    assert entity.entity_type == EntityType.acupoint.value
    row = (
        await session.execute(select(CDomainTerm).where(CDomainTerm.entity_id == term.entity_id))
    ).scalar_one()
    assert row.term_type == CDomainTermType.acupoint.value
    # no implicit publication
    assert not await CDomainService(session).public_visibility(term.entity_id)


async def test_invalid_relation_rejected(session: AsyncSession) -> None:
    researcher = await _principal(session, "c2", UserRoleCode.SCHOLAR_RESEARCHER)
    svc = CDomainService(session)
    t1 = await svc.create_term(principal=researcher, term_type="acupoint", term_name="合谷")
    t2 = await svc.create_term(principal=researcher, term_type="meridian", term_name="手阳明大肠经")
    # self-link rejected
    with pytest.raises(ValueError, match="cannot link a term to itself"):
        await svc.create_relation(
            principal=researcher,
            source_term_entity_id=t1.entity_id,
            target_term_entity_id=t1.entity_id,
            relation_type="located_in",
        )
    # unknown target term rejected
    with pytest.raises(ValueError, match="does not exist"):
        await svc.create_relation(
            principal=researcher,
            source_term_entity_id=t1.entity_id,
            target_term_entity_id="00000000-0000-7000-8000-000000000000",
            relation_type="located_in",
        )
    # missing evidence rejected (fail-closed)
    with pytest.raises(ValueError, match="evidence does not exist"):
        await svc.create_relation(
            principal=researcher,
            source_term_entity_id=t1.entity_id,
            target_term_entity_id=t2.entity_id,
            relation_type="located_in",
            evidence_id="00000000-0000-7000-8000-000000000000",
        )
    with pytest.raises(ValueError, match="term_name is required"):
        await svc.create_term(principal=researcher, term_type="technique", term_name="")


async def test_evidence_binding_and_relations(session: AsyncSession) -> None:
    researcher = await _principal(session, "c3", UserRoleCode.SCHOLAR_RESEARCHER)
    svc = CDomainService(session)
    point = await svc.create_term(principal=researcher, term_type="acupoint", term_name="合谷")
    meridian = await svc.create_term(
        principal=researcher, term_type="meridian", term_name="手阳明大肠经"
    )
    ev_id = await _evidence(session)
    relation = await svc.create_relation(
        principal=researcher,
        source_term_entity_id=point.entity_id,
        target_term_entity_id=meridian.entity_id,
        relation_type="located_in",
        evidence_id=ev_id,
    )
    assert relation.evidence_id == ev_id
    # immutability: binding cannot be mutated post-create
    with pytest.raises(ValueError, match="immutable"):
        relation.evidence_id = None
        await session.flush()


async def test_source_version_citation_retrieval(session: AsyncSession) -> None:
    """Historical retrieval returns source/version/citation (E-05)."""
    researcher, reviewer, entity_id = await _published_c_term(session, "合谷", "acupoint")
    svc = CDomainService(session)
    public = await svc.get_public_term(entity_id)
    assert public is not None
    assert public["publication_status"] == "PUBLISHED"
    assert public["term_name"] == "合谷"
    # canonical passage = versioned literature anchor (source + version context)
    assert public["canonical_passage"]["passage_id"] is not None
    assert public["canonical_passage"]["version_id"] is not None
    assert public["canonical_passage"]["lineage_hash"] is not None  # version digest (E-13)
    _ = researcher, reviewer


async def test_no_implicit_publication(session: AsyncSession) -> None:
    researcher = await _principal(session, "c4", UserRoleCode.SCHOLAR_RESEARCHER)
    svc = CDomainService(session)
    term = await svc.create_term(principal=researcher, term_type="technique", term_name="燔针劫刺")
    assert not await svc.public_visibility(term.entity_id)
    source, _ = await SourceRepository(session).create_idempotent(
        source_key=f"p1-05-noimp-{id(session)}", title="史料"
    )
    artifact = await svc.admit_term_artifact(
        principal=researcher,
        term_entity_id=term.entity_id,
        source_id=source.id,
        content=b"term record",
        provenance_status=ProvenanceStatus.VERIFIED,
        rights_status=RightsStatus.CUSTOMER_OWNED,
    )
    assert artifact.admission_state == "admitted"
    assert not await svc.public_visibility(term.entity_id)  # admitted ≠ published


async def test_public_visibility_obeys_publication_and_withdrawal(session: AsyncSession) -> None:
    researcher, reviewer, entity_id = await _published_c_term(session, "足三里", "acupoint")
    svc = CDomainService(session)
    assert await svc.public_visibility(entity_id)
    assert await svc.get_public_term(entity_id) is not None
    # withdrawal → public projection disappears immediately
    artifacts = await ContentArtifactRepository(session).get_by_subject_entity(entity_id)
    await PublicationService(session).withdraw(artifact_id=artifacts[0].id, actor=reviewer)
    assert not await svc.public_visibility(entity_id)
    assert await svc.get_public_term(entity_id) is None
    _ = researcher


async def test_unpublished_c_term_not_public(session: AsyncSession) -> None:
    researcher = await _principal(session, "c5", UserRoleCode.SCHOLAR_RESEARCHER)
    term = await CDomainService(session).create_term(
        principal=researcher, term_type="disease_symptom", term_name="未发布病证"
    )
    assert await CDomainService(session).get_public_term(term.entity_id) is None


async def test_public_relations_require_evidence(session: AsyncSession) -> None:
    """E-05 negative: un-evidenced relations never appear in public projections."""
    researcher = await _principal(session, "c6", UserRoleCode.SCHOLAR_RESEARCHER)
    svc = CDomainService(session)
    point = await svc.create_term(principal=researcher, term_type="acupoint", term_name="三阴交")
    meridian = await svc.create_term(
        principal=researcher, term_type="meridian", term_name="足太阴脾经"
    )
    # un-evidenced relation (research only)
    await svc.create_relation(
        principal=researcher,
        source_term_entity_id=point.entity_id,
        target_term_entity_id=meridian.entity_id,
        relation_type="located_in",
    )
    source, _ = await SourceRepository(session).create_idempotent(
        source_key=f"p1-05-rev-{id(session)}", title="史料"
    )
    artifact = await svc.admit_term_artifact(
        principal=researcher,
        term_entity_id=point.entity_id,
        source_id=source.id,
        content=b"point",
        provenance_status=ProvenanceStatus.VERIFIED,
        rights_status=RightsStatus.CUSTOMER_OWNED,
    )
    reviewer = await _principal(session, "c6-rev", UserRoleCode.CONTENT_REVIEWER)
    pub = PublicationService(session)
    await pub.submit_for_review(artifact_id=artifact.id, creator=researcher)
    await pub.review(artifact_id=artifact.id, reviewer=reviewer, approve=True)
    await pub.publish(artifact_id=artifact.id, actor=reviewer)
    public = await svc.get_public_term(point.entity_id)
    assert public is not None
    assert public["relations"] == []  # un-evidenced relation excluded
    research = await svc.get_research_term(point.entity_id)
    assert len(research["relations"]) == 1  # visible to researchers


async def test_unauthorized_mutation_rejected(session: AsyncSession) -> None:
    anonymous = Principal(user_id=None, roles=("ANONYMOUS_VISITOR",), permissions=frozenset())
    researcher = await _principal(session, "c7", UserRoleCode.SCHOLAR_RESEARCHER)
    svc = CDomainService(session)
    with pytest.raises(PermissionError, match="assertion:create"):
        await svc.create_term(principal=anonymous, term_type="acupoint", term_name="合谷")
    term = await svc.create_term(principal=researcher, term_type="acupoint", term_name="合谷")
    with pytest.raises(PermissionError, match="assertion:create"):
        await svc.create_relation(
            principal=anonymous,
            source_term_entity_id=term.entity_id,
            target_term_entity_id=term.entity_id,
            relation_type="located_in",
        )


async def test_c_term_search_integration_public_and_research(session: AsyncSession) -> None:
    """P1-08 integration: published C terms discoverable publicly; drafts excluded."""
    await _published_c_term(session, "曲池", "acupoint")
    researcher = await _principal(session, "c8", UserRoleCode.SCHOLAR_RESEARCHER)
    draft = await CDomainService(session).create_term(
        principal=researcher, term_type="technique", term_name="草稿刺法甲"
    )
    _ = draft
    public = await SearchService(session).public_search(query="曲池")
    assert any(h.kind == "c_term" and h.title == "曲池" for h in public.hits)
    draft_public = await SearchService(session).public_search(query="草稿刺法甲")
    assert not any(h.kind == "c_term" for h in draft_public.hits)
    research = await SearchService(session).research_search(
        query="草稿刺法甲", principal=researcher
    )
    assert any(h.kind == "c_term" and h.title == "草稿刺法甲" for h in research.hits)


async def test_forbidden_clinical_behavior_absent(session: AsyncSession) -> None:
    """AB-14 negative: no diagnosis/treatment/prescription/ranking surface."""
    import inspect

    # no service method name or model column carries prescription/recommendation
    # semantics — the only occurrences are the docstring prohibition statements.
    from hfm.models.c_domain import CDomainRelationType, CDomainTermType

    forbidden_identifiers = (
        "def prescribe",
        "def diagnose",
        "def recommend",
        "def treat",
        "prescription_",
        "diagnosis_",
        "treatment_",
        "recommend_",
    )
    for module in (c_domain_module,):
        for line in inspect.getsource(module).splitlines():
            stripped = line.strip()
            if stripped.startswith(("def ", "class ", "async def ", "    ")) and any(
                f in stripped for f in forbidden_identifiers
            ):
                raise AssertionError(f"C-domain surface leaks clinical semantics: {stripped}")
    # no enum value suggests prescription/ranking
    for enum_cls in (CDomainTermType, CDomainRelationType):
        for member in enum_cls:
            assert "prescription" not in member.value, f"clinical enum value: {member.value}"
            assert "diagnosis" not in member.value, f"clinical enum value: {member.value}"
            assert "treatment" not in member.value, f"clinical enum value: {member.value}"
    # retrieval returns only historical records — a plain read raises no recommendation
    researcher = await _principal(session, "c9", UserRoleCode.SCHOLAR_RESEARCHER)
    term = await CDomainService(session).create_term(
        principal=researcher, term_type="disease_symptom", term_name="痹证"
    )
    research = await CDomainService(session).get_research_term(term.entity_id)
    assert set(research.keys()) <= {
        "entity_id",
        "term_type",
        "term_name",
        "publication_status",
        "relations",
        "canonical_passage",
    }
