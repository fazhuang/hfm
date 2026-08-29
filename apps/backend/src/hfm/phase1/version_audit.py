"""Version / audit / reconciliation services (P1-13 — E-13).

Implements the frozen P1-13 acceptance criterion: immutable lineage, batch
metrics, and reconciliation PASS are recorded; fail-closed inconsistency
handling; append-only audit journal; preservation of provenance/history.

  - AuditService: append-only journal for governed state changes
    (admission decisions, publication transitions, domain record creation);
  - VersionLineageService: deterministic lineage chains over
    versions.parent_version_id (I2), fail-closed on broken/cyclic chains,
    deterministic lineage digest;
  - ReconciliationService: computes count + canonical digest for a governed
    scope, compares against the recorded expectation, persists an immutable
    PASS/FAIL run, and raises (fail-closed) on mismatch.

No unrestricted event-sourcing framework is introduced — this is the
smallest implementation satisfying the frozen acceptance criteria.
"""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from hfm.core.hashing import calculate_canonical_metadata_sha256
from hfm.db.base import BaseModel
from hfm.models.assertion import Assertion
from hfm.models.audit import AuditLog
from hfm.models.chapter import Chapter
from hfm.models.citation import Citation
from hfm.models.content_artifact import ContentArtifact
from hfm.models.edition import Edition
from hfm.models.entity import Entity
from hfm.models.event import Event
from hfm.models.evidence import Evidence
from hfm.models.passage import Passage
from hfm.models.person import Person
from hfm.models.publication import PublicationRecord
from hfm.models.reconciliation import ReconciliationRun, ReconciliationStatus
from hfm.models.source import Source
from hfm.models.source_ref import SourceRef
from hfm.models.version import Version
from hfm.models.work import Work
from hfm.repositories.audit import AuditLogRepository
from hfm.repositories.reconciliation import ReconciliationRunRepository


class ReconciliationMismatchError(ValueError):
    """Fail-closed: actual metrics differ from the recorded expectation."""


class AuditService:
    """Append-only governed-state-change journal (P1-13)."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def record(
        self,
        *,
        actor_id: str | None,
        action: str,
        target_type: str,
        target_id: str,
        detail: str | None = None,
    ) -> AuditLog:
        """Record one immutable audit entry (no update/delete path)."""
        if not action or not target_type or not target_id:
            raise ValueError("audit action/target_type/target_id are required")
        entry = AuditLog(
            actor_id=actor_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            detail=detail,
        )
        self.session.add(entry)
        await self.session.flush()
        return entry

    async def list_recent(self, limit: int = 50) -> list[AuditLog]:
        return await AuditLogRepository(self.session).list_recent(limit=limit)

    async def for_target(self, target_type: str, target_id: str) -> list[AuditLog]:
        return await AuditLogRepository(self.session).list_by_target(target_type, target_id)


@dataclass(frozen=True)
class LineageNode:
    """One deterministic version-lineage node (leaf → root walk)."""

    version_id: str
    version_name: str
    edition_id: str
    parent_version_id: str | None


class VersionLineageService:
    """Deterministic lineage verification over versions.parent_version_id."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def lineage(self, version_id: str) -> list[LineageNode]:
        """Walk the parent chain deterministically (leaf → root).

        Fail-closed: a missing version, a broken (orphan) parent link, or a
        cycle raises ValueError — lineage must never silently degrade.
        """
        chain: list[LineageNode] = []
        seen: set[str] = set()
        current_id: str | None = version_id
        while current_id is not None:
            if current_id in seen:
                raise ValueError(f"version lineage cycle detected at {current_id}")
            seen.add(current_id)
            version = await self.session.get(Version, current_id)
            if version is None:
                raise ValueError(f"version lineage broken: missing version {current_id}")
            chain.append(
                LineageNode(
                    version_id=version.id,
                    version_name=version.version_name,
                    edition_id=version.edition_id,
                    parent_version_id=version.parent_version_id,
                )
            )
            current_id = version.parent_version_id
        return chain

    async def lineage_hash(self, version_id: str) -> str:
        """Deterministic digest of the lineage chain (E-04/E-13)."""
        chain = await self.lineage(version_id)
        payload = [
            {
                "version_id": node.version_id,
                "edition_id": node.edition_id,
                "version_name": node.version_name,
            }
            for node in chain
        ]
        return calculate_canonical_metadata_sha256(payload)

    async def integrity_report(self) -> dict[str, int]:
        """Count broken/cyclic lineage links across all versions (E-13)."""
        versions = (await self.session.execute(select(Version))).scalars().all()
        orphan_parents = 0
        cycles = 0
        for version in versions:
            try:
                await self.lineage(version.id)
            except ValueError as exc:
                if "cycle" in str(exc):
                    cycles += 1
                else:
                    orphan_parents += 1
        return {
            "versions": len(versions),
            "orphan_parents": orphan_parents,
            "cycles": cycles,
            "ok": orphan_parents == 0 and cycles == 0,
        }


#: Governed canonical scopes for reconciliation (count + canonical digest).
_SCOPE_MODELS: dict[str, type[BaseModel]] = {
    "table:sources": Source,
    "table:source_refs": SourceRef,
    "table:evidences": Evidence,
    "table:assertions": Assertion,
    "table:citations": Citation,
    "table:works": Work,
    "table:editions": Edition,
    "table:versions": Version,
    "table:chapters": Chapter,
    "table:passages": Passage,
    "table:entities": Entity,
    "table:persons": Person,
    "table:events": Event,
    "table:content_artifacts": ContentArtifact,
    "table:publication_records": PublicationRecord,
}


class ReconciliationService:
    """Recorded batch metrics + fail-closed reconciliation (P1-13)."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def reconcile(
        self,
        *,
        scope: str,
        expected_count: int,
        expected_hash: str,
        created_by: str | None = None,
    ) -> ReconciliationRun:
        """Recompute the scope's metrics, compare, record, and fail closed.

        On mismatch the immutable FAIL run is still recorded (E-13 evidence)
        and ReconciliationMismatchError is raised — a WARN-only completion is
        never accepted.
        """
        model = self._model_for_scope(scope)
        actual_count, actual_hash = await self._compute(model)
        status = (
            ReconciliationStatus.PASS
            if (actual_count == expected_count and actual_hash == expected_hash)
            else ReconciliationStatus.FAIL
        )
        run = ReconciliationRun(
            scope=scope,
            expected_count=expected_count,
            expected_hash=expected_hash,
            actual_count=actual_count,
            actual_hash=actual_hash,
            status=status.value,
            created_by=created_by,
        )
        self.session.add(run)
        await self.session.flush()
        await AuditService(self.session).record(
            actor_id=created_by,
            action=f"reconciliation.{status.value.lower()}",
            target_type="reconciliation_run",
            target_id=run.id,
            detail=(
                f"scope={scope} expected=({expected_count},{expected_hash}) "
                f"actual=({actual_count},{actual_hash})"
            ),
        )
        if status == ReconciliationStatus.FAIL:
            raise ReconciliationMismatchError(
                f"reconciliation {scope} FAIL: expected ({expected_count}, {expected_hash}) "
                f"actual ({actual_count}, {actual_hash})"
            )
        return run

    async def latest_for_scope(self, scope: str) -> ReconciliationRun | None:
        return await ReconciliationRunRepository(self.session).latest_for_scope(scope)

    async def _compute(self, model: type[BaseModel]) -> tuple[int, str]:
        """Deterministic count + canonical digest over a model's rows (sorted ids)."""
        stmt = select(model.id)
        ids = [str(v) for v in (await self.session.execute(stmt)).scalars().all()]
        count = len(ids)
        digest = calculate_canonical_metadata_sha256(sorted(ids))
        return count, digest

    def _model_for_scope(self, scope: str) -> type[BaseModel]:
        if scope in _SCOPE_MODELS:
            return _SCOPE_MODELS[scope]
        if scope.startswith("batch:"):
            # content-batch scope: the canonical batch table is
            # content_artifacts (admitted/rejected records)
            return ContentArtifact
        raise ValueError(f"unknown reconciliation scope: {scope}")


async def governed_table_counts(session: AsyncSession) -> dict[str, int]:
    """Row counts across governed canonical tables (batch metrics snapshot)."""
    counts: dict[str, int] = {}
    for scope, model in sorted(_SCOPE_MODELS.items()):
        value = (await session.execute(select(func.count()).select_from(model))).scalar_one()
        counts[scope] = value
    return counts
