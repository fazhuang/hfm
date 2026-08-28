"""Evidence repository (CD-3, I1 provenance + integrity + taint)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select

from hfm.core.hashing import calculate_canonical_metadata_sha256
from hfm.models.evidence import Evidence
from hfm.repositories.base import BaseRepository

_TAINT_STATUSES = {"clean", "source_withdrawn", "quarantined"}


class EvidenceRepository(BaseRepository[Evidence]):
    """CRUD for Evidence with provenance, integrity and taint lifecycle."""

    model = Evidence

    @staticmethod
    def _compute_content_hash(
        description: str,
        evidence_level: str,
        source_ref_id: str | None,
        source_passage_id: str | None,
    ) -> str:
        payload = {
            "description": description,
            "evidence_level": evidence_level,
            "source_ref_id": source_ref_id,
            "source_passage_id": source_passage_id,
        }
        return calculate_canonical_metadata_sha256(
            {k: v for k, v in payload.items() if v is not None}
        )

    async def create(self, **kwargs: Any) -> Evidence:
        source_ref_id = kwargs.get("source_ref_id")
        source_passage_id = kwargs.get("source_passage_id")
        if source_ref_id is None and source_passage_id is None:
            raise ValueError("evidence must anchor to a source_ref or a passage (I1)")
        description = str(kwargs.get("description") or "")
        if not description:
            raise ValueError("evidence description is required")
        level = kwargs.get("evidence_level")
        level_value = getattr(level, "value", level) if level is not None else "LEVEL_3"
        kwargs["content_hash"] = self._compute_content_hash(
            description,
            str(level_value),
            str(source_ref_id) if source_ref_id else None,
            str(source_passage_id) if source_passage_id else None,
        )
        return await super().create(**kwargs)

    async def update(self, id: str, **kwargs: Any) -> Evidence | None:
        instance = await self.get_by_id(id)
        if instance is None:
            return None
        if "taint_status" in kwargs:
            self._validate_taint_status(str(kwargs["taint_status"]))
        # provenance anchors / content_hash are immutable — base guard rejects them
        return await super().update(id, **kwargs)

    async def mark_tainted(
        self, id: str, status: str, reason: str | None = None
    ) -> Evidence | None:
        """Set the taint lifecycle state (CA-024 REUSE)."""
        self._validate_taint_status(status)
        return await self.update(
            id,
            taint_status=status,
            tainted_at=datetime.now(UTC),
            taint_reason=reason,
        )

    async def get_by_source_ref(self, source_ref_id: str) -> list[Evidence]:
        stmt = select(Evidence).where(Evidence.source_ref_id == source_ref_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    def _validate_taint_status(status: str) -> None:
        if status not in _TAINT_STATUSES:
            raise ValueError(f"invalid taint status: {status}")
