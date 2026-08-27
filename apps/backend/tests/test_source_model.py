"""Tests for the Source model (CD-0 — ADAPT, I4/I5)."""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from hfm.repositories.source import SourceRepository


async def test_source_key_direct_mutation_rejected(session: AsyncSession) -> None:
    """Model-level guard: source_key cannot be reassigned after creation (I5)."""
    repo = SourceRepository(session)
    source, _ = await repo.create_idempotent(source_key="stable-key", title="t")
    with pytest.raises(ValueError):
        source.source_key = "changed-key"


async def test_source_construction_and_idempotent_create(session: AsyncSession) -> None:
    repo = SourceRepository(session)
    source, created = await repo.create_idempotent(
        source_key="key-huangfu-jiayijing",
        source_type="ancient_text",
        title="针灸甲乙经",
        rights_basis="public_domain",
    )
    assert created is True
    assert source.id  # UUIDv7 stable id assigned
    assert source.source_key == "key-huangfu-jiayijing"


async def test_source_key_immutability_no_duplicate(session: AsyncSession) -> None:
    repo = SourceRepository(session)
    await repo.create_idempotent(source_key="k1", title="first")
    # re-import with the same key: returns existing, no silent overwrite (I4/I5)
    existing, created = await repo.create_idempotent(source_key="k1", title="OVERWRITE-ATTEMPT")
    assert created is False
    assert existing.title == "first"
    assert await repo.count() == 1


async def test_direct_duplicate_source_key_rejected(session: AsyncSession) -> None:
    repo = SourceRepository(session)
    await repo.create(source_key="dup-key")
    with pytest.raises(IntegrityError):
        await repo.create(source_key="dup-key")


async def test_get_by_key(session: AsyncSession) -> None:
    repo = SourceRepository(session)
    await repo.create_idempotent(source_key="find-me")
    assert (await repo.get_by_key("find-me")) is not None
    assert (await repo.get_by_key("missing")) is None
