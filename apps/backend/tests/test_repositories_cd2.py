"""CD-2 repository behavior + FK negative tests."""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from hfm.repositories.chapter import ChapterRepository
from hfm.repositories.edition import EditionRepository
from hfm.repositories.passage import PassageRepository
from hfm.repositories.version import VersionRepository
from hfm.repositories.work import WorkRepository


async def test_work_update_rejects_immutable_id(session: AsyncSession) -> None:
    from hfm.models.work import Work

    repo = WorkRepository(session)
    work = await repo.create(title="玄晏春秋")
    assert "id" in Work.immutable_fields
    updated = await repo.update(work.id, description="辑佚")
    assert updated is not None
    assert updated.description == "辑佚"


async def test_edition_delete_cascades_to_versions(session: AsyncSession) -> None:
    """FK CASCADE: deleting an Edition removes its Versions (HFB semantics)."""
    work = await WorkRepository(session).create(title="针灸甲乙经")
    edition = await EditionRepository(session).create(work_id=work.id, edition_name="四库本")
    version = await VersionRepository(session).create(
        edition_id=edition.id, version_name="四库全书本"
    )
    assert await EditionRepository(session).delete(edition.id) is True
    assert (await VersionRepository(session).get_by_id(version.id)) is None


async def test_chapter_delete_cascades_to_passages(session: AsyncSession) -> None:
    work = await WorkRepository(session).create(title="针灸甲乙经")
    chapter = await ChapterRepository(session).create(work_id=work.id, title="卷一")
    passage = await PassageRepository(session).create(chapter_id=chapter.id, content_text="条文")
    assert await ChapterRepository(session).delete(chapter.id) is True
    assert (await PassageRepository(session).get_by_id(passage.id)) is None


async def test_cross_work_chapter_fk_rejected(session: AsyncSession) -> None:
    """Wrong parent type: chapter referencing a missing Work is rejected."""
    repo = ChapterRepository(session)
    with pytest.raises(IntegrityError):
        await repo.create(work_id="no-such-work", title="孤儿章节")


async def test_cd2_protected_fields_guard(session: AsyncSession) -> None:
    """CD-2 protected fields (version_id / lineage) reject post-create mutation."""
    from hfm.models.passage import Passage

    assert "version_id" in Passage.immutable_fields
    work = await WorkRepository(session).create(title="针灸甲乙经")
    chapter = await ChapterRepository(session).create(work_id=work.id, title="卷一")
    passage = await PassageRepository(session).create(chapter_id=chapter.id, content_text="条文")
    with pytest.raises(ValueError):
        await PassageRepository(session).update(passage.id, version_id="any")
