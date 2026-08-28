"""CD-5 repository behavior tests (Citation)."""

from sqlalchemy.ext.asyncio import AsyncSession

from hfm.models.citation import Citation
from hfm.models.entity import EntityType
from hfm.repositories.assertion import AssertionRepository
from hfm.repositories.citation import CitationRepository
from hfm.repositories.entity import EntityRepository


async def _make_assertion(session: AsyncSession) -> str:
    entity = await EntityRepository(session).create(entity_type=EntityType.person, name="皇甫谧")
    return (
        await AssertionRepository(session).create(
            subject_entity_id=entity.id, predicate="born_in", value="安定"
        )
    ).id


async def test_citation_crud_and_get_by_target(session: AsyncSession) -> None:
    target = await _make_assertion(session)
    repo = CitationRepository(session)
    citation = await repo.create(target_assertion_id=target, quote_text="引文一")
    assert (await repo.get_by_id(citation.id)) is not None
    assert len(await repo.get_by_target_assertion(target)) == 1
    assert await repo.delete(citation.id) is True
    assert await repo.count() == 0


async def test_citation_immutable_fields_declared(session: AsyncSession) -> None:
    assert {
        "id",
        "target_assertion_id",
        "evidence_id",
        "version_id",
        "passage_id",
        "quote_text",
        "created_by",
    } <= Citation.immutable_fields
    assert "note" not in Citation.immutable_fields  # note is mutable metadata
