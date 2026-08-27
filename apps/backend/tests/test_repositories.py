"""Repository behavior tests (CD-0 — BaseRepository ADAPT)."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from hfm.models.institution import InstitutionType
from hfm.models.source import Source
from hfm.repositories.base import BaseRepository
from hfm.repositories.institution import InstitutionRepository
from hfm.repositories.source import SourceRepository


class _SourceRepo(BaseRepository[Source]):
    model = Source


async def test_base_repository_crud_round_trip(session: AsyncSession) -> None:
    repo = InstitutionRepository(session)
    created = await repo.create(name="甘肃博物馆", type=InstitutionType.archive)
    assert (await repo.get_by_id(created.id)) is not None
    assert await repo.count() == 1
    assert len(await repo.list_all()) == 1
    assert await repo.delete(created.id) is True
    assert await repo.count() == 0


async def test_base_repository_update_missing_returns_none(session: AsyncSession) -> None:
    repo = InstitutionRepository(session)
    assert (await repo.update("missing-id", name="x")) is None


async def test_base_repository_generic_instantiation(session: AsyncSession) -> None:
    """BaseRepository can be instantiated with a concrete model."""
    repo = _SourceRepo(session)
    created = await repo.create(source_key="generic-test")
    assert (await repo.get_by_id(created.id)) is not None


async def test_source_repository_create_idempotent(session: AsyncSession) -> None:
    repo = SourceRepository(session)
    _, created = await repo.create_idempotent(source_key="idem-key")
    assert created is True
    _, created_again = await repo.create_idempotent(source_key="idem-key")
    assert created_again is False


async def test_update_rejects_immutable_fields(session: AsyncSession) -> None:
    """BaseRepository.update must reject stable-identity fields (I5)."""
    repo = SourceRepository(session)
    source, _ = await repo.create_idempotent(source_key="immutable", title="t")
    with pytest.raises(ValueError):
        await repo.update(source.id, source_key="changed")
    # mutable fields remain updatable
    updated = await repo.update(source.id, title="t2")
    assert updated is not None
    assert updated.title == "t2"
    assert updated.source_key == "immutable"


def test_immutable_fields_declared_on_model() -> None:
    """id is immutable on every model; source_key additionally on Source."""
    from hfm.models.source import Source

    assert "id" in Source.immutable_fields
    assert "source_key" in Source.immutable_fields
