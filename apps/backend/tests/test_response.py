"""Tests for the API response envelope (migrated Batch 1 asset — PORT)."""

from hfm.utils.response import api_response


def test_default_envelope() -> None:
    payload = api_response()
    assert payload["success"] is True
    assert payload["message"] == "ok"
    assert payload["data"] is None
    assert "timestamp" in payload


def test_envelope_with_data_message_meta() -> None:
    payload = api_response(data={"status": "ok"}, message="done", meta={"request_id": "r1"})
    assert payload["data"] == {"status": "ok"}
    assert payload["message"] == "done"
    assert payload["request_id"] == "r1"
    assert payload["success"] is True


def test_envelope_success_false() -> None:
    payload = api_response(data=None, success=False, message="failed")
    assert payload["success"] is False
    assert payload["data"] is None
