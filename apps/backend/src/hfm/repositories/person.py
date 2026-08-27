"""Person repository (CD-1)."""

from __future__ import annotations

from hfm.models.person import Person
from hfm.repositories.base import BaseRepository


class PersonRepository(BaseRepository[Person]):
    """CRUD for Person (a typed Entity extension)."""

    model = Person
