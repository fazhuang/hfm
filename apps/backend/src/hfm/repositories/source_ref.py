"""SourceRef repository (CD-0)."""

from __future__ import annotations

from hfm.models.source_ref import SourceRef
from hfm.repositories.base import BaseRepository


class SourceRefRepository(BaseRepository[SourceRef]):
    """CRUD for SourceRef (anchored to an immutable Source)."""

    model = SourceRef
