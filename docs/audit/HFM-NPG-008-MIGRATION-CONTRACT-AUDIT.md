# HFM NPG-008 — Phase 1 Migration Contract Audit

Date: 2026-08-29  
Mode: READ-ONLY / GOVERNANCE ONLY  
Target branch: `governance/next-phase-authorization`  
Entry state: `READY_FOR_NPG_8_MIGRATION_CONTRACT`  
HFB source snapshot: `03755b57ec0e4c8023d1447619f7d6ead9e44d73`

## 1. Migration contract verdict

**READY_FOR_NPG_9_DAG_ACCEPTANCE_DOD**

The migration boundary, object classifications, lifecycle gates, canonical ownership, evidence chain, artifact integrity, idempotency, reconciliation, rollback, and production authorization separation are explicit. This is a contract/DAG input only; no migration or production authorization is granted.

## 2. Migration lifecycle M0–M7

M0 snapshot verification → M1 mapping verification → M2 isolated dry-run replay → M3 reconciliation → M4 independent production authorization → M5 production import → M6 post-import reconciliation → M7 migration freeze. M0–M3 are preparatory stages. M4 is a separate authorization artifact. M5 is forbidden before M4 PASS. Current Production HFB Import remains `NOT PERFORMED`.

## 3. Migratable object classes

MC-01…MC-08, MC-10 and MC-11 are `TRANSFORM` contracts into HFM canonical ownership. MC-09 is `REFERENCE_ONLY` because HFB reader structures are implementation/UI artifacts. MC-12 is `DO_NOT_MIGRATE` by default: users, credentials, password hashes, sessions/tokens, roles, assignments, and audit identities require a separate security and authorization decision.

## 4. Prohibited migrations

HFB IDs cannot be sole canonical identities; HFM cannot retain HFB runtime/database/API dependencies; HFB production runtime cannot remain a source of truth; mixed ownership and silent schema coercion are forbidden. Metadata without a verified artifact is not an artifact migration. Unknown-rights or medically unsafe records fail closed. Dry-run PASS never means production import.

## 5. Evidence/SourceRef/Citation mapping

HFB Evidence maps to HFM Evidence only with a valid HFM SourceRef/Passage anchor, content hash, provenance and Version binding. HFB SourceRef maps to HFM Source + structured locator semantics; ambiguous locators quarantine. HFB Citation maps to HFM Citation targeting an HFM Assertion and must have a non-orphan Evidence/source/version chain. Any missing link is rejected; no orphan citation is accepted.

## 6. Artifact integrity rules

Each artifact requires an immutable source snapshot, byte/content hash, metadata hash where applicable, target hash verification, byte-level integrity where applicable, MIME/type/readability checks, duplicate detection, completeness, provenance and rights status. Corrupt, missing, duplicate, or unauthorized artifacts are quarantined or rejected. A catalog row or file path alone is not proof of migration.

## 7. Idempotency rules

The batch key is `(SOURCE-SNAPSHOT, MAPPING-CONTRACT-VERSION, source identifier, HFM canonical identity)`. Repeating an identical snapshot/mapping against identical target state creates no duplicate semantic records. Changed inputs require a new batch and explicit conflict/revision handling. Every batch manifest records counts, hashes and reconciliation result.

## 8. Reconciliation rules

M3 and M6 must report source count, accepted count, rejected count, target count, duplicate count, orphan count, hash mismatch count, and mapping failure count. Integrity failures produce `FAIL`, not a warning-only completion. A `PASS` requires explainable count conservation, zero prohibited orphan links, verified hashes, and an inventory of all rejections/quarantine records.

## 9. Credential/RBAC boundary

HFB users, credentials, password hashes, sessions/tokens, roles, permission assignments and audit identities are `DO_NOT_MIGRATE` under NPG-8. HFM identity/RBAC remains HFM-owned; any future integration requires a separate mapping, security review, ownership/consent evidence, fail-closed behavior and independent authorization.

## 10. Production authorization boundary

NPG-8 authorizes no M4, M5, M6 or M7 execution. Production import requires a later independent artifact that names the exact snapshot, mapping contract, target, operator, batch scope, rollback plan, expiry, and acceptance evidence. Current state is **Production HFB Import: NOT PERFORMED**. CD-7 remains `NONEXISTENT`; Phase 1 remains `NOT AUTHORIZED`.

## 11. Blockers for NPG-9

No blocker prevents NPG-9 from defining the migration DAG and acceptance DoD. NPG-9 must carry these prerequisites forward:

- M0–M3 evidence commands and isolated storage must be specified without touching production.
- M4 must remain a separate authorization gate; M5 must be explicitly forbidden before it.
- Customer content batches, rights and publication approval remain separate from HFB technical migration.
- ADR-06 (HFB adapter strategy) and ADR-07 (identity/RBAC strategy) remain decision inputs; this contract does not select an implementation.
- NPG-9 acceptance must test fail-closed evidence/citation mapping, artifact hashes, idempotency, reconciliation and rollback semantics.

These are DAG/DoD inputs, not authorization to implement or migrate.

## 12. Evidence index

| Input | Supports |
| --- | --- |
| `docs/governance/HFM-PHASE1-SCOPE-REGISTER-v1.md` | Fixed NPG-6 scope and HFB disposition |
| `docs/audit/HFM-NPG-006-PHASE1-SCOPE-ARBITRATION.md` | Scope/content/platform separation |
| `docs/governance/HFM-PHASE1-ARCHITECTURE-BOUNDARY-v1.md` | Canonical ownership, public/research and HFB boundaries |
| `docs/governance/HFM-PHASE1-ADR-REGISTER-v1.md` | Open adapter and identity ADR inputs |
| `docs/audit/HFM-NPG-007-ARCHITECTURE-BOUNDARY-AUDIT.md` | Architecture boundary verdict and NPG-8 entry |
| `docs/audit/HFM-NPG-004-HFB-ASSET-REUSE-AUDIT.md` | Fixed HFB snapshot and reuse coupling facts |
| `docs/audit/HFM-NPG-005-CONTENT-ASSET-GAP-ANALYSIS.md` | Customer content and rights gaps |
| `docs/governance/HFM-CONTENT-ASSET-REQUEST-REGISTER-v1.md` | Content batch/publication classifications |
| `docs/governance/HFM-NPG-R1-GOVERNANCE-INPUT-MANIFEST.md` | Governance input integrity |

## 13. Final verdict

**READY_FOR_NPG_9_DAG_ACCEPTANCE_DOD**

No `PHASE_1_AUTHORIZED`, `PHASE_1_FROZEN`, or `PRODUCTION_IMPORT_AUTHORIZED` conclusion is made.
