"""CD-6 Event model tests (stable identity, temporal frame, immutability)."""

from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from hfm.models.entity import Entity, EntityType
from hfm.models.event import EventBoundPrecision, EventType, validate_event_frame
from hfm.repositories.entity import EntityRepository
from hfm.repositories.event import EventRepository


async def _make_event_entity(session: AsyncSession, name: str = "皇甫谧出生") -> Entity:
    return await EntityRepository(session).create(entity_type=EntityType.event, name=name)


async def test_event_typed_entity_identity(session: AsyncSession) -> None:
    """Event identity lives on the CD-1 Entity row (I5, entity_type='event')."""
    entity = await _make_event_entity(session)
    event = await EventRepository(session).create(
        entity_id=entity.id,
        event_type=EventType.birth,
        start_year=215,
        start_precision=EventBoundPrecision.year,
        end_year=215,
        end_precision=EventBoundPrecision.year,
    )
    assert event.entity_id == entity.id
    assert entity.entity_type == EntityType.event.value
    reloaded = await EventRepository(session).get_by_id(event.entity_id)
    assert reloaded is not None
    assert reloaded.event_type == EventType.birth


async def test_event_create_rejects_non_event_entity(session: AsyncSession) -> None:
    """An Event row may only bind to an entity_type='event' Entity."""
    person = await EntityRepository(session).create(entity_type=EntityType.person, name="皇甫谧")
    with pytest.raises(ValueError, match="entity_type='event'"):
        await EventRepository(session).create(entity_id=person.id, event_type=EventType.birth)


async def test_event_create_rejects_missing_entity(session: AsyncSession) -> None:
    with pytest.raises(ValueError, match="does not exist"):
        await EventRepository(session).create(
            entity_id="00000000-0000-7000-8000-000000000000",
            event_type=EventType.birth,
        )


@pytest.mark.parametrize(
    "frame",
    [
        # precision=year requires year present, month/day absent
        dict(
            start_year=None,
            start_precision=EventBoundPrecision.year,
        ),
        # precision=month requires month present
        dict(
            start_year=215,
            start_month=None,
            start_precision=EventBoundPrecision.month,
        ),
        # precision=day requires day present
        dict(
            start_year=215,
            start_month=2,
            start_day=None,
            start_precision=EventBoundPrecision.day,
        ),
        # precision=unknown requires all parts absent
        dict(
            start_year=215,
            start_precision=EventBoundPrecision.unknown,
        ),
        # month out of range
        dict(
            start_year=215,
            start_month=13,
            start_precision=EventBoundPrecision.month,
        ),
        # day out of range
        dict(
            start_year=215,
            start_month=2,
            start_day=32,
            start_precision=EventBoundPrecision.day,
        ),
    ],
)
async def test_event_frame_validation_rejects_invalid(
    session: AsyncSession, frame: dict[str, object]
) -> None:
    entity = await _make_event_entity(session)
    with pytest.raises(ValueError):
        await EventRepository(session).create(
            entity_id=entity.id, event_type=EventType.birth, **frame
        )


async def test_event_frame_start_after_end_rejected(session: AsyncSession) -> None:
    """§16: start must not be after end."""
    entity = await _make_event_entity(session)
    with pytest.raises(ValueError, match="must not be after end"):
        await EventRepository(session).create(
            entity_id=entity.id,
            event_type=EventType.career,
            start_year=282,
            start_precision=EventBoundPrecision.year,
            end_year=215,
            end_precision=EventBoundPrecision.year,
        )


async def test_event_open_interval_allowed(session: AsyncSession) -> None:
    """Unknown bound = open interval (Frozen CD-6: 未知/开放区间按契约允许)."""
    entity = await _make_event_entity(session)
    event = await EventRepository(session).create(
        entity_id=entity.id,
        event_type=EventType.travel,
        start_year=215,
        start_precision=EventBoundPrecision.year,
        # end unknown → open end
    )
    assert event.start_year == 215
    assert event.end_year is None
    assert event.end_precision == EventBoundPrecision.unknown


async def test_event_day_precision_roundtrip(session: AsyncSession) -> None:
    """Full YYYY-MM-DD precision is supported (not reduced to datetime)."""
    entity = await _make_event_entity(session)
    event = await EventRepository(session).create(
        entity_id=entity.id,
        event_type=EventType.meeting,
        start_year=215,
        start_month=6,
        start_day=1,
        start_precision=EventBoundPrecision.day,
        end_year=215,
        end_month=6,
        end_day=1,
        end_precision=EventBoundPrecision.day,
    )
    assert (event.start_year, event.start_month, event.start_day) == (215, 6, 1)
    assert (event.end_year, event.end_month, event.end_day) == (215, 6, 1)


async def test_event_frame_immutable_after_persist(session: AsyncSession) -> None:
    """I4: the canonical temporal frame is immutable once persisted."""
    entity = await _make_event_entity(session)
    repo = EventRepository(session)
    event = await repo.create(
        entity_id=entity.id,
        event_type=EventType.birth,
        start_year=215,
        start_precision=EventBoundPrecision.year,
        end_year=215,
        end_precision=EventBoundPrecision.year,
    )
    await session.flush()
    with pytest.raises(ValueError, match="immutable"):
        await repo.update(event.entity_id, start_year=214)
    with pytest.raises(ValueError, match="immutable"):
        await repo.update(event.entity_id, event_type=EventType.death)


def test_validate_event_frame_helper_units() -> None:
    """Unit-level frame validation (no DB needed)."""
    with pytest.raises(ValueError):
        validate_event_frame(
            start_year=216,
            start_month=None,
            start_day=None,
            start_precision=EventBoundPrecision.year,
            end_year=215,
            end_month=None,
            end_day=None,
            end_precision=EventBoundPrecision.year,
        )
    validate_event_frame(
        start_year=214,
        start_month=None,
        start_day=None,
        start_precision=EventBoundPrecision.year,
        end_year=216,
        end_month=None,
        end_day=None,
        end_precision=EventBoundPrecision.year,
    )
    validate_event_frame(
        start_year=None,
        start_month=None,
        start_day=None,
        start_precision=EventBoundPrecision.unknown,
        end_year=None,
        end_month=None,
        end_day=None,
        end_precision=EventBoundPrecision.unknown,
    )
