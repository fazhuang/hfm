"""Tests for the generic pagination primitives (migrated Batch 2 asset — PORT)."""

from pydantic import ValidationError

from hfm.schemas.common import PaginatedResponse, PaginationParams


def test_pagination_params_defaults() -> None:
    params = PaginationParams()
    assert params.page == 1
    assert params.limit == 20


def test_pagination_params_validation_boundaries() -> None:
    assert PaginationParams(page=1, limit=1).limit == 1
    assert PaginationParams(page=2, limit=100).limit == 100
    for invalid in ({"page": 0}, {"limit": 0}, {"limit": 101}):
        try:
            PaginationParams(**invalid)
        except ValidationError:
            pass
        else:
            raise AssertionError(f"expected ValidationError for {invalid}")


def test_paginated_response_envelope() -> None:
    response = PaginatedResponse(page=2, limit=20, total=45, total_pages=3)
    assert response.page == 2
    assert response.limit == 20
    assert response.total == 45
    assert response.total_pages == 3
    assert response.model_dump() == {
        "page": 2,
        "limit": 20,
        "total": 45,
        "total_pages": 3,
    }
