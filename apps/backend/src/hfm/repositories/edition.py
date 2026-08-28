"""Edition repository (CD-2, lineage same-Work enforcement)."""

from __future__ import annotations

from typing import Any

from hfm.models.edition import Edition
from hfm.repositories.base import BaseRepository


class EditionRepository(BaseRepository[Edition]):
    """CRUD for Edition with lineage enforcement.

    lineage_parent_edition_id is protected (immutable after creation);
    create-time checks enforce same-Work lineage and parent existence.
    """

    model = Edition

    async def _validate_lineage(self, work_id: str, parent_edition_id: str | None) -> None:
        if parent_edition_id is None:
            return
        parent = await self.session.get(Edition, parent_edition_id)
        if parent is None:
            raise ValueError("parent edition does not exist")
        if parent.work_id != work_id:
            raise ValueError("parent edition must belong to the same Work")

    async def create(self, **kwargs: Any) -> Edition:
        work_id = str(kwargs.get("work_id") or "")
        parent_edition_id = kwargs.get("lineage_parent_edition_id")
        await self._validate_lineage(work_id, str(parent_edition_id) if parent_edition_id else None)
        return await super().create(**kwargs)
