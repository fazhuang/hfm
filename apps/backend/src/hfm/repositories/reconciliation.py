"""Reconciliation run repository (P1-13 — append-only PASS/FAIL evidence)."""

from __future__ import annotations

from sqlalchemy import select

from hfm.models.reconciliation import ReconciliationRun
from hfm.repositories.base import BaseRepository


class ReconciliationRunRepository(BaseRepository[ReconciliationRun]):
    """CRUD for recorded reconciliation runs (P1-13).

    BaseRepository.update/delete guard ``immutable_fields`` — recorded batch
    metrics cannot be amended or removed (E-13 evidence preservation).
    """

    model = ReconciliationRun

    async def latest_for_scope(self, scope: str) -> ReconciliationRun | None:
        stmt = (
            select(ReconciliationRun)
            .where(ReconciliationRun.scope == scope)
            .order_by(ReconciliationRun.created_at.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
