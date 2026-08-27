"""Stable identifier infrastructure (CD-0 — Foundation).

UUIDv7 generator ported from HFB `apps/backend/app/db/base.py::uuid7`
@ `03755b5` (generic pure function; no DB coupling). Identifier validation
is HFM-native. Satisfies invariant I5 (Stable Identity).
"""

from __future__ import annotations

import os
import uuid as _uuid
from datetime import UTC, datetime


def uuid7() -> str:
    """Return a time-ordered UUIDv7 (RFC 9562) as a 36-char string.

    Layout: 48-bit unix-ms timestamp | 4-bit version (7) | 12-bit rand_a |
    2-bit variant (2) | 62-bit rand_b.
    """
    ts_ms = int(datetime.now(UTC).timestamp() * 1000) & 0xFFFFFFFFFFFF  # 48 bits
    rand = os.urandom(10)  # 80 random bits
    rand_a = int.from_bytes(rand[:2], "big") & 0x0FFF  # 12 bits
    rand_b = int.from_bytes(rand[2:], "big") & 0x3FFFFFFFFFFFFFFF  # 62 bits
    value = (ts_ms << 80) | (0x7 << 76) | (rand_a << 64) | (0x2 << 62) | rand_b
    return str(_uuid.UUID(int=value))


def is_valid_uuid(value: str) -> bool:
    """Return True if ``value`` is a well-formed canonical UUID string."""
    try:
        return str(_uuid.UUID(value)) == value
    except (ValueError, AttributeError, TypeError):
        return False
