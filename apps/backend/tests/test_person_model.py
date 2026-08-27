"""Tests for the Person model (CD-1 — ADAPT, I5/I4 转写契约)."""

import pytest
from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from hfm.models.entity import Entity, EntityType
from hfm.models.person import Person, PersonDomainStatus
from hfm.repositories.entity import EntityRepository
from hfm.repositories.person import PersonRepository


async def _make_person(session: AsyncSession) -> tuple[Entity, Person]:
    entity_repo = EntityRepository(session)
    person_repo = PersonRepository(session)
    entity = await entity_repo.create(entity_type=EntityType.person, name="皇甫谧")
    person = await person_repo.create(
        entity_id=entity.id,
        name_zh="皇甫謐",
        courtesy_name="士安",
        dynasty="魏晋",
        domain_status=PersonDomainStatus.verified,
    )
    return entity, person


async def test_person_construction_and_entity_link(session: AsyncSession) -> None:
    entity, person = await _make_person(session)
    assert person.entity_id == entity.id  # shared stable identity (I5)
    assert person.domain_status == PersonDomainStatus.verified


async def test_person_requires_entity(session: AsyncSession) -> None:
    """A Person cannot exist without its Entity (1:1 FK, I5)."""
    person_repo = PersonRepository(session)
    with pytest.raises(IntegrityError):
        await person_repo.create(entity_id="missing-entity", name_zh="孤儿")


async def test_person_default_domain_status(session: AsyncSession) -> None:
    entity_repo = EntityRepository(session)
    person_repo = PersonRepository(session)
    entity = await entity_repo.create(entity_type=EntityType.person, name="张仲景")
    person = await person_repo.create(entity_id=entity.id)
    assert person.domain_status == PersonDomainStatus.pending


def test_single_value_field_transcription_guard() -> None:
    """I3/I4 转写契约：Person 不得携带 HFB 单值生平真值列（birth_year 等）。

    这些值在 CD-4 转写为带证据溯源的 Assertion（HFM-MIGRATION-STRATEGY §7），
    复制为真值列将违反 Frozen Assertion Contract（I3 冲突并存 / I4 无静默覆盖）。
    """
    columns = {col.name for col in inspect(Person).columns}
    forbidden = {
        "birth_year",
        "death_year",
        "birth_place",
        "biography",
        "notable_works",
        "expertise",
    }
    assert forbidden.isdisjoint(columns), (
        f"forbidden single-truth columns present: {forbidden & columns}"
    )
