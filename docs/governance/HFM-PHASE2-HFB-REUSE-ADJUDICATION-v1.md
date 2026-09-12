# HFM Phase 2 HFB Reuse Adjudication Register v1

Status: P2-10 IMPLEMENTATION ARTIFACT · GOVERNANCE CONTROL WP (P2-C9)
Authority: HFM-PHASE2-WORK-PACKAGE-CONTRACT-v1.md (P2-10); HFB Asset Reuse Matrix v1.0 (frozen); NPG-004; ADR-06
Taxonomy: `PORT` / `ADAPT` / `REFERENCE_ONLY` / `DEFER` / `REJECT` (frozen P2-10)
Invariant: **HFM runtime zero-coupling is mandatory.** No verdict implies an HFB runtime
import, shared live auth/session, shared credential store, or required HFB runtime service.
Adjudication is reuse classification — never migration execution (M0–M7 NOT EXECUTED).

## Adjudicated candidates

| ID | Source asset | Decision | Reason | Runtime coupling | Migration impact | Security impact | Reuse destination | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ADJ-01 | HFB Authentication (JWT+token_version) | REJECT | HFM-native identity (ADR-07, P1-10); no HFB credential/auth porting | 0 | 0 (MC-12 DO_NOT_MIGRATE) | 0 (no shared auth) | none — HFM-native | Reuse Matrix: Authentication; ADR-07 |
| ADJ-02 | HFB RBAC (8 roles × 21 resources) | REJECT | HFM-native role matrix (ADR-07, P1-10); HFB roles tightly coupled | 0 | 0 | 0 (deny-by-default HFM) | none — HFM-native | Reuse Matrix: RBAC; ADR-07 |
| ADJ-03 | HFB Person model/service/API | REFERENCE_ONLY | HFM canonical Person native (P1-03); semantics informed only | 0 | 0 | 0 | HFM models/person | Reuse Matrix: Person |
| ADJ-04 | HFB Ancient Text FRBR lineage | REFERENCE_ONLY | HFM Work/Edition/Version native (P1-04); informed only | 0 | 0 | 0 | HFM models/work/edition/version | Reuse Matrix: Ancient Text |
| ADJ-05 | HFB Source admission | REFERENCE_ONLY | HFM Source/admission native (P1-01/P1-02) | 0 | 0 | 0 | HFM models/source | Reuse Matrix: Source |
| ADJ-06 | HFB Evidence (Level 1-4 + taint) | REFERENCE_ONLY | HFM Evidence chain native (P1-02) | 0 | 0 | 0 | HFM models/evidence | Reuse Matrix: Evidence |
| ADJ-07 | HFB Citation persistence | REFERENCE_ONLY | HFM Citation native (P1-02) | 0 | 0 | 0 | HFM models/citation | Reuse Matrix: Citation |
| ADJ-08 | HFB Reader backend (repositories/document.py P4) | REFERENCE_ONLY | HFM versioned reader native (P1-07); no reader-code porting | 0 | 0 | 0 | HFM phase1/reader | Reuse Matrix: Reader; P1-07 |
| ADJ-09 | HFB Reader UI (ReaderPage.vue) | ADAPT | Future P2-03 reader surface may selectively adapt UI patterns under HFM locator/rights semantics; zero-coupling condition | 0 | 0 | 0 (no route/auth coupling) | apps/frontend (P2-03) | Reuse Matrix: Reader |
| ADJ-10 | HFB Library UI (pages/library/*) | DEFER | Library surface not in Phase-2 IN scope | 0 | 0 | 0 | none (deferred) | Reuse Matrix: Library; Scope Register |
| ADJ-11 | HFB Search backend (PG ILIKE) | REFERENCE_ONLY | HFM PG-native search implemented (P1-08, ADR-02); ES conditional only | 0 | 0 | 0 | HFM phase1/search | Reuse Matrix: Search; ADR-02 |
| ADJ-12 | HFB Search UI | ADAPT | Future P2-03 search surface may selectively adapt patterns under ADR-02 PG-only; zero-coupling | 0 | 0 | 0 | apps/frontend (P2-03) | Reuse Matrix: Search |
| ADJ-13 | HFB Knowledge workbench UI | DEFER | Knowledge UI not in Phase-2 IN scope | 0 | 0 | 0 | none (deferred) | Reuse Matrix: Knowledge |
| ADJ-14 | HFB Workspace model (ResearchSession chain) | REFERENCE_ONLY | HFM research workspace native (P1-12); informed only | 0 | 0 | 0 | HFM phase1/research_workspace | Reuse Matrix: Workspace |
| ADJ-15 | HFB Workspace UI (ResearchAppLayout) | ADAPT | P2-02 research shell may selectively adapt layout patterns under HFM RBAC/ownership; zero-coupling | 0 | 0 | 0 | apps/frontend (P2-02) | Reuse Matrix: Workspace |
| ADJ-16 | HFB Workflow service | REFERENCE_ONLY | HFM workflow native (P1-12) | 0 | 0 | 0 | HFM phase1/research_workspace | Reuse Matrix: Workflow |
| ADJ-17 | HFB Reports UI | DEFER | Reports surface not in Phase-2 IN scope | 0 | 0 | 0 | none (deferred) | Reuse Matrix: Reports |
| ADJ-18 | HFB Export (markdown) | ADAPT | Future P2-06 export may selectively adapt markdown export pattern; G9 disclaimer retention HFM-native; zero-coupling | 0 | 0 | 0 | P2-06 | Reuse Matrix: Export; G9 |
| ADJ-19 | HFB AI Copilot (Evidence-Gated) | DEFER | P2-C10 AI deferred; requires new governance + G8 guardrails + evaluation set; EVIDENCE_GATE_REFUSAL pattern REFERENCE_ONLY | 0 | 0 | 0 | none (deferred) | Reuse Matrix: AI Copilot; Scope Register |
| ADJ-20 | HFB Media (static JSON refs; models/image.py) | REJECT | HFM-native media lifecycle built (P2-05, ADR-P2-01); no HFB media inheritance; static refs are content leads only | 0 | 0 | 0 | none — HFM-native | Reuse Matrix: Media; ADR-P2-01 |
| ADJ-21 | HFB Rights fields | REFERENCE_ONLY | HFM rights semantics native (content_artifact RightsStatus; P2-05 rights lifecycle) | 0 | 0 | 0 | HFM models + P2-05 | Reuse Matrix: Rights |
| ADJ-22 | HFB Publication (promotion hash) | REFERENCE_ONLY | HFM publication workflow native (P1-09); no content-copy semantics | 0 | 0 | 0 | HFM phase1/publication | Reuse Matrix: Publication |
| ADJ-23 | HFB Snapshot (GenerationProof) | REFERENCE_ONLY | HFM publication snapshots native (P1-09) | 0 | 0 | 0 | HFM phase1/publication | Reuse Matrix: Snapshot |
| ADJ-24 | HFB Teaching (api/v4/education.py) | DEFER | P2-C7 teaching deferred; requires course/journey input + safety review | 0 | 0 | 0 | none (deferred) | Reuse Matrix: Teaching; Scope Register |
| ADJ-25 | HFB Audit models | REFERENCE_ONLY | HFM audit native (P1-13); HFB audit patterns informed only | 0 | 0 | 0 | HFM phase1/version_audit | Reuse Matrix: Audit |
| ADJ-26 | HFB frontend test-setup (jsdom polyfill) | PORT | Executed in Phase 0.3 Batch 3 (documented in test-setup.ts header); zero-coupling | 0 | 0 | 0 | apps/frontend test-setup.ts | test-setup.ts provenance header |
| ADJ-27 | HFB frontend composables (toast/theme/focus) | ADAPT | Phase-1 frontend already adapted patterns; future UI continues selective adaptation under HFM tokens; zero-coupling | 0 | 0 | 0 | apps/frontend | Reuse Matrix; existing composables |

## Accounting

- Items evaluated = **27** (ADJ-01 … ADJ-27)
- PORT = 1 (ADJ-26, executed in Phase 0.3)
- ADAPT = 5 (ADJ-09, 12, 15, 18, 27)
- REFERENCE_ONLY = 13 (ADJ-03…08, 11, 14, 16, 21…23, 25)
- DEFER = 5 (ADJ-10, 13, 17, 19, 24)
- REJECT = 3 (ADJ-01, 02, 20)
- Unclassified = **0**
- Runtime-coupling decisions = **0** (every verdict carries zero-coupling; HFB runtime imports = 0)
