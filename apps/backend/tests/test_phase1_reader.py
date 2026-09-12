"""Phase 1 P1-07 — versioned source reader tests (E-07, AB-09).

A passage locator reproducibly opens source context and citation; no
reader access to unauthorized draft. Covers: valid public resolve
(quotation + source context + citation + rights display); locator
reproducibility (same locator → same version/passage); locator round-trip
and canonical-locator derivation; malformed locator rejection; ancestry
mismatch rejection; unpublished/draft exclusion; withdrawn version
exclusion; publication withdrawal; RBAC denial (research requires
authentication); richer research evidence context; P1-05 canonical-passage
integration; no relation traversal and no clinical surface (AB-14).
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from hfm.core.locator import Locator
from hfm.models.chapter import Chapter
from hfm.models.citation import Citation
from hfm.models.content_artifact import ContentArtifact, ProvenanceStatus, RightsStatus
from hfm.models.edition import Edition
from hfm.models.entity import EntityType
from hfm.models.identity import Role, User, UserRoleCode, user_roles
from hfm.models.passage import Passage
from hfm.models.version import Version
from hfm.models.work import Work
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
from hfm.phase1.reader import ReaderService
from hfm.repositories.assertion import AssertionRepository
from hfm.repositories.citation import CitationRepository
from hfm.repositories.entity import EntityRepository
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


async def _versioned_work(
    session: AsyncSession, title: str = "针灸甲乙经", text: str = "夫医道所兴，其来久矣"
) -> tuple[Principal, Principal, Work, Edition, Version, Chapter, Passage]:
    """Unpublished versioned work with one passage (P1-04 reuse)."""
    researcher = await _principal(
        session, f"r-{hash(title) % 10**6}", UserRoleCode.SCHOLAR_RESEARCHER
    )
    reviewer = await _principal(session, f"rv-{hash(title) % 10**6}", UserRoleCode.CONTENT_REVIEWER)
    svc = LiteratureService(session)
    work = await svc.create_work(principal=researcher, title=title, dynasty="西晋")
    edition = await svc.create_edition(principal=researcher, work_id=work.id, edition_name="宋刻本")
    version = await svc.create_version(
        principal=researcher, edition_id=edition.id, version_name="北宋本"
    )
    chapter = await svc.create_chapter(principal=researcher, work_id=work.id, title="卷一", order=0)
    passage = await svc.create_passage(
        principal=researcher,
        chapter_id=chapter.id,
        content_text=text,
        version_id=version.id,
        order=1,
    )
    return researcher, reviewer, work, edition, version, chapter, passage


async def _publish_work(
    session: AsyncSession, researcher: Principal, reviewer: Principal, work: Work
) -> ContentArtifact:
    """Admit + review + publish a Work artifact via P1-09."""
    source, _ = await SourceRepository(session).create_idempotent(
        source_key=f"rd-src-{hash(work.id) % 10**6}", title="史料"
    )
    artifact = await LiteratureService(session).admit_work_artifact(
        principal=researcher,
        work_id=work.id,
        source_id=source.id,
        content=f"work:{work.id}".encode(),
        provenance_status=ProvenanceStatus.VERIFIED,
        rights_status=RightsStatus.CUSTOMER_OWNED,
    )
    pub = PublicationService(session)
    await pub.submit_for_review(artifact_id=artifact.id, creator=researcher)
    await pub.review(artifact_id=artifact.id, reviewer=reviewer, approve=True)
    await pub.publish(artifact_id=artifact.id, actor=reviewer)
    return artifact


async def _passage_citation(
    session: AsyncSession, passage: Passage, version: Version, note: str = "校勘注"
) -> Citation:
    """Evidence + assertion + citation pinned to the passage (P1-02 reuse)."""
    source, _ = await SourceRepository(session).create_idempotent(
        source_key=f"rd-cit-{hash(passage.id) % 10**6}", title="甲乙经卷三"
    )
    ref = await SourceRefRepository(session).create(source_id=source.id, title="甲乙经引")
    evidence = await EvidenceRepository(session).create(
        description="卷三校勘证据", source_ref_id=ref.id, source_passage_id=passage.id
    )
    entity = await EntityRepository(session).create(entity_type=EntityType.person, name="皇甫谧")
    assertion = await AssertionRepository(session).create(
        subject_entity_id=entity.id, predicate="authored", value="针灸甲乙经"
    )
    await AssertionRepository(session).attach_evidence(assertion.id, evidence.id)
    return await CitationRepository(session).create(
        target_assertion_id=assertion.id,
        quote_text=passage.content_text,
        passage_id=passage.id,
        version_id=version.id,
        note=note,
    )


async def test_public_resolve_opens_source_and_citation(session: AsyncSession) -> None:
    """Acceptance: locator reproducibly opens source context + citation."""
    researcher, reviewer, work, edition, version, chapter, passage = await _versioned_work(session)
    citation = await _passage_citation(session, passage, version)
    await _publish_work(session, researcher, reviewer, work)
    canonical = await LiteratureService(session).passage_locator(passage.id)

    view = await ReaderService(session).resolve_public(locator=canonical.to_locator_string())
    assert view is not None
    assert view["passage_id"] == passage.id
    assert view["quotation"] == "夫医道所兴，其来久矣"  # quotation preserved
    assert view["locator"] == canonical.to_locator_string()
    assert view["publication_status"] == "PUBLISHED"
    # source context
    assert view["work"]["work_id"] == work.id
    assert view["work"]["title"] == "针灸甲乙经"
    assert view["edition"]["edition_id"] == edition.id
    assert view["version"]["version_id"] == version.id
    assert view["version"]["lineage_hash"]  # deterministic lineage digest (E-13)
    assert view["chapter"]["chapter_id"] == chapter.id
    # citation context
    assert [c["citation_id"] for c in view["citations"]] == [citation.id]
    assert view["citations"][0]["quote_text"] == passage.content_text
    # rights display
    assert view["rights"]["rights_status"] == RightsStatus.CUSTOMER_OWNED.value
    assert view["rights"]["publication_status"] == "PUBLISHED"


async def test_locator_reproducibility_same_locator_same_passage(session: AsyncSession) -> None:
    """E-07: reopening the same locator resolves the same version/passage."""
    researcher, reviewer, work, _, version, _, passage = await _versioned_work(session)
    await _publish_work(session, researcher, reviewer, work)
    svc = ReaderService(session)
    canonical = await LiteratureService(session).passage_locator(passage.id)
    first = await svc.resolve_public(locator=canonical.to_locator_string())
    second = await svc.resolve_public(locator=canonical.to_locator_string())
    assert first is not None and second is not None
    assert first["passage_id"] == second["passage_id"] == passage.id
    assert first["version"]["version_id"] == second["version"]["version_id"] == version.id
    assert first["locator"] == second["locator"] == canonical.to_locator_string()
    assert first == second  # deterministic projection


async def test_locator_round_trip_and_canonical_derivation(session: AsyncSession) -> None:
    """Locator string round-trips; resolve-by-passage-id derives canonical."""
    researcher, reviewer, work, edition, version, _, passage = await _versioned_work(session)
    await _publish_work(session, researcher, reviewer, work)
    canonical: Locator = await LiteratureService(session).passage_locator(passage.id)
    reparsed = Locator.from_locator_string(canonical.to_locator_string())
    assert reparsed.work_id == work.id
    assert reparsed.edition_id == edition.id
    assert reparsed.version_id == version.id
    assert reparsed.passage_id == passage.id
    # string-level round trip is lossless; resolution is anchored on the
    # entity ids (physical segments are display-only, E-07)
    assert reparsed.to_locator_string() == canonical.to_locator_string()
    assert reparsed.to_locator_string() != "unlocated"
    # resolving by passage id returns the same canonical locator
    view = await ReaderService(session).resolve_public(passage_id=passage.id)
    assert view is not None and view["locator"] == canonical.to_locator_string()


async def test_malformed_locator_fails_closed_public(session: AsyncSession) -> None:
    """Negative: malformed locators never open anything publicly (fail closed)."""
    svc = ReaderService(session)
    assert await svc.resolve_public(locator="garbage") is None
    assert await svc.resolve_public(locator="work:only,no-passage") is None
    assert await svc.resolve_public(locator="unknown:key,passage:p1") is None
    assert await svc.resolve_public(locator="") is None
    assert await svc.resolve_public(passage_id="") is None
    assert await svc.resolve_public(passage_id="00000000-0000-7000-8000-000000000000") is None


async def test_ancestry_mismatch_rejected(session: AsyncSession) -> None:
    """Negative: locator entity ids must match the passage ancestry."""
    researcher, reviewer, work, _, version, _, passage = await _versioned_work(session)
    await _publish_work(session, researcher, reviewer, work)
    canonical = await LiteratureService(session).passage_locator(passage.id)
    # wrong version id
    wrong = Locator.from_locator_string(canonical.to_locator_string())
    wrong.version_id = "00000000-0000-7000-8000-000000000000"
    assert await ReaderService(session).resolve_public(locator=wrong.to_locator_string()) is None
    with pytest.raises(ValueError, match="version_id does not match"):
        await ReaderService(session).resolve_research(
            principal=researcher, locator=wrong.to_locator_string()
        )
    # wrong work id
    wrong2 = Locator.from_locator_string(canonical.to_locator_string())
    wrong2.work_id = "00000000-0000-7000-8000-000000000000"
    with pytest.raises(ValueError, match="work_id does not match"):
        await ReaderService(session).resolve_research(
            principal=researcher, locator=wrong2.to_locator_string()
        )
    _ = version


async def test_unpublished_passage_not_public(session: AsyncSession) -> None:
    """Negative: draft content never resolves publicly (no unauthorized draft)."""
    _, reviewer, _, _, _, _, passage = await _versioned_work(session, "玄晏春秋")
    researcher = await _principal(session, "draft-r", UserRoleCode.SCHOLAR_RESEARCHER)
    canonical = await LiteratureService(session).passage_locator(passage.id)
    assert (
        await ReaderService(session).resolve_public(locator=canonical.to_locator_string()) is None
    )
    # authenticated research reader still resolves the draft passage
    research = await ReaderService(session).resolve_research(
        principal=researcher, locator=canonical.to_locator_string()
    )
    assert research["passage_id"] == passage.id
    assert research["publication_status"] == "UNPUBLISHED"
    _ = reviewer


async def test_withdrawn_version_excluded_publicly(session: AsyncSession) -> None:
    """Negative: a passage pinned to a withdrawn version is not publicly readable."""
    researcher, reviewer, work, _, version, _, passage = await _versioned_work(session)
    await _publish_work(session, researcher, reviewer, work)
    version.withdrawn_at = datetime.now(UTC)
    await session.flush()
    canonical = await LiteratureService(session).passage_locator(passage.id)
    assert (
        await ReaderService(session).resolve_public(locator=canonical.to_locator_string()) is None
    )
    # research reader remains available (authenticated), withdrawal is visible
    research = await ReaderService(session).resolve_research(
        principal=researcher, locator=canonical.to_locator_string()
    )
    assert research["version"]["withdrawn_at"] is not None


async def test_publication_withdrawal_hides_passage(session: AsyncSession) -> None:
    """Negative: withdrawing the publication immediately hides the passage."""
    researcher, reviewer, work, _, version, _, passage = await _versioned_work(session)
    artifact = await _publish_work(session, researcher, reviewer, work)
    canonical = await LiteratureService(session).passage_locator(passage.id)
    assert (
        await ReaderService(session).resolve_public(locator=canonical.to_locator_string())
        is not None
    )
    await PublicationService(session).withdraw(artifact_id=artifact.id, actor=reviewer)
    assert (
        await ReaderService(session).resolve_public(locator=canonical.to_locator_string()) is None
    )
    _ = version


async def test_research_reader_requires_authentication(session: AsyncSession) -> None:
    """Negative: research reader denies anonymous access (P1-10 RBAC)."""
    anonymous = Principal(user_id=None, roles=("ANONYMOUS_VISITOR",), permissions=frozenset())
    with pytest.raises(PermissionError, match="authentication"):
        await ReaderService(session).resolve_research(
            principal=anonymous, passage_id="00000000-0000-7000-8000-000000000000"
        )


async def test_research_reader_richer_evidence_context(session: AsyncSession) -> None:
    """Research reader exposes the full evidence chain; public view does not."""
    researcher, reviewer, work, _, version, _, passage = await _versioned_work(session)
    citation = await _passage_citation(session, passage, version)
    await _publish_work(session, researcher, reviewer, work)
    canonical = await LiteratureService(session).passage_locator(passage.id)
    public = await ReaderService(session).resolve_public(locator=canonical.to_locator_string())
    research = await ReaderService(session).resolve_research(
        principal=researcher, locator=canonical.to_locator_string()
    )
    assert public is not None
    # public: evidence metadata only (no internal description/taint/source title)
    assert len(public["evidence"]) == 1
    assert public["evidence"][0]["evidence_id"]
    assert "description" not in public["evidence"][0]
    assert "taint_status" not in public["evidence"][0]
    assert "source_ref_title" not in public["evidence"][0]
    assert "target_assertion_id" not in public["citations"][0]
    assert "note" not in public["citations"][0]
    # research: full evidence chain + citation target
    assert len(research["evidence"]) == 1
    assert research["evidence"][0]["description"] == "卷三校勘证据"
    assert research["evidence"][0]["taint_status"] == "clean"
    assert research["evidence"][0]["source_ref_title"] == "甲乙经引"
    assert research["evidence"][0]["source_title"] == "甲乙经卷三"
    assert research["citations"][0]["citation_id"] == citation.id
    assert research["citations"][0]["target_assertion_id"] is not None
    assert research["citations"][0]["note"] == "校勘注"


async def test_c_domain_canonical_passage_public_via_published_term(session: AsyncSession) -> None:
    """P1-05 integration: a published C term makes its canonical passage readable."""
    researcher = await _principal(session, "c-rd", UserRoleCode.SCHOLAR_RESEARCHER)
    reviewer = await _principal(session, "c-rv", UserRoleCode.CONTENT_REVIEWER)
    # work stays UNPUBLISHED — only the C term is published
    _, _, work, _, _, _, passage = await _versioned_work(session, "甲乙经草稿", "合谷者，手阳明")
    svc = CDomainService(session)
    term = await svc.create_term(
        principal=researcher,
        term_type="acupoint",
        term_name="合谷",
        canonical_passage_id=passage.id,
        description="历史术语记录",
    )
    source, _ = await SourceRepository(session).create_idempotent(
        source_key=f"rd-cterm-{hash(passage.id) % 10**6}", title="史料"
    )
    artifact = await svc.admit_term_artifact(
        principal=researcher,
        term_entity_id=term.entity_id,
        source_id=source.id,
        content="term:合谷".encode(),
        provenance_status=ProvenanceStatus.VERIFIED,
        rights_status=RightsStatus.CUSTOMER_OWNED,
    )
    pub = PublicationService(session)
    await pub.submit_for_review(artifact_id=artifact.id, creator=researcher)
    await pub.review(artifact_id=artifact.id, reviewer=reviewer, approve=True)
    await pub.publish(artifact_id=artifact.id, actor=reviewer)
    assert not await LiteratureService(session).public_visibility(work.id)
    canonical = await LiteratureService(session).passage_locator(passage.id)
    view = await ReaderService(session).resolve_public(locator=canonical.to_locator_string())
    assert view is not None
    assert view["passage_id"] == passage.id
    assert view["quotation"] == "合谷者，手阳明"
    assert view["rights"]["publication_status"] == "PUBLISHED"


async def test_public_evidence_bound_passage_readable(session: AsyncSession) -> None:
    """Evidence bound to a PUBLISHED artifact makes the passage publicly readable."""
    researcher = await _principal(session, "ev-rd", UserRoleCode.SCHOLAR_RESEARCHER)
    reviewer = await _principal(session, "ev-rv", UserRoleCode.CONTENT_REVIEWER)
    _, _, work, _, version, _, passage = await _versioned_work(session, "针灸甲乙经", "十二经脉")
    # publish a term artifact; bind an Evidence to the passage with that artifact
    svc = CDomainService(session)
    term = await svc.create_term(principal=researcher, term_type="meridian", term_name="十二经脉")
    source, _ = await SourceRepository(session).create_idempotent(
        source_key=f"rd-ev-{hash(passage.id) % 10**6}", title="史料"
    )
    artifact = await svc.admit_term_artifact(
        principal=researcher,
        term_entity_id=term.entity_id,
        source_id=source.id,
        content="term:十二经脉".encode(),
        provenance_status=ProvenanceStatus.VERIFIED,
        rights_status=RightsStatus.CUSTOMER_OWNED,
    )
    pub = PublicationService(session)
    await pub.submit_for_review(artifact_id=artifact.id, creator=researcher)
    await pub.review(artifact_id=artifact.id, reviewer=reviewer, approve=True)
    await pub.publish(artifact_id=artifact.id, actor=reviewer)
    await EvidenceRepository(session).create(
        description="经脉证据",
        source_passage_id=passage.id,
        artifact_id=artifact.id,
    )
    assert not await LiteratureService(session).public_visibility(work.id)
    canonical = await LiteratureService(session).passage_locator(passage.id)
    view = await ReaderService(session).resolve_public(locator=canonical.to_locator_string())
    assert view is not None and view["passage_id"] == passage.id
    _ = version


async def test_no_relation_traversal_no_clinical_surface(session: AsyncSession) -> None:
    """AB-14 negative: reader output is bounded; no clinical/relation surface."""
    import inspect

    import hfm.phase1.reader as reader_module

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
    for line in inspect.getsource(reader_module).splitlines():
        stripped = line.strip()
        if stripped.startswith(("def ", "class ", "async def ")) and any(
            f in stripped for f in forbidden_identifiers
        ):
            raise AssertionError(f"reader surface leaks clinical semantics: {stripped}")
    researcher, reviewer, work, _, version, _, passage = await _versioned_work(session)
    await _publish_work(session, researcher, reviewer, work)
    canonical = await LiteratureService(session).passage_locator(passage.id)
    view = await ReaderService(session).resolve_public(locator=canonical.to_locator_string())
    assert view is not None
    # bounded keys: no relation traversal, no recommendation surface
    assert set(view.keys()) <= {
        "locator",
        "passage_id",
        "quotation",
        "translation",
        "notes",
        "work",
        "edition",
        "version",
        "chapter",
        "citations",
        "evidence",
        "rights",
        "publication_status",
    }
    assert "relations" not in view
    _ = reviewer, version
