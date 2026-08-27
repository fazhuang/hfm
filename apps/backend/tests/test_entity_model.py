"""Tests for Entity + EntityType (CD-1 — ADAPT/REUSE)."""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from hfm.models.entity import Entity, EntityType
from hfm.repositories.entity import EntityRepository


async def test_entity_construction(session: AsyncSession) -> None:
    repo = EntityRepository(session)
    entity = await repo.create(entity_type=EntityType.person, name="皇甫谧", name_zh="皇甫謐")
    assert entity.id  # stable UUIDv7 identity (I5)
    assert entity.entity_type == EntityType.person
    assert entity.name == "皇甫谧"


async def test_entity_invalid_type_rejected(session: AsyncSession) -> None:
    repo = EntityRepository(session)
    with pytest.raises(IntegrityError):
        await repo.create(entity_type="not-a-type", name="x")


async def test_entity_get_by_type(session: AsyncSession) -> None:
    repo = EntityRepository(session)
    await repo.create(entity_type=EntityType.acupoint, name="合谷")
    await repo.create(entity_type=EntityType.acupoint, name="商阳")
    await repo.create(entity_type=EntityType.place, name="安定")
    acupoints = await repo.get_by_type(EntityType.acupoint)
    assert {a.name for a in acupoints} == {"合谷", "商阳"}


async def test_entity_crud(session: AsyncSession) -> None:
    repo = EntityRepository(session)
    entity = await repo.create(entity_type=EntityType.work, name="针灸甲乙经")
    assert await repo.get_by_id(entity.id) is not None
    updated = await repo.update(entity.id, description="十二卷")
    assert updated is not None
    assert updated.description == "十二卷"
    assert await repo.delete(entity.id) is True


def test_entity_type_values_are_canonical_families() -> None:
    """EntityType is the frozen canonical family set; no catch-all / medical-class values."""
    assert set(EntityType) == {
        EntityType.person,
        EntityType.work,
        EntityType.place,
        EntityType.institution,
        EntityType.concept,
        EntityType.acupoint,
        EntityType.event,
    }
    assert Entity is not None
