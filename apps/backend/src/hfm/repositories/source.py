"""Source repository (CD-0 + Lineage §2.5 withdrawal cascade)."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select

from hfm.models.evidence import Evidence
from hfm.models.source import Source
from hfm.models.source_ref import SourceRef
from hfm.repositories.base import BaseRepository


class SourceRepository(BaseRepository[Source]):
    """CRUD for the immutable Source identity."""

    model = Source

    async def get_by_key(self, source_key: str) -> Source | None:
        stmt = select(Source).where(Source.source_key == source_key)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_idempotent(self, **kwargs: object) -> tuple[Source, bool]:
        """Create a source unless ``source_key`` already exists (I5/I4).

        Returns (source, created) where created=False means an existing
        source with the same key was returned unchanged (no silent overwrite).
        """
        key = kwargs.get("source_key")
        if key is None:
            raise ValueError("source_key is required for idempotent create")
        existing = await self.get_by_key(str(key))
        if existing is not None:
            return existing, False
        instance = await self.create(**kwargs)
        return instance, True

    async def mark_withdrawn(self, source_id: str, reason: str | None = None) -> Source | None:
        """Withdraw a Source and cascade-taint its anchored Evidences (Lineage §2.5).

        Cascade: Source withdrawn → related SourceRefs → anchored Evidences
        marked taint=source_withdrawn → Citations to them are rejected.
        """
        source = await self.get_by_id(source_id)
        if source is None:
            return None
        source.withdrawn_at = datetime.now(UTC)
        await self.session.flush()

        ref_stmt = select(SourceRef.id).where(SourceRef.source_id == source_id)
        ref_ids = list((await self.session.execute(ref_stmt)).scalars().all())
        if ref_ids:
            ev_stmt = select(Evidence).where(Evidence.source_ref_id.in_(ref_ids))
            evidences = list((await self.session.execute(ev_stmt)).scalars().all())
            for evidence in evidences:
                evidence.taint_status = "source_withdrawn"
                evidence.tainted_at = datetime.now(UTC)
                evidence.taint_reason = reason or "source withdrawn"
            await self.session.flush()
        return source
