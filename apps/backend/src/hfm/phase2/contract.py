"""Phase-2 contract verifier orchestrator (P2-00).

Ties the scope taxonomy, cross-document traceability, DAG structure,
negative-boundary guardrails, HFB zero-coupling, migration state, and the
fixture-based acceptance policy into one machine-verifiable contract report
(P2-00-AC-01 / P2-00-AC-02 / P2-00-AC-03).

Read-only: parses the frozen Phase-2 governance contracts; mutates nothing.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from hfm.phase2.guardrails import GuardrailReport, run_guardrails
from hfm.phase2.scope import ScopeRegister, parse_scope_register
from hfm.phase2.traceability import TraceReport, build_trace_report

#: AC rows whose frozen criterion text explicitly permits fixture usage.
_FIXTURE_AC_RE = re.compile(r"^\| (P2-\d{2}) \| (P2-\d{2}-AC-\d{2}) \| [^|]*fixture", re.I | re.M)


@dataclass(frozen=True)
class FixturePolicy:
    """Fixture-based acceptance policy state (P2-00-AC-03)."""

    documented: bool
    policy_path: str
    fixture_permitted_acs: tuple[str, ...]

    @property
    def applied_to_at_least_one_wp_ac(self) -> bool:
        return bool(self.fixture_permitted_acs)

    @property
    def ok(self) -> bool:
        return self.documented and self.applied_to_at_least_one_wp_ac


@dataclass(frozen=True)
class VerificationReport:
    """Aggregate contract-verifier output."""

    repo_root: Path
    scope: ScopeRegister
    trace: TraceReport
    guardrails: GuardrailReport
    fixture: FixturePolicy

    @property
    def ok(self) -> bool:
        return self.scope.valid and self.trace.ok and self.guardrails.ok and self.fixture.ok

    def summary(self) -> dict[str, object]:
        """Compact machine-readable closure counts."""
        return {
            "scope_count": self.scope.p2c_rows,
            "wp_count": self.trace.wp_count,
            "dag_node_count": self.trace.dag_node_count,
            "ac_count": self.trace.ac_count,
            "evidence_count": self.trace.evidence_count,
            "dod_count": self.trace.dod_count,
            "unmapped_scope": len(self.trace.unmapped_scope),
            "wp_without_dag": len(self.trace.wp_without_dag),
            "wp_without_ac": len(self.trace.wp_without_ac),
            "wp_without_evidence": len(self.trace.wp_without_evidence),
            "ac_without_evidence": len(self.trace.ac_without_evidence),
            "invalid_references": len(self.trace.invalid_references),
            "duplicate_ids": len(self.trace.duplicate_ids),
            "ok": self.ok,
        }


def default_repo_root() -> Path:
    """Repo root: <repo>/apps/backend/src/hfm/phase2 -> parents[5]."""
    return Path(__file__).resolve().parents[5]


def verify_fixture_policy(repo_root: Path, acceptance_path: Path) -> FixturePolicy:
    """P2-00-AC-03: policy documented and applied to >=1 frozen WP AC."""
    policy_path = repo_root / "docs" / "governance" / "HFM-PHASE2-FIXTURE-POLICY-v1.md"
    documented = policy_path.is_file()
    text = acceptance_path.read_text(encoding="utf-8")
    fixture_acs = tuple(sorted({m.group(2) for m in _FIXTURE_AC_RE.finditer(text)}))
    return FixturePolicy(
        documented=documented,
        policy_path=str(policy_path),
        fixture_permitted_acs=fixture_acs,
    )


def verify_phase2_contract(repo_root: Path | None = None) -> VerificationReport:
    """Run the full Phase-2 contract verification (P2-00 acceptance criteria)."""
    root = repo_root or default_repo_root()
    gov = root / "docs" / "governance"
    scope = parse_scope_register(gov / "HFM-PHASE2-SCOPE-REGISTER-v1.md")
    trace = build_trace_report(root, scope)
    guardrails = run_guardrails(root)
    fixture = verify_fixture_policy(root, gov / "HFM-PHASE2-ACCEPTANCE-CONTRACT-v1.md")
    return VerificationReport(
        repo_root=root,
        scope=scope,
        trace=trace,
        guardrails=guardrails,
        fixture=fixture,
    )
