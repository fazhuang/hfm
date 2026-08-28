"""CD-6 strong DB probes — raw SQL bypassing repositories (§35).

These exercise the events / event_relations / event_assertions table
constraints directly: invalid FK, invalid enum, precision consistency,
ranges, start<=end, self-relation, duplicates — via raw INSERTs only
(bypassing repository guards entirely).
"""

from __future__ import annotations

import pytest
import sqlalchemy as sa
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from hfm.models.entity import EntityType
from hfm.models.event import EventBoundPrecision, EventType
from hfm.repositories.entity import EntityRepository
from hfm.repositories.event import EventRepository


async def _insert_event(
    session: AsyncSession,
    entity_id: str,
    *,
    event_type: str = "birth",
    start_year: int | None = 215,
    start_precision: str = "year",
    end_year: int | None = 215,
    end_precision: str = "year",
) -> None:
    await session.execute(
        sa.text(
            "INSERT INTO events (entity_id, event_type, start_year, start_precision,"
            " end_year, end_precision, created_at, updated_at)"
            " VALUES (:eid, :etype, :sy, :sp, :ey, :ep, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
        ),
        {
            "eid": entity_id,
            "etype": event_type,
            "sy": start_year,
            "sp": start_precision,
            "ey": end_year,
            "ep": end_precision,
        },
    )


async def _make_event_entity(session: AsyncSession) -> str:
    entity = await EntityRepository(session).create(entity_type=EntityType.event, name="探针事件")
    return entity.id


async def test_db_probe_invalid_fk_entity(session: AsyncSession) -> None:
    """Invalid FK: events.entity_id must reference a real entity row."""
    with pytest.raises(IntegrityError):
        await _insert_event(session, "00000000-0000-7000-8000-000000000000", event_type="birth")


async def test_db_probe_invalid_event_type_enum(session: AsyncSession) -> None:
    """Invalid enum: event_type must be one of the frozen values."""
    entity_id = await _make_event_entity(session)
    with pytest.raises(IntegrityError):
        await _insert_event(session, entity_id, event_type="supernova")


async def test_db_probe_invalid_precision_enum(session: AsyncSession) -> None:
    entity_id = await _make_event_entity(session)
    with pytest.raises(IntegrityError):
        await _insert_event(session, entity_id, start_precision="century")


async def test_db_probe_precision_year_requires_year(session: AsyncSession) -> None:
    """precision='year' with NULL year must be rejected (CHECK consistency)."""
    entity_id = await _make_event_entity(session)
    with pytest.raises(IntegrityError):
        await _insert_event(session, entity_id, start_year=None, start_precision="year")


async def test_db_probe_precision_unknown_requires_nulls(session: AsyncSession) -> None:
    """precision='unknown' with a year present must be rejected."""
    entity_id = await _make_event_entity(session)
    with pytest.raises(IntegrityError):
        await _insert_event(
            session,
            entity_id,
            start_year=215,
            start_precision="unknown",
            end_year=None,
            end_precision="unknown",
        )


async def test_db_probe_invalid_month(session: AsyncSession) -> None:
    entity_id = await _make_event_entity(session)
    with pytest.raises(IntegrityError):
        await session.execute(
            sa.text(
                "INSERT INTO events (entity_id, event_type, start_year, start_month,"
                " start_precision, end_year, end_precision, created_at, updated_at)"
                " VALUES (:eid, 'birth', 215, 13, 'month', 215, 'month',"
                " CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
            ),
            {"eid": entity_id},
        )


async def test_db_probe_end_before_start(session: AsyncSession) -> None:
    """start<=end must hold at the DB level (§16)."""
    entity_id = await _make_event_entity(session)
    with pytest.raises(IntegrityError):
        await _insert_event(
            session,
            entity_id,
            start_year=282,
            start_precision="year",
            end_year=215,
            end_precision="year",
        )


async def test_db_probe_self_relation(session: AsyncSession) -> None:
    """entity_id <> event_id must hold at the DB level."""
    entity_id = await _make_event_entity(session)
    event = await EventRepository(session).create(
        entity_id=entity_id,
        event_type=EventType.birth,
        start_year=215,
        start_precision=EventBoundPrecision.year,
        end_year=215,
        end_precision=EventBoundPrecision.year,
    )
    with pytest.raises(IntegrityError):
        await session.execute(
            sa.text(
                "INSERT INTO event_relations (id, entity_id, event_id, relation_role,"
                " created_at, updated_at)"
                " VALUES (:rid, :entity, :event, 'actor', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
            ),
            {
                "rid": "99999999-0000-7000-8000-000000000001",
                "entity": entity_id,
                "event": event.entity_id,
            },
        )


async def test_db_probe_relation_duplicate_unique(session: AsyncSession) -> None:
    """UNIQUE(entity_id, event_id, relation_role) at the DB level."""
    from hfm.models.event_relation import EventRelationRole
    from hfm.repositories.event_relation import EventRelationRepository

    entity_id = await _make_event_entity(session)
    event = await EventRepository(session).create(
        entity_id=entity_id,
        event_type=EventType.birth,
        start_year=215,
        start_precision=EventBoundPrecision.year,
        end_year=215,
        end_precision=EventBoundPrecision.year,
    )
    person = await EntityRepository(session).create(entity_type=EntityType.person, name="皇甫谧")
    repo = EventRelationRepository(session)
    await repo.create(
        entity_id=person.id, event_id=event.entity_id, relation_role=EventRelationRole.actor
    )
    with pytest.raises(IntegrityError):
        await session.execute(
            sa.text(
                "INSERT INTO event_relations (id, entity_id, event_id, relation_role,"
                " created_at, updated_at)"
                " VALUES (:rid, :entity, :event, 'actor', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
            ),
            {
                "rid": "99999999-0000-7000-8000-000000000002",
                "entity": person.id,
                "event": event.entity_id,
            },
        )


async def test_db_probe_relation_invalid_fk(session: AsyncSession) -> None:
    """event_relations.event_id must reference an events row."""
    person = await EntityRepository(session).create(entity_type=EntityType.person, name="皇甫谧")
    with pytest.raises(IntegrityError):
        await session.execute(
            sa.text(
                "INSERT INTO event_relations (id, entity_id, event_id, relation_role,"
                " created_at, updated_at)"
                " VALUES (:rid, :entity, :event, 'actor', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
            ),
            {
                "rid": "99999999-0000-7000-8000-000000000003",
                "entity": person.id,
                "event": "00000000-0000-7000-8000-000000000000",
            },
        )


async def test_db_probe_aggregation_subject_mismatch(session: AsyncSession) -> None:
    """P1 fix (direct-DB): raw INSERT with subject != event is rejected by the trigger."""
    from hfm.repositories.assertion import AssertionRepository

    entity_id = await _make_event_entity(session)
    event = await EventRepository(session).create(
        entity_id=entity_id,
        event_type=EventType.birth,
        start_year=215,
        start_precision=EventBoundPrecision.year,
        end_year=215,
        end_precision=EventBoundPrecision.year,
    )
    person = await EntityRepository(session).create(entity_type=EntityType.person, name="皇甫谧")
    person_assertion = await AssertionRepository(session).create(
        subject_entity_id=person.id, predicate="born_in", value="安定"
    )
    with pytest.raises(IntegrityError, match="subject mismatch"):
        await session.execute(
            sa.text(
                "INSERT INTO event_assertions (event_id, assertion_id) VALUES (:event, :assertion)"
            ),
            {"event": event.entity_id, "assertion": person_assertion.id},
        )


async def test_db_probe_aggregation_subject_match_allowed(session: AsyncSession) -> None:
    """Direct-DB: raw INSERT succeeds when subject_entity_id == event_id."""
    from hfm.repositories.assertion import AssertionRepository

    entity_id = await _make_event_entity(session)
    event = await EventRepository(session).create(
        entity_id=entity_id,
        event_type=EventType.birth,
        start_year=215,
        start_precision=EventBoundPrecision.year,
        end_year=215,
        end_precision=EventBoundPrecision.year,
    )
    assertion = await AssertionRepository(session).create(
        subject_entity_id=event.entity_id, predicate="occurred_at", value="公元215年"
    )
    await session.execute(
        sa.text(
            "INSERT INTO event_assertions (event_id, assertion_id) VALUES (:event, :assertion)"
        ),
        {"event": event.entity_id, "assertion": assertion.id},
    )
    await session.flush()
    rows = (await session.execute(sa.text("SELECT COUNT(*) FROM event_assertions"))).scalar_one()
    assert rows == 1


async def test_db_probe_event_delete_cascades_aggregation(session: AsyncSession) -> None:
    """event_assertions CASCADE: deleting the events row removes aggregation edges."""
    entity_id = await _make_event_entity(session)
    event = await EventRepository(session).create(
        entity_id=entity_id,
        event_type=EventType.birth,
        start_year=215,
        start_precision=EventBoundPrecision.year,
        end_year=215,
        end_precision=EventBoundPrecision.year,
    )
    from hfm.repositories.assertion import AssertionRepository

    assertion = await AssertionRepository(session).create(
        subject_entity_id=event.entity_id, predicate="occurred_at", value="公元215年"
    )
    await EventRepository(session).attach_assertion(event.entity_id, assertion.id)
    await session.execute(
        sa.text("DELETE FROM events WHERE entity_id = :eid"), {"eid": event.entity_id}
    )
    await session.flush()
    rows = (await session.execute(sa.text("SELECT COUNT(*) FROM event_assertions"))).scalar_one()
    assert rows == 0
