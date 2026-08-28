"""Tests for the Citation model (CD-5 — ADAPT, CA-022 + Lineage §2.3)."""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from hfm.models.entity import EntityType
from hfm.repositories.assertion import AssertionRepository
from hfm.repositories.citation import CitationRepository
from hfm.repositories.entity import EntityRepository


async def _make_assertion(session: AsyncSession) -> str:
    entity = await EntityRepository(session).create(entity_type=EntityType.person, name="皇甫谧")
    assertion = await AssertionRepository(session).create(
        subject_entity_id=entity.id, predicate="born_in", value="安定"
    )
    return assertion.id


async def test_citation_construction(session: AsyncSession) -> None:
    target = await _make_assertion(session)
    repo = CitationRepository(session)
    citation = await repo.create(
        target_assertion_id=target,
        quote_text="皇甫谧，安定人",
        note="引《晋书》",
        created_by="actor-ref",
    )
    assert citation.id
    assert citation.target_assertion_id == target
    assert citation.quote_text == "皇甫谧，安定人"
    assert citation.note == "引《晋书》"


async def test_citation_requires_target(session: AsyncSession) -> None:
    repo = CitationRepository(session)
    with pytest.raises(ValueError):
        await repo.create(target_assertion_id=None, quote_text="x")


async def test_citation_target_fk_orphan_rejected(session: AsyncSession) -> None:
    repo = CitationRepository(session)
    with pytest.raises(ValueError):
        await repo.create(target_assertion_id="missing-assertion")


async def test_citation_binding_immutable(session: AsyncSession) -> None:
    """I4: reference-binding fields reject post-create mutation."""
    target = await _make_assertion(session)
    repo = CitationRepository(session)
    citation = await repo.create(target_assertion_id=target, quote_text="原引文")
    with pytest.raises(ValueError):
        await repo.update(citation.id, quote_text="篡改引文")
    with pytest.raises(ValueError):
        citation.quote_text = "直接篡改"
    with pytest.raises(ValueError):
        citation.target_assertion_id = "other"
    # note is mutable metadata
    updated = await repo.update(citation.id, note="补注")
    assert updated is not None
    assert updated.note == "补注"
    assert updated.quote_text == "原引文"  # binding unchanged


async def test_citation_target_restrict_on_delete(session: AsyncSession) -> None:
    """Deleting a cited Assertion fails (RESTRICT — stable reference)."""
    target = await _make_assertion(session)
    repo = CitationRepository(session)
    await repo.create(target_assertion_id=target, quote_text="受保护引用")
    with pytest.raises(IntegrityError):
        await AssertionRepository(session).delete(target)
