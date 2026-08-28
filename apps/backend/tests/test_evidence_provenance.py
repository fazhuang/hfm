"""I1 Provenance tests for Evidence (CD-3)."""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from hfm.repositories.chapter import ChapterRepository
from hfm.repositories.evidence import EvidenceRepository
from hfm.repositories.passage import PassageRepository
from hfm.repositories.source import SourceRepository
from hfm.repositories.source_ref import SourceRefRepository
from hfm.repositories.work import WorkRepository


async def _make_passage(session: AsyncSession) -> str:
    work = await WorkRepository(session).create(title="针灸甲乙经")
    chapter = await ChapterRepository(session).create(work_id=work.id, title="卷一")
    passage = await PassageRepository(session).create(
        chapter_id=chapter.id, content_text="凡刺之要"
    )
    return passage.id


async def test_invariant_i1_evidence_source_ref_source_traceability(
    session: AsyncSession,
) -> None:
    """I1: Evidence → SourceRef → Source is fully traceable."""
    source, _ = await SourceRepository(session).create_idempotent(
        source_key="i1-src", title="外台秘要"
    )
    ref = await SourceRefRepository(session).create(source_id=source.id, title="外台秘要")
    evidence = await EvidenceRepository(session).create(
        description="转引考证", source_ref_id=ref.id
    )
    # evidence → source_ref → source
    resolved_ref = await SourceRefRepository(session).get_by_id(evidence.source_ref_id or "")
    assert resolved_ref is not None
    resolved_source = await SourceRepository(session).get_by_id(resolved_ref.source_id)
    assert resolved_source is not None
    assert resolved_source.source_key == "i1-src"


async def test_invariant_i1_evidence_passage_anchor(session: AsyncSession) -> None:
    """I1: Evidence can anchor to an in-system Passage (CD-2)."""
    passage_id = await _make_passage(session)
    evidence = await EvidenceRepository(session).create(
        description="条文内证", source_passage_id=passage_id
    )
    assert evidence.source_passage_id == passage_id
    resolved = await PassageRepository(session).get_by_id(evidence.source_passage_id or "")
    assert resolved is not None
    assert resolved.content_text == "凡刺之要"


async def test_evidence_invalid_source_ref_rejected(session: AsyncSession) -> None:
    """Invalid provenance reference is rejected (FK)."""
    repo = EvidenceRepository(session)
    with pytest.raises(IntegrityError):
        await repo.create(description="坏引用", source_ref_id="missing-source-ref")


async def test_evidence_source_ref_restrict_on_delete(session: AsyncSession) -> None:
    """Deleting a SourceRef that anchors Evidence fails (RESTRICT, I1 immutability)."""
    source, _ = await SourceRepository(session).create_idempotent(
        source_key="restrict-src", title="千金要方"
    )
    ref = await SourceRefRepository(session).create(source_id=source.id, title="千金要方")
    await EvidenceRepository(session).create(description="锚定证据", source_ref_id=ref.id)
    with pytest.raises(IntegrityError):
        await SourceRefRepository(session).delete(ref.id)


async def test_evidence_content_hash_deterministic(session: AsyncSession) -> None:
    """Integrity: same payload → same content_hash."""
    source, _ = await SourceRepository(session).create_idempotent(
        source_key="hash-src", title="素问"
    )
    ref = await SourceRefRepository(session).create(source_id=source.id, title="素问")
    repo = EvidenceRepository(session)
    first = await repo.create(description="确定性哈希", source_ref_id=ref.id)
    second = await repo.create(description="确定性哈希", source_ref_id=ref.id)
    assert first.content_hash == second.content_hash
    assert len(first.content_hash or "") == 64
