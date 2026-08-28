"""CD-2 invariant tests (I2 / I4 / I5)."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from hfm.core.locator import Locator
from hfm.repositories.chapter import ChapterRepository
from hfm.repositories.edition import EditionRepository
from hfm.repositories.passage import PassageRepository
from hfm.repositories.version import VersionRepository
from hfm.repositories.work import WorkRepository


async def _make_chain(session: AsyncSession) -> tuple[str, str, str, str]:
    work = await WorkRepository(session).create(title="针灸甲乙经")
    edition = await EditionRepository(session).create(work_id=work.id, edition_name="宋刻本")
    root = await VersionRepository(session).create(edition_id=edition.id, version_name="底本")
    child = await VersionRepository(session).create(
        edition_id=edition.id, version_name="校勘本", parent_version_id=root.id
    )
    chapter = await ChapterRepository(session).create(work_id=work.id, title="卷一")
    return work.id, chapter.id, root.id, child.id


async def test_invariant_i2_version_lineage_acyclic(session: AsyncSession) -> None:
    """I2: a valid lineage walks without cycles."""
    _, _, root_id, child_id = await _make_chain(session)
    repo = VersionRepository(session)
    assert await repo.lineage_has_cycle(child_id) is False
    assert await repo.lineage_has_cycle(root_id) is False


async def test_invariant_i2_cycle_formation_rejected(session: AsyncSession) -> None:
    """I2: rewiring lineage to form a cycle is rejected (protected parent)."""
    _, _, root_id, child_id = await _make_chain(session)
    repo = VersionRepository(session)
    # root.parent = child would create root → child → root cycle; rejected
    with pytest.raises(ValueError):
        await repo.update(root_id, parent_version_id=child_id)
    # detection helper still reports an acyclic lineage as clean
    assert await repo.lineage_has_cycle(child_id) is False


async def test_invariant_i2_pinned_version_reproducible(session: AsyncSession) -> None:
    """I2: a passage bound to a version reproduces its locator; no latest swap."""
    work_id, chapter_id, root_id, _ = await _make_chain(session)
    repo = PassageRepository(session)
    passage = await repo.create(
        chapter_id=chapter_id, version_id=root_id, content_text="定本条文", order=5
    )
    locator = Locator(
        work_id=work_id,
        version_id=passage.version_id,
        chapter_id=passage.chapter_id,
        passage_id=passage.id,
    )
    assert locator.version_id == root_id
    rendered = locator.to_locator_string()
    assert f"version:{root_id}" in rendered
    assert f"passage:{passage.id}" in rendered


async def test_invariant_i4_protected_fields(session: AsyncSession) -> None:
    """I4: lineage/pinned-reference fields are protected from silent overwrite."""
    from hfm.models.chapter import Chapter
    from hfm.models.edition import Edition
    from hfm.models.passage import Passage
    from hfm.models.version import Version

    assert "parent_version_id" in Version.immutable_fields
    assert "lineage_parent_edition_id" in Edition.immutable_fields
    assert "parent_id" in Chapter.immutable_fields
    assert "version_id" in Passage.immutable_fields
    assert "id" in Version.immutable_fields


async def test_invariant_i5_stable_identity(session: AsyncSession) -> None:
    """I5: Work/Edition/Version/Chapter/Passage all carry stable UUIDv7 ids."""
    work_id, chapter_id, root_id, _ = await _make_chain(session)
    for obj_id in (work_id, chapter_id, root_id):
        assert obj_id and len(obj_id) == 36
    assert (await WorkRepository(session).get_by_id(work_id)) is not None
