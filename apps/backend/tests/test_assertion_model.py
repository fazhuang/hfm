"""Tests for the Assertion model (CD-4 — NEW, Assertion Contract)."""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from hfm.models.assertion import AssertionType, Confidence, EditorialStatus
from hfm.models.entity import EntityType
from hfm.repositories.assertion import AssertionRepository
from hfm.repositories.entity import EntityRepository


async def _make_person_entity(session: AsyncSession, name: str = "皇甫谧") -> str:
    entity = await EntityRepository(session).create(entity_type=EntityType.person, name=name)
    return entity.id


async def test_assertion_construction(session: AsyncSession) -> None:
    subject = await _make_person_entity(session)
    repo = AssertionRepository(session)
    assertion = await repo.create(
        subject_entity_id=subject,
        predicate="born_in",
        value="安定",
        assertion_type=AssertionType.BIOGRAPHICAL,
        confidence=Confidence.high,
        editorial_status=EditorialStatus.draft,
        created_by="actor-ref",
    )
    assert assertion.id  # stable identity (I5)
    assert assertion.subject_entity_id == subject
    assert assertion.predicate == "born_in"
    assert assertion.value == "安定"
    assert assertion.revision == 1


async def test_assertion_requires_subject(session: AsyncSession) -> None:
    repo = AssertionRepository(session)
    with pytest.raises(ValueError):
        await repo.create(predicate="born_in", value="安定")


async def test_assertion_requires_value_or_object(session: AsyncSession) -> None:
    subject = await _make_person_entity(session)
    repo = AssertionRepository(session)
    with pytest.raises(ValueError):
        await repo.create(subject_entity_id=subject, predicate="born_in")


async def test_assertion_subject_fk_orphan_rejected(session: AsyncSession) -> None:
    """Subject referential integrity (I5): missing Entity rejected at DB level."""
    repo = AssertionRepository(session)
    with pytest.raises(IntegrityError):
        await repo.create(subject_entity_id="missing-entity", predicate="x", value="y")


async def test_assertion_content_immutable(session: AsyncSession) -> None:
    """I4: content fields reject post-create mutation (repository + model)."""
    subject = await _make_person_entity(session)
    repo = AssertionRepository(session)
    assertion = await repo.create(subject_entity_id=subject, predicate="born_in", value="安定")
    with pytest.raises(ValueError):
        await repo.update(assertion.id, predicate="died_in")
    with pytest.raises(ValueError):
        await repo.update(assertion.id, value="篡改")
    with pytest.raises(ValueError):
        assertion.predicate = "died_in"
    with pytest.raises(ValueError):
        assertion.subject_entity_id = "other"


async def test_assertion_editorial_status_transition(session: AsyncSession) -> None:
    """editorial_status is the mutable research state (not publication)."""
    subject = await _make_person_entity(session)
    repo = AssertionRepository(session)
    assertion = await repo.create(
        subject_entity_id=subject, predicate="authored", value="针灸甲乙经"
    )
    updated = await repo.update(assertion.id, editorial_status=EditorialStatus.approved)
    assert updated is not None
    assert updated.editorial_status == EditorialStatus.approved
    assert updated.value == "针灸甲乙经"  # content unchanged


def test_assertion_enums() -> None:
    assert {e.value for e in AssertionType} == {
        "biographical",
        "textual",
        "relational",
        "historical",
        "general",
    }
    assert {e.value for e in EditorialStatus} == {"draft", "reviewed", "approved", "withdrawn"}
    assert {e.value for e in Confidence} == {"low", "medium", "high"}
