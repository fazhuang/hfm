"""Entity repository (CD-1)."""

from __future__ import annotations

from sqlalchemy import select

from hfm.models.entity import Entity, EntityType
from hfm.repositories.base import BaseRepository


class EntityRepository(BaseRepository[Entity]):
    """CRUD for typed entities."""

    model = Entity

    async def get_by_type(self, entity_type: EntityType) -> list[Entity]:
        stmt = select(Entity).where(Entity.entity_type == entity_type.value).order_by(Entity.name)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
