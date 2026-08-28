"""Assertion ↔ Evidence relation tests (CD-4, M:N, no overwrite)."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from hfm.models.entity import EntityType
from hfm.repositories.assertion import AssertionRepository
from hfm.repositories.entity import EntityRepository
from hfm.repositories.evidence import EvidenceRepository
from hfm.repositories.source import SourceRepository
from hfm.repositories.source_ref import SourceRefRepository


async def _make_evidence(session: AsyncSession, desc: str = "证据") -> str:
    source, _ = await SourceRepository(session).create_idempotent(
        source_key=f"ev-{desc}", title="素问"
    )
    ref = await SourceRefRepository(session).create(source_id=source.id, title="素问")
    return (await EvidenceRepository(session).create(description=desc, source_ref_id=ref.id)).id


async def _make_subject(session: AsyncSession) -> str:
    return (await EntityRepository(session).create(entity_type=EntityType.person, name="皇甫谧")).id


async def test_assertion_multiple_evidence(session: AsyncSession) -> None:
    """One assertion / multiple evidence (EVIDENCE §2.1)."""
    subject = await _make_subject(session)
    e1 = await _make_evidence(session, "证据一")
    e2 = await _make_evidence(session, "证据二")
    repo = AssertionRepository(session)
    assertion = await repo.create(subject_entity_id=subject, predicate="born_in", value="安定")
    assert await repo.attach_evidence(assertion.id, e1) is True
    assert await repo.attach_evidence(assertion.id, e2) is True
    assert sorted(await repo.get_evidence_ids(assertion.id)) == sorted([e1, e2])


async def test_assertion_evidence_no_overwrite(session: AsyncSession) -> None:
    """Attaching evidence never overwrites prior relations."""
    subject = await _make_subject(session)
    e1 = await _make_evidence(session, "甲证")
    e2 = await _make_evidence(session, "乙证")
    repo = AssertionRepository(session)
    first = await repo.create(subject_entity_id=subject, predicate="authored", value="甲乙经")
    second = await repo.create(subject_entity_id=subject, predicate="authored", value="甲乙经校本")
    await repo.attach_evidence(first.id, e1)
    await repo.attach_evidence(second.id, e2)
    # first assertion's evidence is untouched by second's relation
    assert await repo.get_evidence_ids(first.id) == [e1]
    assert await repo.get_evidence_ids(second.id) == [e2]


async def test_assertion_duplicate_evidence_relation_noop(session: AsyncSession) -> None:
    subject = await _make_subject(session)
    e1 = await _make_evidence(session, "唯一证")
    repo = AssertionRepository(session)
    assertion = await repo.create(subject_entity_id=subject, predicate="born_in", value="安定")
    assert await repo.attach_evidence(assertion.id, e1) is True
    assert await repo.attach_evidence(assertion.id, e1) is False  # duplicate no-op
    assert await repo.get_evidence_ids(assertion.id) == [e1]


async def test_assertion_attach_missing_evidence_rejected(session: AsyncSession) -> None:
    subject = await _make_subject(session)
    repo = AssertionRepository(session)
    assertion = await repo.create(subject_entity_id=subject, predicate="born_in", value="安定")
    with pytest.raises(ValueError):
        await repo.attach_evidence(assertion.id, "missing-evidence")
    with pytest.raises(ValueError):
        await repo.attach_evidence("missing-assertion", "x")


async def test_assertion_detach_evidence(session: AsyncSession) -> None:
    subject = await _make_subject(session)
    e1 = await _make_evidence(session, "可分离证")
    repo = AssertionRepository(session)
    assertion = await repo.create(subject_entity_id=subject, predicate="born_in", value="安定")
    await repo.attach_evidence(assertion.id, e1)
    assert await repo.detach_evidence(assertion.id, e1) is True
    assert await repo.get_evidence_ids(assertion.id) == []
