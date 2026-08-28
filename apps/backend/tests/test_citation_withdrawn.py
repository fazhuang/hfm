"""Withdrawn-reference gate tests (CD-5, DAG gate: 撤回引用)."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from hfm.models.assertion import EditorialStatus
from hfm.models.entity import EntityType
from hfm.repositories.assertion import AssertionRepository
from hfm.repositories.citation import CitationRepository
from hfm.repositories.entity import EntityRepository


async def _make_withdrawn_assertion(session: AsyncSession) -> str:
    entity = await EntityRepository(session).create(entity_type=EntityType.person, name="皇甫谧")
    repo = AssertionRepository(session)
    assertion = await repo.create(subject_entity_id=entity.id, predicate="born_in", value="旧说")
    await repo.update(assertion.id, editorial_status=EditorialStatus.withdrawn)
    return assertion.id


async def test_citation_withdrawn_assertion_rejected(session: AsyncSession) -> None:
    """A new citation cannot target a withdrawn assertion (撤回引用 gate)."""
    withdrawn_id = await _make_withdrawn_assertion(session)
    repo = CitationRepository(session)
    with pytest.raises(ValueError):
        await repo.create(target_assertion_id=withdrawn_id, quote_text="撤回后引用")


async def test_citation_active_assertion_allowed(session: AsyncSession) -> None:
    """Active assertions remain citable."""
    entity = await EntityRepository(session).create(entity_type=EntityType.person, name="张仲景")
    assertion = await AssertionRepository(session).create(
        subject_entity_id=entity.id, predicate="authored", value="伤寒杂病论"
    )
    repo = CitationRepository(session)
    citation = await repo.create(target_assertion_id=assertion.id, quote_text="伤寒论序")
    assert citation.target_assertion_id == assertion.id
