"""Chapter repository (CD-2)."""

from __future__ import annotations

from hfm.models.chapter import Chapter
from hfm.repositories.base import BaseRepository


class ChapterRepository(BaseRepository[Chapter]):
    """CRUD for Chapter."""

    model = Chapter
