# HFM NPG-006 — Phase 1 Scope Arbitration

Date: 2026-08-29  
Mode: READ-ONLY / GOVERNANCE ONLY  
Target branch: `governance/next-phase-authorization`  
Governance HEAD: `3821606a5ad77e5bc47b00afa5662b109104d296`  
Parent baseline: `0167b1702dac13993a5206f63752eafcc8e5387e`  
Entry state: `READY_FOR_NPG_6_SCOPE_ARBITRATION`

## 1. Authority and method

This arbitration uses only the frozen customer source, Gemini archive, NPG-000…005 audits, boundary register, fact summary, content request register, R1 manifest, scope-readiness recheck, and worktree-drift root-cause record. L1 is explicit customer fact; L2 is necessary product derivation; L3 is non-binding design/technical input. Only L1/L2 justify inclusion. Every candidate is assigned exactly one scope verdict in the companion register.

This is a candidate scope decision, not Phase 1 authorization, a frozen architecture, a migration authorization, or a CD-7 creation.

## 2. Arbitration result

The minimum Phase 1 product boundary is the two-layer public portal/research experience, A/B/C/D domain surfaces, historical reader/search, provenance/evidence/version chain, content admission/publication controls, and identity/RBAC. HFM’s existing canonical data layer supports the foundation but does not provide these end-user capabilities. Missing customer files constrain population and publication; they do not remove the platform capabilities from candidate scope.

## 3. Grouped scope verdicts

### IN

`P1-GOV`, `P1-CONTENT`, `P1-A`, `P1-B`, `P1-C`, `P1-D`, `P1-PORTAL`, `P1-RESEARCH`, `P1-READER`, `P1-SEARCH`, `P1-PUBLISH`, `P1-RBAC`, `P1-EVIDENCE`, `P1-VERSION`.

### DEPENDENCY_ONLY

`P1-HFB-EVIDENCE` — only as a possible migration source into the HFM canonical chain; no HFB schema copy or automatic reuse.

### DEFERRED

`P1-DISPLAY`, `P1-HFB-LIBRARY`, `P1-HFB-READER`, `P1-HFB-WORKSPACE`, `P1-HFB-RBAC`, `P1-AI`, `P1-3D`, `P1-VR`, `P1-XR`, `P1-TRAIN`.

### REJECTED

`P1-CLINICAL` — clinical acupuncture recommendation/treatment suggestion is outside the digital-humanities, teaching, and research boundary.

The complete first-principles record (A–H for every candidate), content dependency, and HFB reuse disposition is in [HFM-PHASE1-SCOPE-REGISTER-v1.md](/Users/likeming/Sites/hfm/docs/governance/HFM-PHASE1-SCOPE-REGISTER-v1.md).

## 4. Medical and product boundaries

- P1-C is historical/textual/scholarly retrieval: disease-term search may return relevant *Zhen Jiu Jia Yi Jing* passages, points, chapters, citations, evidence, and versions.
- No diagnosis, treatment recommendation, main/auxiliary point prescription, efficacy claim, dosage, contraindication, or individualized clinical advice is in scope.
- Display mode is separate from 3D/VR/XR. A possible large-screen/touch adaptation is deferred pending device facts; it does not authorize immersive technology.
- HFB capability existence is not an HFM reuse decision. The register records `ADAPT`, `MIGRATE`, `REFERENCE_ONLY`, or `REJECT` independently of scope verdict.
- Production HFB Import remains `NOT PERFORMED`; CD-7 remains `NONEXISTENT`; Phase 1 remains `NOT AUTHORIZED`.

## 5. Unresolved architecture decisions for NPG-7

These are deliberately converted to NPG-7 decisions rather than left as final NPG-6 scope verdicts:

1. Public portal versus research backend physical deployment and trust boundaries.
2. HFM API/module boundaries and publication snapshot/withdrawal model.
3. Identity, institutional roles, reviewer separation of duties, and tenant model.
4. Search implementation and indexing scope; Elasticsearch is not selected.
5. Object/media storage and delivery; MinIO is not selected.
6. Display hardware/offline/accessibility requirements.
7. HFB adaptation/migration boundary and licensing/content-rights separation.
8. Whether any AI research assistance is later proposed with an independent evaluation and refusal contract.

## 6. Migration questions for NPG-8

- Map HFB Evidence/SourceRef/Citation into HFM canonical entities without row-copying incompatible schemas.
- Define admission manifests, source hashes, version/locator transforms, and rejection handling.
- Decide whether HFB Library/Reader/Workspace/RBAC interaction patterns can be adapted after HFM contracts and role policy exist.
- Establish a content-batch import protocol for CA-01…CA-05; no production import is authorized here.
- Reassess HFB corpus metadata only after customer ownership, provenance, completeness, and rights are proven.

## 7. Content dependencies

The Content Asset Request Register records CA-01…CA-10. Import blockers are CA-01…CA-05 (files, versions, structured data, provenance); publication blockers are CA-06, CA-07, and CA-10 (formal heritage evidence, personal/portrait permissions, media rights). CA-08 and CA-09 remain non-blocking unknowns for platform scope. “Customer has an asset” is not evidence that a file was delivered or that publication is allowed.

## 8. Acceptance implications

Minimum acceptance must prove:

- public/research separation and deny-by-default RBAC;
- content admission rejects missing provenance/rights and preserves SourceRef→Evidence→Citation→Version lineage;
- reader/search return historical source material with locators and no clinical recommendation semantics;
- publication review, withdrawal, rollback, and observable status are distinct from research data;
- content population is measured by explicit batches, not by platform capability claims;
- HFB reuse, if selected later, is tested against HFM contracts and not inferred from HFB existence.

## 9. Blockers preventing scope freeze

No blocker prevents this candidate arbitration from proceeding. Final architecture and implementation scope cannot yet be frozen because they are NPG-7 decisions; customer content/rights remain batch and publication gates, not global platform blockers. This report does not authorize development, migration, import, deployment, CD-7, or Phase 1 implementation.

## 10. Evidence index

| Evidence | Purpose |
| --- | --- |
| `docs/governance/inputs/HFM-CLIENT-CONFIRMED-REQUIREMENTS-v1.md` | L1 customer facts, users, goals, asset categories, two-layer direction, deferred immersive scope |
| `docs/governance/inputs/HFM-GEMINI-ORIGINAL-IMPLEMENTATION-PROPOSAL-v1.md` | L3/non-binding proposal separation and medical boundary |
| `docs/audit/HFM-NPG-000-BASELINE-INTEGRITY-AUDIT.md` | Parent baseline and Phase 0.4 integrity facts |
| `docs/audit/HFM-NPG-001-CUSTOMER-REQUIREMENT-AUTHORITY.md` | L1/L2/L3 authority classification |
| `docs/audit/HFM-NPG-002-GEMINI-PROPOSAL-SEPARATION.md` | Candidate treatment of A–R design items |
| `docs/audit/HFM-NPG-003-CURRENT-CAPABILITY-INVENTORY.md` | HFM implemented/absent capability facts |
| `docs/audit/HFM-NPG-004-HFB-ASSET-REUSE-AUDIT.md` | HFB snapshot assets and candidate dispositions |
| `docs/audit/HFM-NPG-005-CONTENT-ASSET-GAP-ANALYSIS.md` | Customer content evidence and gaps |
| `docs/audit/HFM-NPG-BOUNDARY-REGISTER.md` | Medical, public/research, import, CD-7, and authorization boundaries |
| `docs/governance/HFM-CONTENT-ASSET-REQUEST-REGISTER-v1.md` | Explicit content import/publication/non-blocking classifications |
| `docs/governance/HFM-NPG-R1-GOVERNANCE-INPUT-MANIFEST.md` | Frozen input paths and hashes |
| `docs/audit/HFM-NPG-SCOPE-READINESS-RECHECK.md` | Platform READY / content PARTIAL result |
| `docs/audit/HFM-NPG-WORKTREE-DRIFT-ROOT-CAUSE.md` | Containment evidence and no implementation change claim |

## 11. Final verdict

**READY_FOR_NPG_7_ARCHITECTURE_BOUNDARY**

This verdict authorizes only transition to NPG-7 architecture-boundary arbitration. It does not output `PHASE_1_AUTHORIZED` or `PHASE_1_FROZEN`.
