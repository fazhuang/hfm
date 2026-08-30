"""Phase-2 invariant-supersession verifier tests (governance amendment).

Covers the supersession contract failure paths:
  - valid register PASS;
  - missing required field / duplicate ASSERTION_ID / Class P or B
    supersession / missing replacement / missing replay binding / invalid
    authority / supersession cycle -> FAIL.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]

_spec = importlib.util.spec_from_file_location(
    "supersession_verifier", REPO_ROOT / "scripts" / "verify-invariant-supersessions.py"
)
assert _spec is not None
verifier_module = importlib.util.module_from_spec(_spec)
sys.modules["supersession_verifier"] = verifier_module
_spec.loader.exec_module(verifier_module)  # type: ignore[union-attr]
verifier: Any = verifier_module

P200 = "bd0d39e76fe5a8289006664514af9250a7f84f14"
P205 = "b53c897cfffd287516ecb1ed230df2f8f83687d9"
REAL_TEST = "apps/backend/tests/test_phase2_media.py::test_p2_current_migration_head_0014"
AUTHORITY = (
    "HFM-PHASE2-WORK-PACKAGE-CONTRACT-v1.md (P2-05 allowed module alembic/versions/00XX_p2_*)"
)


def _entry(
    assertion_id: str = "ASN-TEST-0001",
    cls: str = "H",
    status: str = "SUPERSEDED",
    superseded_by: str = "ASN-TEST-0002",
    replacement: str = REAL_TEST,
    replay_base: str = P200,
    authority: str = AUTHORITY,
    **overrides: str,
) -> dict[str, str]:
    fields: dict[str, str] = {
        "ASSERTION_ID": assertion_id,
        "CLASS": cls,
        "HISTORICAL_TEST": "apps/backend/tests/some_test.py::test_x",
        "INTRODUCED_AT_BASELINE": P200,
        "HISTORICAL_EXPECTATION": "snapshot expectation",
        "SUPERSEDED_BY_ASSERTION_ID": superseded_by,
        "SUPERSEDING_AUTHORITY": authority,
        "EFFECTIVE_FROM": P205,
        "CURRENT_REPLACEMENT_TEST": replacement,
        "HISTORICAL_REPLAY_BASELINE": replay_base,
        "HISTORICAL_REPLAY_COMMAND": "pytest -q",
        "RATIONALE": "test rationale",
        "STATUS": status,
    }
    fields.update(overrides)
    return fields


def _register_file(tmp_path: Path, entries: list[dict[str, str]]) -> Path:
    lines = ["# Synthetic register"]
    for entry in entries:
        lines.append("")
        lines.append(f"### {entry['ASSERTION_ID']}")
        lines.append("```")
        for key, value in entry.items():
            lines.append(f"{key}: {value}")
        lines.append("```")
    path = tmp_path / "register.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def _run(register: Path) -> Any:
    return verifier.validate(REPO_ROOT, register)


def test_valid_register_passes(tmp_path: Path) -> None:
    register = _register_file(
        tmp_path,
        [
            _entry(replacement=REAL_TEST),
            _entry(
                assertion_id="ASN-TEST-0002",
                cls="C",
                status="ACTIVE",
                superseded_by="N/A",
                replacement=REAL_TEST,
            ),
        ],
    )
    report = _run(register)
    assert report.ok, report.errors


def test_real_register_passes() -> None:
    register = (
        REPO_ROOT / "docs" / "governance" / "HFM-PHASE2-INVARIANT-SUPERSESSION-REGISTER-v1.md"
    )
    report = _run(register)
    assert report.ok, report.errors


def test_missing_required_field_fails(tmp_path: Path) -> None:
    entry = _entry()
    del entry["RATIONALE"]
    report = _run(_register_file(tmp_path, [entry]))
    assert not report.ok
    assert any("missing required fields" in e for e in report.errors)


def test_duplicate_assertion_id_fails(tmp_path: Path) -> None:
    report = _run(_register_file(tmp_path, [_entry(), _entry()]))
    assert not report.ok
    assert any("duplicate ASSERTION_ID" in e for e in report.errors)


def test_class_p_supersession_fails(tmp_path: Path) -> None:
    report = _run(_register_file(tmp_path, [_entry(cls="P")]))
    assert not report.ok
    assert any("P supersession attempt is forbidden" in e for e in report.errors)


def test_class_b_supersession_fails(tmp_path: Path) -> None:
    report = _run(_register_file(tmp_path, [_entry(cls="B")]))
    assert not report.ok
    assert any("B supersession attempt is forbidden" in e for e in report.errors)


def test_missing_replacement_test_fails(tmp_path: Path) -> None:
    report = _run(_register_file(tmp_path, [_entry(replacement="apps/backend/tests/nope.py::x")]))
    assert not report.ok
    assert any("replacement test file not found" in e for e in report.errors)


def test_missing_replay_binding_fails(tmp_path: Path) -> None:
    report = _run(
        _register_file(
            tmp_path,
            [
                _entry(replay_base="N/A"),
                _entry(
                    assertion_id="ASN-TEST-0002",
                    cls="C",
                    status="ACTIVE",
                    superseded_by="N/A",
                    replacement=REAL_TEST,
                ),
            ],
        )
    )
    assert not report.ok
    assert any("replay baseline" in e for e in report.errors)


def test_invalid_authority_fails(tmp_path: Path) -> None:
    report = _run(_register_file(tmp_path, [_entry(authority="NONEXISTENT-FILE.md (x)")]))
    assert not report.ok
    assert any("authority file not found" in e for e in report.errors)


def test_supersession_cycle_fails(tmp_path: Path) -> None:
    a = _entry(assertion_id="ASN-CYC-A", superseded_by="ASN-CYC-B", replacement=REAL_TEST)
    b = _entry(assertion_id="ASN-CYC-B", superseded_by="ASN-CYC-A", replacement=REAL_TEST)
    report = _run(_register_file(tmp_path, [a, b]))
    assert not report.ok
    assert any("cycle" in e for e in report.errors)


def test_active_entry_cannot_carry_supersession(tmp_path: Path) -> None:
    report = _run(
        _register_file(
            tmp_path,
            [_entry(cls="C", status="ACTIVE", superseded_by="ASN-TEST-0002")],
        )
    )
    assert not report.ok
    assert any("active entry carries SUPERSEDED_BY" in e for e in report.errors)
