"""Work repository (CD-2)."""

from __future__ import annotations

from hfm.models.work import Work
from hfm.repositories.base import BaseRepository


class WorkRepository(BaseRepository[Work]):
    """CRUD for Work."""

    model = Work
