"""Passage repository (CD-2, locator + cross-Work consistency)."""

from __future__ import annotations

from typing import Any

from sqlalchemy import select

from hfm.models.chapter import Chapter
from hfm.models.edition import Edition
from hfm.models.passage import Passage
from hfm.models.version import Version
from hfm.repositories.base import BaseRepository


class PassageRepository(BaseRepository[Passage]):
    """CRUD for Passage with cross-Work version/chapter consistency (P0)."""

    model = Passage

    async def _validate_cross_work(self, chapter_id: str, version_id: str | None) -> None:
        """A passage's version must belong to the same Work as its chapter."""
        chapter = await self.session.get(Chapter, chapter_id)
        if chapter is None:
            raise ValueError("chapter does not exist")
        if version_id is None:
            return
        version = await self.session.get(Version, version_id)
        if version is None:
            raise ValueError("version does not exist")
        edition = await self.session.get(Edition, version.edition_id)
        version_work_id = edition.work_id if edition is not None else None
        if version_work_id != chapter.work_id:
            raise ValueError("passage version must belong to the same Work as its chapter")

    async def create(self, **kwargs: Any) -> Passage:
        chapter_id = str(kwargs.get("chapter_id") or "")
        version_id = kwargs.get("version_id")
        await self._validate_cross_work(chapter_id, str(version_id) if version_id else None)
        return await super().create(**kwargs)

    async def update(self, id: str, **kwargs: Any) -> Passage | None:
        instance = await self.get_by_id(id)
        if instance is None:
            return None
        new_chapter_id = str(kwargs.get("chapter_id", instance.chapter_id) or "")
        new_version_id = kwargs.get("version_id", instance.version_id)
        await self._validate_cross_work(
            new_chapter_id, str(new_version_id) if new_version_id else None
        )
        return await super().update(id, **kwargs)

    async def get_by_chapter(self, chapter_id: str) -> list[Passage]:
        stmt = select(Passage).where(Passage.chapter_id == chapter_id).order_by(Passage.order)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
