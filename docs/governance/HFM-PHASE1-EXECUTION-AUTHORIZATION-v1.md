# HFM Phase 1 Execution Authorization v1

Status: `PHASE_1_EXECUTION: AUTHORIZED`  
Governance baseline: `29c5b856f221a12bac9de13e1a5043c5d05208e2`  
Authorized scope: frozen 14-WP DAG, accepted ADR decisions, and existing acceptance/evidence contracts only.

## Authorization boundary

Execution is authorized only within the frozen Phase 1 governance contracts. It does not authorize production HFB Import, M5, deferred modules, rejected clinical recommendation/treatment semantics, CD-7, or scope expansion. Any change to Scope, Architecture Boundary, accepted ADRs, DAG, Acceptance, Evidence, or DoD requires an explicit governance amendment.

## Accepted ADR decisions

- ADR-01: single modular deployment with strict logical/security public-research separation.
- ADR-02: PostgreSQL native search with `pg_trgm`/GIN; no Elasticsearch requirement.
- ADR-05: explicit `/api/v1/public/*`, `/api/v1/research/*`, `/api/v1/admin/*` namespaces, independent public schemas, repository/service filtering.
- ADR-06: offline staged HFB adapter/migration, no HFB runtime dependency, M0–M7 governance.
- ADR-07: HFM-native identity/RBAC, default deny, no HFB credential migration.

## Initial executable frontier

`P1-00` and `P1-01` are the initial executable frontier. `P1-00` has no DAG predecessor; `P1-01` requires the governance predecessor and the accepted adapter contract. No downstream WP is executable merely because an ADR is accepted. Each later WP requires every DAG predecessor to be `PASS` and its own acceptance preconditions to be met.

## Preserved states

- Production HFB Import: `NOT PERFORMED / NOT AUTHORIZED`; M5 remains forbidden until an independent M4 authorization passes.
- CD-7: `NONEXISTENT`.
- Deferred: Display, HFB UI/Workspace/RBAC reuse, AI, 3D, VR, XR, Virtual Training.
- Rejected: clinical acupuncture recommendation/treatment suggestion.
- Phase 1 implementation agents may not bypass DAG, ADR, RBAC, evidence, publication, or change-control gates.
