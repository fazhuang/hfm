# mypy: disable-error-code="import-untyped,import-not-found"
# pyright: reportMissingImports=false
"""Phase-2 P2-05 media & rights lifecycle tests.

Proves the frozen P2-05 acceptance criteria:
  - P2-05-AC-01 media without sufficient rights metadata cannot publish
    (fail-closed);
  - P2-05-AC-02 original vs public derivative separation with byte-hash
    binding;
  - P2-05-AC-03 withdrawal removes the public derivative from the public
    projection while retaining the row for audit;
  - P2-05-AC-04 redaction/watermark token is deterministic on fixture.
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import AsyncGenerator
from datetime import date

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from hfm.phase2.media import MediaAsset, MediaAssetState, MediaRights, MediaService
from hfm.phase2.media.service import (
    compute_sha256,
    hash_matches,
    redaction_token,
    rights_sufficient,
    verify_asset_bytes,
)

#: 64-hex fixture hashes.
SHA_A = hashlib.sha256(b"original-bytes-a").hexdigest()
SHA_D = hashlib.sha256(b"derivative-bytes-d").hexdigest()
SHA_E = hashlib.sha256(b"other-bytes").hexdigest()


@pytest_asyncio.fixture
async def media(session: AsyncSession) -> AsyncGenerator[MediaService, None]:
    yield MediaService(session)


async def test_ac01_publish_fail_closed_without_rights(media: MediaService) -> None:
    """No rights metadata → never publishable (fail-closed)."""
    asset = await media.ingest(
        object_key="orig-1",
        mime_type="image/jpeg",
        byte_size=1024,
        sha256=SHA_A,
        rights=MediaRights(
            holder="示范中心", license_basis="展览授权", publication_permission=False
        ),
    )
    assert not rights_sufficient(asset)
    try:
        await media.publish(asset.object_key)
        raise AssertionError("publish must fail without publication permission")
    except ValueError:
        pass
    assert asset.publication_state == MediaAssetState.DRAFT


async def test_ac01_ingest_requires_rights(media: MediaService) -> None:
    """Ingestion without holder/license basis is rejected."""
    try:
        await media.ingest(
            object_key="orig-2",
            mime_type="image/png",
            byte_size=10,
            sha256=SHA_E,
            rights=MediaRights(holder="", license_basis=""),
        )
        raise AssertionError("ingest must reject empty rights metadata")
    except ValueError:
        pass


async def test_ac01_publish_with_rights_succeeds(media: MediaService) -> None:
    asset = await media.ingest(
        object_key="orig-3",
        mime_type="image/jpeg",
        byte_size=2048,
        sha256=SHA_A,
        rights=MediaRights(
            holder="示范中心",
            license_basis="公开展示授权",
            publication_permission=True,
        ),
    )
    published = await media.publish(asset.object_key)
    assert published.publication_state == MediaAssetState.PUBLISHED


async def test_ac02_derivative_bound_to_original(media: MediaService) -> None:
    original = await media.ingest(
        object_key="orig-4",
        mime_type="image/jpeg",
        byte_size=2048,
        sha256=SHA_A,
        rights=MediaRights(
            holder="示范中心",
            license_basis="公开展示授权",
            publication_permission=True,
        ),
    )
    derivative = await media.create_derivative(
        original_object_key=original.object_key,
        object_key="deriv-4",
        mime_type="image/webp",
        byte_size=512,
        sha256=SHA_D,
        redaction_rule="blur-faces",
    )
    linked = await media.find_original(derivative)
    assert linked is not None
    assert linked.object_key == original.object_key
    assert hash_matches(original, SHA_A)
    assert not hash_matches(original, SHA_D)


async def test_ac02_derivative_requires_existing_original(media: MediaService) -> None:
    try:
        await media.create_derivative(
            original_object_key="missing-orig",
            object_key="deriv-x",
            mime_type="image/webp",
            byte_size=1,
            sha256=SHA_D,
            redaction_rule="blur-faces",
        )
        raise AssertionError("derivative must require an existing original")
    except ValueError:
        pass


async def test_ac03_withdrawal_removes_from_public_projection(media: MediaService) -> None:
    asset = await media.ingest(
        object_key="orig-5",
        mime_type="image/jpeg",
        byte_size=1024,
        sha256=SHA_A,
        rights=MediaRights(
            holder="示范中心",
            license_basis="公开展示授权",
            publication_permission=True,
        ),
    )
    await media.publish(asset.object_key)
    assert any(a.object_key == asset.object_key for a in await media.public_projection())

    withdrawn = await media.withdraw(asset.object_key)
    assert withdrawn.publication_state == MediaAssetState.WITHDRAWN

    projection = await media.public_projection()
    assert not any(a.object_key == asset.object_key for a in projection)
    # Row retained for auditability (withdrawal never deletes the record).
    retained = await media.get(asset.object_key)
    assert retained is not None
    assert retained.publication_state == MediaAssetState.WITHDRAWN


async def test_ac03_withdrawn_derivative_excluded_from_projection(media: MediaService) -> None:
    original = await media.ingest(
        object_key="orig-6",
        mime_type="image/jpeg",
        byte_size=1024,
        sha256=SHA_A,
        rights=MediaRights(
            holder="示范中心",
            license_basis="公开展示授权",
            publication_permission=True,
        ),
    )
    derivative = await media.create_derivative(
        original_object_key=original.object_key,
        object_key="deriv-6",
        mime_type="image/webp",
        byte_size=256,
        sha256=SHA_D,
        redaction_rule="crop-seal",
    )
    await media.publish(derivative.object_key)
    assert any(a.object_key == derivative.object_key for a in await media.public_projection())
    await media.withdraw(derivative.object_key)
    assert not any(a.object_key == derivative.object_key for a in await media.public_projection())


async def test_ac04_redaction_token_deterministic(media: MediaService) -> None:
    """Same object identity + rule → same token; different rule → different."""
    first = redaction_token("orig-7", SHA_A, "blur-faces")
    again = redaction_token("orig-7", SHA_A, "blur-faces")
    other = redaction_token("orig-7", SHA_A, "crop-seal")
    assert first == again
    assert first != other
    assert len(first) == 64

    asset = await media.ingest(
        object_key="orig-7",
        mime_type="image/jpeg",
        byte_size=512,
        sha256=SHA_A,
        rights=MediaRights(
            holder="示范中心",
            license_basis="公开展示授权",
            publication_permission=True,
        ),
    )
    derivative = await media.create_derivative(
        original_object_key=asset.object_key,
        object_key="deriv-7",
        mime_type="image/webp",
        byte_size=128,
        sha256=SHA_D,
        redaction_rule="blur-faces",
    )
    assert derivative.redaction_token == first
    assert derivative.redaction_token == redaction_token(
        asset.object_key, asset.sha256, "blur-faces"
    )


async def test_state_machine_rejects_withdrawn_republish(media: MediaService) -> None:
    asset = await media.ingest(
        object_key="orig-8",
        mime_type="image/jpeg",
        byte_size=512,
        sha256=SHA_A,
        rights=MediaRights(
            holder="示范中心",
            license_basis="公开展示授权",
            publication_permission=True,
        ),
    )
    await media.publish(asset.object_key)
    await media.withdraw(asset.object_key)
    try:
        await media.publish(asset.object_key)
        raise AssertionError("withdrawn media must not be re-published")
    except ValueError:
        pass


async def test_model_importable() -> None:
    """Media model registers on the accepted declarative base."""
    assert MediaAsset.__tablename__ == "media_assets"
    assert MediaAssetState.DRAFT == "draft"
    assert MediaAssetState.WITHDRAWN == "withdrawn"


class _FixtureStore:
    """Fixture-backed object store (ADR-P2-01 storage abstraction)."""

    def __init__(self, objects: dict[str, bytes]) -> None:
        self._objects = objects

    async def get_bytes(self, object_key: str) -> bytes:
        if object_key not in self._objects:
            raise OSError(object_key)
        return self._objects[object_key]


async def test_p104_expired_rights_rejected(media: MediaService) -> None:
    """Expired rights_expiry fails closed on publication (P1-04)."""
    asset = await media.ingest(
        object_key="orig-exp-1",
        mime_type="image/jpeg",
        byte_size=128,
        sha256=SHA_A,
        rights=MediaRights(
            holder="示范中心",
            license_basis="公开展示授权",
            publication_permission=True,
            rights_expiry=date(2020, 1, 1),
        ),
    )
    assert not rights_sufficient(asset, today=date(2026, 1, 1))
    try:
        await media.publish(asset.object_key, today=date(2026, 1, 1))
        raise AssertionError("expired rights must deny publication")
    except ValueError:
        pass


async def test_p104_future_expiry_allowed(media: MediaService) -> None:
    """Future expiry allows publication when all other conditions hold."""
    asset = await media.ingest(
        object_key="orig-fut-1",
        mime_type="image/jpeg",
        byte_size=128,
        sha256=SHA_A,
        rights=MediaRights(
            holder="示范中心",
            license_basis="公开展示授权",
            publication_permission=True,
            rights_expiry=date(2030, 1, 1),
        ),
    )
    assert rights_sufficient(asset, today=date(2026, 1, 1))
    published = await media.publish(asset.object_key, today=date(2026, 1, 1))
    assert published.publication_state == MediaAssetState.PUBLISHED


async def test_p104_expiry_boundary_deterministic(media: MediaService) -> None:
    """Expiry boundary is deterministic: expiry == today is allowed; the next
    day is denied."""
    asset = await media.ingest(
        object_key="orig-bnd-1",
        mime_type="image/jpeg",
        byte_size=128,
        sha256=SHA_A,
        rights=MediaRights(
            holder="示范中心",
            license_basis="公开展示授权",
            publication_permission=True,
            rights_expiry=date(2026, 6, 1),
        ),
    )
    assert rights_sufficient(asset, today=date(2026, 6, 1))
    assert not rights_sufficient(asset, today=date(2026, 6, 2))
    assert rights_sufficient(asset, today=date(2026, 5, 31))


async def test_p105_actual_bytes_verified(media: MediaService) -> None:
    """Real artifact bytes are verified against the bound hash (P1-05)."""
    asset = await media.ingest(
        object_key="orig-bytes-1",
        mime_type="image/jpeg",
        byte_size=11,
        sha256=SHA_A,
        rights=MediaRights(
            holder="示范中心", license_basis="公开展示授权", publication_permission=True
        ),
    )
    store = _FixtureStore({"orig-bytes-1": b"original-bytes-a"})
    assert await verify_asset_bytes(asset, store) is True
    assert compute_sha256(b"original-bytes-a") == SHA_A


async def test_p105_tampered_bytes_fail(media: MediaService) -> None:
    """Tampered object bytes fail the byte-hash verification."""
    asset = await media.ingest(
        object_key="orig-bytes-2",
        mime_type="image/jpeg",
        byte_size=12,
        sha256=SHA_A,
        rights=MediaRights(
            holder="示范中心", license_basis="公开展示授权", publication_permission=True
        ),
    )
    store = _FixtureStore({"orig-bytes-2": b"tampered bytes"})
    assert await verify_asset_bytes(asset, store) is False


async def test_p105_declared_hash_mismatch_fail(media: MediaService) -> None:
    """A stored hash that does not match the actual bytes fails."""
    asset = await media.ingest(
        object_key="orig-bytes-3",
        mime_type="image/jpeg",
        byte_size=12,
        sha256=SHA_D,
        rights=MediaRights(
            holder="示范中心", license_basis="公开展示授权", publication_permission=True
        ),
    )
    store = _FixtureStore({"orig-bytes-3": b"original-bytes-a"})
    assert await verify_asset_bytes(asset, store) is False


async def test_p106_derivative_self_reference_fail(media: MediaService) -> None:
    """A derivative cannot reference itself (P1-06)."""
    original = await media.ingest(
        object_key="orig-self-1",
        mime_type="image/jpeg",
        byte_size=128,
        sha256=SHA_A,
        rights=MediaRights(
            holder="示范中心", license_basis="公开展示授权", publication_permission=True
        ),
    )
    try:
        await media.create_derivative(
            original_object_key=original.object_key,
            object_key=original.object_key,
            mime_type="image/webp",
            byte_size=64,
            sha256=SHA_D,
            redaction_rule="blur",
        )
        raise AssertionError("self-referencing derivative must be rejected")
    except ValueError:
        pass


async def test_p106_derivative_distinct_hash_enforced(media: MediaService) -> None:
    """A derivative must differ in bytes from its original (separation)."""
    original = await media.ingest(
        object_key="orig-same-1",
        mime_type="image/jpeg",
        byte_size=128,
        sha256=SHA_A,
        rights=MediaRights(
            holder="示范中心", license_basis="公开展示授权", publication_permission=True
        ),
    )
    try:
        await media.create_derivative(
            original_object_key=original.object_key,
            object_key="deriv-same-1",
            mime_type="image/jpeg",
            byte_size=128,
            sha256=SHA_A,
            redaction_rule="none",
        )
        raise AssertionError("byte-identical derivative must be rejected")
    except ValueError:
        pass


async def test_p106_derivative_bytes_independently_verified(media: MediaService) -> None:
    """Derivative bytes are independently verified against its own hash."""
    original = await media.ingest(
        object_key="orig-ind-1",
        mime_type="image/jpeg",
        byte_size=128,
        sha256=SHA_A,
        rights=MediaRights(
            holder="示范中心", license_basis="公开展示授权", publication_permission=True
        ),
    )
    derivative = await media.create_derivative(
        original_object_key=original.object_key,
        object_key="deriv-ind-1",
        mime_type="image/webp",
        byte_size=20,
        sha256=SHA_D,
        redaction_rule="crop-seal",
    )
    store = _FixtureStore({"deriv-ind-1": b"derivative-bytes-d"})
    assert await verify_asset_bytes(derivative, store) is True
    assert derivative.sha256 != original.sha256


def test_p2_current_migration_head_0014() -> None:
    """Frontier-2 current-state migration verification (not an accepted-file
    modification): the authorized P2-05 schema migration leaves a single
    linear head 0014 with revisions 0001..0014."""
    import pathlib

    versions = pathlib.Path("/Users/likeming/Sites/hfm/apps/backend/alembic/versions")
    revisions = set()
    for path in versions.glob("*.py"):
        text = path.read_text(encoding="utf-8")
        match = re.search(r'revision\s*=\s*["\']([^"\']+)["\']', text)
        if match:
            revisions.add(match.group(1))
    assert revisions == {f"{i:04d}" for i in range(1, 15)}
    assert "0014" in revisions
