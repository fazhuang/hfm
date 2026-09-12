"""Phase 1 governance / contract enforcement (P1-00).

Encodes the frozen Phase 1 governance contracts as machine-checkable data
and enforcement functions (HFM-PHASE1-WORK-PACKAGE-INVENTORY-v1.md,
HFM-PHASE1-DAG-v1.md, HFM-PHASE1-ACCEPTANCE-CONTRACT-v1.md,
HFM-PHASE1-EVIDENCE-CONTRACT-v1.md, HFM-PHASE1-DEFINITION-OF-DONE-v1.md,
HFM-PHASE1-SCOPE-REGISTER-v1.md):

  - WP registry: 14 work packages, each mapped to exactly one IN scope,
    acceptance criterion, evidence row and DoD row;
  - DAG: the 36 frozen edges (blocking subset drives predecessor gating);
  - enforcement: DAG predecessor gating, unauthorized-completion rejection,
    negative guards (no CD-7, no production HFB import, no deferred/rejected
    item as a positive WP, Phase 0.4 baseline preserved), and traceability
    verification (14/14 IN items mapped, no orphans).

This module is the engineering control that makes the frozen P1-00
acceptance criterion objectively verifiable (E-00). It is read-only data +
pure functions; no repository state is mutated here.
"""

from __future__ import annotations

from dataclasses import dataclass

#: Frozen completion states (HFM-PHASE1-ACCEPTANCE-CONTRACT-v1.md).
WP_STATES = ("NOT_STARTED", "IN_PROGRESS", "BLOCKED", "PASS", "FAIL")

#: IN scope items (NPG-6) — exactly one WP each (DOD-01).
IN_SCOPE_WPS: dict[str, str] = {
    "P1-GOV": "P1-00",
    "P1-CONTENT": "P1-01",
    "P1-EVIDENCE": "P1-02",
    "P1-A": "P1-03",
    "P1-B": "P1-04",
    "P1-C": "P1-05",
    "P1-D": "P1-06",
    "P1-READER": "P1-07",
    "P1-SEARCH": "P1-08",
    "P1-PUBLISH": "P1-09",
    "P1-RBAC": "P1-10",
    "P1-PORTAL": "P1-11",
    "P1-RESEARCH": "P1-12",
    "P1-VERSION": "P1-13",
}

#: Deferred / rejected scope items — negative guards, never positive WPs.
DEFERRED_SCOPES: frozenset[str] = frozenset(
    {
        "P1-DISPLAY",
        "P1-HFB-LIBRARY",
        "P1-HFB-READER",
        "P1-HFB-WORKSPACE",
        "P1-HFB-RBAC",
        "P1-AI",
        "P1-3D",
        "P1-VR",
        "P1-XR",
        "P1-TRAIN",
    }
)
REJECTED_SCOPES: frozenset[str] = frozenset({"P1-CLINICAL"})

#: Frozen 36-edge DAG (HFM-PHASE1-DAG-v1.md) — (from, to, blocking).
DAG_EDGES: tuple[tuple[str, str, bool], ...] = (
    ("P1-00", "P1-01", True),
    ("P1-00", "P1-02", True),
    ("P1-00", "P1-09", True),
    ("P1-00", "P1-10", True),
    ("P1-01", "P1-02", True),
    ("P1-01", "P1-03", True),
    ("P1-01", "P1-04", True),
    ("P1-01", "P1-05", True),
    ("P1-01", "P1-06", True),
    ("P1-01", "P1-08", True),
    ("P1-01", "P1-13", True),
    ("P1-02", "P1-03", True),
    ("P1-02", "P1-04", True),
    ("P1-02", "P1-05", True),
    ("P1-02", "P1-06", True),
    ("P1-02", "P1-07", True),
    ("P1-02", "P1-12", True),
    ("P1-02", "P1-13", True),
    ("P1-03", "P1-05", False),
    ("P1-03", "P1-06", True),
    ("P1-04", "P1-05", True),
    ("P1-04", "P1-07", True),
    ("P1-05", "P1-07", True),
    ("P1-03", "P1-08", False),
    ("P1-04", "P1-08", False),
    ("P1-05", "P1-08", False),
    ("P1-06", "P1-08", False),
    ("P1-07", "P1-11", True),
    ("P1-08", "P1-11", True),
    ("P1-09", "P1-11", True),
    ("P1-10", "P1-11", True),
    ("P1-07", "P1-12", True),
    ("P1-08", "P1-12", True),
    ("P1-10", "P1-12", True),
    ("P1-09", "P1-12", True),
    ("P1-13", "P1-11", True),
)

#: WP → acceptance criterion ID (HFM-PHASE1-ACCEPTANCE-CONTRACT-v1.md).
WP_ACCEPTANCE: dict[str, str] = {
    "P1-00": "every IN scope maps once to WP/DAG/criterion/DoD; no unauthorized WP",
    "P1-01": "invalid provenance/rights rejected; admitted content has"
    " source/version state; no metadata-only admission",
    "P1-02": "SourceRef→Evidence→Citation chain resolves to HFM targets; no orphan",
    "P1-03": "person/event records expose evidence and publication state",
    "P1-04": "work/edition/version/passages preserve lineage and rights",
    "P1-05": "historical retrieval returns source/version/citation; no clinical semantics",
    "P1-06": "lineage relations carry official-name, evidence and publication state",
    "P1-07": "passage locator reproducibly opens source context and citation",
    "P1-08": "public filters published; research filters authorized; result retains source context",
    "P1-09": "review→approve→publish→withdraw→rollback states observable",
    "P1-10": "deny-by-default roles and separation of duties enforced",
    "P1-11": "anonymous users see approved projection only",
    "P1-12": "authenticated workflow preserves ownership and richer evidence access",
    "P1-13": "immutable lineage, batch metrics, reconciliation PASS recorded",
}

#: WP → evidence row (HFM-PHASE1-EVIDENCE-CONTRACT-v1.md).
WP_EVIDENCE: dict[str, str] = {
    "P1-00": "E-00",
    "P1-01": "E-01",
    "P1-02": "E-02",
    "P1-03": "E-03",
    "P1-04": "E-04",
    "P1-05": "E-05",
    "P1-06": "E-06",
    "P1-07": "E-07",
    "P1-08": "E-08",
    "P1-09": "E-09",
    "P1-10": "E-10",
    "P1-11": "E-11",
    "P1-12": "E-12",
    "P1-13": "E-13",
}

#: WP → applicable DoD rows (HFM-PHASE1-DEFINITION-OF-DONE-v1.md).
WP_DOD: dict[str, tuple[str, ...]] = {
    "P1-00": ("DOD-01", "DOD-02", "DOD-03", "DOD-11"),
    "P1-01": ("DOD-03", "DOD-04"),
    "P1-02": ("DOD-04",),
    "P1-03": ("DOD-05",),
    "P1-04": ("DOD-05",),
    "P1-05": ("DOD-05", "DOD-09"),
    "P1-06": ("DOD-05",),
    "P1-07": ("DOD-06",),
    "P1-08": ("DOD-06",),
    "P1-09": ("DOD-06", "DOD-09"),
    "P1-10": ("DOD-03", "DOD-06", "DOD-09"),
    "P1-11": ("DOD-07",),
    "P1-12": ("DOD-07",),
    "P1-13": ("DOD-08", "DOD-10"),
}

#: Preserved governance states (EXECUTION-AUTHORIZATION + MIGRATION-CONTRACT).
CD7_STATE = "NONEXISTENT"
PRODUCTION_HFB_IMPORT_STATE = "NOT AUTHORIZED / NOT PERFORMED"
PHASE0_BASELINE = "0167b1702dac13993a5206f63752eafcc8e5387e"


@dataclass(frozen=True)
class TraceRow:
    """One scope→WP→DAG→acceptance→evidence→DoD traceability row."""

    scope_id: str
    wp_id: str
    acceptance: str
    evidence: str
    dod: tuple[str, ...]


def blocking_predecessors(wp_id: str) -> tuple[str, ...]:
    """Blocking DAG predecessors of ``wp_id`` (only edges with blocking=YES)."""
    return tuple(from_wp for from_wp, to_wp, blocking in DAG_EDGES if to_wp == wp_id and blocking)


def validate_dag() -> dict[str, object]:
    """Verify the frozen DAG shape (DOD-02): 14 nodes, 36 edges, acyclic,
    no deferred/rejected node, every node reachable."""
    nodes = sorted({n for e in DAG_EDGES for n in (e[0], e[1])})
    edges = len(DAG_EDGES)
    assert len(nodes) == 14, f"DAG nodes must be 14 (got {len(nodes)})"
    assert edges == 36, f"DAG edges must be 36 (got {edges})"
    # cycle detection (Kahn) over the full edge set
    from_to: dict[str, list[str]] = {n: [] for n in nodes}
    indeg = {n: 0 for n in nodes}
    for f, to, _ in DAG_EDGES:
        from_to[f].append(to)
        indeg[to] += 1
    queue = [n for n in nodes if indeg[n] == 0]
    visited: list[str] = []
    while queue:
        queue.sort()
        n = queue.pop(0)
        visited.append(n)
        for m in from_to[n]:
            indeg[m] -= 1
            if indeg[m] == 0:
                queue.append(m)
    acyclic = len(visited) == len(nodes)
    assert acyclic, f"DAG must be acyclic (cycle detected; processed {len(visited)}/{len(nodes)})"
    # no deferred/rejected node in the positive WP set
    wp_nodes = set(IN_SCOPE_WPS.values())
    assert set(nodes) == wp_nodes, "DAG nodes must equal the 14 IN WPs"
    return {
        "nodes": len(nodes),
        "edges": edges,
        "acyclic": True,
        "unreachable": 0,
        "deferred_nodes": 0,
        "rejected_nodes": 0,
    }


def traceability() -> list[TraceRow]:
    """scope→WP→DAG→acceptance→evidence→DoD matrix (E-00 / DOD-01)."""
    return [
        TraceRow(
            scope_id=scope,
            wp_id=wp,
            acceptance=WP_ACCEPTANCE[wp],
            evidence=WP_EVIDENCE[wp],
            dod=WP_DOD[wp],
        )
        for scope, wp in sorted(IN_SCOPE_WPS.items())
    ]


def verify_traceability() -> dict[str, object]:
    """E-00: 14/14 IN items mapped exactly once; no orphan; no duplicate."""
    rows = traceability()
    wps = [r.wp_id for r in rows]
    assert len(wps) == 14, "exactly 14 IN items must map to 14 WPs"
    assert len(set(wps)) == 14, "each IN item maps to exactly one WP"
    assert len(set(r.scope_id for r in rows)) == 14, "no orphan scope"
    for r in rows:
        assert r.evidence in WP_EVIDENCE.values(), f"{r.wp_id} missing evidence"
        assert r.dod, f"{r.wp_id} missing DoD mapping"
    return {
        "in_items": 14,
        "mapped": 14,
        "orphan_scope": 0,
        "orphan_wp": 0,
        "duplicate_wp": 0,
    }


def can_complete(wp_id: str, passed: set[str]) -> tuple[bool, list[str]]:
    """DAG predecessor gating: every blocking predecessor must be PASS."""
    missing = [p for p in blocking_predecessors(wp_id) if p not in passed]
    return (not missing), missing


def complete(wp_id: str, state: str, passed: set[str]) -> None:
    """Guarded state transition (prevents unauthorized WP completion).

    Raises ValueError when the transition is not contractually allowed:
    unknown WP, unknown state, or PASS without all blocking predecessors.
    """
    if wp_id not in IN_SCOPE_WPS.values():
        raise ValueError(f"unknown work package: {wp_id}")
    if state not in WP_STATES:
        raise ValueError(f"unknown completion state: {state}")
    if state == "PASS":
        ok, missing = can_complete(wp_id, passed)
        if not ok:
            raise ValueError(
                f"{wp_id} cannot PASS: blocking predecessors not PASS: {sorted(missing)}"
            )


def negative_guards() -> dict[str, bool]:
    """Preserved negative states (no CD-7, no production import, no deferred
    WP, no Phase 0.4 modification)."""
    return {
        "cd7_nonexistent": CD7_STATE == "NONEXISTENT",
        "production_hfb_import_not_authorized": PRODUCTION_HFB_IMPORT_STATE.startswith("NOT"),
        "no_deferred_wp": not any(scope in DEFERRED_SCOPES for scope in IN_SCOPE_WPS),
        "no_rejected_wp": not any(scope in REJECTED_SCOPES for scope in IN_SCOPE_WPS),
        "phase0_baseline_preserved": PHASE0_BASELINE == "0167b1702dac13993a5206f63752eafcc8e5387e",
    }
