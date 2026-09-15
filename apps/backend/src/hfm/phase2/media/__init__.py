"""HFM Phase 2 media & rights lifecycle (P2-05).

Media object registry with rights metadata, byte-hash binding,
original/derivative linkage, publication state, and redaction tokens per
ADR-P2-01: binaries live in S3-compatible object storage; PostgreSQL holds
metadata only. Publication is fail-closed: it requires explicit rights
metadata plus a publication grant.

Privacy gating (``HFM-ASSET-PRESENTATION-POLICY.md`` §4) is enforced by the
database as well as the service: P3 material is never published, and P2
material reaches the public projection only as a redacted derivative.
"""

from __future__ import annotations

from hfm.phase2.media.models import (
    GATED_PRIVACY_CLASSES,
    MediaAsset,
    MediaAssetState,
    PrivacyClass,
)
from hfm.phase2.media.service import MediaRights, MediaService

__all__ = [
    "GATED_PRIVACY_CLASSES",
    "MediaAsset",
    "MediaAssetState",
    "MediaRights",
    "MediaService",
    "PrivacyClass",
]
