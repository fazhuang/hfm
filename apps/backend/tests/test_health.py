"""Health endpoint tests for the HFM backend skeleton."""

from fastapi.testclient import TestClient

from hfm.main import app


def test_health_ok() -> None:
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "hfm"}


def test_ready_ok() -> None:
    client = TestClient(app)
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready", "service": "hfm"}
