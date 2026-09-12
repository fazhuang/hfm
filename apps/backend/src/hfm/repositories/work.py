"""Work repository (CD-2 + P1-04 typed-Entity identity)."""

from __future__ import annotations

from typing import Any

from hfm.models.entity import Entity, EntityType
from hfm.models.work import Work
from hfm.repositories.base import BaseRepository


class WorkRepository(BaseRepository[Work]):
    """CRUD for Work (P1-04: optional typed-Entity identity, I5)."""

    model = Work

    async def create(self, **kwargs: Any) -> Work:
        """Create a Work; when ``entity_id`` is given it must resolve to an
        existing entity_type='work' Entity (typed-Entity backbone, I5)."""
        entity_id = kwargs.get("entity_id")
        if entity_id is not None:
            entity = await self.session.get(Entity, str(entity_id))
            if entity is None:
                raise ValueError("work entity does not exist")
            if entity.entity_type != EntityType.work.value:
                raise ValueError("work entity must have entity_type='work'")
        return await super().create(**kwargs)

    async def get_by_entity_id(self, entity_id: str) -> Work | None:
        """Resolve a Work by its typed-Entity identity (I5)."""
        from sqlalchemy import select

        stmt = select(Work).where(Work.entity_id == entity_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
