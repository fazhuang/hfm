"""Tests for stable identifiers (CD-0 — Foundation, I5)."""

import uuid as _uuid

from hfm.core.identifiers import is_valid_uuid, uuid7


def _timestamp_ms(value: str) -> int:
    """Extract the 48-bit unix-ms timestamp from a UUIDv7 string."""
    return _uuid.UUID(value).int >> 80


def test_uuid7_format() -> None:
    value = uuid7()
    assert len(value) == 36
    assert value[14] == "7"  # version nibble
    assert value[19] in ("8", "9", "a", "b")  # variant nibble
    assert is_valid_uuid(value)


def test_uuid7_unique_and_time_ordered() -> None:
    first = uuid7()
    second = uuid7()
    assert first != second
    # time-ordered: the 48-bit ms timestamp must be non-decreasing
    assert _timestamp_ms(first) <= _timestamp_ms(second)


def test_uuid7_uniqueness_bulk() -> None:
    values = {uuid7() for _ in range(200)}
    assert len(values) == 200


def test_is_valid_uuid_rejects_invalid() -> None:
    assert not is_valid_uuid("not-a-uuid")
    assert not is_valid_uuid("")
    assert not is_valid_uuid("00000000-0000-0000-0000-00000000000")  # wrong length
    assert is_valid_uuid("00000000-0000-7000-8000-000000000000")
