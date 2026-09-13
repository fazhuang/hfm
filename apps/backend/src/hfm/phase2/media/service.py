"""Media & rights service (P2-05 — ADR-P2-01).

Fail-closed lifecycle over the media registry:

  - ingest: byte-hash binding; rights metadata required (holder + basis);
  - derivative: original/derivative linkage with hash binding;
  - grant: derivative-only publication grant for redacted P2 material
    (policy §4.1) — the original stays sealed;
  - publish: requires sufficient rights metadata plus a publication
    grant (P2-05-AC-01);
  - withdraw: projection-state change; the row is retained for audit
    (P2-05-AC-03);
  - redaction/watermark token: deterministic from object identity + rule
    (P2-05-AC-04).

Privacy gating (``HFM-ASSET-PRESENTATION-POLICY.md`` §4) is enforced in
the database as well as here: P3 is never published, and a P2 original is
never published — only its redacted derivative, carrying its own grant.

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

from hfm.phase2.media.models import GATED_PRIVACY_CLASSES, MediaAsset, MediaAssetState, PrivacyClass

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
    privacy_class: str = PrivacyClass.P0


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
        if rights.privacy_class in GATED_PRIVACY_CLASSES and rights.publication_permission:
            raise MediaRightsError(
                f"{rights.privacy_class} material cannot carry a publication permission — "
                "P2 is published only as a redacted derivative and P3 is never published"
            )
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
            privacy_class=rights.privacy_class,
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
            privacy_class=original.privacy_class,
            publication_state=MediaAssetState.DRAFT,
            redaction_token=redaction_token(original.object_key, original.sha256, redaction_rule),
        )
        self.session.add(derivative)
        await self.session.flush()
        return derivative

    async def grant_derivative_publication(self, object_key: str) -> MediaAsset:
        """Grant a redacted derivative permission to be published (policy §4.1).

        This is the only path by which gated (P2) material can reach the
        public projection, and it deliberately never touches the original:
        the original keeps ``publication_permission = false`` and stays
        ``draft``, so the unredacted bytes are unreachable through every
        public endpoint. Fail-closed on anything that is not a redacted
        derivative.
        """
        asset = await self.get(object_key)
        if asset is None:
            raise MediaRightsError(f"media not found: {object_key}")
        if asset.original_object_key is None:
            raise MediaRightsError(
                "a publication grant can only be set on a derivative — "
                f"{object_key} is an original"
            )
        if not asset.redaction_token:
            raise MediaRightsError(f"derivative {object_key} carries no redaction token")
        if asset.privacy_class == PrivacyClass.P3:
            raise MediaRightsError("P3 material must never enter the public projection")
        asset.derivative_publication_permission = True
        await self.session.flush()
        return asset

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
        if asset.privacy_class == PrivacyClass.P3:
            raise MediaRightsError("P3 material must never enter the public projection")
        if asset.privacy_class == PrivacyClass.P2 and asset.original_object_key is None:
            raise MediaRightsError(
                "a P2 original cannot be published — publish its redacted derivative instead"
            )
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
    """Fail-closed eligibility: explicit rights metadata + a publication
    grant, and rights not expired (P1-04). ``today`` makes the time
    comparison deterministic and timezone-safe (UTC date by default).
    Expiry is inclusive: an asset is eligible on its expiry date and denied
    from the next day onward.

    A grant is either the ordinary ``publication_permission`` (P0/P1
    material cleared directly) or the derivative-only grant a redacted P2
    derivative carries (policy §4.1). The privacy class itself is enforced
    by ``publish`` and by database check constraints — this predicate only
    answers the rights question.
    """
    reference = today or datetime.now(UTC).date()
    granted = bool(asset.publication_permission or asset.derivative_publication_permission)
    return bool(
        granted
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


#: Object-key markers per public projection category. Order matters: the first
#: match wins, so a person's film folder classifies as a film rather than as
#: person material.
_PUBLIC_CATEGORY_MARKERS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("paper", ("论文",)),
    ("movie", ("电影",)),
    ("classic", ("论著", "版本")),
    ("person", ("其传", "其言", "后论", "画像")),
)


def public_category(object_key: str) -> str:
    """Public projection category for a media object key.

    Derived from the object-key path, which mirrors how the client delivery
    directory is organised: papers, classics and films, plus a person's own
    biography (其传), words (其言), later discourse (后论) and portrait (画像).
    Keys matching nothing fall back to ``"other"``.
    """
    for category, markers in _PUBLIC_CATEGORY_MARKERS:
        if any(marker in object_key for marker in markers):
            return category
    return "other"
