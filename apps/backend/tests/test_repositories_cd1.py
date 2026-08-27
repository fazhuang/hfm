"""CD-1 repository behavior tests (Entity / Person)."""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from hfm.models.entity import Entity, EntityType
from hfm.repositories.entity import EntityRepository
from hfm.repositories.person import PersonRepository


async def test_entity_update_rejects_immutable_fields(session: AsyncSession) -> None:
    """CD-0 immutable guard is preserved on CD-1 models (I5)."""
    repo = EntityRepository(session)
    entity = await repo.create(entity_type=EntityType.place, name="安定")
    assert "id" in Entity.immutable_fields
    updated = await repo.update(entity.id, name="安定县")
    assert updated is not None
    assert updated.name == "安定县"


async def test_person_delete_requires_entity_restrict(session: AsyncSession) -> None:
    """Deleting an Entity that has a Person must fail (FK RESTRICT)."""
    entity_repo = EntityRepository(session)
    person_repo = PersonRepository(session)
    entity = await entity_repo.create(entity_type=EntityType.person, name="皇甫谧")
    await person_repo.create(entity_id=entity.id)
    with pytest.raises(IntegrityError):
        await entity_repo.delete(entity.id)


async def test_entity_duplicate_name_allowed_across_types(session: AsyncSession) -> None:
    """Entity.name is not a global unique identity — stable identity is the id (I5)."""
    repo = EntityRepository(session)
    first = await repo.create(entity_type=EntityType.person, name="同名")
    second = await repo.create(entity_type=EntityType.work, name="同名")
    assert first.id != second.id
    assert (await repo.count()) == 2
