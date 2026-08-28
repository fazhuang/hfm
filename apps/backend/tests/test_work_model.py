"""Tests for the Work model (CD-2 — REUSE, CA-007)."""

from sqlalchemy.ext.asyncio import AsyncSession

from hfm.models.entity import EntityType
from hfm.repositories.entity import EntityRepository
from hfm.repositories.work import WorkRepository


async def test_work_construction(session: AsyncSession) -> None:
    repo = WorkRepository(session)
    work = await repo.create(
        title="针灸甲乙经", dynasty="魏晋", category="医学/针灸", is_extant=True
    )
    assert work.id  # stable UUIDv7 (I5)
    assert work.title == "针灸甲乙经"
    assert work.is_extant is True


async def test_work_author_entity_link(session: AsyncSession) -> None:
    """Work.author_entity_id references a CD-1 Entity (person)."""
    entity_repo = EntityRepository(session)
    work_repo = WorkRepository(session)
    author = await entity_repo.create(entity_type=EntityType.person, name="皇甫谧")
    work = await work_repo.create(title="玄晏春秋", author_entity_id=author.id)
    assert work.author_entity_id == author.id
    resolved = await entity_repo.get_by_id(work.author_entity_id or "")
    assert resolved is not None
    assert resolved.entity_type == EntityType.person


async def test_work_crud(session: AsyncSession) -> None:
    repo = WorkRepository(session)
    work = await repo.create(title="甲乙经辑佚", is_extant=False)
    fetched = await repo.get_by_id(work.id)
    assert fetched is not None
    updated = await repo.update(work.id, description="辑佚本")
    assert updated is not None
    assert updated.description == "辑佚本"
    assert await repo.delete(work.id) is True
