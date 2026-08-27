"""Canonical hashing utilities (migrated Batch 1 asset — PORT).

Source: HFB `apps/backend/app/core/canonical_hash.py` @ `03755b5`.
No domain coupling; used for physical-byte and canonical-metadata identity.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any


def calculate_bytes_sha256(data: bytes) -> str:
    """Return the lowercase hex SHA-256 digest of raw bytes."""
    return hashlib.sha256(data).hexdigest()


def canonical_json(obj: Any) -> str:
    """Serialize ``obj`` to canonical JSON per RFC 8785 (JCS).

    For metadata payloads (strings, ints, bools, null, nested dicts/lists),
    JCS reduces to: sorted object keys, compact separators, UTF-8, no
    insignificant whitespace.
    """
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def calculate_canonical_metadata_sha256(metadata: Any) -> str:
    """Return the SHA-256 of the canonical JSON form of ``metadata``."""
    canonical = canonical_json(metadata)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
