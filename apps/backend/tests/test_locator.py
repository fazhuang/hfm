"""Tests for the structured Locator value object (CD-0 — Foundation)."""

from hfm.core.locator import Locator


def test_construction_and_fields() -> None:
    locator = Locator(work_id="w1", passage_id="p9", volume="2", page="12a", line="3")
    assert locator.work_id == "w1"
    assert locator.passage_id == "p9"
    assert locator.volume == "2"
    assert locator.page == "12a"


def test_to_locator_string() -> None:
    locator = Locator(work_id="w1", version_id="v2", volume="3", section="上", page="7")
    rendered = locator.to_locator_string()
    assert "work:w1" in rendered
    assert "version:v2" in rendered
    assert "loc:3.上.7" in rendered


def test_empty_locator() -> None:
    assert Locator().is_empty() is True
    assert Locator().to_locator_string() == "unlocated"
    assert Locator(volume="1").is_empty() is False


def test_json_round_trip() -> None:
    locator = Locator(work_id="w1", passage_id="p9", page="12")
    payload = locator.model_dump(exclude_none=True)
    restored = Locator.from_mapping(payload)
    assert restored == locator


def test_from_mapping_none() -> None:
    assert Locator.from_mapping(None).is_empty()


def test_equality() -> None:
    a = Locator(work_id="w1", page="3")
    b = Locator(work_id="w1", page="3")
    c = Locator(work_id="w1", page="4")
    assert a == b
    assert a != c
