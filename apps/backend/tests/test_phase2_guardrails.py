"""Phase-2 P2-00 negative-boundary guardrail tests.

Proves P2-00-AC-02 (deferred/rejected leakage = 0, HFB runtime dependency =
0, unauthorized production migration = 0) and the failure-detection paths
with synthetic violating files (the scan roots are parameterized, so a
violation in a temp directory is always detected).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from hfm.phase2.guardrails import (
    GuardrailReport,
    run_guardrails,
    scan_forbidden_markers,
    scan_hfb_coupling,
    scan_migration_versions,
)

REPO_ROOT = Path(__file__).resolve().parents[3]


@pytest.fixture(scope="module")
def guardrails() -> GuardrailReport:
    return run_guardrails(REPO_ROOT)


def test_frozen_boundary_states(guardrails: GuardrailReport) -> None:
    assert guardrails.clinical == "REJECTED"
    assert guardrails.ai == "DEFERRED"
    assert guardrails.display == "DEFERRED"
    assert guardrails.xr == "DEFERRED"
    assert guardrails.credential_migration == "DO_NOT_MIGRATE"
    assert guardrails.production_hfb_import == "NOT AUTHORIZED"
    assert guardrails.m4_m7 == "NOT AUTHORIZED"
    assert guardrails.ok


def test_hfb_zero_coupling_repo_wide(guardrails: GuardrailReport) -> None:
    # Line-anchored import scan over apps/backend/src and apps/backend/tests.
    assert guardrails.hfb_coupling_findings == ()
    assert guardrails.hfb_coupling_clean


def test_no_forbidden_markers_on_phase2_surface(guardrails: GuardrailReport) -> None:
    # The verifier's own vocabulary file is excluded from the marker scan.
    assert guardrails.forbidden_marker_findings == ()
    assert guardrails.marker_clean


def test_adr_gates_satisfied(guardrails: GuardrailReport) -> None:
    assert guardrails.accepted_adrs == frozenset({"ADR-P2-01", "ADR-P2-02"})
    assert guardrails.adr_gates == {"P2-05": "ADR-P2-01", "P2-07": "ADR-P2-02"}
    assert guardrails.adr_gate_violations == ()


def test_migration_invariant(guardrails: GuardrailReport) -> None:
    # Single head 0013; exactly 13 revisions; no 0014.
    assert guardrails.migration_ok
    assert "0013" in guardrails.migration_heads
    assert "0014" not in guardrails.migration_revisions
    assert len(guardrails.migration_heads) == 1


# --- failure detection paths ------------------------------------------------------


def test_hfb_import_detected(tmp_path: Path) -> None:
    src = tmp_path / "violation.py"
    src.write_text("from hfb.evidence import x\nimport hfb.models\n", encoding="utf-8")
    findings = scan_hfb_coupling(tmp_path)
    assert "violation.py" in findings


def test_hfb_import_not_flagged_inside_string(tmp_path: Path) -> None:
    src = tmp_path / "assertion.py"
    src.write_text('assert "from hfb" not in text\n', encoding="utf-8")
    assert scan_hfb_coupling(tmp_path) == ()


def test_forbidden_ai_import_detected(tmp_path: Path) -> None:
    src = tmp_path / "ai.py"
    src.write_text("import torch\n", encoding="utf-8")
    findings = scan_forbidden_markers(tmp_path)
    assert findings and "forbidden-import" in findings[0]


def test_forbidden_xr_import_detected(tmp_path: Path) -> None:
    src = tmp_path / "xr.py"
    src.write_text("from webxr import session\n", encoding="utf-8")
    findings = scan_forbidden_markers(tmp_path)
    assert findings and "forbidden-import" in findings[0]


def test_clinical_surface_detected(tmp_path: Path) -> None:
    src = tmp_path / "clinical.py"
    src.write_text("def acupoint_recommend() -> None:\n    pass\n", encoding="utf-8")
    findings = scan_forbidden_markers(tmp_path)
    assert findings and "clinical-surface" in findings[0]


def test_production_import_detected(tmp_path: Path) -> None:
    src = tmp_path / "importer.py"
    src.write_text("execute_production_import(snapshot)\n", encoding="utf-8")
    findings = scan_forbidden_markers(tmp_path)
    assert findings and "production-import" in findings[0]


def test_credential_migration_detected(tmp_path: Path) -> None:
    src = tmp_path / "auth.py"
    src.write_text("migrate_password_hash(users)\n", encoding="utf-8")
    findings = scan_forbidden_markers(tmp_path)
    assert findings and "credential-migration" in findings[0]


def test_verifier_files_excluded_from_marker_scan(tmp_path: Path) -> None:
    # The verifier declares the forbidden vocabulary; it must not self-trigger.
    src = tmp_path / "guardrails.py"
    src.write_text("CLINICAL_STATE = 'REJECTED'\n", encoding="utf-8")
    findings = scan_forbidden_markers(tmp_path, excluded=frozenset({"guardrails.py"}))
    assert findings == ()


def test_migration_head_detection(tmp_path: Path) -> None:
    versions = tmp_path / "versions"
    versions.mkdir()
    for rev, down in (("0012", "0011"), ("0013", "0012")):
        (versions / f"{rev}.py").write_text(
            f'revision = "{rev}"\ndown_revision = "{down}"\n', encoding="utf-8"
        )
    revisions, heads = scan_migration_versions(versions)
    assert revisions == ("0012", "0013")
    assert heads == ("0013",)
