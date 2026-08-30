"""HFM Phase 2 engineering controls (P2-00 contract verifier)."""

from __future__ import annotations

from hfm.phase2.contract import (
    FixturePolicy,
    VerificationReport,
    verify_fixture_policy,
    verify_phase2_contract,
)
from hfm.phase2.guardrails import GuardrailReport, run_guardrails
from hfm.phase2.scope import ScopeItem, ScopeRegister, parse_scope_register
from hfm.phase2.traceability import Dag, TraceReport, build_trace_report

__all__ = [
    "Dag",
    "FixturePolicy",
    "GuardrailReport",
    "ScopeItem",
    "ScopeRegister",
    "TraceReport",
    "VerificationReport",
    "build_trace_report",
    "parse_scope_register",
    "run_guardrails",
    "verify_fixture_policy",
    "verify_phase2_contract",
]
