"""Evidence chain verification service (P1-02 — Source/Artifact/Version →
Evidence → Citation).

Fail-closed: resolving a chain that contains an orphan or unresolvable
reference raises; the integrity report enumerates orphans across the chain.
No citation is accepted without a valid evidence backing (direct Evidence
edge or the target Assertion's evidence set); no Evidence is valid without
a provenance anchor (SourceRef or in-system Passage). Fail-closed.
"""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from hfm.models.assertion import Assertion, assertion_evidences
from hfm.models.citation import Citation
from hfm.models.evidence import Evidence
from hfm.models.source import Source
from hfm.models.source_ref import SourceRef


@dataclass(frozen=True)
class ChainResolved:
    """A fully resolved Source→SourceRef→Evidence→Citation chain node set."""

    citation_id: str
    assertion_id: str
    evidence_ids: tuple[str, ...]
    source_ref_ids: tuple[str, ...]
    source_ids: tuple[str, ...]
    direct_evidence_id: str | None


class EvidenceChainService:
    """Fail-closed chain resolution and orphan detection (P1-02)."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def resolve_citation(self, citation_id: str) -> ChainResolved:
        """Resolve and verify the full chain for one citation; fail closed."""
        citation = await self.session.get(Citation, citation_id)
        if citation is None:
            raise ValueError("citation does not exist (orphan citation)")
        assertion = await self.session.get(Assertion, citation.target_assertion_id)
        if assertion is None:
            raise ValueError("citation target assertion missing (orphan citation)")
        evidence_ids = list(
            (
                await self.session.execute(
                    select(assertion_evidences.c.evidence_id).where(
                        assertion_evidences.c.assertion_id == assertion.id
                    )
                )
            )
            .scalars()
            .all()
        )
        if citation.evidence_id is not None and citation.evidence_id not in evidence_ids:
            evidence_ids.insert(0, citation.evidence_id)
        if not evidence_ids:
            raise ValueError("citation has no valid evidence backing (orphan citation)")
        source_ref_ids: list[str] = []
        source_ids: list[str] = []
        for ev_id in evidence_ids:
            evidence = await self.session.get(Evidence, ev_id)
            if evidence is None:
                raise ValueError(f"evidence missing: {ev_id} (orphan evidence)")
            if evidence.source_ref_id is not None:
                source_ref_ids.append(evidence.source_ref_id)
                ref = await self.session.get(SourceRef, evidence.source_ref_id)
                if ref is None:
                    raise ValueError(f"source_ref missing: {evidence.source_ref_id}")
                source = await self.session.get(Source, ref.source_id)
                if source is None:
                    raise ValueError(f"source missing: {ref.source_id}")
                source_ids.append(source.id)
            elif evidence.source_passage_id is None:
                raise ValueError(f"evidence has no provenance anchor: {ev_id}")
        return ChainResolved(
            citation_id=citation.id,
            assertion_id=assertion.id,
            evidence_ids=tuple(evidence_ids),
            source_ref_ids=tuple(dict.fromkeys(source_ref_ids)),
            source_ids=tuple(dict.fromkeys(source_ids)),
            direct_evidence_id=citation.evidence_id,
        )

    async def integrity_report(self) -> dict[str, int]:
        """Count orphan links across the chain (E-02: zero orphan links)."""
        orphan_citations = 0
        orphan_evidences = 0
        orphan_refs = 0
        citations = (await self.session.execute(select(Citation))).scalars().all()
        for c in citations:
            try:
                await self.resolve_citation(c.id)
            except ValueError:
                orphan_citations += 1
        evidences = (await self.session.execute(select(Evidence))).scalars().all()
        for ev in evidences:
            if ev.source_ref_id is not None:
                ref = await self.session.get(SourceRef, ev.source_ref_id)
                if ref is None:
                    orphan_refs += 1
                elif await self.session.get(Source, ref.source_id) is None:
                    orphan_refs += 1
            elif ev.source_passage_id is None:
                orphan_evidences += 1  # no provenance anchor (DB CHECK also guards)
        return {
            "orphan_citations": orphan_citations,
            "orphan_evidences": orphan_evidences,
            "orphan_source_refs": orphan_refs,
            "total_citations": len(citations),
            "total_evidences": len(evidences),
        }
