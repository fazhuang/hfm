"""HFM Phase 2 media & rights lifecycle (P2-05).

Media object registry with rights metadata, byte-hash binding,
original/derivative linkage, publication state, and redaction tokens per
ADR-P2-01: binaries live in S3-compatible object storage; PostgreSQL holds
metadata only. Publication is fail-closed: it requires explicit rights
metadata plus publication permission.
"""

from __future__ import annotations

from hfm.phase2.media.models import MediaAsset, MediaAssetState
from hfm.phase2.media.service import MediaRights, MediaService

__all__ = ["MediaAsset", "MediaAssetState", "MediaRights", "MediaService"]
