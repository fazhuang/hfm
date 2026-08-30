# HFM Phase 2 Definition of Done v1

Status: GOVERNANCE CANDIDATE · READY FOR INDEPENDENT AUDIT · NOT IMPLEMENTATION AUTHORIZATION
Every DoD below is required for Phase-2 closure. No DoD is kept for padding; each maps to a real closure condition.

| DOD-ID | Scope provenance | Exact PASS condition |
| --- | --- | --- |
| DOD-P2-01 | P2-00 | 9/9 IN scope items have exactly one WP mapping, one DAG position, AC, evidence and DoD coverage; DEPENDENCY_ONLY items documented as non-WP tracks. |
| DOD-P2-02 | P2-00 | DAG has 11 nodes, 12 declared edges, zero cycles, zero unreachable nodes, and no numbering-based dependency. |
| DOD-P2-03 | all WPs | Every WP AC is binary PASS/FAIL and bound to a concrete artifact/test; no subjective AC text remains. |
| DOD-P2-04 | all WPs | Every WP has candidate-bound evidence (E2-00…E2-31) with command/result/commit; no evidence is a bare screenshot. |
| DOD-P2-05 | P2-01/03/04/06 | Frontend surfaces consume the accepted Phase-1 API contracts and backend contracts are unchanged; contract integrity tests pass. |
| DOD-P2-06 | P2-01/02/03 | Public/research separation holds in the UI: anonymous surface shows published projection only; research/admin require authentication; leakage negatives pass. |
| DOD-P2-07 | P2-02/09 | RBAC deny-by-default enforced in UI: role matrix, route guards, audit logging; escalation negatives pass. |
| DOD-P2-08 | P2-00 | Deferred/rejected scope leakage = 0 across Phase-2 modules (guardrail scan). |
| DOD-P2-09 | P2-10 | HFB runtime dependencies = 0 across Phase-2 modules; no verdict implies runtime coupling. |
| DOD-P2-10 | P2-05 | Media rights/provenance integrity: original vs derivative hash binding, rights-metadata fail-closed publication, withdrawal removes public projection. |
| DOD-P2-11 | P2-07 | Deployment reproducibility: env separation, secret boundary, migration gate, backup/restore verified on test env; release rollback procedure documented. |
| DOD-P2-12 | P2-08 | Observability/release gate: health/ready probes, structured logging, and automated release gates (lint+type+test+build) all PASS in CI. |
| DOD-P2-13 | P2-10/P2-07 | Migration authorization integrity: M0–M3 preparation stays within frozen contract bounds; M4/M5/M6/M7 not executed; production import NOT PERFORMED. |
| DOD-P2-14 | all WPs | Integrated product acceptance reproduces all criteria and negative evidence, records PASS/FAIL states, and closes the trace matrix with zero exceptions. |

## Accounting

- DoD total = 14 (DOD-P2-01 … DOD-P2-14)
- Each DoD maps to ≥1 WP and ≥1 evidence row (machine-checkable)
