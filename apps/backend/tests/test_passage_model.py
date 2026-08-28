"""Tests for the Passage model (CD-2 — REUSE + locator, I2)."""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from hfm.core.locator import Locator
from hfm.repositories.chapter import ChapterRepository
from hfm.repositories.edition import EditionRepository
from hfm.repositories.passage import PassageRepository
from hfm.repositories.version import VersionRepository
from hfm.repositories.work import WorkRepository


async def _make_chain(session: AsyncSession) -> tuple[str, str, str]:
    """Build work → edition → version → chapter; return (work, chapter, version) ids."""
    work = await WorkRepository(session).create(title="针灸甲乙经")
    edition = await EditionRepository(session).create(work_id=work.id, edition_name="宋刻本")
    version = await VersionRepository(session).create(edition_id=edition.id, version_name="北宋本")
    chapter = await ChapterRepository(session).create(work_id=work.id, title="卷一")
    return work.id, chapter.id, version.id


async def test_passage_construction(session: AsyncSession) -> None:
    work_id, chapter_id, version_id = await _make_chain(session)
    repo = PassageRepository(session)
    passage = await repo.create(
        chapter_id=chapter_id, version_id=version_id, content_text="凡灸刺之要", order=1
    )
    assert passage.id
    assert passage.chapter_id == chapter_id
    assert passage.version_id == version_id  # pinned fixed reference


async def test_passage_requires_chapter(session: AsyncSession) -> None:
    repo = PassageRepository(session)
    with pytest.raises(IntegrityError):
        await repo.create(chapter_id="missing-chapter", content_text="孤儿条文")


async def test_passage_locator_resolution(session: AsyncSession) -> None:
    """Locator reproducibility: locator derived from the FK chain (I2)."""
    work_id, chapter_id, version_id = await _make_chain(session)
    repo = PassageRepository(session)
    passage = await repo.create(
        chapter_id=chapter_id, version_id=version_id, content_text="甲乙经条文", order=2
    )
    locator = Locator(
        work_id=work_id,
        version_id=passage.version_id,
        chapter_id=passage.chapter_id,
        passage_id=passage.id,
    )
    rendered = locator.to_locator_string()
    assert f"work:{work_id}" in rendered
    assert f"passage:{passage.id}" in rendered
    assert f"version:{version_id}" in rendered
    assert not locator.is_empty()


async def test_passage_pinned_version_not_swapped(session: AsyncSession) -> None:
    """I2: no silent 'latest' swap — the pinned version stays on update."""
    _, chapter_id, version_id = await _make_chain(session)
    repo = PassageRepository(session)
    passage = await repo.create(
        chapter_id=chapter_id, version_id=version_id, content_text="定本条文"
    )
    updated = await repo.update(passage.id, notes="校勘注")
    assert updated is not None
    assert updated.version_id == version_id  # pinned reference unchanged
    assert updated.content_text == "定本条文"
