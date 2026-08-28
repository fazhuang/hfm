"""Tests for the Chapter model (CD-2 — REUSE, CA-014)."""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from hfm.repositories.chapter import ChapterRepository
from hfm.repositories.work import WorkRepository


async def test_chapter_construction(session: AsyncSession) -> None:
    work = await WorkRepository(session).create(title="针灸甲乙经")
    repo = ChapterRepository(session)
    chapter = await repo.create(work_id=work.id, title="卷一", order=1)
    assert chapter.id
    assert chapter.work_id == work.id
    assert chapter.order == 1


async def test_chapter_requires_work(session: AsyncSession) -> None:
    repo = ChapterRepository(session)
    with pytest.raises(IntegrityError):
        await repo.create(work_id="missing-work", title="孤儿章节")


async def test_chapter_hierarchy_parent(session: AsyncSession) -> None:
    work = await WorkRepository(session).create(title="针灸甲乙经")
    repo = ChapterRepository(session)
    parent = await repo.create(work_id=work.id, title="卷一")
    child = await repo.create(work_id=work.id, title="第一节", parent_id=parent.id)
    assert child.parent_id == parent.id
    resolved = await repo.get_by_id(child.parent_id or "")
    assert resolved is not None
    assert resolved.title == "卷一"
