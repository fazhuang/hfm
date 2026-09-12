"""Phase-2 P2-10 adjudication machine-parse evidence (P1-09 correction).

Binds the frozen E2-29 machine-parse requirement: the committed
HFM-PHASE2-HFB-REUSE-ADJUDICATION-v1.md register parses to exactly 27
classified items with the frozen taxonomy counts, zero unclassified, zero
duplicates, zero invalid taxonomy, zero missing required fields, and zero
runtime-coupling verdicts.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]

_spec = importlib.util.spec_from_file_location(
    "reuse_parser", REPO_ROOT / "scripts" / "check-reuse-adjudication.py"
)
assert _spec is not None
parser_module = importlib.util.module_from_spec(_spec)
sys.modules["reuse_parser"] = parser_module
_spec.loader.exec_module(parser_module)  # type: ignore[union-attr]
parser: Any = parser_module


@pytest.fixture(scope="module")
def report() -> Any:
    register = REPO_ROOT / "docs" / "governance" / "HFM-PHASE2-HFB-REUSE-ADJUDICATION-v1.md"
    return parser.parse_register(register)


def test_total_items(report: Any) -> None:
    assert report.total == 27


def test_taxonomy_counts_exact(report: Any) -> None:
    assert report.counts == {
        "PORT": 1,
        "ADAPT": 5,
        "REFERENCE_ONLY": 13,
        "DEFER": 5,
        "REJECT": 3,
    }


def test_no_unclassified(report: Any) -> None:
    assert report.unclassified == []
    assert report.invalid_taxonomy == []


def test_no_duplicate_item_ids(report: Any) -> None:
    assert report.duplicates == []


def test_required_fields_present(report: Any) -> None:
    assert report.missing_fields == []


def test_no_runtime_coupling_verdicts(report: Any) -> None:
    assert report.runtime_coupling == []


def test_register_ok(report: Any) -> None:
    assert report.ok
