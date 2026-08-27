"""Request ID middleware — injects X-Request-ID into every response.

Migrated Batch 1 asset (ADAPT). Source: HFB `apps/backend/app/middleware/request_id.py`
@ `03755b5`. Adaptations: HFM namespace import; strict typing of `call_next`.
"""

from __future__ import annotations

import re
import time
from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from hfm.core.logging import get_logger

logger = get_logger(__name__)

_MAX_REQUEST_ID_LENGTH = 128
_VALID_REQUEST_ID_RE = re.compile(r"^[a-zA-Z0-9\-_.@]+$")


def _sanitize_request_id(raw: str | None) -> str:
    """Validate or replace a client-supplied request ID.

    Rejects IDs that contain newlines, control characters, or are >128 chars.
    Returns a fresh UUID v4 if the supplied value is unsafe.
    """
    if raw is None:
        return str(uuid4())
    if len(raw) > _MAX_REQUEST_ID_LENGTH:
        return str(uuid4())
    if not _VALID_REQUEST_ID_RE.match(raw):
        return str(uuid4())
    return raw


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Ensures every response carries a valid X-Request-ID header.

    Registered as the outermost layer so error handlers and downstream
    middleware always have access to ``request.state.request_id``.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        inbound = request.headers.get("X-Request-ID") or request.headers.get("x-request-id")
        request_id = _sanitize_request_id(inbound)
        request.state.request_id = request_id

        start = time.monotonic()
        logger.info(
            "request_started request_id=%s method=%s path=%s",
            request_id,
            request.method,
            request.url.path,
        )

        try:
            response = await call_next(request)
        except Exception:
            elapsed_ms = round((time.monotonic() - start) * 1000, 2)
            logger.exception(
                "request_failed request_id=%s method=%s path=%s elapsed_ms=%s",
                request_id,
                request.method,
                request.url.path,
                elapsed_ms,
            )
            raise

        elapsed_ms = round((time.monotonic() - start) * 1000, 2)
        logger.info(
            "request_completed request_id=%s method=%s path=%s status=%d elapsed_ms=%s",
            request_id,
            request.method,
            request.url.path,
            response.status_code,
            elapsed_ms,
        )
        response.headers["X-Request-ID"] = request_id

        return response
