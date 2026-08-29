"""Application import and scope tests for the HFM backend skeleton."""

from fastapi.routing import APIRoute

from hfm.main import app


def test_app_importable() -> None:
    assert app.title == "HFM"
    assert app.version == "0.2.0"  # Phase 1 API surface added


def test_no_business_routes() -> None:
    """Skeleton phase must not expose any business endpoints."""
    paths = {route.path for route in app.routes if isinstance(route, APIRoute)}
    for forbidden in (
        "/person",
        "/books",
        "/evidence",
        "/citations",
        "/search",
        "/auth",
        "/publication",
        "/media",
        "/teaching",
    ):
        assert forbidden not in paths
