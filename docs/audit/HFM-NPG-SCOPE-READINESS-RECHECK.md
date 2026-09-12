# HFM NPG Scope Readiness Recheck

Date: 2026-08-29
Mode: READ-ONLY / EVIDENCE-ONLY
Target branch: `governance/next-phase-authorization`
HEAD: `1d9cc5c8b48c37e06f7cc9f5dfccf08d73c07a72`
Parent baseline: `0167b1702dac13993a5206f63752eafcc8e5387e`

## 1. Governance input integrity

| Gate | Evidence | Result |
| --- | --- | --- |
| R1-G1 Baseline working environment | `git merge-base --is-ancestor 0167b17 HEAD` exit 0; exactly one post-parent commit, governance-only. HEAD and parent blobs for `scripts/core_completion/dry_run.py` are both `06c5c375...`; the live worktree blob is `ffb988789...` and `git status` reports `M scripts/core_completion/dry_run.py`. | **BLOCK**: committed branch lineage is valid, but the live implementation/frozen-file worktree is not clean. |
| R1-G1 Phase 0.4 history | `git diff 0167b17..HEAD` contains only newly added governance/audit documents; no implementation, migration, schema, test, CD-7, or Phase 1 code path. | PASS |
| R1-G2 Customer source | `docs/governance/inputs/HFM-CLIENT-CONFIRMED-REQUIREMENTS-v1.md` preserves CR-001…CR-010 as L1 facts and labels L2/L3 separately. | PASS |
| R1-G3 Gemini source | `docs/governance/inputs/HFM-GEMINI-ORIGINAL-IMPLEMENTATION-PROPOSAL-v1.md` is explicitly L3, non-binding, and has no implementation authorization. Three.js/WebGL/WebXR/Neo4j/Elasticsearch/MinIO/WebSocket/ECharts/D3/720 VR/8-week schedule remain non-requirements; 3D/VR/XR are deferred. | PASS |
| R1-G4 Content unknowns | `docs/governance/HFM-CONTENT-ASSET-REQUEST-REGISTER-v1.md` records CA-01…CA-10 with explicit import, publication, non-blocking, and confirmation statuses. | PASS |
| R1-G5 Manifest | Every listed SHA-256/path in `HFM-NPG-R1-GOVERNANCE-INPUT-MANIFEST.md` recomputed to an exact match (11/11 listed artifacts). | PASS |

Phase 0.4 remains `COMPLETE / ACCEPTED / ARCHIVED / FROZEN`; Production HFB Import remains `NOT PERFORMED`; CD-7 remains `NONEXISTENT`; Phase 1 remains `NOT AUTHORIZED`. The accepted `7960fb64...` is retained as a candidate and is not relabeled as the completion baseline.

## 2. PLATFORM_SCOPE_READINESS

**READY**

The frozen L1/L2 governance inputs are sufficient to arbitrate platform boundaries and candidate scope for: the public portal/research backend split, A/B/C/D domain framing, reader, historical search, evidence/citation, publication workflow, RBAC, display modes, and content admission. This is scope arbitration readiness only; it is not implementation authorization and does not select a final stack or reuse decision.

Required boundary conditions carried forward:

- HFB capability existence is evidence for a reuse candidate, not an automatic HFM reuse decision.
- “按病寻穴” may be considered only as historical/source retrieval with provenance; treatment recommendation,主配穴 ranking, diagnosis, efficacy, dosage, contraindication, or individualized clinical semantics are rejected unless separately authorized.
- Digital-humanities search is not clinical decision support.
- Public content must be separated from research/internal content and from source evidence versus editorial interpretation.
- 3D, VR, XR, virtual training, and unchosen technical products remain deferred or unresolved options.

## 3. CONTENT_DELIVERY_READINESS

**PARTIAL**

The customer asset request register is sufficiently formalized for controlled intake, but delivery readiness is incomplete. The repository does not contain the customer’s complete source packages, version-by-version digital files, provenance records, structured 128-article/349-acupoint datasets, complete genealogy evidence, or publication permissions. “Customer confirms possession” is therefore not treated as “file received” or “publishable.”

## 4. Remaining global blockers

- **ACCEPTANCE_BLOCKER — R1-G1-01:** live worktree contains an uncommitted change to frozen `scripts/core_completion/dry_run.py`; the exact parent object is clean and byte-identical at HEAD, but the current checkout cannot be certified as an untouched parent environment. No cleanup was performed.

No `GLOBAL_GOVERNANCE_BLOCKER` is asserted for missing content: the request register makes those effects explicit and local to import/publication.

## 5. Platform blockers

None for entering scope arbitration. Final architecture, stack, physical deployment split, display hardware, and HFB reuse remain decisions to arbitrate, not silently frozen requirements.

## 6. Content import blockers

- **CONTENT_IMPORT_BLOCKER:** CA-01 person/history evidence files and event-level SourceRef/Evidence locations not received.
- **CONTENT_IMPORT_BLOCKER:** CA-02 works/fragmentary literature inventory, versions, and full-text packages not confirmed or received.
- **CONTENT_IMPORT_BLOCKER:** CA-03 *Zhen Jiu Jia Yi Jing* version manifest, scans/text, completeness, and hashes not received.
- **CONTENT_IMPORT_BLOCKER:** CA-04 128-article structured data is not verified; repository prose is not counted as records.
- **CONTENT_IMPORT_BLOCKER:** CA-05 349-point, meridian, disease-term, and needling-method structures are not verified or received; any future use remains historical retrieval only.

## 7. Publication blockers

- **CONTENT_PUBLICATION_BLOCKER:** CA-06 formal intangible-heritage project evidence, level, and publication authorization are not confirmed.
- **CONTENT_PUBLICATION_BLOCKER:** CA-07 inheritor personal-information, portrait, attribution, and publication permissions are not confirmed.
- **CONTENT_PUBLICATION_BLOCKER:** CA-10 campus/activity media rights and public-display permissions are not confirmed.

## 8. Non-blocking unknowns

- **NON_BLOCKING_UNKNOWN:** CA-08 operational/display materials for the formally named demonstration center; the official name itself is confirmed.
- **NON_BLOCKING_UNKNOWN:** CA-09 teaching/research outcome packages; use cases are confirmed, while later content intake remains open.
- **NON_BLOCKING_UNKNOWN:** exact administrator/reviewer role cardinalities, display-device details, and physical versus logical deployment split; these do not prevent candidate platform scope arbitration.
- **NON_BLOCKING_UNKNOWN:** final HFB asset decisions; NPG-4 records candidates only and does not authorize reuse.

## 9. Evidence index

| Evidence | Bound location | Supports |
| --- | --- | --- |
| Branch/status/log/ancestry | HFM Git checkout; `1d9cc5c8...`, parent `0167b170...` | Target binding, one governance-only descendant, dirty worktree |
| Parent/HEAD/live blobs | `scripts/core_completion/dry_run.py` | Byte identity of committed file and uncommitted live drift |
| Customer source | `docs/governance/inputs/HFM-CLIENT-CONFIRMED-REQUIREMENTS-v1.md` | L1 facts, authority separation, deferred items, dual-layer direction |
| Gemini archive | `docs/governance/inputs/HFM-GEMINI-ORIGINAL-IMPLEMENTATION-PROPOSAL-v1.md` | L3/non-binding treatment and medical boundary |
| Content request register | `docs/governance/HFM-CONTENT-ASSET-REQUEST-REGISTER-v1.md` | CA-01…CA-10 and explicit blocker classifications |
| Governance manifest | `docs/governance/HFM-NPG-R1-GOVERNANCE-INPUT-MANIFEST.md` | Paths and SHA-256 integrity |
| Phase 0.4 archive/evidence | `docs/governance/BASELINE-MANAGEMENT.md`, `docs/audit/HFM-PHASE0.4-CORE-COMPLETION-*` | Frozen status, no production import, no CD-7, no Phase 1 |
| HFM/HFB inventories | `docs/audit/HFM-NPG-003-*`, `HFM-NPG-004-*`, `HFM-NPG-005-*` | Current capability and asset/content facts; not authorization |

## 10. Final recommendation

Dual-track result:

- `PLATFORM_SCOPE_READINESS: READY`
- `CONTENT_DELIVERY_READINESS: PARTIAL`

Because R1-G1 is blocked by the dirty live checkout, the overall recommendation is:

**NOT_READY_FOR_NPG_6_SCOPE_ARBITRATION**

This report authorizes no Phase 1 work, migration, import, CD-7, DAG, DoD, architecture, technology stack, or final HFB reuse decision.
