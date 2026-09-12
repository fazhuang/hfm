# HFM NPG-009 — DAG / Acceptance / Evidence / DoD Audit

Date: 2026-08-29  
Mode: READ-ONLY / GOVERNANCE ONLY  
Entry: `READY_FOR_NPG_9_DAG_ACCEPTANCE_DOD`  
Parent baseline: `0167b1702dac13993a5206f63752eafcc8e5387e`

## 1. Cross-consistency result

| Measure | Result |
| --- | ---: |
| IN scope item count | 14 |
| Work package count | 14 |
| Mapped scope item count | 14 |
| Unmapped scope item count | 0 |
| Unauthorized WP count | 0 |
| DAG node count | 14 |
| DAG edge count | 36 |
| Unreachable node count | 0 |
| Cycle count | 0 |
| Acceptance criterion count | 14 |
| Evidence mapping count | 14 |
| Acceptance criteria without evidence | 0 |
| DoD item count | 12 |
| DoD items without scope provenance | 0 |

The companion documents are the single trace chain: Scope Register → Work Package Inventory → DAG → Acceptance Contract → Evidence Contract → Definition of Done. Each IN scope has one accountable WP and one acceptance/evidence path.

## 2. Deferred/rejected guard

Display, HFB UI reuse, HFB Workspace reuse, HFB RBAC reuse, AI, 3D, VR, XR, and Virtual Training are not DAG nodes or positive DoD obligations. Clinical acupuncture recommendation/treatment suggestion is rejected and appears only as a negative acceptance guard.

## 3. ADR handling

ADR-01 (deployment), ADR-02 (search), ADR-05 (API separation), ADR-06 (HFB adapter), and ADR-07 (identity/RBAC) are `PRE_IMPLEMENTATION_BLOCKING` for the corresponding implementation choices. ADR-03 (relation storage) and ADR-04 (media storage) are `IMPLEMENTATION_LOCAL` unless their choice changes a frozen boundary. NPG-9 does not select any technology.

## 4. Content and migration separation

Platform DoD does not require all customer assets to be populated. Content batches use the separate Manifest→Admission→Validation→Rights→Normalization→Evidence→Approval→Import→Reconciliation→Publication template. NPG-8 M0–M3 may be preparatory evidence; M4–M7 are not Phase 1 prerequisites unless separately authorized. Production HFB Import remains `NOT PERFORMED`.

## 5. Remaining blockers

No cross-consistency failure blocks NPG-10 governance freeze. Before implementation, the PRE_IMPLEMENTATION_BLOCKING ADRs must be decided through their own records; before content import/publication, customer files, rights, provenance, and batch evidence must pass. These are explicit gates, not hidden dependencies or scope expansion.

## 6. Final verdict

**READY_FOR_NPG_10_GOVERNANCE_FREEZE**

This verdict is limited to governance freeze of the DAG/acceptance/evidence/DoD contracts. It does not authorize Phase 1, production import, or CD-7.
