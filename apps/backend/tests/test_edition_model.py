"""Tests for the Edition model (CD-2 — REUSE, CA-008)."""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from hfm.repositories.edition import EditionRepository
from hfm.repositories.work import WorkRepository


async def _make_work(session: AsyncSession) -> str:
    work = await WorkRepository(session).create(title="针灸甲乙经")
    return work.id


async def test_edition_construction(session: AsyncSession) -> None:
    work_id = await _make_work(session)
    repo = EditionRepository(session)
    edition = await repo.create(work_id=work_id, edition_name="宋刻本", era="北宋")
    assert edition.id
    assert edition.work_id == work_id
    assert edition.edition_name == "宋刻本"


async def test_edition_requires_work(session: AsyncSession) -> None:
    """Missing parent Work must be rejected (FK)."""
    repo = EditionRepository(session)
    with pytest.raises(IntegrityError):
        await repo.create(work_id="missing-work", edition_name="孤儿版本")


async def test_edition_lineage_parent(session: AsyncSession) -> None:
    """lineage_parent_edition_id self-FK links edition provenance."""
    work_id = await _make_work(session)
    repo = EditionRepository(session)
    parent = await repo.create(work_id=work_id, edition_name="底本")
    child = await repo.create(
        work_id=work_id, edition_name="校勘本", lineage_parent_edition_id=parent.id
    )
    assert child.lineage_parent_edition_id == parent.id
    resolved_parent = await repo.get_by_id(child.lineage_parent_edition_id or "")
    assert resolved_parent is not None
    assert resolved_parent.edition_name == "底本"
