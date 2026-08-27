"""Tests for the system information endpoints (migrated Batch 3 asset — ADAPT)."""

from fastapi.testclient import TestClient

from hfm.main import app


def test_version_endpoint() -> None:
    client = TestClient(app)
    response = client.get("/version")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["project"] == "HFM"
    assert body["data"]["version"]
    assert body["data"]["environment"]


def test_live_endpoint() -> None:
    response = TestClient(app).get("/live")
    assert response.status_code == 200
    body = response.json()
    assert body["data"] == {"alive": True}
    assert body["message"] == "Process is alive"


def test_config_endpoint_public_only() -> None:
    response = TestClient(app).get("/config")
    assert response.status_code == 200
    data = response.json()["data"]
    assert set(data) <= {"project_name", "version", "environment"}
    assert data["project_name"] == "HFM"
