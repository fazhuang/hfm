"""Tests for the SourceRef model (CD-0 — REUSE/EXTEND, I1)."""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from hfm.core.locator import Locator
from hfm.models.source_ref import SourceRef
from hfm.repositories.source import SourceRepository
from hfm.repositories.source_ref import SourceRefRepository


async def test_source_ref_requires_source(session: AsyncSession) -> None:
    """I1 provenance seed: a SourceRef cannot exist without an immutable Source."""
    repo = SourceRefRepository(session)
    with pytest.raises(IntegrityError):
        await repo.create(title="无源引用")


async def test_source_ref_anchored_to_source(session: AsyncSession) -> None:
    source_repo = SourceRepository(session)
    ref_repo = SourceRefRepository(session)
    source, _ = await source_repo.create_idempotent(source_key="src-ref-test")
    ref = await ref_repo.create(
        source_id=source.id,
        title="太平圣惠方",
        author="王怀隐",
        edition_info="宋刊本",
        locator=Locator(work_id="w1", volume="3", page="12").model_dump(exclude_none=True),
    )
    assert ref.source_id == source.id
    assert ref.locator is not None
    assert ref.locator["work_id"] == "w1"


async def test_source_ref_restrict_on_source_delete(session: AsyncSession) -> None:
    """FK RESTRICT: deleting a Source that has SourceRefs must fail."""
    source_repo = SourceRepository(session)
    ref_repo = SourceRefRepository(session)
    source, _ = await source_repo.create_idempotent(source_key="restrict-test")
    await ref_repo.create(source_id=source.id, title="受保护引用")
    with pytest.raises(IntegrityError):
        await source_repo.delete(source.id)


def test_source_ref_requires_title() -> None:
    assert SourceRef.__table__.c.title.nullable is False
