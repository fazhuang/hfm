"""Citation repository (CD-5, withdrawn gate + immutable binding)."""

from __future__ import annotations

from typing import Any

from sqlalchemy import select

from hfm.models.assertion import EditorialStatus
from hfm.models.citation import Citation
from hfm.repositories.base import BaseRepository


class CitationRepository(BaseRepository[Citation]):
    """CRUD for Citation with withdrawn-reference gate and pinned binding."""

    model = Citation

    async def create(self, **kwargs: Any) -> Citation:
        target_assertion_id = kwargs.get("target_assertion_id")
        if target_assertion_id is None:
            raise ValueError("citation target_assertion_id is required")
        # resolve target assertion — withdrawn assertions cannot be newly cited
        from hfm.models.assertion import Assertion

        assertion = await self.session.get(Assertion, str(target_assertion_id))
        if assertion is None:
            raise ValueError("target assertion does not exist")
        if assertion.editorial_status == EditorialStatus.withdrawn:
            raise ValueError("cannot cite a withdrawn assertion (withdrawn-reference gate)")
        # FK existence for optional pins is enforced by the database (SET NULL / RESTRICT)
        return await super().create(**kwargs)

    async def get_by_target_assertion(self, target_assertion_id: str) -> list[Citation]:
        stmt = select(Citation).where(Citation.target_assertion_id == target_assertion_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
