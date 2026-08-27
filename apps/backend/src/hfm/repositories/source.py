"""Source repository (CD-0)."""

from __future__ import annotations

from sqlalchemy import select

from hfm.models.source import Source
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
