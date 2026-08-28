"""Chapter repository (CD-2, hierarchy same-Work enforcement)."""

from __future__ import annotations

from typing import Any

from hfm.models.chapter import Chapter
from hfm.repositories.base import BaseRepository


class ChapterRepository(BaseRepository[Chapter]):
    """CRUD for Chapter with hierarchy enforcement.

    parent_id is protected (immutable after creation); create-time checks
    enforce same-Work parent and parent existence.
    """

    model = Chapter

    async def _validate_parent(self, work_id: str, parent_id: str | None) -> None:
        if parent_id is None:
            return
        parent = await self.session.get(Chapter, parent_id)
        if parent is None:
            raise ValueError("parent chapter does not exist")
        if parent.work_id != work_id:
            raise ValueError("parent chapter must belong to the same Work")

    async def create(self, **kwargs: Any) -> Chapter:
        work_id = str(kwargs.get("work_id") or "")
        parent_id = kwargs.get("parent_id")
        await self._validate_parent(work_id, str(parent_id) if parent_id else None)
        return await super().create(**kwargs)
