"""Tests for the Evidence model (CD-3 — REUSE, CA-021/CA-024 + integrity)."""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from hfm.models.evidence import EvidenceLevel
from hfm.repositories.evidence import EvidenceRepository
from hfm.repositories.source import SourceRepository
from hfm.repositories.source_ref import SourceRefRepository


async def _make_source_ref(session: AsyncSession) -> str:
    source, _ = await SourceRepository(session).create_idempotent(
        source_key="evidence-src", title="太平圣惠方"
    )
    ref = await SourceRefRepository(session).create(source_id=source.id, title="太平圣惠方")
    return ref.id


async def test_evidence_construction_with_source_ref(session: AsyncSession) -> None:
    source_ref_id = await _make_source_ref(session)
    repo = EvidenceRepository(session)
    evidence = await repo.create(
        description="针灸甲乙经条文考证",
        evidence_level=EvidenceLevel.LEVEL_2,
        source_ref_id=source_ref_id,
    )
    assert evidence.id
    assert evidence.evidence_level == EvidenceLevel.LEVEL_2
    assert evidence.source_ref_id == source_ref_id
    assert evidence.content_hash  # integrity digest computed (I1)
    assert evidence.taint_status == "clean"


async def test_evidence_requires_anchor(session: AsyncSession) -> None:
    """I1: orphan Evidence (no source_ref / no passage) is rejected."""
    repo = EvidenceRepository(session)
    with pytest.raises(ValueError):
        await repo.create(description="孤儿证据")


async def test_evidence_content_hash_protected(session: AsyncSession) -> None:
    """I4: content_hash is derived integrity — post-create mutation rejected."""
    source_ref_id = await _make_source_ref(session)
    repo = EvidenceRepository(session)
    evidence = await repo.create(
        description="定稿证据", evidence_level=EvidenceLevel.LEVEL_1, source_ref_id=source_ref_id
    )
    with pytest.raises(ValueError):
        await repo.update(evidence.id, content_hash="tampered")
    # direct ORM mutation of content_hash is rejected (model @validates)
    with pytest.raises(ValueError):
        evidence.content_hash = "tampered-direct"


async def test_evidence_content_fields_immutable(session: AsyncSession) -> None:
    """I4: description / evidence_level are immutable — no stale content_hash."""
    source_ref_id = await _make_source_ref(session)
    repo = EvidenceRepository(session)
    evidence = await repo.create(
        description="定稿", evidence_level=EvidenceLevel.LEVEL_2, source_ref_id=source_ref_id
    )
    with pytest.raises(ValueError):
        await repo.update(evidence.id, description="篡改内容")
    with pytest.raises(ValueError):
        await repo.update(evidence.id, evidence_level=EvidenceLevel.LEVEL_4)
    # direct ORM mutation is rejected too
    with pytest.raises(ValueError):
        evidence.description = "直接篡改"
    with pytest.raises(ValueError):
        evidence.evidence_level = EvidenceLevel.LEVEL_4


async def test_evidence_taint_lifecycle(session: AsyncSession) -> None:
    """CA-024 REUSE: clean → source_withdrawn taint transition."""
    source_ref_id = await _make_source_ref(session)
    repo = EvidenceRepository(session)
    evidence = await repo.create(description="待污损证据", source_ref_id=source_ref_id)
    tainted = await repo.mark_tainted(evidence.id, "source_withdrawn", reason="source withdrawn")
    assert tainted is not None
    assert tainted.taint_status == "source_withdrawn"
    assert tainted.taint_reason == "source withdrawn"
    assert tainted.tainted_at is not None


async def test_evidence_invalid_taint_status_rejected(session: AsyncSession) -> None:
    source_ref_id = await _make_source_ref(session)
    repo = EvidenceRepository(session)
    evidence = await repo.create(description="x", source_ref_id=source_ref_id)
    with pytest.raises(ValueError):
        await repo.mark_tainted(evidence.id, "not-a-status")


def test_evidence_level_values() -> None:
    assert {e.value for e in EvidenceLevel} == {"LEVEL_1", "LEVEL_2", "LEVEL_3", "LEVEL_4"}


async def test_evidence_requires_description(session: AsyncSession) -> None:
    source_ref_id = await _make_source_ref(session)
    repo = EvidenceRepository(session)
    with pytest.raises(ValueError):
        await repo.create(description="", source_ref_id=source_ref_id)


async def test_evidence_db_level_anchor_check(session: AsyncSession) -> None:
    """DB-level CHECK enforces at least one provenance anchor (I1)."""
    from hfm.models.evidence import Evidence

    # bypass repository validation via raw model insert with no anchors
    instance = Evidence(description="raw insert")
    session.add(instance)
    with pytest.raises(IntegrityError):
        await session.flush()
