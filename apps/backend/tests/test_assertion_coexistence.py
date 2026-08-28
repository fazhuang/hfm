"""I3 Assertion Coexistence tests (CD-4 — high-risk acceptance item)."""

from sqlalchemy.ext.asyncio import AsyncSession

from hfm.models.assertion import AssertionType, EditorialStatus
from hfm.models.entity import EntityType
from hfm.repositories.assertion import AssertionRepository
from hfm.repositories.entity import EntityRepository


async def _make_person(session: AsyncSession, name: str) -> str:
    return (await EntityRepository(session).create(entity_type=EntityType.person, name=name)).id


async def test_i3_same_subject_same_predicate_multiple_assertions(
    session: AsyncSession,
) -> None:
    """I3: multiple assertions may share subject + predicate."""
    subject = await _make_person(session, "皇甫谧")
    repo = AssertionRepository(session)
    a = await repo.create(subject_entity_id=subject, predicate="born_in", value="公元215年")
    b = await repo.create(subject_entity_id=subject, predicate="born_in", value="公元214年")
    assert a.id != b.id
    assert len(await repo.get_by_subject(subject)) == 2


async def test_i3_conflicting_assertions_coexist(session: AsyncSession) -> None:
    """I3: conflicting assertions coexist; neither deletes the other."""
    subject = await _make_person(session, "皇甫谧")
    repo = AssertionRepository(session)
    await repo.create(
        subject_entity_id=subject,
        predicate="born_in",
        value="公元215年",
        assertion_type=AssertionType.BIOGRAPHICAL,
        editorial_status=EditorialStatus.approved,
    )
    await repo.create(
        subject_entity_id=subject,
        predicate="born_in",
        value="公元214年",
        assertion_type=AssertionType.BIOGRAPHICAL,
        editorial_status=EditorialStatus.reviewed,
    )
    all_assertions = await repo.get_by_subject(subject)
    assert len(all_assertions) == 2
    assert {a.value for a in all_assertions} == {"公元215年", "公元214年"}


async def test_i4_new_assertion_does_not_overwrite(session: AsyncSession) -> None:
    """I4: creating a new assertion never overwrites prior ones."""
    subject = await _make_person(session, "皇甫谧")
    repo = AssertionRepository(session)
    first = await repo.create(subject_entity_id=subject, predicate="born_in", value="旧说")
    second = await repo.create(subject_entity_id=subject, predicate="born_in", value="新说")
    # both remain; the "preferred" status does not delete the alternative
    remaining = await repo.get_by_subject(subject)
    assert len(remaining) == 2
    assert first.id in {a.id for a in remaining}
    assert second.id in {a.id for a in remaining}


async def test_i4_no_unique_subject_predicate_constraint(session: AsyncSession) -> None:
    """There is no UNIQUE(subject,predicate) — coexistence is structural."""
    from typing import cast

    from sqlalchemy import Table, UniqueConstraint

    from hfm.models.assertion import Assertion

    constraints = cast(Table, Assertion.__table__).constraints
    unique_constraints = {
        tuple(uc.columns.keys()) for uc in constraints if isinstance(uc, UniqueConstraint)
    }
    assert ("subject_entity_id", "predicate") not in unique_constraints
