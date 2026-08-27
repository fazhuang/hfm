"""Tests for the structured logging utilities (migrated Batch 1 asset — PORT)."""

import json
import logging

from hfm.core.logging import ConsoleFormatter, JSONFormatter, configure_logging, get_logger


def _make_record(
    name: str = "hfm.test",
    level: int = logging.INFO,
    msg: str = "hello",
) -> logging.LogRecord:
    return logging.LogRecord(
        name=name,
        level=level,
        pathname=__file__,
        lineno=1,
        msg=msg,
        args=(),
        exc_info=None,
    )


def test_json_formatter_outputs_valid_json() -> None:
    out = JSONFormatter().format(_make_record())
    parsed = json.loads(out)
    assert parsed["level"] == "INFO"
    assert parsed["logger"] == "hfm.test"
    assert parsed["message"] == "hello"
    assert parsed["module"] == "test_logging"
    assert "timestamp" in parsed


def test_json_formatter_includes_exception() -> None:
    try:
        raise ValueError("bad value")
    except ValueError as exc:
        record = logging.LogRecord(
            name="hfm.test_exc",
            level=logging.ERROR,
            pathname=__file__,
            lineno=1,
            msg="boom",
            args=(),
            exc_info=(type(exc), exc, exc.__traceback__),
        )
    parsed = json.loads(JSONFormatter().format(record))
    assert parsed["exception"] == {"type": "ValueError", "message": "bad value"}


def test_console_formatter_contains_level_and_message() -> None:
    out = ConsoleFormatter().format(_make_record(level=logging.WARNING, msg="warn me"))
    assert "WARNING" in out
    assert "warn me" in out


def test_get_logger_and_configure_logging() -> None:
    logger = get_logger("hfm.config_test")
    assert logger.name == "hfm.config_test"
    configure_logging("DEBUG")
    root = logging.getLogger()
    assert root.level == logging.DEBUG
    assert len(root.handlers) >= 1
    configure_logging("INFO")
    assert root.level == logging.INFO
