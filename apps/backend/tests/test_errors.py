"""Tests for unified error handling (migrated Batch 1 asset — ADAPT)."""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from hfm.core.error_handlers import register_error_handlers
from hfm.core.exceptions import NotFoundException, ValidationException
from hfm.middleware.request_id import RequestIDMiddleware, _sanitize_request_id


def _make_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(RequestIDMiddleware)
    register_error_handlers(app)

    @app.get("/boom-validation")
    async def boom_validation() -> None:
        raise ValidationException("bad input")

    @app.get("/boom-notfound")
    async def boom_notfound() -> None:
        raise NotFoundException(entity_type="widget", entity_id="w1")

    @app.get("/boom-generic")
    async def boom_generic() -> None:
        raise RuntimeError("secret detail")

    return app


def test_validation_error_envelope() -> None:
    client = TestClient(_make_app())
    response = client.get("/boom-validation")
    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
    assert body["meta"]["error_code"] == "VALIDATION_ERROR"
    assert response.headers["X-Request-ID"]


def test_not_found_error_envelope() -> None:
    client = TestClient(_make_app())
    response = client.get("/boom-notfound")
    assert response.status_code == 404
    assert response.json()["meta"]["error_code"] == "NOT_FOUND"


def test_generic_500_envelope_does_not_leak_detail() -> None:
    client = TestClient(_make_app(), raise_server_exceptions=False)
    response = client.get("/boom-generic")
    assert response.status_code == 500
    body = response.json()
    assert body["meta"]["error_code"] == "INTERNAL_ERROR"
    assert "secret detail" not in str(body)


def test_request_id_sanitization() -> None:
    generated = _sanitize_request_id(None)
    assert len(generated) == 36  # uuid4 string
    assert _sanitize_request_id("a" * 200) != "a" * 200
    assert _sanitize_request_id("good-id_1.2-3@x") == "good-id_1.2-3@x"
    assert _sanitize_request_id("bad\nid") != "bad\nid"


def test_request_id_header_echoes_client_value() -> None:
    client = TestClient(_make_app())
    response = client.get("/boom-validation", headers={"X-Request-ID": "client-abc"})
    assert response.headers["X-Request-ID"] == "client-abc"
