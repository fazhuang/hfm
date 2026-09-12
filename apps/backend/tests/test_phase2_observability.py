# mypy: disable-error-code="import-untyped,import-not-found"
# pyright: reportMissingImports=false
"""Phase-2 P2-08 observability/release-gate tests.

Proves the frozen P2-08 acceptance criteria:
  - P2-08-AC-01 health/ready probes respond correctly (no false-healthy);
  - P2-08-AC-03 structured logs emitted on the request lifecycle.
"""

from __future__ import annotations

import io
import json
import logging

from hfm.core.logging_probes import probe_health, probe_ready
from hfm.core.logging_request_log import RequestLogRecord, log_request, request_log_entry


def test_ac01_health_probe_ok() -> None:
    result = probe_health()
    assert result.status == "ok"
    assert result.name == "health"


def test_ac01_ready_when_dependencies_ready() -> None:
    result = probe_ready(dependencies_ready=True, detail="database ok")
    assert result.status == "ok"


def test_ac01_no_false_healthy_when_dependency_down() -> None:
    result = probe_ready(dependencies_ready=False, detail="database down")
    assert result.status == "not_ready"


def test_ac03_structured_log_emitted_on_request_lifecycle() -> None:
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    logger = logging.getLogger("test.request_log")
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    logger.propagate = False
    try:
        record = RequestLogRecord(
            request_id="req-123",
            method="GET",
            path="/api/v1/public/home",
            status=200,
            duration_ms=12,
        )
        log_request(logger, record)
        emitted = stream.getvalue().strip()
        assert emitted
        parsed = json.loads(emitted)
        assert parsed["request_id"] == "req-123"
        assert parsed["method"] == "GET"
        assert parsed["status"] == 200
        assert parsed["event"] == "request.end"
    finally:
        logger.removeHandler(handler)


def test_ac03_structured_entry_deterministic() -> None:
    record = RequestLogRecord("req-1", "GET", "/x", 200, 5)
    assert request_log_entry(record) == request_log_entry(record)
