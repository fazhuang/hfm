"""Phase 1 P1-02 — evidence chain tests (Source→SourceRef→Evidence→Citation).

Fail-closed: orphan citation/evidence/source rejected; no citation without
valid evidence backing; no evidence without provenance anchor.
"""

from __future__ import annotations

from typing import Any

import pytest
import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession

from hfm.models.entity import EntityType
from hfm.models.evidence import Evidence
from hfm.phase1.evidence_chain import EvidenceChainService
from hfm.repositories.assertion import AssertionRepository
from hfm.repositories.citation import CitationRepository
from hfm.repositories.entity import EntityRepository
from hfm.repositories.evidence import EvidenceRepository
from hfm.repositories.source import SourceRepository
from hfm.repositories.source_ref import SourceRefRepository


async def _source_ref(session: AsyncSession) -> tuple[Any, Any]:
    source, _ = await SourceRepository(session).create_idempotent(
        source_key="chain-src", title="史料"
    )
    ref = await SourceRefRepository(session).create(source_id=source.id, title="史料引")
    return source, ref


async def _evidence(session: AsyncSession, ref: Any) -> Evidence:
    return await EvidenceRepository(session).create(description="链上证据", source_ref_id=ref.id)


async def _assertion(session: AsyncSession) -> Any:
    entity = await EntityRepository(session).create(entity_type=EntityType.person, name="皇甫谧")
    return await AssertionRepository(session).create(
        subject_entity_id=entity.id, predicate="authored", value="针灸甲乙经"
    )


async def test_valid_chain_resolves(session: AsyncSession) -> None:
    source, ref = await _source_ref(session)
    evidence = await _evidence(session, ref)
    assertion = await _assertion(session)
    await AssertionRepository(session).attach_evidence(assertion.id, evidence.id)
    citation = await CitationRepository(session).create(
        target_assertion_id=assertion.id, quote_text="引文"
    )
    chain = await EvidenceChainService(session).resolve_citation(citation.id)
    assert chain.source_ids == (source.id,)
    assert chain.source_ref_ids == (ref.id,)
    assert chain.evidence_ids == (evidence.id,)
    assert chain.assertion_id == assertion.id


async def test_orphan_citation_rejected(session: AsyncSession) -> None:
    with pytest.raises(ValueError, match="citation does not exist"):
        await EvidenceChainService(session).resolve_citation("00000000-0000-7000-8000-000000000000")


async def test_citation_without_evidence_rejected(session: AsyncSession) -> None:
    """No Citation without valid Evidence backing (E-02)."""
    assertion = await _assertion(session)
    citation = await CitationRepository(session).create(
        target_assertion_id=assertion.id, quote_text="无证据引文"
    )
    with pytest.raises(ValueError, match="no valid evidence backing"):
        await EvidenceChainService(session).resolve_citation(citation.id)


async def test_orphan_evidence_rejected(session: AsyncSession) -> None:
    """A citation whose assertion loses its evidence backing is fail-closed."""
    source, ref = await _source_ref(session)
    evidence = await _evidence(session, ref)
    assertion = await _assertion(session)
    await AssertionRepository(session).attach_evidence(assertion.id, evidence.id)
    citation = await CitationRepository(session).create(target_assertion_id=assertion.id)
    # detach the only evidence → the citation has no evidence backing (orphan)
    await session.execute(
        sqlalchemy.text(
            "DELETE FROM assertion_evidences WHERE assertion_id = :aid AND evidence_id = :eid"
        ),
        {"aid": assertion.id, "eid": evidence.id},
    )
    await session.flush()
    with pytest.raises(ValueError, match="no valid evidence backing"):
        await EvidenceChainService(session).resolve_citation(citation.id)


async def test_integrity_report_zero_orphans(session: AsyncSession) -> None:
    source, ref = await _source_ref(session)
    evidence = await _evidence(session, ref)
    assertion = await _assertion(session)
    await AssertionRepository(session).attach_evidence(assertion.id, evidence.id)
    await CitationRepository(session).create(target_assertion_id=assertion.id)
    report = await EvidenceChainService(session).integrity_report()
    assert report["orphan_citations"] == 0
    assert report["orphan_evidences"] == 0
    assert report["orphan_source_refs"] == 0
