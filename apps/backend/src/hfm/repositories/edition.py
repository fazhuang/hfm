"""Edition repository (CD-2)."""

from __future__ import annotations

from hfm.models.edition import Edition
from hfm.repositories.base import BaseRepository


class EditionRepository(BaseRepository[Edition]):
    """CRUD for Edition."""

    model = Edition
