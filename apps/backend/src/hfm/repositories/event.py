"""Event repository (CD-6 — NEW, CA-004)."""

from __future__ import annotations

from typing import Any

from sqlalchemy import select

from hfm.models.assertion import EditorialStatus, assertion_evidences
from hfm.models.entity import Entity, EntityType
from hfm.models.event import Event, EventBoundPrecision, event_assertions, validate_event_frame
from hfm.repositories.base import BaseRepository


class EventRepository(BaseRepository[Event]):
    """CRUD for the Event aggregate (typed-Entity extension)."""

    model = Event

    async def get_by_id(self, id: str) -> Event | None:
        """Resolve by the semantic identity (events.entity_id = entities.id)."""
        stmt = select(Event).where(Event.entity_id == id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, **kwargs: Any) -> Event:
        """Create an Event row bound to an existing entity_type='event' Entity.

        The temporal frame is validated before insert (consistency,
        ranges, start<=end); the DB CHECKs are the backstop (§35).
        """
        entity_id = kwargs.get("entity_id")
        if entity_id is None:
            raise ValueError("event entity_id is required")
        entity = await self.session.get(Entity, str(entity_id))
        if entity is None:
            raise ValueError("event entity does not exist")
        if entity.entity_type != EntityType.event.value:
            raise ValueError("event entity must have entity_type='event'")
        start_precision = EventBoundPrecision(kwargs.get("start_precision", "unknown"))
        end_precision = EventBoundPrecision(kwargs.get("end_precision", "unknown"))
        validate_event_frame(
            start_year=kwargs.get("start_year"),
            start_month=kwargs.get("start_month"),
            start_day=kwargs.get("start_day"),
            start_precision=start_precision,
            end_year=kwargs.get("end_year"),
            end_month=kwargs.get("end_month"),
            end_day=kwargs.get("end_day"),
            end_precision=end_precision,
        )
        payload = dict(kwargs)
        payload["start_precision"] = start_precision.value
        payload["end_precision"] = end_precision.value
        return await super().create(**payload)

    async def attach_assertion(self, event_id: str, assertion_id: str) -> None:
        """Aggregate an Assertion to the Event (事件证据链, Frozen Canonical §1).

        Rejects withdrawn Assertions (withdrawn-reference gate — CD-5
        consistency): a withdrawn claim cannot anchor an event's record.
        """
        event = await self.get_by_id(event_id)
        if event is None:
            raise ValueError("event does not exist")
        from hfm.models.assertion import Assertion

        assertion = await self.session.get(Assertion, assertion_id)
        if assertion is None:
            raise ValueError("assertion does not exist")
        if assertion.editorial_status == EditorialStatus.withdrawn:
            raise ValueError("cannot aggregate a withdrawn assertion (withdrawn-reference gate)")
        stmt = select(event_assertions).where(
            event_assertions.c.event_id == event_id,
            event_assertions.c.assertion_id == assertion_id,
        )
        if (await self.session.execute(stmt)).first() is not None:
            return  # idempotent aggregation
        await self.session.execute(
            event_assertions.insert().values(event_id=event_id, assertion_id=assertion_id)
        )
        await self.session.flush()

    async def assertion_ids(self, event_id: str) -> list[str]:
        """Aggregated assertion ids (Event → Assertion)."""
        stmt = select(event_assertions.c.assertion_id).where(
            event_assertions.c.event_id == event_id
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def evidence_ids(self, event_id: str) -> list[str]:
        """Evidence ids reachable from the event via its Assertions (I1 chain)."""
        stmt = (
            select(assertion_evidences.c.evidence_id)
            .join(
                event_assertions,
                event_assertions.c.assertion_id == assertion_evidences.c.assertion_id,
            )
            .where(event_assertions.c.event_id == event_id)
        )
        result = await self.session.execute(stmt)
        return list(dict.fromkeys(result.scalars().all()))
