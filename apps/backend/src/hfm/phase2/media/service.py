"""Media & rights service (P2-05 — ADR-P2-01).

Fail-closed lifecycle over the media registry:

  - ingest: byte-hash binding; rights metadata required (holder + basis);
  - derivative: original/derivative linkage with hash binding;
  - publish: requires sufficient rights metadata plus publication
    permission (P2-05-AC-01);
  - withdraw: projection-state change; the row is retained for audit
    (P2-05-AC-03);
  - redaction/watermark token: deterministic from object identity + rule
    (P2-05-AC-04).

Binary bytes are never stored here — object keys point into S3-compatible
object storage; PostgreSQL holds metadata only (ADR-P2-01).
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import UTC, date, datetime
from typing import Protocol

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from hfm.phase2.media.models import MediaAsset, MediaAssetState

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class ObjectStore(Protocol):
    """S3-compatible object storage abstraction (ADR-P2-01)."""

    async def get_bytes(self, object_key: str) -> bytes: ...


class MediaRightsError(ValueError):
    """Raised when media rights metadata is insufficient (fail-closed)."""


@dataclass(frozen=True)
class MediaRights:
    """Rights metadata required before publication (ADR-P2-01)."""

    holder: str
    license_basis: str
    restriction: str | None = None
    rights_expiry: date | None = None
    publication_permission: bool = False


class MediaService:
    """Media lifecycle operations (metadata registry only)."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, object_key: str) -> MediaAsset | None:
        stmt = select(MediaAsset).where(MediaAsset.object_key == object_key)
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def ingest(
        self,
        *,
        object_key: str,
        mime_type: str,
        byte_size: int,
        sha256: str,
        rights: MediaRights,
        provenance: str | None = None,
    ) -> MediaAsset:
        """Register an original media object with byte-hash binding.

        Rights metadata is mandatory at ingestion (fail-closed): an asset
        without a rights holder and license basis can never become eligible
        for publication.
        """
        if not rights.holder.strip() or not rights.license_basis.strip():
            raise MediaRightsError("media ingestion requires a rights holder and license basis")
        if not _SHA256_RE.match(sha256):
            raise ValueError(f"invalid sha256 binding: {sha256}")
        asset = MediaAsset(
            object_key=object_key,
            mime_type=mime_type,
            byte_size=byte_size,
            sha256=sha256,
            rights_holder=rights.holder.strip(),
            license_basis=rights.license_basis.strip(),
            restriction=rights.restriction,
            rights_expiry=rights.rights_expiry,
            publication_permission=rights.publication_permission,
            publication_state=MediaAssetState.DRAFT,
            provenance=provenance,
        )
        self.session.add(asset)
        await self.session.flush()
        return asset

    async def create_derivative(
        self,
        *,
        original_object_key: str,
        object_key: str,
        mime_type: str,
        byte_size: int,
        sha256: str,
        redaction_rule: str,
    ) -> MediaAsset:
        """Create a public derivative bound to its original (hash linkage).

        The derivative's deterministic redaction/watermark token derives
        from the original object identity plus the redaction rule
        (P2-05-AC-04).
        """
        original = await self.get(original_object_key)
        if original is None:
            raise MediaRightsError(f"original media not found: {original_object_key}")
        if object_key == original_object_key:
            raise MediaRightsError("a derivative cannot reference itself")
        if not _SHA256_RE.match(sha256):
            raise ValueError(f"invalid sha256 binding: {sha256}")
        if sha256 == original.sha256:
            raise MediaRightsError("a derivative must differ in bytes from its original")
        derivative = MediaAsset(
            object_key=object_key,
            original_object_key=original.object_key,
            mime_type=mime_type,
            byte_size=byte_size,
            sha256=sha256,
            rights_holder=original.rights_holder,
            license_basis=original.license_basis,
            restriction=original.restriction,
            rights_expiry=original.rights_expiry,
            publication_permission=original.publication_permission,
            publication_state=MediaAssetState.DRAFT,
            redaction_token=redaction_token(original.object_key, original.sha256, redaction_rule),
        )
        self.session.add(derivative)
        await self.session.flush()
        return derivative

    async def find_original(self, asset: MediaAsset) -> MediaAsset | None:
        """Resolve the original of a derivative (None for originals)."""
        if asset.original_object_key is None:
            return None
        return await self.get(asset.original_object_key)

    async def publish(self, object_key: str, *, today: date | None = None) -> MediaAsset:
        """Publish an asset — fail-closed without sufficient rights (AC-01)."""
        asset = await self.get(object_key)
        if asset is None:
            raise MediaRightsError(f"media not found: {object_key}")
        if not rights_sufficient(asset, today=today):
            raise MediaRightsError("media cannot be published without sufficient rights metadata")
        if asset.publication_state == MediaAssetState.WITHDRAWN:
            raise MediaRightsError("withdrawn media cannot be re-published")
        asset.publication_state = MediaAssetState.PUBLISHED
        await self.session.flush()
        return asset

    async def withdraw(self, object_key: str) -> MediaAsset:
        """Withdraw an asset — projection removed, row retained (AC-03)."""
        asset = await self.get(object_key)
        if asset is None:
            raise MediaRightsError(f"media not found: {object_key}")
        asset.publication_state = MediaAssetState.WITHDRAWN
        await self.session.flush()
        return asset

    async def public_projection(self) -> list[MediaAsset]:
        """Published derivatives visible to the public projection (AC-03)."""
        stmt = (
            select(MediaAsset)
            .where(MediaAsset.publication_state == MediaAssetState.PUBLISHED)
            .order_by(MediaAsset.created_at)
        )
        return list((await self.session.execute(stmt)).scalars().all())


def rights_sufficient(asset: MediaAsset, *, today: date | None = None) -> bool:
    """Fail-closed eligibility: explicit rights metadata + permission, and
    rights not expired (P1-04). ``today`` makes the time comparison
    deterministic and timezone-safe (UTC date by default). Expiry is
    inclusive: an asset is eligible on its expiry date and denied from the
    next day onward."""
    reference = today or datetime.now(UTC).date()
    return bool(
        asset.publication_permission
        and asset.rights_holder.strip()
        and asset.license_basis.strip()
        and (asset.rights_expiry is None or asset.rights_expiry >= reference)
    )


def compute_sha256(data: bytes) -> str:
    """Canonical hash of actual artifact bytes."""
    return hashlib.sha256(data).hexdigest()


def hash_matches(asset: MediaAsset, sha256: str) -> bool:
    """Byte-hash binding check (P2-05-AC-02)."""
    return asset.sha256 == sha256


async def verify_asset_bytes(asset: MediaAsset, store: ObjectStore) -> bool:
    """Verify the ACTUAL artifact bytes against the bound hash (P1-05).

    Fetches the real bytes from the object store, computes the canonical
    hash, and fails closed on any mismatch. The caller-supplied hash is
    never trusted on its own.
    """
    try:
        actual = await store.get_bytes(asset.object_key)
    except OSError:
        return False
    return compute_sha256(actual) == asset.sha256


def redaction_token(object_key: str, sha256: str, rule: str) -> str:
    """Deterministic redaction/watermark token (P2-05-AC-04)."""
    return hashlib.sha256(f"{object_key}:{sha256}:{rule}".encode()).hexdigest()
