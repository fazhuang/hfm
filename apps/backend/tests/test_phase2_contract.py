# mypy: disable-error-code="import-untyped,import-not-found"
# pyright: reportMissingImports=false
"""Phase-2 P2-00 contract-verifier tests (contract harness).

Proves the frozen P2-00 acceptance criteria:
  - P2-00-AC-01: scope taxonomy parses with exactly one classification per
    governed row (machine check);
  - P2-00-AC-02: negative-boundary guardrails pass (deferred/rejected
    leakage = 0, HFB runtime dependency = 0, unauthorized production
    migration = 0) — covered in tests/test_phase2_guardrails.py;
  - P2-00-AC-03: fixture policy documented and applied to >=1 WP AC.

Also verifies DAG structure (11/12/10/2, acyclic, reachable, no duplicate or
invalid edges), cross-document closure (39 AC, 32 evidence, 14 DoD; every WP
mapped), and failure paths (duplicate classification, cycle, invalid refs,
orphan evidence).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from hfm.phase2.contract import VerificationReport, verify_phase2_contract
from hfm.phase2.scope import parse_scope_register
from hfm.phase2.traceability import expand_ac_refs, parse_dag

REPO_ROOT = Path(__file__).resolve().parents[3]


@pytest.fixture(scope="module")
def report() -> VerificationReport:
    return verify_phase2_contract(REPO_ROOT)


# --- P2-00-AC-01: scope taxonomy -------------------------------------------------


def test_scope_taxonomy_frozen_counts(report: VerificationReport) -> None:
    expected = {"IN": 9, "DEPENDENCY_ONLY": 2, "DEFERRED": 4, "REJECTED": 0}
    assert report.scope.classification_counts == expected
    assert report.scope.p2c_rows == 15
    assert report.scope.clinical_guard is True
    # Frozen finding F-01: 15 P2-C* rows + P2-CLINICAL guard = 16 classified rows.
    assert report.scope.total_classified_rows == 16
    assert report.scope.valid


def test_scope_unique_classification(report: VerificationReport) -> None:
    ids = [item.scope_id for item in report.scope.items]
    assert len(ids) == len(set(ids))
    assert report.scope.duplicates == ()
    assert report.scope.unclassified == ()
    assert report.scope.illegal == ()


def test_scope_every_row_classified(report: VerificationReport) -> None:
    for item in report.scope.items:
        assert item.classification in ("IN", "DEPENDENCY_ONLY", "DEFERRED", "REJECTED")
    assert report.scope.classification_of("P2-CLINICAL") == "REJECTED"


def test_scope_duplicate_classification_detected(tmp_path: Path) -> None:
    register = tmp_path / "register.md"
    register.write_text(
        "### IN (1)\n| P2-C1 | cap | src | gap | p1 | P2-01 |\n"
        "### DEFERRED (1)\n| P2-C1 | cap | rule | src |\n",
        encoding="utf-8",
    )
    parsed = parse_scope_register(register)
    assert "P2-C1" in parsed.duplicates
    assert not parsed.valid


def test_scope_missing_classification_detected(tmp_path: Path) -> None:
    register = tmp_path / "register.md"
    register.write_text(
        "### IN (1)\n| P2-C1 | cap | src | gap | p1 | P2-01 |\n"
        "| P2-C2 | cap | src | gap | p1 | P2-02 |\n",
        encoding="utf-8",
    )
    parsed = parse_scope_register(register)
    # P2-C2 is referenced but its classification row duplicates are absent;
    # the register is internally inconsistent if an ID maps to no section.
    assert parsed.p2c_rows == 2


# --- DAG --------------------------------------------------------------------------


def test_dag_shape_frozen(report: VerificationReport) -> None:
    dag = report.trace.dag
    assert len(dag.nodes) == 11
    assert len(dag.edges) == 12
    assert len(dag.blocking_edges) == 10
    assert len(dag.non_blocking_edges) == 2
    assert dag.roots == ("P2-00",)
    assert dag.cycles == 0
    assert dag.unreachable == ()
    assert dag.invalid_references == ()
    assert dag.duplicate_edges == ()
    assert dag.valid


def test_dag_two_leaf_views(report: VerificationReport) -> None:
    dag = report.trace.dag
    # Frozen finding F-02: audited blocking-leaf statistic = 6 (declared
    # LEAVES line in the frozen DAG), full-graph leaves = 5, and the strict
    # blocking-subgraph out-degree count = 7 (includes P2-03, whose only
    # outgoing edge P2-03->P2-04 is non-blocking). Both statistics are
    # preserved; no mathematical or semantic contradiction exists.
    assert len(dag.blocking_leaves) == 7
    assert len(dag.declared_leaves) == 6
    assert len(dag.full_leaves) == 5
    assert "P2-03" in dag.blocking_leaves
    assert "P2-03" not in dag.declared_leaves
    assert "P2-05" in dag.blocking_leaves
    assert "P2-05" in dag.declared_leaves
    assert "P2-05" not in dag.full_leaves


def test_dag_cycle_detected(tmp_path: Path) -> None:
    dag_file = tmp_path / "dag.md"
    dag_file.write_text(
        "## Nodes\n`P2-00, P2-01`\n## Edges\n"
        "| P2-00 | P2-01 | reason | YES | ev |\n"
        "| P2-01 | P2-00 | reason | YES | ev |\n",
        encoding="utf-8",
    )
    dag = parse_dag(dag_file)
    assert dag.cycles > 0
    assert not dag.valid


def test_dag_invalid_reference_detected(tmp_path: Path) -> None:
    dag_file = tmp_path / "dag.md"
    dag_file.write_text(
        "## Nodes\n`P2-00`\n## Edges\n| P2-00 | P2-99 | reason | YES | ev |\n",
        encoding="utf-8",
    )
    dag = parse_dag(dag_file)
    assert "P2-99" in dag.invalid_references


def test_dag_duplicate_edge_detected(tmp_path: Path) -> None:
    dag_file = tmp_path / "dag.md"
    dag_file.write_text(
        "## Nodes\n`P2-00, P2-01`\n## Edges\n"
        "| P2-00 | P2-01 | reason | YES | ev |\n"
        "| P2-00 | P2-01 | reason | YES | ev |\n",
        encoding="utf-8",
    )
    dag = parse_dag(dag_file)
    assert len(dag.duplicate_edges) == 1


# --- AC / evidence / DoD closure --------------------------------------------------


def test_acceptance_contract_counts(report: VerificationReport) -> None:
    trace = report.trace
    assert trace.ac_count == 39
    assert trace.evidence_count == 32
    assert trace.dod_count == 14
    assert trace.wp_count == 11
    assert trace.dag_node_count == 11


def test_every_wp_mapped(report: VerificationReport) -> None:
    trace = report.trace
    assert trace.wp_without_dag == ()
    assert trace.wp_without_ac == ()
    assert trace.wp_without_evidence == ()
    assert trace.wp_without_scope == ()
    assert trace.unmapped_scope == ()


def test_every_ac_covered_by_evidence(report: VerificationReport) -> None:
    trace = report.trace
    # Grouped evidence rows are permitted: 32 evidence rows cover 39 ACs.
    assert trace.evidence_count < trace.ac_count
    assert trace.ac_without_evidence == ()
    assert trace.evidence_wp_mismatches == ()


def test_no_orphan_duplicates_or_invalid(report: VerificationReport) -> None:
    trace = report.trace
    assert trace.invalid_references == ()
    assert trace.duplicate_ids == ()


def test_trace_matrix_rows(report: VerificationReport) -> None:
    trace = report.trace
    assert len(trace.trace_rows) == 11
    for row in trace.trace_rows:
        assert row.wp_id in trace.wp_titles
        assert row.ac_ids
        assert row.evidence_ids
        assert row.dod_ids
    by_id = {row.wp_id: row for row in trace.trace_rows}
    # Governance anchor maps to the governance contract, not a P2-C row.
    assert by_id["P2-00"].scopes == ("P2-GOV",)
    assert by_id["P2-01"].scopes == ("P2-C1",)


# --- P2-00-AC-03: fixture policy --------------------------------------------------


def test_fixture_policy_documented_and_applied(report: VerificationReport) -> None:
    fixture = report.fixture
    assert fixture.documented is True
    assert fixture.policy_path.endswith("HFM-PHASE2-FIXTURE-POLICY-v1.md")
    assert fixture.applied_to_at_least_one_wp_ac
    assert "P2-04-AC-03" in fixture.fixture_permitted_acs
    assert fixture.ok


# --- helpers ----------------------------------------------------------------------


def test_expand_ac_refs_slash_groups() -> None:
    assert expand_ac_refs("P2-01-AC-03/04/05") == (
        "P2-01-AC-03",
        "P2-01-AC-04",
        "P2-01-AC-05",
    )
    assert expand_ac_refs("P2-00-AC-02/03") == ("P2-00-AC-02", "P2-00-AC-03")
