"""Audit log repository (P1-13 — append-only governed-state journal)."""

from __future__ import annotations

from sqlalchemy import select

from hfm.models.audit import AuditLog
from hfm.repositories.base import BaseRepository


class AuditLogRepository(BaseRepository[AuditLog]):
    """CRUD for the append-only audit journal (P1-13).

    BaseRepository.update/delete guard ``immutable_fields`` — audit entries
    cannot be amended or removed (I4, provenance/history preservation).
    """

    model = AuditLog

    async def list_recent(self, limit: int = 50) -> list[AuditLog]:
        stmt = select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_by_target(self, target_type: str, target_id: str) -> list[AuditLog]:
        stmt = (
            select(AuditLog)
            .where(AuditLog.target_type == target_type, AuditLog.target_id == target_id)
            .order_by(AuditLog.created_at)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
