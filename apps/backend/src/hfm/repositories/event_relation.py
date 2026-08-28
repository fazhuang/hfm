"""EventRelation repository (CD-6 — Person/Event 关系, ADAPT CA-001)."""

from __future__ import annotations

from typing import Any

from sqlalchemy import select

from hfm.models.entity import Entity
from hfm.models.event_relation import EventRelation, EventRelationRole
from hfm.repositories.base import BaseRepository
from hfm.repositories.event import EventRepository


class EventRelationRepository(BaseRepository[EventRelation]):
    """CRUD for Person/Event relations (structural binding, immutable)."""

    model = EventRelation

    async def create(self, **kwargs: Any) -> EventRelation:
        entity_id = kwargs.get("entity_id")
        event_id = kwargs.get("event_id")
        if entity_id is None or event_id is None:
            raise ValueError("event relation requires entity_id and event_id")
        if str(entity_id) == str(event_id):
            raise ValueError("relation entity_id must not equal event_id")
        entity = await self.session.get(Entity, str(entity_id))
        if entity is None:
            raise ValueError("relation entity does not exist")
        event = await EventRepository(self.session).get_by_id(str(event_id))
        if event is None:
            raise ValueError("relation event does not exist")
        role = kwargs.get("relation_role")
        if role is None:
            raise ValueError("event relation requires relation_role")
        EventRelationRole(str(role))  # raises for invalid role values
        payload = dict(kwargs)
        if isinstance(payload.get("relation_role"), EventRelationRole):
            payload["relation_role"] = payload["relation_role"].value
        return await super().create(**payload)

    async def list_by_event(self, event_id: str) -> list[EventRelation]:
        stmt = (
            select(EventRelation)
            .where(EventRelation.event_id == event_id)
            .order_by(EventRelation.created_at)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_by_entity(self, entity_id: str) -> list[EventRelation]:
        stmt = (
            select(EventRelation)
            .where(EventRelation.entity_id == entity_id)
            .order_by(EventRelation.created_at)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
