"""Version repository (CD-2, I2 lineage enforcement + withdrawal)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select

from hfm.models.version import Version
from hfm.repositories.base import BaseRepository


class VersionRepository(BaseRepository[Version]):
    """CRUD for Version with lineage enforcement (I2).

    parent_version_id is protected (immutable after creation); create-time
    checks enforce same-Edition lineage and parent existence, so post-create
    multi-node cycles cannot be formed. lineage_has_cycle provides
    reproducible detection for verification.
    """

    model = Version

    async def _validate_lineage(self, edition_id: str, parent_version_id: str | None) -> None:
        if parent_version_id is None:
            return
        parent = await self.session.get(Version, parent_version_id)
        if parent is None:
            raise ValueError("parent version does not exist")
        if parent.edition_id != edition_id:
            raise ValueError("parent version must belong to the same Edition")

    async def create(self, **kwargs: Any) -> Version:
        edition_id = str(kwargs.get("edition_id") or "")
        parent_version_id = kwargs.get("parent_version_id")
        await self._validate_lineage(
            edition_id, str(parent_version_id) if parent_version_id else None
        )
        return await super().create(**kwargs)

    async def mark_withdrawn(self, version_id: str) -> Version | None:
        """Mark a Version withdrawn (Frozen Canonical §2 — I2).

        Withdrawn Versions cannot be newly cited by Citations.
        """
        version = await self.get_by_id(version_id)
        if version is None:
            return None
        version.withdrawn_at = datetime.now(UTC)
        await self.session.flush()
        return version

    async def get_by_edition(self, edition_id: str) -> list[Version]:
        stmt = (
            select(Version).where(Version.edition_id == edition_id).order_by(Version.version_name)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def lineage_has_cycle(self, version_id: str) -> bool:
        """Walk the parent chain and report a cycle (detection helper)."""
        seen: set[str] = set()
        current: str | None = version_id
        while current is not None:
            if current in seen:
                return True
            seen.add(current)
            stmt = select(Version.parent_version_id).where(Version.id == current)
            result = await self.session.execute(stmt)
            current = result.scalar_one_or_none()
        return False
