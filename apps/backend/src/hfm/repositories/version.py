"""Version repository (CD-2, I2)."""

from __future__ import annotations

from sqlalchemy import select

from hfm.models.version import Version
from hfm.repositories.base import BaseRepository


class VersionRepository(BaseRepository[Version]):
    """CRUD for Version with lineage awareness (I2)."""

    model = Version

    async def get_by_edition(self, edition_id: str) -> list[Version]:
        stmt = (
            select(Version).where(Version.edition_id == edition_id).order_by(Version.version_name)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def lineage_has_cycle(self, version_id: str) -> bool:
        """I2: walk the parent chain and report a cycle (detection, not enforcement).

        Enforcement of acyclic lineage is a service-layer concern (out of CD-2);
        this helper provides reproducible detection for lineage validation.
        """
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
