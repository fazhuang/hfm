"""Phase 1 P1-00 governance enforcement tests.

Proves the frozen P1-00 acceptance criterion (E-00 / DOD-01/02/11):
  - 14/14 IN scope items map exactly once to WP/DAG/criterion/evidence/DoD;
  - DAG shape: 14 nodes, 36 edges, acyclic, no deferred/rejected node;
  - DAG predecessor gating: PASS requires all blocking predecessors PASS;
  - unauthorized WP/state transitions are rejected;
  - negative guards: CD-7 NONEXISTENT, production HFB import NOT AUTHORIZED,
    no deferred/rejected item as a positive WP, Phase 0.4 baseline preserved.
"""

from __future__ import annotations

import pytest

from hfm.phase1.governance import (
    CD7_STATE,
    DAG_EDGES,
    DEFERRED_SCOPES,
    IN_SCOPE_WPS,
    PHASE0_BASELINE,
    REJECTED_SCOPES,
    WP_ACCEPTANCE,
    WP_DOD,
    WP_EVIDENCE,
    WP_STATES,
    blocking_predecessors,
    can_complete,
    complete,
    negative_guards,
    traceability,
    validate_dag,
    verify_traceability,
)


def test_dag_shape_frozen() -> None:
    result = validate_dag()
    assert result == {
        "nodes": 14,
        "edges": 36,
        "acyclic": True,
        "unreachable": 0,
        "deferred_nodes": 0,
        "rejected_nodes": 0,
    }


def test_traceability_14_of_14_no_orphan() -> None:
    result = verify_traceability()
    assert result == {
        "in_items": 14,
        "mapped": 14,
        "orphan_scope": 0,
        "orphan_wp": 0,
        "duplicate_wp": 0,
    }
    rows = traceability()
    assert len(rows) == 14
    assert {r.scope_id for r in rows} == set(IN_SCOPE_WPS)
    assert {r.wp_id for r in rows} == set(IN_SCOPE_WPS.values())
    for r in rows:
        assert r.evidence == WP_EVIDENCE[r.wp_id]
        assert r.dod == WP_DOD[r.wp_id]
        assert r.acceptance == WP_ACCEPTANCE[r.wp_id]


def test_dag_predecessor_gating() -> None:
    # P1-01 requires P1-00; P1-02 requires P1-00 and P1-01
    ok, missing = can_complete("P1-01", set())
    assert not ok and missing == ["P1-00"]
    ok, missing = can_complete("P1-01", {"P1-00"})
    assert ok and missing == []
    ok, missing = can_complete("P1-02", {"P1-00"})
    assert not ok and set(missing) == {"P1-01"}
    ok, missing = can_complete("P1-02", {"P1-00", "P1-01"})
    assert ok and missing == []


def test_initial_frontier_only_p1_00_and_p1_01() -> None:
    """P1-00 has no predecessor; P1-01 requires only P1-00 (executable
    frontier per EXECUTION-AUTHORIZATION)."""
    assert blocking_predecessors("P1-00") == ()
    assert blocking_predecessors("P1-01") == ("P1-00",)
    assert blocking_predecessors("P1-11") == (
        "P1-07",
        "P1-08",
        "P1-09",
        "P1-10",
        "P1-13",
    )


def test_unauthorized_completion_rejected() -> None:
    # P1-02 cannot PASS before P1-00 and P1-01 PASS
    with pytest.raises(ValueError, match="blocking predecessors"):
        complete("P1-02", "PASS", passed={"P1-00"})
    with pytest.raises(ValueError, match="blocking predecessors"):
        complete("P1-03", "PASS", passed={"P1-01"})  # P1-02 missing
    # P1-01 can PASS once P1-00 PASS
    complete("P1-01", "PASS", passed={"P1-00"})  # no raise
    # unknown WP / unknown state rejected
    with pytest.raises(ValueError, match="unknown work package"):
        complete("P1-99", "PASS", passed=set())
    with pytest.raises(ValueError, match="unknown completion state"):
        complete("P1-00", "DONE", passed=set())


def test_no_downstream_completion_without_chain() -> None:
    """Completing downstream WPs requires their full blocking chain."""
    for wp in ("P1-05", "P1-07", "P1-11", "P1-12", "P1-13"):
        with pytest.raises(ValueError, match="blocking predecessors"):
            complete(wp, "PASS", passed={"P1-00", "P1-01"})


def test_p1_09_gate_is_dag_blocking_only() -> None:
    """The frozen DAG gates P1-09 on P1-00 alone (36-edge contract); the
    inventory precondition column lists inputs, not DAG gates."""
    assert blocking_predecessors("P1-09") == ("P1-00",)
    complete("P1-09", "PASS", passed={"P1-00"})  # no raise
    # P1-11 additionally requires P1-13 (DAG edge P1-13→P1-11)
    with pytest.raises(ValueError, match="blocking predecessors"):
        complete("P1-11", "PASS", passed={"P1-07", "P1-08", "P1-09", "P1-10"})


def test_negative_guards() -> None:
    guards = negative_guards()
    assert all(guards.values())
    assert CD7_STATE == "NONEXISTENT"
    assert PHASE0_BASELINE == "0167b1702dac13993a5206f63752eafcc8e5387e"


def test_no_deferred_rejected_scope_is_positive_wp() -> None:
    assert not (DEFERRED_SCOPES & set(IN_SCOPE_WPS))
    assert not (REJECTED_SCOPES & set(IN_SCOPE_WPS))
    # clinical recommendation is REJECTED, never a WP
    assert "P1-CLINICAL" in REJECTED_SCOPES
    assert "P1-CLINICAL" not in IN_SCOPE_WPS


def test_dag_edges_all_reference_known_wps() -> None:
    wps = set(IN_SCOPE_WPS.values())
    for f, to, blocking in DAG_EDGES:
        assert f in wps and to in wps
        assert isinstance(blocking, bool)


def test_wp_states_contract() -> None:
    assert WP_STATES == ("NOT_STARTED", "IN_PROGRESS", "BLOCKED", "PASS", "FAIL")
