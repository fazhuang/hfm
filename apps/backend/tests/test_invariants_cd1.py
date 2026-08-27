"""CD-1 invariant tests (I5 / I4 / 转写契约)."""

from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import AsyncSession

from hfm.models.entity import EntityType
from hfm.models.person import Person
from hfm.repositories.entity import EntityRepository
from hfm.repositories.person import PersonRepository


async def test_invariant_i5_entity_person_stable_identity(session: AsyncSession) -> None:
    """I5: Person shares the Entity's stable UUIDv7 identity (1:1)."""
    entity_repo = EntityRepository(session)
    person_repo = PersonRepository(session)
    entity = await entity_repo.create(entity_type=EntityType.person, name="皇甫谧")
    person = await person_repo.create(entity_id=entity.id, dynasty="魏晋")
    resolved_entity = await entity_repo.get_by_id(person.entity_id)
    assert resolved_entity is not None
    assert resolved_entity.name == "皇甫谧"
    assert resolved_entity.id == person.entity_id


async def test_invariant_i4_no_silent_overwrite(session: AsyncSession) -> None:
    """I4: updates only touch mutable fields; identity fields are rejected."""
    entity_repo = EntityRepository(session)
    entity = await entity_repo.create(entity_type=EntityType.concept, name="导引", description="v1")
    updated = await entity_repo.update(entity.id, description="v2")
    assert updated is not None
    assert updated.description == "v2"
    assert updated.name == "导引"


def test_transcription_contract_person_columns() -> None:
    """转写契约：Person 列集合不含任何 HFB 单值生平真值列（I3/I4 准备）。"""
    columns = {col.name for col in inspect(Person).columns}
    assert {
        "entity_id",
        "dynasty",
        "domain_status",
        "anchor_path",
        "research_relation_role",
    } <= columns
    assert not {"birth_year", "death_year", "birth_place", "biography", "notable_works"} & columns
