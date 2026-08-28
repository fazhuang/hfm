# HFM Phase 1 Governance Freeze Manifest v1

Status: NPG-10 GOVERNANCE FREEZE CANDIDATE  
Branch: `governance/next-phase-authorization`  
Phase 0.4 parent baseline: `0167b1702dac13993a5206f63752eafcc8e5387e`  
Current governance candidate input commit: `3821606a5ad77e5bc47b00afa5662b109104d296`  
Final freeze commit: recorded in the NPG-010 post-commit audit and final acceptance record.

## Frozen artifact register

All listed files are byte-hash-bound inputs to the freeze. The manifest itself is the binding index and is verified by its committed Git blob after freeze.

| Path | SHA-256 | Governance role | Authority | Binding status |
| --- | --- | --- | --- | --- |
| `docs/governance/HFM-PHASE1-SCOPE-REGISTER-v1.md` | `281722177ac04643691f3eb241df18e1d8b00c4114873db63f35dc4d0769d73e` | NPG-6 scope registry | L1/L2 | FROZEN INPUT |
| `docs/audit/HFM-NPG-006-PHASE1-SCOPE-ARBITRATION.md` | `bdbf9283c8e178bf4aec7f8c49719ad23df561ba70da7c3af1238cac9888b13f` | NPG-6 arbitration | L1/L2 audit | FROZEN INPUT |
| `docs/governance/HFM-PHASE1-ARCHITECTURE-BOUNDARY-v1.md` | `2464276e5c9ea02331674e32e53d4890e793651dfb13e4ebb06585be5f09fb0e` | NPG-7 architecture boundaries | L1/L2 | FROZEN INPUT |
| `docs/governance/HFM-PHASE1-ADR-REGISTER-v1.md` | `56faf9ad3a1a0ff39b07a22edd73e23f7640be71bf742433f29ce4479fa01b1f` | ADR candidates | L3 options / governance | FROZEN INPUT |
| `docs/audit/HFM-NPG-007-ARCHITECTURE-BOUNDARY-AUDIT.md` | `6a6dd72502bb47c167b2b0d145b8f05e64d707e1985c680c6a43bda13c368d1e` | NPG-7 audit | L1/L2 audit | FROZEN INPUT |
| `docs/governance/HFM-PHASE1-MIGRATION-CONTRACT-v1.md` | `ec4bcc7430d0b283bface1825cd982cb21a729158256740294e1f4aff1672dc5` | NPG-8 migration contract | L1/L2 | FROZEN INPUT |
| `docs/governance/HFM-PHASE1-MIGRATION-OBJECT-REGISTER-v1.md` | `e73a64a0ad6ee33e1504e017632902ef806dfc98a558a1bf6c46e9d4f3b985d3` | Migration object classes | L1/L2 | FROZEN INPUT |
| `docs/audit/HFM-NPG-008-MIGRATION-CONTRACT-AUDIT.md` | `2a6980fd77c64b9054ebe0ed10de70fcd1cfb140fec365fe33d5935186207715` | NPG-8 audit | L1/L2 audit | FROZEN INPUT |
| `docs/governance/HFM-PHASE1-WORK-PACKAGE-INVENTORY-v1.md` | `763b102770e01aaedf611caca25f8c83ffef669179fe6a772ad6e93abea2fc1e` | NPG-9 work packages | L1/L2 | FROZEN INPUT |
| `docs/governance/HFM-PHASE1-DAG-v1.md` | `970044eabafb91c67bf7218a25b46bc570cd4db41b9af4e4e1645365682ccb30` | NPG-9 DAG | L1/L2 | FROZEN INPUT |
| `docs/governance/HFM-PHASE1-ACCEPTANCE-CONTRACT-v1.md` | `879072b2204b18e49ca2b14267af78255420630c015cb9a79ce5d301a7b4a042` | NPG-9 acceptance | L1/L2 | FROZEN INPUT |
| `docs/governance/HFM-PHASE1-EVIDENCE-CONTRACT-v1.md` | `2faf03f62735cf3f2b997776561e2a758e72d350447aac5992325c386b975613` | NPG-9 evidence | L1/L2 | FROZEN INPUT |
| `docs/governance/HFM-PHASE1-DEFINITION-OF-DONE-v1.md` | `b1a8328a63dfd325ee4c35c43b4a5fc1ab140c39eb67824c16c3f9abbeae57b2` | NPG-9 DoD | L1/L2 | FROZEN INPUT |
| `docs/governance/HFM-PHASE1-CONTENT-BATCH-DOD-TEMPLATE-v1.md` | `c373758cc4b93ffc30258e1ca97775fcb0488a853111d952d240f1ad72c2441e` | Content batch DoD | L1/L2 | FROZEN INPUT |
| `docs/audit/HFM-NPG-009-DAG-ACCEPTANCE-DOD-AUDIT.md` | `4de19c630553228506620f4985d9055a8ce35049d07ed2cef373d198c9e255ad` | NPG-9 audit | L1/L2 audit | FROZEN INPUT |
| `docs/governance/inputs/HFM-CLIENT-CONFIRMED-REQUIREMENTS-v1.md` | `6130a25796f1f4c88fee993d5d39b3f6c6391027f4102855d4c9cc24dc37b453` | Customer authority source | L1 | FROZEN INPUT |
| `docs/governance/HFM-NPG-R1-GOVERNANCE-INPUT-MANIFEST.md` | `e346aa87a430f6cf26a61269b9a60a7987cbc6894949fb76da367c084a4c527a` | Governance input manifest | L1/L2/L3 register | FROZEN INPUT |
| `docs/audit/HFM-NPG-BOUNDARY-REGISTER.md` | `53e9b0ea57d10101001a33a1bf783e20291bc4da63e994bc715ca30d749fc837` | Product boundary register | L1/L2 | FROZEN INPUT |

Frozen artifact count: **18** (excluding this index and the NPG-010 audit).

## Frozen invariants

```text
IN scope: 14
DEPENDENCY_ONLY: HFB Evidence / SourceRef / Citation mapping
DEFERRED: Display; HFB UI/Workspace/RBAC reuse; AI; 3D; VR; XR; Virtual Training
REJECTED: Clinical acupuncture recommendation / treatment suggestion
Work packages: 14
DAG nodes / edges: 14 / 36
Acceptance criteria / evidence mappings: 14 / 14
DoD items: 12
Cross-consistency failures: 0
PRE_IMPLEMENTATION_BLOCKING ADRs: ADR-01, ADR-02, ADR-05, ADR-06, ADR-07
Production HFB Import: NOT PERFORMED
CD-7: NONEXISTENT
Phase 1: NOT AUTHORIZED
```

NPG-10 status is `GOVERNANCE_FROZEN_PENDING_INDEPENDENT_AUTHORIZATION`. Unresolved ADRs remain unresolved; this manifest makes no technical selection and authorizes no implementation, migration, production import, or CD-7.
