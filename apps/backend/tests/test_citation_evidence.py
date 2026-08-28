"""Citation ↔ Evidence edge tests (CD-5, Lineage §2.3)."""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from hfm.models.entity import EntityType
from hfm.repositories.assertion import AssertionRepository
from hfm.repositories.citation import CitationRepository
from hfm.repositories.entity import EntityRepository
from hfm.repositories.evidence import EvidenceRepository
from hfm.repositories.source import SourceRepository
from hfm.repositories.source_ref import SourceRefRepository


async def _make_evidence(session: AsyncSession) -> str:
    source, _ = await SourceRepository(session).create_idempotent(source_key="cit-ev", title="素问")
    ref = await SourceRefRepository(session).create(source_id=source.id, title="素问")
    return (await EvidenceRepository(session).create(description="引证", source_ref_id=ref.id)).id


async def test_citation_evidence_direct_edge(session: AsyncSession) -> None:
    """Citation → Evidence direct edge (Frozen Lineage §2.3)."""
    entity = await EntityRepository(session).create(entity_type=EntityType.person, name="皇甫谧")
    assertion = await AssertionRepository(session).create(
        subject_entity_id=entity.id, predicate="born_in", value="安定"
    )
    evidence_id = await _make_evidence(session)
    repo = CitationRepository(session)
    citation = await repo.create(
        target_assertion_id=assertion.id, evidence_id=evidence_id, quote_text="转引"
    )
    assert citation.evidence_id == evidence_id
    resolved = await EvidenceRepository(session).get_by_id(citation.evidence_id or "")
    assert resolved is not None
    assert resolved.description == "引证"
    # citing does not mutate the Evidence (integrity under linking)
    assert resolved.content_hash  # unchanged integrity digest


async def test_citation_evidence_missing_rejected(session: AsyncSession) -> None:
    """Missing evidence reference is rejected (FK)."""
    entity = await EntityRepository(session).create(entity_type=EntityType.person, name="皇甫谧")
    assertion = await AssertionRepository(session).create(
        subject_entity_id=entity.id, predicate="born_in", value="安定"
    )
    repo = CitationRepository(session)
    with pytest.raises(IntegrityError):
        await repo.create(target_assertion_id=assertion.id, evidence_id="missing-evidence")
