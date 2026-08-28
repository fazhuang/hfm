"""CD-4 repository behavior + provenance tests (Assertion)."""

from sqlalchemy.ext.asyncio import AsyncSession

from hfm.models.assertion import Assertion
from hfm.models.entity import EntityType
from hfm.repositories.assertion import AssertionRepository
from hfm.repositories.entity import EntityRepository


async def _make_subject(session: AsyncSession) -> str:
    return (await EntityRepository(session).create(entity_type=EntityType.person, name="皇甫谧")).id


async def test_assertion_crud_and_get_by_subject(session: AsyncSession) -> None:
    subject = await _make_subject(session)
    repo = AssertionRepository(session)
    assertion = await repo.create(
        subject_entity_id=subject, predicate="studied_under", value="席坦"
    )
    assert (await repo.get_by_id(assertion.id)) is not None
    assert len(await repo.get_by_subject(subject)) == 1
    # editorial_status is the mutable research field
    updated = await repo.update(assertion.id, editorial_status="withdrawn")
    assert updated is not None
    assert updated.editorial_status == "withdrawn"
    assert updated.value == "席坦"  # content unchanged
    assert await repo.delete(assertion.id) is True
    assert await repo.count() == 0


async def test_assertion_immutable_fields_declared(session: AsyncSession) -> None:
    assert {
        "id",
        "subject_entity_id",
        "predicate",
        "value",
        "object_entity_id",
        "assertion_type",
        "confidence",
        "revision",
        "created_by",
    } <= Assertion.immutable_fields
    assert "editorial_status" not in Assertion.immutable_fields


async def test_assertion_object_entity_relation(session: AsyncSession) -> None:
    """Relational assertion: object_entity_id points to another Entity."""
    person = (
        await EntityRepository(session).create(entity_type=EntityType.person, name="皇甫谧")
    ).id
    place = (await EntityRepository(session).create(entity_type=EntityType.place, name="安定")).id
    repo = AssertionRepository(session)
    assertion = await repo.create(
        subject_entity_id=person, predicate="born_in", object_entity_id=place
    )
    assert assertion.object_entity_id == place
    resolved = await EntityRepository(session).get_by_id(assertion.object_entity_id or "")
    assert resolved is not None
    assert resolved.entity_type == EntityType.place
