# HFD Phase 0 Re-Acceptance + HFM Provisional Architecture Baseline Validation

Date: 2026-08-27 (Asia/Shanghai)  
Mode: READ-ONLY audit; this file is the only generated deliverable.

## 1. Final Verdict

**CONDITIONAL PASS**. The HFB deliverables are now in the source-of-truth
repository and their central capability conclusions are directionally sound.
The HFM provisional baseline is **VALIDATED_WITH_CORRECTIONS**, not eligible
for immediate Frozen promotion: the reuse matrix omits required capabilities,
labels its rows `Frozen v1.0` while still provisional, and overstates reuse for
public Library/Search surfaces. Current environment restrictions also prevent
fresh PG/browser/Node runtime proof.

## 2. Repository Baseline

| Repository | Branch | HEAD | Worktree at audit start |
| --- | --- | --- | --- |
| HFB (`/Users/likeming/Sites/hfb`) | `main` | `2d98b610a63d2b0347ff5ec7fcd1d598913f3521` | `M docs/12-context/project-state-2026-08-26.md`; `docs/audit/` untracked delivery |
| HFM (`/Users/likeming/Sites/hfm`) | `main` | `7583ef757b135a7d2cf45834f54b9e6fc91f053d` | `M docs/12-context/project-state-2026-08-26.md`; `docs/audit/` pre-existing/untracked |

HFM provisional baseline: `ba4f615401b573f69b0aef1353d9b8262b6ea8d4`.  
Governance HEAD: `7583ef7`; it correctly describes `ba4f615` as Provisional.

## 3. Previous BLOCK Root Cause

**RESOLVED.** Both required files exist at
`/Users/likeming/Sites/hfb/docs/audit/`, are v1.1, and name HFB branch `main`,
HEAD `2d98b610…`, working-tree status, generation time, and evidence path.

## 4. Claude v1.1 Corrections Verification

| Correction | Verdict | Independent result |
| --- | --- | --- |
| 1. Report/HEAD binding | **CONFIRMED** | File headers and HFB `rev-parse` match; both reports identify `2d98b610…`. |
| 2. Reuse call-chain evidence | **PARTIAL** | Core Person/Book/Source/Evidence/Citation/Reader chains are present, but some domain rows still stop at model/migration (for example `VersionRelation`, `TCMEntity`, `Institution`); “every item” is not demonstrated. |
| 3. Five implementation layers | **CONFIRMED** | Reports explicitly distinguish SPECIFIED, IMPLEMENTED, ENFORCED, TESTED, RUNTIME and retain Chronology/Geography as DOC_ONLY. |
| 4. Snapshot taxonomy | **CONFIRMED** | Publication Model, Publication Snapshot, and Research Replay Snapshot are separately defined; only replay snapshot is implemented. |
| 5. Runtime boundary | **PARTIAL** | The report honestly lists PG-trigger runtime, anonymous access, medical display enforcement, and stable public URI as unverified; those boundaries could not be freshly closed here. |

## 5. Counter-Evidence Recheck

All 12 items were re-read against HFB source and the v1.1 register.

| # | Result | Recheck |
| ---: | --- | --- |
| 1 | CLAUDE CONFIRMED | Version/VersionRelation/version-center capability exists. |
| 2 | CLAUDE CONFIRMED | SourceRef → Evidence → Citation lineage and tests exist. |
| 3 | CLAUDE CONFIRMED | Candidate manifest/artifact immutability and hash paths exist. |
| 4 | CLAUDE CONFIRMED | Admission is a multi-stage state machine, not one published flag. |
| 5 | CLAUDE CONFIRMED | `production_query_policy.py` requires approved admission plus successful promotion, and fails closed for unsupported models; fresh runtime was unavailable. |
| 6 | CLAUDE CONFIRMED | Research replay snapshot is not presented as a public publication snapshot. |
| 7 | CLAUDE CONFIRMED | Reader exists, but the public anonymous/published reader requires extension. |
| 8 | CLAUDE CONFIRMED | RBAC and cross-workspace negative-test claims have source/test references. |
| 9 | CLAUDE CONFIRMED | Document rights fields are separated from missing media-rights governance. |
| 10 | CLAUDE CONFIRMED | Evidence gating is not claimed to be medical compliance. |
| 11 | CLAUDE CONFIRMED | Audit models/triggers/migrations are cited, not documentation-only. |
| 12 | CLAUDE CONFIRMED | Stable trace/hash identity is not equated with a defined public canonical URI. |

Independent code anchors: `middleware/auth.py:39-61` requires a valid JWT;
`services/production_query_policy.py:75-136` applies the fail-closed
production predicate; `models/production_promotion.py:67-71` stores hashes,
not a publication content copy; `models/image.py:21-31` has only basic image
metadata. No `PublicationSnapshot` or `PublishedRepresentation` symbol exists
under HFB backend/frontend source.

## 6. Test Baseline Recheck

Official entrypoints were read from `Makefile`, `pyproject.toml`, root and
frontend `package.json`, and `.github/workflows/{lint,test,build}.yml`.

| Check | Fresh result | Interpretation |
| --- | --- | --- |
| Ruff check + format | PASS (`388 files already formatted`) | Fresh static proof. |
| CI strict mypy, 22 files | **FAIL: 8 errors**, all in `api/v1/source_admissions.py` | Existing G15 remains open; errors are missing annotations/generic arguments. |
| ESLint | **UNAVAILABLE** | Official `--cache` and no-cache attempts hit HFB sandbox `EPERM` on `.eslintcache`. |
| Prettier | **FAIL** | Existing formatting warnings plus a syntax error in `apps/frontend/src/pages/prototype/Phase2PrototypePage.vue:369` (literal `<projectId>` inside `<code>`). |
| vue-tsc | **UNAVAILABLE** | HFB sandbox blocked `dist/tsconfig.tsbuildinfo`; disabling incremental conflicts with composite config. |
| Vite/Vitest | **UNAVAILABLE** | Vite could not write `apps/frontend/node_modules/.vite-temp`. |
| Backend unit+integration | **FAIL: 2610 passed, 9 failed, 106 errors, 700.40s** | 106 errors and the 9 failures are dominated by the same sandbox-blocked PostgreSQL/lifespan path (`PermissionError: [Errno 1]`); this is not a clean candidate PASS. |
| PG / ES / MinIO / backend HTTP | UNAVAILABLE | PG connection returned sandbox `Operation not permitted`; ports 8000/9200/9000 refused. |
| Browser E2E | NOT RUN | No live backend/PG runtime was available. |

The prior v1.1 counts (`2724/0/0`, `807`, `27/27`) are retained only as
historical, candidate-bound evidence. They do not become fresh runtime PASS in
this environment. The reported `2561/9/106` versus `2724/0/0` explanation is
plausible and consistent with the observed PG sandbox restriction, but cannot
be independently upgraded beyond **INCONCLUSIVE** without a reachable PG
environment and a clean candidate-bound artifact.

G15 classification: **ENTRY GATE for Phase 1 business coding**, **not a reason
to redo Phase 0**. It is also a Phase 1 quality-gate deliverable; it remains a
real blocking CI defect and must not be hidden or fixed in this audit.

## 7. HFB Capability Reality Matrix

| Capability | HFB reality | Codex verdict | Confidence |
| --- | --- | --- | --- |
| Authentication | JWT/cookie auth with token-version revocation; authenticated routes | REUSE | HIGH |
| RBAC | 8 roles and permission guards; SoD is incomplete | EXTEND | HIGH |
| Person | Model/repository/service/API/test; verified filtering | REUSE | HIGH |
| Ancient Text | FRBR, Book/ClassicalVersion/Version/Chapter/Passage and reader assets | EXTEND | HIGH |
| Source | Source admission with staged reviews and audit | REUSE | HIGH |
| Evidence | Evidence levels, taint, candidate publication grounding | REUSE | HIGH |
| Citation | Evidence-targeted persistence and withdrawn-reference rejection | REUSE | HIGH |
| Reader | Research reader/runtime evidence; no anonymous publication reader | EXTEND | HIGH |
| Library | Existing research/library pages; public withdrawn/publication semantics incomplete | EXTEND | MEDIUM |
| Search | PostgreSQL ILIKE service/API; ES is reserved/conditional, auth applies | EXTEND | HIGH |
| Knowledge | Knowledge pages and v4 visualization for authenticated workbench | REUSE | MEDIUM |
| Workspace | ResearchSession/workspace ownership and ACL paths | REUSE | HIGH |
| Workflow | Research workflow service and v4 research API | REUSE | HIGH |
| Reports | Research reports and markdown export | REUSE | HIGH |
| Export | Markdown exists; PDF/print and public disclaimers do not | EXTEND | HIGH |
| AI Copilot | Evidence-gated AI service; medical guardrails absent | EXTEND | HIGH |
| Media | Static exhibition video references; no governed media asset model | DEPRECATE | HIGH |
| Rights | Document/version/admission rights fields; media rights lifecycle absent | EXTEND | HIGH |
| Publication | Promotion/hash and fail-closed research query; no publication model/snapshot | NEW | HIGH |
| Snapshot | Research replay snapshot exists; public publication snapshot absent | EXTEND | HIGH |
| Teaching | v4 education evidence gate, authenticated and not medical-compliance complete | EXTEND | HIGH |
| Audit | Several append-only domain audit logs; no single public-content AuditEvent | EXTEND | HIGH |

## 8. HFM Reuse Matrix Validation

**CORRECTIONS REQUIRED.** The 18-row matrix has sound core classifications for
Source, Evidence, Citation, Publication, Media, and the rights split. It is
not complete against the required capability list: Workspace, Workflow, Audit,
and Snapshot are absent. Library and Search are marked plain `REUSE` although
their stated HFM target is Public Portal and HFB lacks anonymous published
access; both should be `EXTEND`. Ancient Text and Person are acceptable only
because their migration strategies explicitly include public extension.

Every row also says `Frozen v1.0` while the document header says Provisional.
That is a governance contradiction and must be corrected before freeze.

### False NEW findings

No material false NEW was found. Publication and governed Media are genuinely
missing. The omitted Workspace/Workflow/Audit/Snapshot rows are omissions, not
false NEW decisions.

### False REUSE findings

1. **Library** — change to `EXTEND` for anonymous/public publication filters.
2. **Search** — change to `EXTEND` for anonymous public access and publication
   index semantics; ES selection remains conditional.
3. **Ancient Text/Public Reader boundary** — keep the explicit public extension
   in the strategy and do not treat research Reader as a complete public asset.

## 9. HFM Technical Baseline Validation

**CORRECTIONS REQUIRED.** Most choices reuse HFB's Python/FastAPI/Vue/PostgreSQL
family and respect the no-HFB-runtime rule. The following are the correct
technical classifications:

| Area | Verdict | Basis |
| --- | --- | --- |
| Backend / Frontend / Database / Testing / CI | JUSTIFIED | Proven HFB stack and explicit CI sources. |
| Cache / Queue (Redis) | JUSTIFIED_WITH_CONDITIONS | HFB role is claimed but Redis was not independently verified in the report/runtime; introduce only for measured need. |
| Object Storage (MinIO) | JUSTIFIED_WITH_CONDITIONS | G4 media requirement justifies it, but HFB MinIO was not running in the audited environment. |
| Search (Elasticsearch) | JUSTIFIED_WITH_CONDITIONS | HFB has PostgreSQL ILIKE MVP and ES reservation; public/research ES needs target-scale/index requirements. |
| Observability | UNKNOWN | Audit/logging exists, but an observability stack and runtime SLO evidence are not established. |
| Auth / RBAC | JUSTIFIED_WITH_CONDITIONS | Port proven auth/RBAC, then implement anonymous Visitor and SoD. |
| Export | JUSTIFIED_WITH_CONDITIONS | Markdown is proven; PDF/print/disclaimer requirements are new. |
| Media Processing | JUSTIFIED_WITH_CONDITIONS | Needed for G4 only; no unnecessary processing platform is selected. |

## 10. Architecture Greenfield + Capability Brownfield

**PARTIALLY_ALIGNED.** HFM is an independent repository and explicitly rejects
permanent HFB runtime coupling, which is aligned. It also identifies many
selective ports. The incomplete matrix and public-surface `REUSE` overstatements
prevent a fully aligned verdict until corrected.

## 11. HFM Runtime Dependency Boundary

**ALIGNED.** HFM baseline explicitly rejects importing/calling HFB runtime and
requires Port/Adapt artifacts. No HFM code exists yet that creates a permanent
runtime dependency.

## 12. HFM Data Inheritance Strategy

**ALIGNED_WITH_CONDITIONS.** The baseline points to Port/Adapt and a later
canonical HFM model; it does not require copying HFB's live database. Phase 1
must define migration/import contracts for Entity, Assertion, Evidence, Source,
Citation, Version, Publication, Rights, and Teaching before PI migration.

## 13. Baseline Governance Validation

**CORRECT.** `BASELINE-MANAGEMENT.md` correctly maps `82f5e64` to repository
init, `ba4f615` to Provisional Architecture Baseline, and `7583ef7` to current
governance. It does not call `ba4f615` Frozen. The matrix's row-level `Frozen`
labels nevertheless need correction.

## 14. Phase 1 Gate Classification

| Item | Classification | Rationale |
| --- | --- | --- |
| G1 医学合规 | PHASE 1 DELIVERABLE | Design and enforce before medical public release. |
| G2 匿名访问策略 | PHASE 1 DELIVERABLE | Define public route/auth semantics before portal delivery. |
| G3 发布快照建模 | PHASE 1 DELIVERABLE | New publication model and snapshot isolation. |
| G4 非遗媒体架构 | PHASE 1 DELIVERABLE | Rights-aware asset lifecycle is new target capability. |
| G7 Separation of Duties | PHASE 1 DELIVERABLE | Implement before governed publication workflows. |
| G14 测试环境/依赖 | ENTRY GATE | Reliable PG/ES/MinIO test path is required for business coding acceptance. |
| G15 quality gate/mypy | ENTRY GATE | Blocking CI type errors remain open; do not conceal them. |

## 15. Monorepo Skeleton Entry Decision

MONOREPO SKELETON: **ALLOWED**  
PI MIGRATION: **NOT ALLOWED**  
PHASE 1 BUSINESS CODING: **NOT ALLOWED**

Skeleton work is separable from migration and business implementation. This
decision does not authorize any of those activities in this read-only audit.

## 16. P0 / P1 / P2 / P3 Findings

| Level | Findings |
| --- | --- |
| P0 | None newly found in the HFB source-admission/evidence lineage; anonymous/public publication and medical/media governance remain pre-release gaps. |
| P1 | HFM matrix incomplete; row statuses contradict provisional governance; Library/Search public reuse overstated; G14/G15 prevent reliable Phase 1 coding acceptance. |
| P2 | Observability basis is unspecified; ES/Redis/MinIO conditions need measurable requirements; public canonical URI/version semantics remain undefined. |
| P3 | Current sandbox prevents fresh PG/HTTP/browser and cache-writing Node checks; HFB Python is 3.13 while CI declares 3.12. |

## 17. Required Corrections Before Freeze

1. Expand the HFM reuse matrix to include Workspace, Workflow, Audit, Snapshot
   and all requested capabilities, with a Model → Service → API → Test/Runtime
   evidence chain or an explicit unavailable boundary.
2. Change public Library/Search classifications to EXTEND and normalize every
   matrix row status from `Frozen v1.0` to `Provisional v1.0`.
3. Resolve G14/G15 in a reachable, candidate-bound CI-compatible environment;
   retain the eight mypy errors as open until the blocking gate is actually
   closed.

## 18. Frozen Baseline Eligibility

**NOT ELIGIBLE.** The core architecture direction is salvageable and does not
require a new Phase 0, but the three corrections above must land through a
subsequent governance change before promotion.

## HFM Final Additional Ruling

**HFM PROVISIONAL BASELINE: VALIDATED_WITH_CORRECTIONS**

`ba4f615` is not rejected: its greenfield repository/no-runtime-coupling and
selective reuse direction is supported by HFB facts. It is not yet eligible to
be called Frozen.

## Terminal Summary

```text
HFD PHASE 0 RE-ACCEPTANCE
+ HFM BASELINE VALIDATION
======================================

HFB
---
Branch: main
HEAD: 2d98b610a63d2b0347ff5ec7fcd1d598913f3521
Working Tree: M docs/12-context/project-state-2026-08-26.md + docs/audit/ delivery

HFM
---
Branch: main
HEAD: 7583ef757b135a7d2cf45834f54b9e6fc91f053d
Working Tree: pre-existing M docs/12-context/project-state-2026-08-26.md + docs/audit/
Repository Init Baseline: 82f5e64
Provisional Architecture Baseline: ba4f615
Governance HEAD: 7583ef7

Previous BLOCK Root Cause: RESOLVED
Claude v1.1: PARTIAL
HFB Re-Acceptance: CONDITIONAL PASS
HFM Reuse Matrix: CORRECTIONS REQUIRED
HFM Technical Baseline: CORRECTIONS REQUIRED
Architecture Greenfield + Capability Brownfield: PARTIAL
HFM PROVISIONAL BASELINE: VALIDATED_WITH_CORRECTIONS
Gate Classification:
G1: PHASE 1 DELIVERABLE
G2: PHASE 1 DELIVERABLE
G3: PHASE 1 DELIVERABLE
G4: PHASE 1 DELIVERABLE
G7: PHASE 1 DELIVERABLE
G14: ENTRY GATE
G15: ENTRY GATE
MONOREPO SKELETON: ALLOWED
PI MIGRATION: NOT ALLOWED
PHASE 1 BUSINESS CODING: NOT ALLOWED
P0 Blockers: 0 new; public release gaps remain
P1 Major: 4
P2 Minor: 3
P3 Observations: 4
FINAL VERDICT: CONDITIONAL PASS
Frozen Baseline Eligibility: NOT ELIGIBLE
Required Corrections:
1. Complete and correct the HFM reuse matrix.
2. Normalize provisional/frozen status and public Library/Search verdicts.
3. Close G14/G15 with candidate-bound CI-compatible proof.
```
