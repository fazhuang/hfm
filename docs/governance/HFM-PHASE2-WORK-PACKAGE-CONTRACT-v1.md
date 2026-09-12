# HFM Phase 2 Work Package Contract v1

Status: GOVERNANCE CANDIDATE · READY FOR INDEPENDENT AUDIT · NO IMPLEMENTATION AUTHORIZATION
Phase-1 Completion Baseline: `c17be40be6f055498fde11c0042e71d3a1056a7c`
Each WP has an atomic acceptance boundary, explicit dependency structure, rollback independence, and evidence independence. No "big-bang" frontend WP exists.

## P2-00 Phase-2 Governance / Runtime Foundation

- **Purpose**: formalize the Phase-2 governance contract (scope binding, DAG, AC/Evidence/DoD contracts, ADR binding, fixture-based acceptance policy) and a machine-verifiable contract harness.
- **Authoritative Requirement Sources**: Phase-1 Completion Baseline; CR-001…CR-022; NPG-001; frozen Phase-1 governance conventions (DAG/AC/Evidence/DoD/ADR patterns).
- **Predecessors**: none (root). External input: Phase-1 completion baseline (accepted).
- **In Scope**: Phase-2 scope/DAG/AC/evidence/DoD contracts; ADR-P2-01/02 binding; negative-boundary guardrail checks; fixture-based acceptance policy; scope→WP→DAG→AC→evidence→DoD trace matrix.
- **Out of Scope**: business features; UI pages; migration execution; content population.
- **Allowed Modules**: `docs/governance/HFM-PHASE2-*`, `docs/governance/adr/HFM-PHASE2-*`, `apps/backend/tests/test_phase2_*` (contract-harness tests only), `apps/backend/src/hfm/phase2/` (contract-verifier runtime only).
- **Forbidden Boundaries**: no clinical/AI/3D/VR/XR/display semantics; no HFB runtime dependency; no production import; no identity/credential migration.
- **Acceptance Criteria**: P2-00-AC-01, P2-00-AC-02, P2-00-AC-03 (see Acceptance Contract).
- **Required Evidence**: E2-00…E2-01.
- **Negative Evidence**: zero deferred/rejected leakage in Phase-2 modules; zero HFB runtime imports.
- **DoD Contribution**: DOD-P2-01, DOD-P2-02, DOD-P2-08, DOD-P2-09.
- **Rollback / Failure Semantics**: governance-only WP; a failed contract check blocks the Phase-2 baseline, not runtime rollback.

## P2-01 Public Frontend Foundation

- **Purpose**: HFM-native anonymous-first public shell: routing, layout, design tokens, public-API client, error/empty/loading states, accessibility minimum, responsive behavior, published-projection-only rendering, media display slot.
- **Authoritative Requirement Sources**: CR-004/009/021; DR-001; G2; ADR-01/05; P1-11 (accepted).
- **Predecessors**: P2-00 (blocking). External: P1-11 API (accepted).
- **In Scope**: anonymous routing; public layout/navigation; design tokens (typography/spacing/color/radius per HFM tokens); public-API client (consumes `/api/v1/public/*`); error/empty/loading states; withdrawn-content behavior; responsive breakpoints; accessibility minimum; media display integration point (non-blocking).
- **Out of Scope**: research/auth surfaces; admin surfaces; media lifecycle implementation; content population; HFB UI wholesale inheritance.
- **Allowed Modules**: `apps/frontend/src/**` (public shell), design-system tokens, `apps/frontend/src/__tests__/**`.
- **Forbidden Boundaries**: no research/admin route reachable anonymously; no backend change beyond public-API consumption; no clinical semantics; no 3D/VR/XR.
- **Acceptance Criteria**: P2-01-AC-01…P2-01-AC-05.
- **Required Evidence**: E2-02…E2-04.
- **Negative Evidence**: anonymous access to research/admin routes denied (route-guard test); withdrawn content absent from public projection.
- **DoD Contribution**: DOD-P2-05, DOD-P2-06, DOD-P2-07.
- **Rollback / Failure Semantics**: UI-only; feature-flag or route-removal rollback; no data migration.

## P2-02 Research / Admin Frontend Foundation

- **Purpose**: authenticated research + admin shell: login, role-aware routing, admin/publication UI (review/approve/publish/withdraw/rollback), research workspace shell, audit-logged admin actions.
- **Authoritative Requirement Sources**: CR-002/003/009; DR-002; ADR-05/07; P1-10, P1-12, P1-09 (accepted).
- **Predecessors**: P2-00 (blocking). External: P1-10 RBAC API (accepted).
- **In Scope**: auth flow (login/logout/token, revocation handling); role-aware routing (deny-by-default); publication admin workflows; research workspace shell; audit-logged admin actions.
- **Out of Scope**: public surfaces; media lifecycle; export internals; credential migration.
- **Allowed Modules**: `apps/frontend/src/**` (research/admin shell), `apps/frontend/src/__tests__/**`.
- **Forbidden Boundaries**: no route reachable without authentication; no privilege escalation; no HFB RBAC inheritance.
- **Acceptance Criteria**: P2-02-AC-01…P2-02-AC-04.
- **Required Evidence**: E2-05…E2-07.
- **Negative Evidence**: unauthenticated redirect; role-mismatch denial; audit log entry on privileged action.
- **DoD Contribution**: DOD-P2-06, DOD-P2-07.
- **Rollback / Failure Semantics**: UI-only; token revocation honored; no data mutation outside audited workflows.

## P2-03 Reader / Search Frontend

- **Purpose**: locator-based reader surface (quotation, source context, citation/evidence context, rights, publication state) and role-scoped search surface, built on the public foundation.
- **Authoritative Requirement Sources**: CR-003/005; Gemini L/M; AB-09/10; P1-07, P1-08 (accepted).
- **Predecessors**: P2-01 (blocking).
- **In Scope**: reader surface (same-locator reproducibility, version/passage navigation); search surface (public filter = published only; research filter = authorized); empty/error/loading states; withdrawn/draft invisibility.
- **Out of Scope**: clinical recommendation semantics; relation-traversal features; media lifecycle.
- **Allowed Modules**: `apps/frontend/src/**` (reader/search surfaces), `apps/frontend/src/__tests__/**`.
- **Forbidden Boundaries**: no clinical output (diagnosis/treatment/prescription/ranking); no unauthorized draft/private display; no research leakage into anonymous view.
- **Acceptance Criteria**: P2-03-AC-01…P2-03-AC-04.
- **Required Evidence**: E2-08…E2-10.
- **Negative Evidence**: forbidden-term negative test; withdrawn-passage absence test.
- **DoD Contribution**: DOD-P2-05, DOD-P2-06.
- **Rollback / Failure Semantics**: UI-only; route removal rollback.

## P2-04 Heritage Visualization

- **Purpose**: evidence-bound lineage visualization (tree/timeline/network) for heritage transmission and cultural chronology, fed by the P1-06 relations API.
- **Authoritative Requirement Sources**: CR-006; Gemini N; G10; P1-06 (accepted).
- **Predecessors**: P2-01 (blocking); P2-03 (non-blocking drill-down integration).
- **In Scope**: lineage tree/timeline/network views; evidence-bound node display; unverified/private node hiding; empty-genealogy state; responsive behavior.
- **Out of Scope**: relation-data fabrication; genealogy completeness (client-dependent); clinical semantics.
- **Allowed Modules**: `apps/frontend/src/**` (visualization surface), `apps/frontend/src/__tests__/**`.
- **Forbidden Boundaries**: no display of unverified/unauthorized nodes publicly; no fabricated lineage.
- **Acceptance Criteria**: P2-04-AC-01…P2-04-AC-03.
- **Required Evidence**: E2-11…E2-13.
- **Negative Evidence**: unverified-node absence test.
- **DoD Contribution**: DOD-P2-05.
- **Rollback / Failure Semantics**: UI-only; visualization feature-flag rollback.

## P2-05 Media & Rights Lifecycle

- **Purpose**: HFM-native media model and rights lifecycle: original asset vs public derivative, rights metadata, license/use basis, redaction/watermark, withdrawal, hash binding, versioning, retention; fail-closed publication.
- **Authoritative Requirement Sources**: CR-013/015; MC-02; G4/G13; ADR-P2-01; AB-06.
- **Predecessors**: P2-00 (blocking); ADR-P2-01 (decision gate).
- **In Scope**: media schema (original/derivative); object-storage integration (S3-compatible abstraction); upload/ingestion with byte-hash binding; rights metadata (holder, license/use basis, restriction, expiry); public-derivative generation; redaction/watermark; withdrawal via projection state; retention policy; MIME/type/size/source/provenance/version lineage.
- **Out of Scope**: content population; clinical semantics; full customer media delivery.
- **Allowed Modules**: `apps/backend/src/hfm/phase2/media*`, `apps/backend/src/hfm/models/`, `apps/backend/alembic/versions/00XX_p2_*`, `apps/backend/tests/test_phase2_media*`.
- **Forbidden Boundaries**: no binary blobs in the relational DB without evidence; no publication without sufficient rights metadata; no HFB media inheritance.
- **Acceptance Criteria**: P2-05-AC-01…P2-05-AC-04.
- **Required Evidence**: E2-14…E2-16.
- **Negative Evidence**: rights-absent fail-closed test; original/derivative hash mismatch test.
- **DoD Contribution**: DOD-P2-10.
- **Rollback / Failure Semantics**: batch-level rollback; withdrawal removes public projection only; quarantine on conflict.

## P2-06 Export / Print

- **Purpose**: markdown (and PDF if justified) export with disclaimer retention (G9) and print styles for research and public surfaces.
- **Authoritative Requirement Sources**: G9; Reuse Matrix Export disposition; CR-003/009.
- **Predecessors**: P2-02 (blocking).
- **In Scope**: export endpoints (markdown; PDF conditional); disclaimer retention in every export output; print styles; withdrawn-content export block.
- **Out of Scope**: clinical output; content population.
- **Allowed Modules**: `apps/backend/src/hfm/phase2/export*`, `apps/frontend/src/**` (export UI), tests.
- **Forbidden Boundaries**: no export of withdrawn/private content; no clinical semantics in exported output.
- **Acceptance Criteria**: P2-06-AC-01…P2-06-AC-03.
- **Required Evidence**: E2-17…E2-19.
- **Negative Evidence**: withdrawn-content export denial test.
- **DoD Contribution**: DOD-P2-05.
- **Rollback / Failure Semantics**: export-only; no state mutation.

## P2-07 Deployment / Operations Foundation

- **Purpose**: development/test/production environment separation, configuration/secret boundary, database migration gate, health checks, backup/restore, release/rollback gates; CI/CD boundary definition.
- **Authoritative Requirement Sources**: CR-009/021; ADR-P2-02; Technology Baseline; ADR-01.
- **Predecessors**: P2-00 (blocking); ADR-P2-02 (decision gate).
- **In Scope**: dev/test/prod environment definitions; config boundary; secret boundary (no committed secrets); database migration gate in release; health/ready verification; backup/restore procedure; rollback procedure; CI/CD boundary (deploy ≠ import).
- **Out of Scope**: production execution until audit; production HFB import; observability stack (P2-08).
- **Allowed Modules**: `infra/**`, `scripts/**`, CI workflow definitions.
- **Forbidden Boundaries**: no merging of public/research security boundaries for deployment convenience; no production import under deploy authorization.
- **Acceptance Criteria**: P2-07-AC-01…P2-07-AC-04.
- **Required Evidence**: E2-20…E2-22.
- **Negative Evidence**: secret-scan failure test; migration-gate-before-deploy test.
- **DoD Contribution**: DOD-P2-11, DOD-P2-13.
- **Rollback / Failure Semantics**: release rollback procedure; backup/restore verified on test env.

## P2-08 Observability / Release Gates

- **Purpose**: structured logging, request metrics, health/ready probes, and automated release gates (lint/type/test/build) as the CI baseline; observability without an un-justified heavy stack.
- **Authoritative Requirement Sources**: Technology Baseline (observability TO BE DECIDED); CR-009; G14 context.
- **Predecessors**: P2-07 (blocking).
- **In Scope**: structured logging baseline; request metrics; health/ready probes; release-gate automation; CI workflow definition; no Prometheus/Grafana/OTel default (conditional on evidence).
- **Out of Scope**: production operations runbooks beyond baseline; heavy observability stack.
- **Allowed Modules**: `infra/**`, CI workflows, `apps/backend/src/hfm/core/logging*`.
- **Forbidden Boundaries**: no gate weakening to manufacture PASS.
- **Acceptance Criteria**: P2-08-AC-01…P2-08-AC-03.
- **Required Evidence**: E2-23…E2-25.
- **Negative Evidence**: release-gate failure demonstrates FAIL (no silent skip).
- **DoD Contribution**: DOD-P2-12.
- **Rollback / Failure Semantics**: gate fail blocks release; rollback via P2-07 procedure.

## P2-09 Unified Admin Audit View

- **Purpose**: read-only admin UI for audit-log browsing and reconciliation-result viewing (P1-13).
- **Authoritative Requirement Sources**: G12; P1-13 (accepted); CR-003.
- **Predecessors**: P2-02 (blocking).
- **In Scope**: audit-log browsing UI (role-gated); reconciliation PASS/FAIL display; read-only presentation.
- **Out of Scope**: audit mutation; governance changes.
- **Allowed Modules**: `apps/frontend/src/**` (admin audit surface), tests.
- **Forbidden Boundaries**: no mutation endpoints in UI; no unauthorized role access.
- **Acceptance Criteria**: P2-09-AC-01…P2-09-AC-03.
- **Required Evidence**: E2-26…E2-28.
- **Negative Evidence**: non-admin denial test; read-only enforcement test.
- **DoD Contribution**: DOD-P2-07.
- **Rollback / Failure Semantics**: read-only; no state mutation.

## P2-10 HFB Reuse Adjudication

- **Purpose**: per-item HFB reuse verdicts (PORT / ADAPT / REFERENCE_ONLY / DEFER / REJECT) covering HFB library, reader, workspace, RBAC, media-related reusable assets, and frontend reusable components, with zero-coupling reaffirmation and gating for any future PORT/ADAPT work.
- **Authoritative Requirement Sources**: CR-022/010; NPG-004; HFB Asset Reuse Matrix (frozen); ADR-06.
- **Predecessors**: P2-00 (blocking).
- **In Scope**: adjudication register; per-item verdicts with evidence; zero-coupling rule reaffirmation; gating rule (no PORT/ADAPT without an adjudicated verdict); credential-migration exclusion.
- **Out of Scope**: any HFB porting or implementation; license/credential migration; production import.
- **Allowed Modules**: `docs/audit/HFM-PHASE2-*`, `docs/governance/HFM-PHASE2-*` (register).
- **Forbidden Boundaries**: no verdict implies HFB runtime dependency; no identity/credential migration (MC-12).
- **Acceptance Criteria**: P2-10-AC-01…P2-10-AC-03.
- **Required Evidence**: E2-29…E2-31.
- **Negative Evidence**: zero HFB runtime imports across Phase-2 modules.
- **DoD Contribution**: DOD-P2-09, DOD-P2-13.
- **Rollback / Failure Semantics**: governance artifact; a rejected verdict cannot be bypassed without a new decision.

## Accounting

- WP total = 11 (P2-00…P2-10)
- IN scope items mapped = 9 (P2-C1→P2-01, P2-C2→P2-02, P2-C3→P2-03, P2-C4→P2-04, P2-C5→P2-05, P2-C6→P2-06, P2-C9→P2-10, P2-C13→P2-07+P2-08, P2-C15→P2-09; P2-00 anchors the governance contract)
- DEPENDENCY_ONLY scope items (P2-C8, P2-C14) are non-WP tracks governed by the frozen Migration Contract and the fixture-based intake policy — no acceptance target in Phase-2
- Every WP maps to ≥1 IN scope item; every IN scope item maps to ≥1 WP
