"""Core domain invariant tests (CD-0).

I1 Provenance — every SourceRef is anchored to an immutable Source.
I5 Stable Identity — source_key is unique and idempotent across re-import.
Idempotency — same source snapshot key + same migration semantics → same state.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from hfm.core.locator import Locator
from hfm.repositories.source import SourceRepository
from hfm.repositories.source_ref import SourceRefRepository


async def test_invariant_i1_provenance_seed(session: AsyncSession) -> None:
    """I1: a SourceRef always resolves to its Source."""
    source_repo = SourceRepository(session)
    ref_repo = SourceRefRepository(session)
    source, _ = await source_repo.create_idempotent(source_key="i1-source")
    ref = await ref_repo.create(
        source_id=source.id,
        title="证据锚定引用",
        locator=Locator(work_id="w9", page="1").model_dump(exclude_none=True),
    )
    assert ref.source_id == source.id
    resolved = await source_repo.get_by_id(ref.source_id)
    assert resolved is not None
    assert resolved.source_key == "i1-source"


async def test_invariant_i5_stable_identity_idempotent(session: AsyncSession) -> None:
    """I5: re-importing the same source_key yields the same identity, once."""
    repo = SourceRepository(session)
    first, created_first = await repo.create_idempotent(source_key="stable-key", title="origin")
    second, created_second = await repo.create_idempotent(source_key="stable-key", title="origin")
    assert created_first is True
    assert created_second is False
    assert first.id == second.id
    assert await repo.count() == 1


async def test_idempotency_no_state_change_on_repeat(session: AsyncSession) -> None:
    """Repeat import must not mutate the existing record (I4 no silent overwrite)."""
    repo = SourceRepository(session)
    await repo.create_idempotent(source_key="immutable-key", rights_basis="public_domain")
    existing, _ = await repo.create_idempotent(
        source_key="immutable-key",
        rights_basis="restricted",  # would-be overwrite
    )
    assert existing.rights_basis == "public_domain"
