"""API error handlers — convert exceptions to a unified JSON response.

Migrated Batch 1 asset (ADAPT). Source: HFB `apps/backend/app/core/error_handlers.py`
@ `03755b5`. Adaptations:
  - HFM namespace (hfm.core.exceptions / hfm.core.logging);
  - removed HFB `InvalidStatusTransitionError` handler (domain status machine);
  - strict typing: handlers accept `Exception` (FastAPI `ExceptionHandler`
    contravariance) and narrow via `isinstance`.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from hfm.core.exceptions import DomainException
from hfm.core.logging import get_logger

logger = get_logger(__name__)


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _get_request_id(request: Request) -> str:
    return getattr(request.state, "request_id", "unknown")


def _error_envelope(
    status_code: int,
    message: str,
    error_code: str,
    request_id: str,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "success": False,
        "timestamp": _now_iso(),
        "data": None,
        "message": message,
        "meta": {
            "error_code": error_code,
            "request_id": request_id,
            "metadata": metadata or {},
        },
    }


def _attach_request_id(request: Request, response: JSONResponse) -> None:
    """Ensure the X-Request-ID header is present on every error response."""
    rid = _get_request_id(request)
    if rid and rid != "unknown" and "X-Request-ID" not in response.headers:
        response.headers["X-Request-ID"] = rid


async def domain_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """DomainException → unified error envelope."""
    assert isinstance(exc, DomainException)
    logger.warning(
        "domain_error error_code=%s status=%d message=%s request_id=%s",
        exc.error_code,
        exc.status_code,
        exc.message,
        _get_request_id(request),
    )
    resp = JSONResponse(
        status_code=exc.status_code,
        content=_error_envelope(
            status_code=exc.status_code,
            message=exc.message,
            error_code=exc.error_code,
            request_id=_get_request_id(request),
            metadata=exc.metadata,
        ),
    )
    _attach_request_id(request, resp)
    return resp


async def request_validation_handler(request: Request, exc: Exception) -> JSONResponse:
    """FastAPI RequestValidationError → 422 unified format."""
    assert isinstance(exc, RequestValidationError)
    logger.warning(
        "request_validation_error errors=%s request_id=%s",
        str(exc.errors()),
        _get_request_id(request),
    )
    resp = JSONResponse(
        status_code=422,
        content=_error_envelope(
            status_code=422,
            message="Request validation failed",
            error_code="REQUEST_VALIDATION_ERROR",
            request_id=_get_request_id(request),
            metadata={"validation_errors": exc.errors()},
        ),
    )
    _attach_request_id(request, resp)
    return resp


async def http_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Starlette/FastAPI HTTPException → unified format."""
    assert isinstance(exc, StarletteHTTPException)
    logger.warning(
        "http_exception status=%d detail=%s request_id=%s",
        exc.status_code,
        exc.detail,
        _get_request_id(request),
    )
    resp = JSONResponse(
        status_code=exc.status_code,
        content=_error_envelope(
            status_code=exc.status_code,
            message=str(exc.detail),
            error_code="HTTP_ERROR",
            request_id=_get_request_id(request),
        ),
    )
    _attach_request_id(request, resp)
    return resp


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all for unexpected errors — 500, no detail leaked."""
    logger.exception(
        "unhandled_error type=%s message=%s request_id=%s",
        type(exc).__name__,
        str(exc),
        _get_request_id(request),
    )
    resp = JSONResponse(
        status_code=500,
        content=_error_envelope(
            status_code=500,
            message="Internal server error",
            error_code="INTERNAL_ERROR",
            request_id=_get_request_id(request),
        ),
    )
    _attach_request_id(request, resp)
    return resp


def register_error_handlers(app: FastAPI) -> None:
    """Register the unified error handlers on a FastAPI application."""
    app.add_exception_handler(DomainException, domain_exception_handler)
    app.add_exception_handler(RequestValidationError, request_validation_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
