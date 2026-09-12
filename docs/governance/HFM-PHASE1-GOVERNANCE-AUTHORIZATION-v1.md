# HFM Phase 1 Governance Authorization v1

Status: `AUTHORIZED_FOR_PHASE_1_GOVERNANCE_BASELINE`  
Phase 0.4 Completion Baseline: `0167b1702dac13993a5206f63752eafcc8e5387e`  
Governance Candidate: `acbaa6815df4261cee986894d4ba29c1d3845d90`  
NPG-11 verdict: `AUTHORIZED_FOR_PHASE_1_GOVERNANCE_BASELINE`

## Frozen governance facts

```text
IN Scope: 14
Work Packages: 14
DAG: 14 nodes / 36 edges (31 blocking, 5 non-blocking)
Acceptance: 14
Evidence: 14
DoD: 12
P0 blockers: 0
```

PRE_IMPLEMENTATION_BLOCKING ADRs remain unresolved:

```text
ADR-01
ADR-02
ADR-05
ADR-06
ADR-07
```

No implementation depending on these ADRs may begin before independent resolution and acceptance.

## Invariants

- Production HFB Import: `NOT PERFORMED / NOT AUTHORIZED`.
- CD-7: `NONEXISTENT`.
- Deferred scope is unchanged: Display, HFB UI/Workspace/RBAC reuse, AI, 3D, VR, XR, Virtual Training.
- Rejected scope is unchanged: clinical acupuncture recommendation/treatment suggestion.
- The P2 correction is non-semantic and does not alter scope, architecture, DAG dependencies, acceptance, evidence, or DoD semantics.
- NPG-11 authorization is governance authorization only; it does not authorize implementation, migration, or production import.
