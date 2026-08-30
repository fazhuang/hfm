"""Phase-2 invariant-supersession verifier tests (governance amendment
correction round).

Covers the hardened contract: strict schema (unknown/duplicate fields,
unknown class/status, malformed records), mechanical declared-count
reconciliation, authority semantic validation, baseline identity/ancestry,
supersession graph with active-terminal resolution, machine-executed
historical replay and replacement tests, and future-evolution (0014->0015)
generality with synthetic fixtures.
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

P200 = "bd0d39e76fe5a8289006664514af9250a7f84f14"  # P2-00 acceptance baseline
P205 = "b53c897cfffd287516ecb1ed230df2f8f83687d9"  # P2-05 migration commit
F2 = "d38f871a230ca56713737b7de82f9111e7e73650"  # corrected frontier-2 candidate
REPLACEMENT = "apps/backend/tests/test_phase2_media.py::test_p2_current_migration_head_0014"
AUTHORITY_DOC = "docs/governance/HFM-PHASE2-WORK-PACKAGE-CONTRACT-v1.md"


def _entry(
    assertion_id: str = "ASN-TEST-0001",
    cls: str = "H",
    status: str = "SUPERSEDED",
    superseded_by: str = "ASN-TEST-0002",
    replacement: str = REPLACEMENT,
    replay_base: str = P200,
    effective: str = P205,
    authority_id: str = "P2-05",
    authority_doc: str = AUTHORITY_DOC,
    authority_type: str = "WP_CONTRACT",
    **overrides: str,
) -> dict[str, str]:
    fields: dict[str, str] = {
        "ASSERTION_ID": assertion_id,
        "CLASS": cls,
        "STATUS": status,
        "HISTORICAL_TEST": "apps/backend/tests/some_test.py::test_x",
        "INTRODUCED_AT_BASELINE": P200,
        "INTRODUCED_AT_ROLE": "SYNTHETIC",
        "HISTORICAL_EXPECTATION": "snapshot expectation",
        "SUPERSEDED_BY_ASSERTION_ID": superseded_by,
        "AUTHORITY_TYPE": authority_type,
        "AUTHORITY_ID": authority_id,
        "AUTHORITY_DOCUMENT": authority_doc,
        "AUTHORITY_LOCATOR": "## P2-05 Media & Rights Lifecycle",
        "AUTHORITY_RULE": "ALLOWED_MODULE",
        "AUTHORITY_VALUE": "apps/backend/alembic/versions/00XX_p2_*",
        "EFFECTIVE_FROM": effective,
        "CURRENT_REPLACEMENT_TEST": replacement,
        "REPLAY_BASELINE": replay_base,
        "REPLAY_BASELINE_ROLE": "SYNTHETIC",
        "REPLAY_KIND": "PYTEST",
        "REPLAY_TEST": "tests/test_phase2_guardrails.py",
        "RATIONALE": "test rationale",
    }
    base_lower = {key.lower(): key for key in fields}
    for key, value in overrides.items():
        target = base_lower.get(key.lower())
        if target is not None:
            fields[target] = value
        else:
            fields[key] = value
    return fields


def _active_c(
    cls: str = "C", assertion_id: str = "ASN-TEST-0002", replacement: str = REPLACEMENT
) -> dict[str, str]:
    return {
        "ASSERTION_ID": assertion_id,
        "CLASS": cls,
        "STATUS": "ACTIVE",
        "HISTORICAL_TEST": "N/A",
        "INTRODUCED_AT_BASELINE": P205,
        "INTRODUCED_AT_ROLE": "SYNTHETIC",
        "HISTORICAL_EXPECTATION": "N/A",
        "SUPERSEDED_BY_ASSERTION_ID": "N/A",
        "AUTHORITY_TYPE": "N/A",
        "AUTHORITY_ID": "N/A",
        "AUTHORITY_DOCUMENT": "N/A",
        "AUTHORITY_LOCATOR": "N/A",
        "AUTHORITY_RULE": "N/A",
        "AUTHORITY_VALUE": "N/A",
        "EFFECTIVE_FROM": P205,
        "CURRENT_REPLACEMENT_TEST": replacement,
        "REPLAY_BASELINE": "N/A",
        "REPLAY_BASELINE_ROLE": "N/A",
        "REPLAY_KIND": "N/A",
        "REPLAY_TEST": "N/A",
        "RATIONALE": "current-state replacement",
    }


def _register_file(
    tmp_path: Path, entries: list[dict[str, str]], declared: dict[str, int] | None = None
) -> Path:
    lines = ["# Synthetic register"]
    for entry in entries:
        lines.append("")
        lines.append(f"### {entry['ASSERTION_ID']}")
        lines.append("```")
        for key, value in entry.items():
            lines.append(f"{key}: {value}")
        lines.append("```")
    if declared is not None:
        lines.append("")
        lines.append("## Accounting")
        lines.append("```")
        for decl_key, decl_value in declared.items():
            lines.append(f"{decl_key}: {decl_value}")
        lines.append("```")
    path = tmp_path / "register.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def _pair(tmp_path: Path, **overrides: str) -> Path:
    return _register_file(tmp_path, [_entry(**overrides), _active_c()])


def _run(register: Path) -> Any:
    return verifier.validate(REPO_ROOT, register)


# ---- valid registers ---------------------------------------------------------


def test_valid_register_passes(tmp_path: Path) -> None:
    report = _run(_pair(tmp_path))
    assert report.ok, report.errors


def test_real_register_validate_passes() -> None:
    register = (
        REPO_ROOT / "docs" / "governance" / "HFM-PHASE2-INVARIANT-SUPERSESSION-REGISTER-v1.md"
    )
    report = _run(register)
    assert report.ok, report.errors


# ---- P1-01 declared-count reconciliation -------------------------------------


def test_declared_count_mismatch_fails(tmp_path: Path) -> None:
    register = _register_file(
        tmp_path,
        [_entry(), _active_c()],
        declared={
            "DECLARED_TOTAL": 99,
            "DECLARED_CLASS_H": 3,
            "DECLARED_CLASS_P": 0,
            "DECLARED_CLASS_C": 1,
            "DECLARED_CLASS_B": 0,
            "DECLARED_CLASS_A": 0,
            "DECLARED_ACTIVE": 1,
            "DECLARED_SUPERSEDED": 3,
        },
    )
    report = _run(register)
    assert not report.ok
    assert any("declared total 99" in e for e in report.errors)


# ---- strict schema (P1-06) ---------------------------------------------------


def test_missing_required_field_fails(tmp_path: Path) -> None:
    entry = _entry()
    del entry["RATIONALE"]
    report = _run(_register_file(tmp_path, [entry, _active_c()]))
    assert not report.ok
    assert any("missing required field" in e for e in report.errors)


def test_unknown_field_fails(tmp_path: Path) -> None:
    entry = _entry()
    entry["BOGUS_FIELD"] = "x"
    report = _run(_register_file(tmp_path, [entry, _active_c()]))
    assert not report.ok
    assert any("unknown fields" in e for e in report.errors)


def test_duplicate_field_fails(tmp_path: Path) -> None:
    entry = _entry()
    entry["RATIONALE"] = "first"
    lines = ["# Synthetic register", "", "### ASN-TEST-0001", "```"]
    for key, value in entry.items():
        lines.append(f"{key}: {value}")
    lines.append("RATIONALE: second")
    lines.append("```")
    register = tmp_path / "register.md"
    register.write_text("\n".join(lines), encoding="utf-8")
    report = _run(register)
    assert not report.ok
    assert any("duplicate fields" in e for e in report.errors)


def test_unknown_class_fails(tmp_path: Path) -> None:
    report = _run(_pair(tmp_path, cls="X"))
    assert not report.ok
    assert any("unknown CLASS" in e for e in report.errors)


def test_unknown_status_fails(tmp_path: Path) -> None:
    report = _run(_pair(tmp_path, status="DONE"))
    assert not report.ok
    assert any("unknown STATUS" in e for e in report.errors)


# ---- P1-02 authority semantic validation --------------------------------------


def test_authority_document_missing_fails(tmp_path: Path) -> None:
    report = _run(_pair(tmp_path, authority_doc="docs/governance/NONEXISTENT.md"))
    assert not report.ok
    assert any("authority document not found" in e for e in report.errors)


def test_authority_id_missing_fails(tmp_path: Path) -> None:
    report = _run(_pair(tmp_path, authority_id="P2-NOPE"))
    assert not report.ok
    assert any("authority id 'P2-NOPE' not present" in e for e in report.errors)


def test_authority_unrelated_document_fails(tmp_path: Path) -> None:
    report = _run(
        _pair(
            tmp_path, authority_doc="docs/governance/HFM-PHASE2-CUSTOMER-DEPENDENCY-REGISTER-v1.md"
        )
    )
    assert not report.ok
    assert any(
        ("locator does not resolve" in e) or ("authority id 'P2-05' not present" in e)
        for e in report.errors
    )


def test_authority_disallowed_type_fails(tmp_path: Path) -> None:
    report = _run(_pair(tmp_path, authority_type="WORD_OF_MOUTH"))
    assert not report.ok
    assert any("disallowed authority type" in e for e in report.errors)


# ---- P1-03 baseline identity / ancestry ----------------------------------------


def test_valid_baseline_ancestry_passes(tmp_path: Path) -> None:
    report = _run(_pair(tmp_path))
    assert report.ok, report.errors  # P200 and P205 in ancestry order


def test_nonexistent_baseline_fails(tmp_path: Path) -> None:
    report = _run(_pair(tmp_path, replay_base="0" * 40))
    assert not report.ok
    assert any(("does not exist" in e) or ("not an ancestor" in e) for e in report.errors)


def test_unrelated_baseline_fails(tmp_path: Path) -> None:
    # F2 is valid but NOT an ancestor of effective P205 -> ancestry FAIL
    report = _run(_pair(tmp_path, replay_base=F2))
    assert not report.ok
    assert any("not an ancestor" in e for e in report.errors)


def test_role_identity_binding_fails(tmp_path: Path) -> None:
    # known role P2_00_ACCEPTANCE_BASELINE must be bound to bd0d39e
    entry = _entry()
    entry["INTRODUCED_AT_ROLE"] = "P2_00_ACCEPTANCE_BASELINE"
    entry["INTRODUCED_AT_BASELINE"] = F2  # wrong commit for the role
    report = _run(_register_file(tmp_path, [entry, _active_c()]))
    assert not report.ok
    assert any("bound to wrong commit" in e for e in report.errors)


# ---- P1-05 active terminal resolution -----------------------------------------


def test_active_terminal_resolution_passes(tmp_path: Path) -> None:
    report = _run(_pair(tmp_path))
    assert report.ok, report.errors  # ASN-TEST-0001 -> ASN-TEST-0002 (ACTIVE, Class C)


def test_missing_active_terminal_fails(tmp_path: Path) -> None:
    report = _run(_pair(tmp_path, superseded_by="ASN-MISSING"))
    assert not report.ok
    assert any("does not exist" in e for e in report.errors)


def test_inactive_terminal_fails(tmp_path: Path) -> None:
    terminal = _active_c()
    terminal["STATUS"] = "SUPERSEDED"
    register = _register_file(tmp_path, [_entry(superseded_by="ASN-TEST-0002"), terminal])
    report = _run(register)
    assert not report.ok
    assert any("inactive terminal" in e for e in report.errors)


def test_supersession_cycle_fails(tmp_path: Path) -> None:
    a = _entry(assertion_id="ASN-CYC-A", superseded_by="ASN-CYC-B")
    b = _entry(assertion_id="ASN-CYC-B", superseded_by="ASN-CYC-A")
    report = _run(_register_file(tmp_path, [a, b]))
    assert not report.ok
    assert any("cycle" in e for e in report.errors)


def test_class_p_supersession_fails(tmp_path: Path) -> None:
    report = _run(_pair(tmp_path, cls="P"))
    assert not report.ok
    assert any("P supersession attempt is forbidden" in e for e in report.errors)


def test_class_b_supersession_fails(tmp_path: Path) -> None:
    report = _run(_pair(tmp_path, cls="B"))
    assert not report.ok
    assert any("B supersession attempt is forbidden" in e for e in report.errors)


# ---- P1-07 future 0015 generality (synthetic) ---------------------------------


def test_future_0015_valid_fixture_passes(tmp_path: Path) -> None:
    """0014-class H -> authorized evolution -> 0015-class C replacement."""
    h = _entry(
        assertion_id="ASN-FUT-0014-H",
        superseded_by="ASN-FUT-0015-C",
        effective=F2,
        replay_base=P200,
    )
    c15 = _active_c(assertion_id="ASN-FUT-0015-C")
    register = _register_file(tmp_path, [h, c15])
    report = _run(register)
    assert report.ok, report.errors


def test_future_class_p_supersession_fails(tmp_path: Path) -> None:
    register = _register_file(
        tmp_path,
        [
            _entry(assertion_id="ASN-FUT-0014-H", superseded_by="ASN-FUT-P"),
            _active_c(assertion_id="ASN-FUT-P", cls="P"),
        ],
    )
    report = _run(register)
    assert not report.ok
    assert any(
        ("non-terminal class" in e) or ("P supersession attempt is forbidden" in e)
        for e in report.errors
    )


def test_future_missing_replacement_fails(tmp_path: Path) -> None:
    register = _register_file(
        tmp_path,
        [
            _entry(assertion_id="ASN-FUT-0014-H", superseded_by="ASN-FUT-0015-C"),
            _active_c(assertion_id="ASN-FUT-0015-C", replacement="N/A"),
        ],
    )
    report = _run(register)
    assert not report.ok
    assert any("lacks replacement test" in e for e in report.errors)


# ---- execution: historical replay (P1-04) --------------------------------------


def test_historical_replay_passes() -> None:
    """Machine-executed P2-00 replay at bd0d39e must exit 0."""
    report = AnyReport()
    verifier.execute_replays(REPO_ROOT, report, _real_register())
    assert report.errors == []
    assert report.replays_executed == 3


def test_historical_replay_failure_detected(tmp_path: Path) -> None:
    """Replay at a baseline where the historical test fails (0014 present)."""
    entry = _entry(
        assertion_id="ASN-FAIL-REPLAY",
        superseded_by="ASN-FAIL-TERM",
        replay_base=F2,  # valid commit; guardrails tests FAIL there (head 0014)
        effective=F2,
        replay_test="tests/test_phase2_guardrails.py",
    )
    register = _register_file(tmp_path, [entry, _active_c(assertion_id="ASN-FAIL-TERM")])
    report = AnyReport()
    verifier.execute_replays(REPO_ROOT, report, register)
    assert any("HISTORICAL_REPLAY_FAILURE" in e for e in report.errors)


# ---- execution: replacement tests (P1-05 hardening) ----------------------------


def test_replacement_test_passes() -> None:
    """Machine-executed replacement test of the real active terminal."""
    report = AnyReport()
    verifier.execute_replacements(REPO_ROOT, report, _real_register())
    assert report.errors == []
    assert report.replacements_executed >= 1


def test_replacement_test_failure_detected(tmp_path: Path) -> None:
    register = _register_file(
        tmp_path,
        [
            _active_c(
                assertion_id="ASN-FAIL-REPL",
                replacement="apps/backend/tests/test_phase2_media.py::test_nonexistent",
            )
        ],
    )
    report = AnyReport()
    verifier.execute_replacements(REPO_ROOT, report, register)
    assert any("REPLACEMENT_TEST_FAILURE" in e for e in report.errors)


# ---- P1-02 Round 2: exact clause binding --------------------------------------


def test_authority_exact_clause_passes(tmp_path: Path) -> None:
    """Correct document + correct ID + correct clause (real P2-05 locator)."""
    report = _run(_pair(tmp_path))
    assert report.ok, report.errors
    assert report.authority_bindings_validated == 1


def test_authority_wrong_clause_fails(tmp_path: Path) -> None:
    """Correct doc+ID but locator to a clause that does not authorize the rule."""
    entry = _entry()
    entry["AUTHORITY_LOCATOR"] = "## Accounting"
    report = _run(_register_file(tmp_path, [entry, _active_c()]))
    assert not report.ok
    assert any("authority rule" in e and "not satisfied" in e for e in report.errors)


def test_authority_token_elsewhere_fails(tmp_path: Path) -> None:
    """P2-05 token appears in the Accounting prose but no authorized clause there."""
    entry = _entry()
    entry["AUTHORITY_LOCATOR"] = "## Accounting"
    report = _run(_register_file(tmp_path, [entry, _active_c()]))
    assert not report.ok
    # token presence alone must not validate the authority
    assert not report.ok


def test_authority_unrelated_section_fails(tmp_path: Path) -> None:
    entry = _entry()
    entry["AUTHORITY_LOCATOR"] = "## P2-10 HFB Reuse Adjudication"
    report = _run(_register_file(tmp_path, [entry, _active_c()]))
    assert not report.ok
    assert any("not present inside" in e for e in report.errors)


def test_authority_ambiguous_locator_fails(tmp_path: Path) -> None:
    """A locator that no longer resolves exactly must FAIL (no prefix match)."""
    entry = _entry()
    entry["AUTHORITY_LOCATOR"] = "## P2-"  # no heading equals this exactly
    report = _run(_register_file(tmp_path, [entry, _active_c()]))
    assert not report.ok
    assert any("authority locator does not resolve" in e for e in report.errors)


def test_authority_missing_locator_fails(tmp_path: Path) -> None:
    entry = _entry()
    entry["AUTHORITY_LOCATOR"] = "N/A"
    report = _run(_register_file(tmp_path, [entry, _active_c()]))
    assert not report.ok
    assert any("supersession field AUTHORITY_LOCATOR missing or N/A" in e for e in report.errors)


def test_authority_wrong_value_fails(tmp_path: Path) -> None:
    entry = _entry()
    entry["AUTHORITY_VALUE"] = "apps/frontend/src"  # not authorized by P2-05
    report = _run(_register_file(tmp_path, [entry, _active_c()]))
    assert not report.ok
    assert any("authority rule" in e and "not satisfied" in e for e in report.errors)


# ---- P1-04 Round 2: portable archive replay ------------------------------------


def test_replay_uses_git_archive_no_worktree(tmp_path: Path) -> None:
    """The replay mechanism must not invoke git worktree (prohibition)."""
    entry = _entry(assertion_id="ASN-PORT", superseded_by="ASN-PORT-T", replay_base=P200)
    register = _register_file(tmp_path, [entry, _active_c(assertion_id="ASN-PORT-T")])

    original_run = verifier.subprocess.run
    calls: list[list[str]] = []

    def spy(args: list[str], **kwargs: Any) -> Any:
        calls.append(args)
        return original_run(args, **kwargs)

    verifier.subprocess.run = spy
    try:
        report = AnyReport()
        verifier.execute_replays(REPO_ROOT, report, register)
    finally:
        verifier.subprocess.run = original_run
    assert report.errors == []
    for argv in calls:
        assert "worktree" not in argv, f"git worktree invoked: {argv}"


def test_archive_replay_byte_identity_passes(tmp_path: Path) -> None:
    """Exported bytes match git show <baseline>:<path> (historical byte identity)."""
    import tempfile as _tf

    with _tf.TemporaryDirectory(prefix="hfm-bytes-") as tmp:
        dest = Path(tmp) / "tree"
        dest.mkdir()
        assert verifier.export_baseline(REPO_ROOT, P200, dest)
        test_file = dest / "apps" / "backend" / "tests" / "test_phase2_guardrails.py"
        assert test_file.is_file()
        assert verifier.verify_byte_identity(
            REPO_ROOT, P200, "apps/backend/tests/test_phase2_guardrails.py", test_file
        )


def test_archive_replay_byte_mismatch_fails(tmp_path: Path) -> None:
    import tempfile as _tf

    with _tf.TemporaryDirectory(prefix="hfm-bytes-") as tmp:
        dest = Path(tmp) / "tree"
        dest.mkdir()
        assert verifier.export_baseline(REPO_ROOT, P200, dest)
        test_file = dest / "apps" / "backend" / "tests" / "test_phase2_guardrails.py"
        tampered = tmp_path / "tampered.py"
        tampered.write_bytes(b"# tampered" + test_file.read_bytes())
        assert not verifier.verify_byte_identity(
            REPO_ROOT, P200, "apps/backend/tests/test_phase2_guardrails.py", tampered
        )


def test_historical_test_missing_detected(tmp_path: Path) -> None:
    """A replay test not present in the historical export must FAIL."""
    entry = _entry(
        assertion_id="ASN-MISS-TEST",
        superseded_by="ASN-MISS-T",
        replay_base=P200,
        replay_test="tests/test_phase2_media.py",  # does not exist at bd0d39e
    )
    register = _register_file(tmp_path, [entry, _active_c(assertion_id="ASN-MISS-T")])
    report = AnyReport()
    verifier.execute_replays(REPO_ROOT, report, register)
    assert any("historical test missing" in e for e in report.errors)


def test_replay_cleanup_no_leftovers(tmp_path: Path) -> None:
    """Replay temporary directories are removed (no /tmp/hfm-replay-* residue)."""
    import glob

    before = set(glob.glob("/tmp/hfm-replay-*"))
    entry = _entry(assertion_id="ASN-CLEAN", superseded_by="ASN-CLEAN-T", replay_base=P200)
    register = _register_file(tmp_path, [entry, _active_c(assertion_id="ASN-CLEAN-T")])
    report = AnyReport()
    verifier.execute_replays(REPO_ROOT, report, register)
    after = set(glob.glob("/tmp/hfm-replay-*"))
    assert report.errors == []
    assert after == before


# ---- P1-02 Round 3: exact locator matching (Codex finding) ---------------------


def test_locator_exact_match_passes(tmp_path: Path) -> None:
    """Exact authoritative heading resolves; register locator equals the heading."""
    report = _run(_pair(tmp_path))
    assert report.ok, report.errors


def test_locator_prefix_fails(tmp_path: Path) -> None:
    """Locator `## P2-05` must NOT resolve `## P2-05 Media & Rights Lifecycle`."""
    entry = _entry()
    entry["AUTHORITY_LOCATOR"] = "## P2-05"
    report = _run(_register_file(tmp_path, [entry, _active_c()]))
    assert not report.ok
    assert any("authority locator does not resolve" in e for e in report.errors)


def test_locator_similar_shorter_fails(tmp_path: Path) -> None:
    entry = _entry()
    entry["AUTHORITY_LOCATOR"] = "## P2-05 Media"
    report = _run(_register_file(tmp_path, [entry, _active_c()]))
    assert not report.ok
    assert any("authority locator does not resolve" in e for e in report.errors)


def test_locator_similar_longer_fails(tmp_path: Path) -> None:
    entry = _entry()
    entry["AUTHORITY_LOCATOR"] = "## P2-05 Media & Rights Lifecycle Extra"
    report = _run(_register_file(tmp_path, [entry, _active_c()]))
    assert not report.ok
    assert any("authority locator does not resolve" in e for e in report.errors)


def test_locator_missing_fails(tmp_path: Path) -> None:
    entry = _entry()
    entry["AUTHORITY_LOCATOR"] = "## P2-99 Nonexistent Section"
    report = _run(_register_file(tmp_path, [entry, _active_c()]))
    assert not report.ok
    assert any("authority locator does not resolve" in e for e in report.errors)


def test_locator_duplicate_exact_fails(tmp_path: Path) -> None:
    """Two identical authoritative headings make the locator ambiguous -> FAIL."""
    doc = tmp_path / "doc.md"
    doc.write_text(
        "# Synthetic\n"
        "## P2-05 Media & Rights Lifecycle\nAllowed Modules: x\n"
        "## P2-05 Media & Rights Lifecycle\nAllowed Modules: y\n",
        encoding="utf-8",
    )
    block, ambiguous = verifier.resolve_locator(doc, "## P2-05 Media & Rights Lifecycle")
    assert ambiguous is True
    # through validate() the duplicate exact locator must FAIL
    entry = _entry()
    entry["AUTHORITY_DOCUMENT"] = str(doc)
    entry["AUTHORITY_LOCATOR"] = "## P2-05 Media & Rights Lifecycle"
    report = _run(_register_file(tmp_path, [entry, _active_c()]))
    assert not report.ok
    assert any("ambiguous authority locator" in e for e in report.errors)


# ---- helpers -------------------------------------------------------------------


def _real_register() -> Path:
    return REPO_ROOT / "docs" / "governance" / "HFM-PHASE2-INVARIANT-SUPERSESSION-REGISTER-v1.md"


class AnyReport:
    """Minimal report stand-in for execution helpers."""

    def __init__(self) -> None:
        self.errors: list[str] = []
        self.replays_executed = 0
        self.replacements_executed = 0
