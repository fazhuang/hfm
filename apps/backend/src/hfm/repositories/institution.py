"""Institution repository (CD-0)."""

from __future__ import annotations

from hfm.models.institution import Institution
from hfm.repositories.base import BaseRepository


class InstitutionRepository(BaseRepository[Institution]):
    """CRUD for Institution."""

    model = Institution
