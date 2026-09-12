# HFM NPG-007 — Phase 1 Architecture Boundary Audit

Date: 2026-08-29  
Mode: READ-ONLY / GOVERNANCE ONLY  
Target: `governance/next-phase-authorization`  
Entry: `READY_FOR_NPG_7_ARCHITECTURE_BOUNDARY`  
Parent: `0167b1702dac13993a5206f63752eafcc8e5387e`

## 1. Architecture boundary verdict

**READY_FOR_NPG_8_MIGRATION_CONTRACT**

NPG-6 scope is treated as fixed. The required ownership, public/research, content/evidence, publication, identity, medical, and HFB dependency boundaries are explicit. Product and infrastructure choices remain ADR-required and are not silently selected.

## 2. Required boundaries

AB-01, AB-02, AB-03, AB-04, AB-05, AB-06, AB-07, AB-08, AB-09, AB-10, AB-11, and AB-15 are required contracts. They preserve HFM canonical ownership, evidence/version lineage, two-layer experience separation, content/publication separation, and independent deployment/import gates.

## 3. Forbidden couplings

AB-13, AB-14, and AB-16 forbid permanent HFB runtime dependency, clinical decision-support semantics, and deferred-module dependencies in the Phase 1 core. Historical C-domain retrieval is allowed only with source/evidence/version context.

## 4. ADR-required decisions

ADR-01 through ADR-07 remain open candidates: physical deployment, search, relation storage, media storage, API separation, HFB adapter strategy, and identity/RBAC strategy. No specific product is frozen.

## 5. HFB dependency boundary

HFB Evidence/SourceRef/Citation remains `DEPENDENCY_ONLY` with candidate disposition `MIGRATE`. Any future contract must bind a source snapshot, mapping, canonical HFM targets, validation, reconciliation, fail-closed behavior, idempotency, and removal of HFB runtime dependency. Other HFB reuse candidates remain optional adaptations or references.

## 6. Public/Research separation

The public experience is limited to approved published projections. The research experience is authenticated and may access richer evidence and non-public material under RBAC. Shared core services are acceptable only with explicit policy and projection boundaries; shared ambiguous routes are not.

## 7. Content/Publication separation

Content admission proves source, artifact, version, provenance, rights, and evidence before population. Publication is a separate reviewed state with withdrawal/rollback. Missing CA-01…CA-05 packages block content import, and CA-06/07/10 rights or formal-evidence gaps block publication; they do not erase the platform capability scope.

## 8. Medical safety boundary

The C domain supports historical retrieval of 病证、章节、穴位、经络、刺灸法 and returns source passages, citations, evidence, and versions. It forbids diagnosis, treatment recommendation, prescription generation, clinical ranking, efficacy claims, and automatic 主穴/配穴 recommendations. `P1-CLINICAL` remains rejected.

## 9. NPG-8 migration inputs

NPG-8 may define a migration contract from these boundaries: exact HFB snapshot, source manifest, HFM canonical targets, field/locator transforms, rights/provenance mapping, duplicate and collision policy, validation/reconciliation reports, quarantine and retry behavior, rollback, and proof of no permanent HFB runtime dependency. No migration is authorized by this audit.

## 10. Blockers

No blocker prevents entering NPG-8 migration-contract design. The following are preconditions before implementation or import, not reasons to reopen NPG-6:

- ADR-01…ADR-07 must be decided through their own governance records before corresponding implementation choices are frozen.
- Customer content and rights packages remain content-import/publication gates.
- A migration contract must prove fail-closed provenance and rights behavior before any production import.

The following remain unchanged: Production HFB Import `NOT PERFORMED`; CD-7 `NONEXISTENT`; Phase 1 implementation `NOT AUTHORIZED`.

## 11. Evidence index

| Input | Use |
| --- | --- |
| `docs/governance/HFM-PHASE1-SCOPE-REGISTER-v1.md` | Fixed NPG-6 candidate verdicts and HFB dispositions |
| `docs/audit/HFM-NPG-006-PHASE1-SCOPE-ARBITRATION.md` | NPG-6 scope rationale and content/platform separation |
| `docs/audit/HFM-NPG-BOUNDARY-REGISTER.md` | Existing product and medical boundaries |
| `docs/audit/HFM-NPG-003-CURRENT-CAPABILITY-INVENTORY.md` | HFM canonical foundation and absent product surfaces |
| `docs/audit/HFM-NPG-004-HFB-ASSET-REUSE-AUDIT.md` | HFB coupling, licensing, and candidate reuse dispositions |
| `docs/audit/HFM-NPG-005-CONTENT-ASSET-GAP-ANALYSIS.md` | Customer asset and rights gaps |
| `docs/governance/inputs/HFM-CLIENT-CONFIRMED-REQUIREMENTS-v1.md` | L1 authority and two-layer direction |
| `docs/governance/HFM-NPG-R1-GOVERNANCE-INPUT-MANIFEST.md` | Frozen input integrity |

## 12. Final verdict

**READY_FOR_NPG_8_MIGRATION_CONTRACT**

This is a governance transition only. It does not output `PHASE_1_AUTHORIZED`, `PHASE_1_FROZEN`, or authorize CD-7, implementation, deployment, or migration execution.
