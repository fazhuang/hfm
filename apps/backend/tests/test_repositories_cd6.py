"""CD-6 repository tests: Event aggregation, evidence chain, Person/Event relation."""

from __future__ import annotations

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from hfm.models.entity import EntityType
from hfm.models.event import EventBoundPrecision, EventType
from hfm.models.event_relation import EventRelationRole
from hfm.repositories.assertion import AssertionRepository
from hfm.repositories.entity import EntityRepository
from hfm.repositories.event import EventRepository
from hfm.repositories.event_relation import EventRelationRepository
from hfm.repositories.evidence import EvidenceRepository
from hfm.repositories.source import SourceRepository
from hfm.repositories.source_ref import SourceRefRepository


async def _make_event(session: AsyncSession) -> str:
    entity = await EntityRepository(session).create(entity_type=EntityType.event, name="皇甫谧出生")
    event = await EventRepository(session).create(
        entity_id=entity.id,
        event_type=EventType.birth,
        start_year=215,
        start_precision=EventBoundPrecision.year,
        end_year=215,
        end_precision=EventBoundPrecision.year,
    )
    return event.entity_id


async def test_event_assertion_aggregation_and_evidence_chain(session: AsyncSession) -> None:
    """事件证据链: Event → Assertion → Evidence → SourceRef → Source (I1)."""
    event_id = await _make_event(session)
    person = await EntityRepository(session).create(entity_type=EntityType.person, name="皇甫谧")
    source, _ = await SourceRepository(session).create_idempotent(
        source_key="ssjys", title="世说新语·容止"
    )
    ref = await SourceRefRepository(session).create(source_id=source.id, title="世说新语")
    evidence = await EvidenceRepository(session).create(
        description="皇甫谧年二十余，以为痴", source_ref_id=ref.id
    )
    assertion = await AssertionRepository(session).create(
        subject_entity_id=person.id, predicate="born_in", value="安定"
    )
    await AssertionRepository(session).attach_evidence(assertion.id, evidence.id)

    repo = EventRepository(session)
    await repo.attach_assertion(event_id, assertion.id)
    assert await repo.assertion_ids(event_id) == [assertion.id]
    # evidence reachable via the aggregated assertion (I1 chain)
    assert await repo.evidence_ids(event_id) == [evidence.id]
    # reload: aggregation is persisted
    fresh = EventRepository(session)
    assert await fresh.assertion_ids(event_id) == [assertion.id]


async def test_attach_assertion_rejects_withdrawn(session: AsyncSession) -> None:
    """Withdrawn Assertions cannot anchor an event record (withdrawn-reference gate)."""
    event_id = await _make_event(session)
    person = await EntityRepository(session).create(entity_type=EntityType.person, name="皇甫谧")
    assertion = await AssertionRepository(session).create(
        subject_entity_id=person.id, predicate="born_in", value="安定"
    )
    await AssertionRepository(session).update(assertion.id, editorial_status="withdrawn")
    with pytest.raises(ValueError, match="withdrawn"):
        await EventRepository(session).attach_assertion(event_id, assertion.id)


async def test_attach_assertion_idempotent(session: AsyncSession) -> None:
    event_id = await _make_event(session)
    person = await EntityRepository(session).create(entity_type=EntityType.person, name="皇甫谧")
    assertion = await AssertionRepository(session).create(
        subject_entity_id=person.id, predicate="authored", value="针灸甲乙经"
    )
    repo = EventRepository(session)
    await repo.attach_assertion(event_id, assertion.id)
    await repo.attach_assertion(event_id, assertion.id)  # no error, no duplicate
    assert await repo.assertion_ids(event_id) == [assertion.id]


async def test_attach_assertion_missing_targets(session: AsyncSession) -> None:
    event_id = await _make_event(session)
    person = await EntityRepository(session).create(entity_type=EntityType.person, name="皇甫谧")
    assertion = await AssertionRepository(session).create(
        subject_entity_id=person.id, predicate="authored", value="针灸甲乙经"
    )
    with pytest.raises(ValueError, match="event does not exist"):
        await EventRepository(session).attach_assertion(
            "00000000-0000-7000-8000-000000000000", assertion.id
        )
    with pytest.raises(ValueError, match="assertion does not exist"):
        await EventRepository(session).attach_assertion(
            event_id, "00000000-0000-7000-8000-000000000000"
        )


async def test_assertion_subject_can_be_event_entity(session: AsyncSession) -> None:
    """Assertion Contract §1: subject_entity may be an Event (via its Entity id)."""
    entity = await EntityRepository(session).create(entity_type=EntityType.event, name="皇甫谧出生")
    event = await EventRepository(session).create(
        entity_id=entity.id,
        event_type=EventType.birth,
        start_year=215,
        start_precision=EventBoundPrecision.year,
        end_year=215,
        end_precision=EventBoundPrecision.year,
    )
    assertion = await AssertionRepository(session).create(
        subject_entity_id=event.entity_id, predicate="occurred_in", value="安定"
    )
    assert assertion.subject_entity_id == event.entity_id


async def test_person_event_relation(session: AsyncSession) -> None:
    """Person/Event 关系 (ADAPT CA-001): CD-1 identity reused, role typed."""
    event_id = await _make_event(session)
    person = await EntityRepository(session).create(entity_type=EntityType.person, name="皇甫谧")
    repo = EventRelationRepository(session)
    relation = await repo.create(
        entity_id=person.id,
        event_id=event_id,
        relation_role=EventRelationRole.actor,
        description="出生当事人",
    )
    assert relation.entity_id == person.id
    assert relation.event_id == event_id
    assert relation.relation_role == EventRelationRole.actor
    listed = await repo.list_by_event(event_id)
    assert [r.id for r in listed] == [relation.id]
    listed_by_entity = await repo.list_by_entity(person.id)
    assert [r.id for r in listed_by_entity] == [relation.id]


async def test_person_event_relation_duplicate_role_rejected(session: AsyncSession) -> None:
    """UNIQUE(entity_id, event_id, relation_role)."""
    event_id = await _make_event(session)
    person = await EntityRepository(session).create(entity_type=EntityType.person, name="皇甫谧")
    repo = EventRelationRepository(session)
    await repo.create(entity_id=person.id, event_id=event_id, relation_role=EventRelationRole.actor)
    with pytest.raises(IntegrityError):
        await repo.create(
            entity_id=person.id, event_id=event_id, relation_role=EventRelationRole.actor
        )


async def test_person_event_relation_guards(session: AsyncSession) -> None:
    event_id = await _make_event(session)
    person = await EntityRepository(session).create(entity_type=EntityType.person, name="皇甫谧")
    repo = EventRelationRepository(session)
    with pytest.raises(ValueError, match="entity does not exist"):
        await repo.create(
            entity_id="00000000-0000-7000-8000-000000000000",
            event_id=event_id,
            relation_role=EventRelationRole.actor,
        )
    with pytest.raises(ValueError, match="event does not exist"):
        await repo.create(
            entity_id=person.id,
            event_id="00000000-0000-7000-8000-000000000000",
            relation_role=EventRelationRole.actor,
        )
    with pytest.raises(ValueError, match="not equal"):
        await repo.create(
            entity_id=person.id,
            event_id=person.id,
            relation_role=EventRelationRole.actor,
        )
    with pytest.raises(ValueError):
        await repo.create(entity_id=person.id, event_id=event_id, relation_role="supervisor")


async def test_event_relation_binding_immutable(session: AsyncSession) -> None:
    """I4: relation binding (entity/event/role) is immutable once persisted."""
    event_id = await _make_event(session)
    person = await EntityRepository(session).create(entity_type=EntityType.person, name="皇甫谧")
    repo = EventRelationRepository(session)
    relation = await repo.create(
        entity_id=person.id,
        event_id=event_id,
        relation_role=EventRelationRole.actor,
        description="出生当事人",
    )
    updated = await repo.update(relation.id, description="修订note")
    assert updated is not None and updated.description == "修订note"
    with pytest.raises(ValueError, match="immutable"):
        await repo.update(relation.id, relation_role=EventRelationRole.participant)
    with pytest.raises(ValueError, match="immutable"):
        await repo.update(relation.id, event_id="00000000-0000-7000-8000-000000000000")


async def test_event_delete_requires_entity_restrict(session: AsyncSession) -> None:
    """Deleting an Entity that has an Event must fail (FK RESTRICT)."""
    entity = await EntityRepository(session).create(entity_type=EntityType.event, name="皇甫谧出生")
    await EventRepository(session).create(
        entity_id=entity.id,
        event_type=EventType.birth,
        start_year=215,
        start_precision=EventBoundPrecision.year,
        end_year=215,
        end_precision=EventBoundPrecision.year,
    )
    with pytest.raises(IntegrityError):
        await EntityRepository(session).delete(entity.id)
