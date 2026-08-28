"""Tests for the Version model (CD-2 — REUSE + I2)."""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from hfm.repositories.edition import EditionRepository
from hfm.repositories.version import VersionRepository
from hfm.repositories.work import WorkRepository


async def _make_edition(session: AsyncSession) -> str:
    work = await WorkRepository(session).create(title="针灸甲乙经")
    edition = await EditionRepository(session).create(work_id=work.id, edition_name="宋刻本")
    return edition.id


async def test_version_construction_and_immutable_identity(session: AsyncSession) -> None:
    edition_id = await _make_edition(session)
    repo = VersionRepository(session)
    version = await repo.create(
        edition_id=edition_id, version_name="北宋刻本", is_formal_source=True
    )
    assert version.id
    assert version.edition_id == edition_id
    assert version.is_formal_source is True
    # immutable id guard (I5/I4)
    assert "id" in VersionRepository.model.immutable_fields


async def test_version_requires_edition(session: AsyncSession) -> None:
    repo = VersionRepository(session)
    with pytest.raises(IntegrityError):
        await repo.create(edition_id="missing-edition", version_name="孤儿版本")


async def test_version_lineage_parent(session: AsyncSession) -> None:
    """I2: parent/root lineage via parent_version_id."""
    edition_id = await _make_edition(session)
    repo = VersionRepository(session)
    root = await repo.create(edition_id=edition_id, version_name="底本")
    child = await repo.create(
        edition_id=edition_id, version_name="校勘本", parent_version_id=root.id
    )
    assert child.parent_version_id == root.id
    versions = await repo.get_by_edition(edition_id)
    assert {v.version_name for v in versions} == {"底本", "校勘本"}


async def test_version_missing_parent_rejected(session: AsyncSession) -> None:
    edition_id = await _make_edition(session)
    repo = VersionRepository(session)
    with pytest.raises(ValueError):
        await repo.create(
            edition_id=edition_id, version_name="无父版本", parent_version_id="missing-parent"
        )


async def test_version_cross_edition_parent_rejected(session: AsyncSession) -> None:
    """Lineage parent must belong to the same Edition (I2)."""
    work = await WorkRepository(session).create(title="针灸甲乙经")
    edition_a = await EditionRepository(session).create(work_id=work.id, edition_name="宋刻本")
    edition_b = await EditionRepository(session).create(work_id=work.id, edition_name="四库本")
    parent = await VersionRepository(session).create(edition_id=edition_a.id, version_name="底本")
    repo = VersionRepository(session)
    with pytest.raises(ValueError):
        await repo.create(
            edition_id=edition_b.id, version_name="跨版本谱系", parent_version_id=parent.id
        )


async def test_version_parent_cycle_rejected(session: AsyncSession) -> None:
    """I2: parent_version_id is protected — post-create mutation (cycle formation) rejected."""
    edition_id = await _make_edition(session)
    repo = VersionRepository(session)
    root = await repo.create(edition_id=edition_id, version_name="底本")
    child = await repo.create(
        edition_id=edition_id, version_name="校勘本", parent_version_id=root.id
    )
    # attempting to rewire root.parent = child (would create a cycle) is rejected
    with pytest.raises(ValueError):
        await repo.update(root.id, parent_version_id=child.id)
