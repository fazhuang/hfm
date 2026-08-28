"""CD-3 repository behavior tests (Evidence)."""

from sqlalchemy.ext.asyncio import AsyncSession

from hfm.models.evidence import Evidence
from hfm.repositories.evidence import EvidenceRepository
from hfm.repositories.source import SourceRepository
from hfm.repositories.source_ref import SourceRefRepository


async def _make_source_ref(session: AsyncSession) -> str:
    source, _ = await SourceRepository(session).create_idempotent(
        source_key="repo-src", title="证类本草"
    )
    return (await SourceRefRepository(session).create(source_id=source.id, title="证类本草")).id


async def test_evidence_crud_and_get_by_source_ref(session: AsyncSession) -> None:
    source_ref_id = await _make_source_ref(session)
    repo = EvidenceRepository(session)
    evidence = await repo.create(description="证据一", source_ref_id=source_ref_id)
    assert (await repo.get_by_id(evidence.id)) is not None
    assert len(await repo.get_by_source_ref(source_ref_id)) == 1
    updated = await repo.update(evidence.id, description="证据一（修订）")
    assert updated is not None
    assert updated.description == "证据一（修订）"
    assert await repo.delete(evidence.id) is True
    assert await repo.count() == 0


async def test_evidence_immutable_fields_declared(session: AsyncSession) -> None:
    """I1/I4: provenance anchors + content_hash are protected."""
    assert {"id", "content_hash", "source_ref_id", "source_passage_id"} <= Evidence.immutable_fields
    assert "taint_status" not in Evidence.immutable_fields  # taint is mutable lifecycle


async def test_evidence_update_missing_returns_none(session: AsyncSession) -> None:
    repo = EvidenceRepository(session)
    assert (await repo.update("missing-id", description="x")) is None
