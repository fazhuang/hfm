# HFM NPG-0…NPG-5 Fact Audit Summary

Date: 2026-08-29
Formal baseline under audit: `0167b1702dac13993a5206f63752eafcc8e5387e`
HFB snapshot: `03755b57ec0e4c8023d1447619f7d6ead9e44d73`

## 1. Executive Result

**NOT_READY_FOR_SCOPE_ARBITRATION**

The formal Phase 0.4 Git commit is valid and independently testable, but the live HFM working tree contains uncommitted drift in a frozen CORE-COMPLETION file. The original Gemini proposal needed for a full line-by-line separation audit was not found, and the five client-confirmed content-asset families lack a delivered, provenance/rights-complete register. This audit records the facts and performs no repair.

## 2. Baseline Integrity

- `HEAD == main == origin/main == 0167b1702dac13993a5206f63752eafcc8e5387e` at audit start.
- All named HFM baselines/candidates resolve and form the required ancestor chain.
- `7960fb64` is correctly preserved as the accepted candidate; `0167b170` is the archive/freeze event and formal completion baseline.
- Original v0.1 frozen contract artifact blob IDs are unchanged from `366df697` to `0167b170`.
- No commit after `0167b170` exists on repository refs.
- Audit-start working tree was not clean: `scripts/core_completion/dry_run.py` had an uncommitted formatting diff.
- NPG-0 verdict: **BLOCK**.
- `README.md:43` is ambiguous about `d08e343` versus the self-referential archive baseline; authoritative `BASELINE-MANAGEMENT.md` and the acceptance archive support `0167b170`.

## 3. Customer Requirement Facts

L1 facts are limited to the two construction parties, two primary service institutions, six business goals, user priority `参观者 > 研究者 > 学生`, five asset families, the official organization name and alias boundary, deferral of 3D/VR/virtual training, the public-portal + research-backend direction, and the requirement to arbitrate HFB reuse asset by asset.

Neo4j, Elasticsearch, MinIO, Three.js, WebXR, WebSocket, ECharts, D3, table designs, an eight-week schedule, and acupoint recommendations are not L1 facts.

## 4. Gemini Proposal Separation

- Four business domains: derived organizing model, not four mandated systems.
- Reader and full-text discovery: derived needs, implementation-neutral.
- Transmission lineage: confirmed requirement; visualization/graph technology unresolved.
- 3D, VR/720, WebXR, virtual training: deferred.
- Big screen and touch mode: need client/device decisions.
- ES/Neo4j/MinIO/WebSocket/ECharts/D3 and stack binding: design options.
- Eight weeks: unsupported estimate requiring decision.
- “按病寻穴”: only potentially admissible as historical-source retrieval; current semantics require decision.
- “推荐主配穴”: rejected in the current digital-humanities boundary because it implies treatment recommendation.
- Original Gemini proposal artifact: **NOT FOUND**, so exhaustiveness beyond the enumerated A–R items is unproven.

## 5. Current HFM Capability Inventory

HFM currently has:

- a tested FastAPI/Vue repository skeleton;
- health/system endpoints and basic operational logging/request IDs;
- a frozen SQLAlchemy/Alembic canonical data foundation for Entity, Person, Institution, Work, Edition, Version, Chapter, Passage, Source, SourceRef, Evidence, Assertion, Citation, Event, and EventRelation;
- repositories, invariants, migrations, and CORE-COMPLETION dry-run tooling/evidence.

HFM does not currently have an implemented public portal, research workspace, Library, Reader, Search, identity/RBAC, publication workflow, governed media layer, general knowledge-graph product, AI runtime, reports/export, or admin surface.

Fresh checks against a `/private/tmp` export of the exact Git baseline all exited `0`: backend pytest/Ruff/strict-mypy and frontend ESLint/typecheck/Vitest/build. These prove the foundation, not absent product surfaces or production readiness.

## 6. HFB Reuse Inventory

HFB contains substantial Vue pages/components, Library, Reader, Workspace, Search, Identity/RBAC, Evidence/SourceRef/Citation, version/collation, research workflow, reports/export, graph, AI/RAG, source admission, admin, tests, documentation, and deployment assets.

Candidate findings:

- **ADAPT** is generally appropriate for Vue UX patterns, research workspace, search, auth/RBAC concepts, reports, source admission, admin, test scenarios, deployment and health patterns.
- **MIGRATE** is the candidate for admitted Evidence/SourceRef/Citation data because HFM canonical semantics differ.
- **REFERENCE_ONLY** is appropriate for overlapping ancient-book schemas, fine-grained collation until needed, graph/AI/prompt/schema/governance history, and production-promotion concepts.
- Corpus metadata remains **UNRESOLVED**.
- Static exhibition/media content is **REJECT** as-is pending provenance/rights/accuracy review.

These are candidates, not final decisions. HFB code under `/apps` and `/packages` has an MIT option; repository documentation/data is CC BY-NC-SA 4.0, and third-party/customer content rights remain separate.

## 7. Customer Asset Gap

The client confirms possession of versions, historical materials, heritage certificates, inheritor materials, and campus photos. None has been delivered to the HFM baseline as a publishable, evidence/rights-complete package.

HFB snapshot facts:

- 515 paper metadata rows;
- 92 edition metadata rows, 87 associated with 《针灸甲乙经》;
- external `hfmzl/...` paths, but the referenced PDFs are not tracked in the snapshot;
- no 128-record chapter dataset;
- no 349-record acupoint dataset;
- no meridian/disease/acupuncture-method structured dataset;
- no heritage certificate, inheritor, campus-activity, consent, or display-rights dataset.

The displayed claims “12卷128篇” and “349穴” are prose/seed claims, not structured-data proof.

## 8. Product Boundary Findings

All twelve required boundaries are registered in `HFM-NPG-BOUNDARY-REGISTER.md`. The decisive boundaries are:

- dry-run is not production import;
- research state is not public content;
- public portal is not research backend;
- historical search is not clinical decision support;
- HFB existence is not reuse authority;
- an AI design or technical option is not a customer requirement or frozen architecture decision.

## 9. Critical Unknowns

1. Original Gemini proposal and its source/version/date.
2. Joint-governance owner, client approvers, and responsibility split.
3. Concrete visitor/researcher/student journeys and acceptance metrics.
4. Exact customer asset counts, files, hashes, digitization/OCR/collation state, owners, and storage location.
5. Which 皇甫谧 works are available as full text and under which editions/rights.
6. Whether a real 128-chapter dataset exists and which Version it represents.
7. Whether a real 349-acupoint dataset exists and what source/fields it uses.
8. Whether meridian, disease-pattern, and acupuncture-method datasets exist.
9. Official intangible-heritage item name, level, number, protection unit, and source evidence.
10. Inheritor list, genealogy completeness, relationship evidence, privacy and publication authorization.
11. Campus photo copyright/portrait/underage permissions and certificate display conditions.
12. Public editorial, publication, withdrawal, rollback, and rights-review workflow.
13. Final per-asset HFB reuse decisions and target infrastructure scale/SLA.

## 10. Blockers

### P0

- **P0-NPG-01:** live parent checkout is dirty in frozen `scripts/core_completion/dry_run.py`; no cleanup was authorized or performed.
- **P0-NPG-02:** original Gemini proposal artifact is missing, preventing a provably exhaustive proposal separation audit.
- **P0-NPG-03:** no client asset master register with physical files, provenance, rights, and digitization status; content-dependent scope/count claims cannot be fact-bound.

### P1 risks

- `README.md:43` may cause an operator to mistake `d08e343` for the formal completion baseline.
- HFB metadata/file paths may be mistaken for delivered files or publication rights.
- HFB research-workbench architecture may be copied into the visitor portal without a publication boundary.
- HFB domain schemas and HFM frozen canonical models overlap but are not row-compatible.
- Medical terms and AI/search features can drift from historical research into treatment recommendation.
- HFB test/runtime claims in repository documents are candidate-bound historical evidence; this NPG audit did not re-run HFB runtime/browser/database gates.
- HFM foundation tests are green, but product/user-journey coverage is absent because the product surfaces are absent.

## 11. Evidence Index

| Evidence | Bound object/location | Supports |
| --- | --- | --- |
| Git status/log/refs/ancestry/tree/blob checks | HFM repository; `0167b170` and named ancestors | Baseline identity, dirty worktree, candidate/archive distinction |
| `docs/governance/BASELINE-MANAGEMENT.md` | HFM `0167b170` | Formal baseline, source/candidate chain, boundaries |
| CORE-COMPLETION acceptance archive/evidence + JSON artifact | HFM `0167b170` | 28/28, 9/9, no production import, no CD-7 |
| Frozen domain docs, migrations, models, repositories, APIs/router | HFM `0167b170` | Current capability facts |
| Fresh `/private/tmp` baseline gates | Exported HFM Git object | Backend/frontend build/test/type/lint evidence |
| HFB tree, routes, models, services, tests, license, project-state | HFB `03755b57` | Asset inventory, coupling, license and candidate evidence boundaries |
| `huangfu_mi_exhibition.json` parsed counts | HFB `03755b57` | 515 papers, 92 editions, absent structured asset arrays |
| Client-confirmed requirements in NPG instruction | This audit authority | L1 requirements, priorities, boundaries, known asset families |

## 12. Recommendation for NPG-6

Do not authorize Phase 1 and do not freeze a Phase 1 scope, DAG, DoD, stack, or migration from this report.

Before NPG-6 scope arbitration, obtain:

1. a separately confirmed clean checkout of `0167b170` or an explicit decision about the existing worktree diff;
2. the original Gemini proposal artifact;
3. the client asset master register and representative physical files;
4. provenance, rights, official-name/heritage, genealogy, and publication-authorization evidence;
5. client approval of user journeys and the public/research content handoff;
6. review of NPG-4 candidates to select only assets whose value exceeds coupling and migration risk.

NPG-6 should arbitrate facts into candidate scope and explicit unresolved items. Any implementation authorization must remain a separate governance act.

## Final verdict

**NOT_READY_FOR_SCOPE_ARBITRATION**
