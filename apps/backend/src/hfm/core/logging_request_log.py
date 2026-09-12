"""Structured request-lifecycle logging (P2-08 observability).

Emits one structured JSON record per request lifecycle point, deterministic
for a given request identity, so no request is silently lost (P2-08-AC-03).
Lives under the authorized ``core/logging*`` module glob (sibling of
``core/logging.py``).
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RequestLogRecord:
    """One request-lifecycle observation."""

    request_id: str
    method: str
    path: str
    status: int
    duration_ms: int
    event: str = "request.end"


def request_log_entry(record: RequestLogRecord) -> str:
    """Deterministic structured JSON entry for a request lifecycle event."""
    payload: dict[str, Any] = {
        "event": record.event,
        "request_id": record.request_id,
        "method": record.method,
        "path": record.path,
        "status": record.status,
        "duration_ms": record.duration_ms,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def log_request(logger: logging.Logger, record: RequestLogRecord) -> None:
    """Emit the structured request-lifecycle record (never silently dropped)."""
    logger.info(request_log_entry(record))
