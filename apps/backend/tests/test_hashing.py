"""Tests for the canonical hashing utilities (migrated Batch 1 asset — PORT)."""

from hfm.core.hashing import (
    calculate_bytes_sha256,
    calculate_canonical_metadata_sha256,
    canonical_json,
)


def test_bytes_sha256_known_vectors() -> None:
    assert (
        calculate_bytes_sha256(b"")
        == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    )
    assert (
        calculate_bytes_sha256(b"abc")
        == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    )


def test_canonical_json_sorted_keys_and_compact() -> None:
    assert canonical_json({"b": 1, "a": 2}) == '{"a":2,"b":1}'
    assert canonical_json({"x": None, "nested": {"z": 1, "y": [2, 1]}}) == (
        '{"nested":{"y":[2,1],"z":1},"x":null}'
    )


def test_canonical_json_rejects_nan() -> None:
    try:
        canonical_json({"v": float("nan")})
    except ValueError:
        return
    raise AssertionError("canonical_json must reject NaN (allow_nan=False)")


def test_metadata_sha256_stable_and_order_insensitive() -> None:
    a = calculate_canonical_metadata_sha256({"k1": "v1", "k2": 2})
    b = calculate_canonical_metadata_sha256({"k2": 2, "k1": "v1"})
    assert a == b
    assert len(a) == 64
    assert a == calculate_bytes_sha256(b'{"k1":"v1","k2":2}')
