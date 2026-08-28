"""Passage repository (CD-2, locator)."""

from __future__ import annotations

from sqlalchemy import select

from hfm.models.passage import Passage
from hfm.repositories.base import BaseRepository


class PassageRepository(BaseRepository[Passage]):
    """CRUD for Passage (atomic text unit)."""

    model = Passage

    async def get_by_chapter(self, chapter_id: str) -> list[Passage]:
        stmt = select(Passage).where(Passage.chapter_id == chapter_id).order_by(Passage.order)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
