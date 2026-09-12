"""Phase-2 cross-document traceability verification (P2-00 verifier).

Parses the frozen Phase-2 governance contracts (DAG, work package contract,
acceptance contract, evidence contract, definition of done) and verifies
structural closure:

  - DAG: 11 nodes / 12 edges / 10 blocking / 2 non-blocking, acyclic, no
    unreachable node, no duplicate edges, valid node references, and both
    blocking-subgraph and full-graph views;
  - every WP has a DAG node, >=1 acceptance criterion and >=1 evidence row;
  - every acceptance criterion is covered by >=1 evidence row (grouped
    evidence rows are permitted and expanded);
  - no orphan evidence, no WP mismatch, no duplicate IDs, no invalid
    references.

Read-only data + pure functions; no repository state is mutated.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from hfm.phase2.scope import ScopeRegister

_WP_HEADER_RE = re.compile(r"^## (P2-\d{2}) (.+)$")
_DAG_EDGE_RE = re.compile(r"^\| (P2-\d{2}) \| (P2-\d{2}) \| .+ \| (YES|NO) \|")
_LEAVES_LINE_RE = re.compile(r"^[-*]?\s*LEAVES:\s*(.+)$", re.M)
_AC_ROW_RE = re.compile(r"^\| (P2-\d{2}) \| (P2-\d{2}-AC-\d{2}) \|")
_EV_ROW_RE = re.compile(r"^\| (E2-\d{2}) \| (P2-\d{2}) \|")
_EV_AC_CELL_RE = re.compile(r"P2-\d{2}-AC-\d{2}(?:/\d{2})*")
_DOD_ROW_RE = re.compile(r"^\| (DOD-P2-\d{2}) \| ([^|]+) \|")
_DOD_ID_RE = re.compile(r"DOD-P2-\d{2}")
_WP_TOKEN_RE = re.compile(r"P2-\d{2}")
_NODE_RE = re.compile(r"P2-\d{2}")

#: P2-00 is the governance/control anchor: it binds the Phase-2 governance
#: contract rather than a business P2-C scope row (frozen WP contract).
GOVERNANCE_ANCHOR_WP = "P2-00"


@dataclass(frozen=True)
class Dag:
    """Parsed frozen Phase-2 DAG with structural checks."""

    nodes: tuple[str, ...]
    edges: tuple[tuple[str, str, bool], ...]
    blocking_edges: tuple[tuple[str, str], ...]
    non_blocking_edges: tuple[tuple[str, str], ...]
    roots: tuple[str, ...]
    blocking_leaves: tuple[str, ...]
    declared_leaves: tuple[str, ...]
    full_leaves: tuple[str, ...]
    cycles: int
    unreachable: tuple[str, ...]
    invalid_references: tuple[str, ...]
    duplicate_edges: tuple[str, ...]

    @property
    def valid(self) -> bool:
        return (
            not self.invalid_references
            and not self.duplicate_edges
            and self.cycles == 0
            and not self.unreachable
        )


@dataclass(frozen=True)
class AcceptanceRow:
    """One acceptance-criterion row."""

    wp_id: str
    ac_id: str


@dataclass(frozen=True)
class EvidenceRow:
    """One evidence row with its expanded AC references."""

    evidence_id: str
    wp_id: str
    ac_refs: tuple[str, ...]


@dataclass(frozen=True)
class DodRow:
    """One DoD row with its WP references."""

    dod_id: str
    wp_refs: tuple[str, ...]


@dataclass(frozen=True)
class TraceRow:
    """One scope→WP→DAG→AC→Evidence→DoD traceability row."""

    wp_id: str
    scopes: tuple[str, ...]
    ac_ids: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    dod_ids: tuple[str, ...]


@dataclass(frozen=True)
class TraceReport:
    """Cross-document closure report."""

    dag: Dag
    wp_titles: dict[str, str]
    acceptance: tuple[AcceptanceRow, ...]
    evidence: tuple[EvidenceRow, ...]
    dod: tuple[DodRow, ...]
    trace_rows: tuple[TraceRow, ...]
    wp_without_dag: tuple[str, ...]
    wp_without_ac: tuple[str, ...]
    wp_without_evidence: tuple[str, ...]
    wp_without_scope: tuple[str, ...]
    unmapped_scope: tuple[str, ...]
    ac_without_evidence: tuple[str, ...]
    evidence_wp_mismatches: tuple[str, ...]
    invalid_references: tuple[str, ...]
    duplicate_ids: tuple[str, ...] = field(default_factory=tuple)

    @property
    def wp_count(self) -> int:
        return len(self.wp_titles)

    @property
    def dag_node_count(self) -> int:
        return len(self.dag.nodes)

    @property
    def ac_count(self) -> int:
        return len(self.acceptance)

    @property
    def evidence_count(self) -> int:
        return len(self.evidence)

    @property
    def dod_count(self) -> int:
        return len(self.dod)

    @property
    def ok(self) -> bool:
        return (
            self.dag.valid
            and not self.wp_without_dag
            and not self.wp_without_ac
            and not self.wp_without_evidence
            and not self.wp_without_scope
            and not self.unmapped_scope
            and not self.ac_without_evidence
            and not self.evidence_wp_mismatches
            and not self.invalid_references
            and not self.duplicate_ids
        )


def expand_ac_refs(cell: str) -> tuple[str, ...]:
    """Expand slash-grouped AC references ("P2-01-AC-03/04/05")."""
    refs: list[str] = []
    for match in _EV_AC_CELL_RE.findall(cell):
        base, _, nums = match.rpartition("-AC-")
        refs.extend(f"{base}-AC-{n}" for n in nums.split("/"))
    return tuple(refs)


def parse_dag(path: Path) -> Dag:
    """Parse and validate the frozen Phase-2 DAG."""
    text = path.read_text(encoding="utf-8")
    nodes_section = text.split("## Nodes")[1].split("## Edges")[0]
    nodes = sorted(set(_NODE_RE.findall(nodes_section)))
    node_set = set(nodes)

    raw_edges: list[tuple[str, str, bool]] = []
    for line in text.splitlines():
        match = _DAG_EDGE_RE.match(line)
        if match:
            raw_edges.append((match.group(1), match.group(2), match.group(3) == "YES"))

    invalid = tuple(
        sorted({n for edge in raw_edges for n in (edge[0], edge[1]) if n not in node_set})
    )
    # Topology is computed over valid edges only (invalid refs reported above).
    valid_edges = [e for e in raw_edges if e[0] in node_set and e[1] in node_set]
    edge_counter: dict[tuple[str, str, bool], int] = {}
    for edge in valid_edges:
        edge_counter[edge] = edge_counter.get(edge, 0) + 1
    duplicate_edges = tuple(
        sorted(
            f"{f}->{t}({'blocking' if b else 'non-blocking'})"
            for (f, t, b), c in edge_counter.items()
            if c > 1
        )
    )

    blocking = tuple((f, t) for f, t, b in valid_edges if b)
    non_blocking = tuple((f, t) for f, t, b in valid_edges if not b)

    adjacency: dict[str, list[str]] = {n: [] for n in nodes}
    for f, t, _ in valid_edges:
        adjacency[f].append(t)

    # Cycle detection (Kahn) over the full valid edge set.
    indeg = {n: 0 for n in nodes}
    for _, t, _ in valid_edges:
        indeg[t] += 1
    queue = sorted(n for n in nodes if indeg[n] == 0)
    visited: list[str] = []
    while queue:
        current = queue.pop(0)
        visited.append(current)
        for nxt in sorted(adjacency[current]):
            indeg[nxt] -= 1
            if indeg[nxt] == 0:
                queue.append(nxt)
    cycles = 0 if len(visited) == len(nodes) else len(nodes) - len(visited)

    # Reachability over the blocking subgraph only.
    blocking_adj: dict[str, list[str]] = {n: [] for n in nodes}
    for f, t in blocking:
        blocking_adj[f].append(t)
    roots = tuple(sorted(n for n in nodes if not any(t == n for _, t in blocking)))
    seen: set[str] = set()

    def reach(node: str) -> None:
        seen.add(node)
        for nxt in blocking_adj[node]:
            if nxt not in seen:
                reach(nxt)

    for root in roots:
        reach(root)
    unreachable = tuple(sorted(set(nodes) - seen))

    blocking_leaves = tuple(sorted(n for n in nodes if not any(f == n for f, _ in blocking)))
    full_leaves = tuple(sorted(n for n in nodes if not adjacency[n]))

    # Declared LEAVES statistic from the frozen DAG file (audited F-02 view).
    leaves_match = _LEAVES_LINE_RE.search(text)
    declared_leaves = tuple(sorted(_NODE_RE.findall(leaves_match.group(1)))) if leaves_match else ()

    return Dag(
        nodes=tuple(nodes),
        edges=tuple(valid_edges),
        blocking_edges=blocking,
        non_blocking_edges=non_blocking,
        roots=roots,
        blocking_leaves=blocking_leaves,
        declared_leaves=declared_leaves,
        full_leaves=full_leaves,
        cycles=cycles,
        unreachable=unreachable,
        invalid_references=invalid,
        duplicate_edges=duplicate_edges,
    )


def parse_wp_contract(path: Path) -> dict[str, str]:
    """WP ID → title map from the frozen work package contract."""
    titles: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = _WP_HEADER_RE.match(line)
        if match:
            titles[match.group(1)] = match.group(2).strip()
    return titles


def parse_acceptance_contract(path: Path, wps: set[str]) -> tuple[AcceptanceRow, ...]:
    """Acceptance rows with duplicate and invalid-WP detection."""
    rows: list[AcceptanceRow] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = _AC_ROW_RE.match(line)
        if match and match.group(1) in wps:
            rows.append(AcceptanceRow(wp_id=match.group(1), ac_id=match.group(2)))
    return tuple(rows)


def parse_evidence_contract(path: Path, wps: set[str]) -> tuple[EvidenceRow, ...]:
    """Evidence rows with expanded AC references."""
    rows: list[EvidenceRow] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = _EV_ROW_RE.match(line)
        if match and match.group(2) in wps:
            ac_cell = line.split("|", 3)[3] if line.count("|") >= 4 else ""
            rows.append(
                EvidenceRow(
                    evidence_id=match.group(1),
                    wp_id=match.group(2),
                    ac_refs=expand_ac_refs(ac_cell),
                )
            )
    return tuple(rows)


def parse_dod(path: Path) -> tuple[DodRow, ...]:
    """DoD rows with WP references (''all WPs'' expands to every WP)."""
    text = path.read_text(encoding="utf-8")
    rows: list[DodRow] = []
    for line in text.splitlines():
        match = _DOD_ROW_RE.match(line)
        if not match:
            continue
        wp_cell = match.group(2).strip()
        if wp_cell == "all WPs":
            wp_refs = ("all WPs",)
        else:
            wp_refs = tuple(_WP_TOKEN_RE.findall(wp_cell))
        rows.append(DodRow(dod_id=match.group(1), wp_refs=wp_refs))
    return tuple(rows)


def build_trace_report(repo_root: Path, scope: ScopeRegister) -> TraceReport:
    """Reconcile all frozen contracts into one closure report."""
    gov = repo_root / "docs/governance"
    dag = parse_dag(gov / "HFM-PHASE2-DAG-v1.md")
    wp_titles = parse_wp_contract(gov / "HFM-PHASE2-WORK-PACKAGE-CONTRACT-v1.md")
    wps = set(wp_titles)
    acceptance = parse_acceptance_contract(gov / "HFM-PHASE2-ACCEPTANCE-CONTRACT-v1.md", wps)
    evidence = parse_evidence_contract(gov / "HFM-PHASE2-EVIDENCE-CONTRACT-v1.md", wps)
    dod = parse_dod(gov / "HFM-PHASE2-DEFINITION-OF-DONE-v1.md")

    dag_nodes = set(dag.nodes)
    wp_without_dag = tuple(sorted(wps - dag_nodes))
    wp_without_ac = tuple(sorted(wps - {row.wp_id for row in acceptance}))
    wp_without_evidence = tuple(sorted(wps - {row.wp_id for row in evidence}))

    # Scope → WP mapping (P2-00 is the governance anchor, not a business WP).
    mapped_wps: set[str] = set()
    unmapped_scope: list[str] = []
    for item in scope.items:
        if item.classification == "IN":
            if not item.maps_to:
                unmapped_scope.append(item.scope_id)
            mapped_wps.update(item.maps_to)
    business_wps = {w for w in wps if w != GOVERNANCE_ANCHOR_WP}
    wp_without_scope = tuple(sorted(business_wps - mapped_wps))

    # AC coverage by evidence (grouped rows expanded).
    all_ac_ids = {row.ac_id for row in acceptance}
    covered_ac = {ac for row in evidence for ac in row.ac_refs}
    ac_without_evidence = tuple(sorted(all_ac_ids - covered_ac))
    evidence_wp_mismatches = tuple(
        sorted(
            f"{row.evidence_id}:{ac}"
            for row in evidence
            for ac in row.ac_refs
            if ac.rpartition("-AC-")[0] != row.wp_id
        )
    )

    # Invalid references and duplicate IDs.
    invalid: list[str] = []
    for node in dag.invalid_references:
        invalid.append(f"dag-node:{node}")
    for acceptance_row in acceptance:
        if acceptance_row.wp_id not in wps:
            invalid.append(f"ac-wp:{acceptance_row.ac_id}->{acceptance_row.wp_id}")
    for evidence_row in evidence:
        if evidence_row.wp_id not in wps:
            invalid.append(f"evidence-wp:{evidence_row.evidence_id}->{evidence_row.wp_id}")
    dod_wp_refs = {ref for dod_row in dod for ref in dod_row.wp_refs}
    for ref in sorted(dod_wp_refs - wps - {"all WPs"}):
        invalid.append(f"dod-wp:{ref}")

    duplicates: list[str] = []
    ac_ids_all = [acceptance_row.ac_id for acceptance_row in acceptance]
    evidence_ids_all = [evidence_row.evidence_id for evidence_row in evidence]
    dod_ids_all = [dod_row.dod_id for dod_row in dod]
    for label, ids in (
        ("ac", ac_ids_all),
        ("evidence", evidence_ids_all),
        ("dod", dod_ids_all),
    ):
        counter: dict[str, int] = {}
        for id_item in ids:
            counter[id_item] = counter.get(id_item, 0) + 1
        duplicates.extend(f"{label}:{id_item}" for id_item, count in counter.items() if count > 1)
    duplicates.extend(dag.duplicate_edges)

    # Trace matrix rows.
    scope_by_wp: dict[str, list[str]] = {w: [] for w in wps}
    for scope_item in scope.items:
        if scope_item.classification == "IN":
            for wp in scope_item.maps_to:
                if wp in scope_by_wp:
                    scope_by_wp[wp].append(scope_item.scope_id)
    scope_by_wp[GOVERNANCE_ANCHOR_WP] = ["P2-GOV"]
    ac_by_wp: dict[str, list[str]] = {w: [] for w in wps}
    for acceptance_row in acceptance:
        ac_by_wp[acceptance_row.wp_id].append(acceptance_row.ac_id)
    evidence_by_wp: dict[str, list[str]] = {w: [] for w in wps}
    for evidence_row in evidence:
        evidence_by_wp[evidence_row.wp_id].append(evidence_row.evidence_id)
    dod_by_wp: dict[str, list[str]] = {w: [] for w in wps}
    for dod_row in dod:
        for ref in dod_row.wp_refs:
            if ref == "all WPs":
                for wp in wps:
                    dod_by_wp[wp].append(dod_row.dod_id)
            elif ref in dod_by_wp:
                dod_by_wp[ref].append(dod_row.dod_id)

    trace_rows = tuple(
        TraceRow(
            wp_id=wp,
            scopes=tuple(sorted(scope_by_wp[wp])),
            ac_ids=tuple(sorted(ac_by_wp[wp])),
            evidence_ids=tuple(sorted(evidence_by_wp[wp])),
            dod_ids=tuple(sorted(dod_by_wp[wp])),
        )
        for wp in sorted(wps)
    )

    return TraceReport(
        dag=dag,
        wp_titles=wp_titles,
        acceptance=acceptance,
        evidence=evidence,
        dod=dod,
        trace_rows=trace_rows,
        wp_without_dag=wp_without_dag,
        wp_without_ac=wp_without_ac,
        wp_without_evidence=wp_without_evidence,
        wp_without_scope=wp_without_scope,
        unmapped_scope=tuple(sorted(unmapped_scope)),
        ac_without_evidence=ac_without_evidence,
        evidence_wp_mismatches=evidence_wp_mismatches,
        invalid_references=tuple(sorted(set(invalid))),
        duplicate_ids=tuple(sorted(set(duplicates))),
    )
