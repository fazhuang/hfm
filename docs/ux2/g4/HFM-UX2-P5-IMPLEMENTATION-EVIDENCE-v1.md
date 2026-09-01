# HFM-UX2-P5 Implementation Evidence v1

Status: UX2-P5 IMPLEMENTATION CANDIDATE · ready for independent audit
(pre-WP baseline `6e77f2b6697f2e17f48b53910ddfeae051c3571b`)

## 1. WP Identity

```text
WP = UX2-P5 · Homepage Exhibition Narrative
PRE_WP_BASELINE = 6e77f2b6697f2e17f48b53910ddfeae051c3571b
P5_AUTHORITATIVE_DEPENDENCIES = [UX2-P0, UX2-P1, UX2-P2, UX2-P3, UX2-P4]
  (WP DAG: P5 ← P0 + P1 + P2 + P3 + P4)
DEPENDENCIES_SATISFIED = YES (P0..P4 all FROZEN)
P5_CONTRACT_SOURCE =
  docs/ux2/g4/HFM-UX2-G4-WORK-PACKAGE-DAG-v1.md (UX2-P5 row)
  docs/ux2/g4/HFM-UX2-G4-PRODUCTION-IMPLEMENTATION-CONTRACT-v1.md (candidate 07)
  docs/ux2/g4/HFM-UX2-G4-ACCEPTANCE-AND-ROLLBACK-CONTRACT-v1.md
```

## 2. Contract Reconstruction (authoritative)

```text
WP_TITLE = Homepage Exhibition Narrative
P5_OBJECTIVE = Align HomeView to frozen narrative grammar (already matching);
               apply state labels; verify cross-links to implemented surfaces.
P5_MODIFY_ALLOWLIST = views/HomeView.vue
P5_CREATE_ALLOWLIST = __tests__/ux2_p5_*.spec.ts · e2e/ux2-p5-*.spec.ts
P5_READ_ONLY = data/homeProjection.ts · data/researchProjection.ts · P0 primitives
P5_FORBIDDEN = new promotional/historical copy · news-portal layout ·
               data/homeProjection.ts modification · router/data/types/
               services/backend changes
P5_NEGATIVE_BOUNDARIES = NB-01 · NB-05 · G1-A §9 homepage boundary (N-09/N-13)
P5_DEFINITION_OF_DONE = narrative order/grammar conform; links resolve to
                        implemented surfaces; suite green
P5_ROLLBACK_BOUNDARY = view-only
```

## 3. HOMEPAGE_SOURCE_MATRIX (every narrative block traces to governed sources)

| Section | Domain | Source path / symbol | CTA destination |
| --- | --- | --- | --- |
| Hero | P1 | data/homeProjection.ts HOME_HERO (from corePerson) | /persons/person-huangfu-mi · /jiayi · /search |
| Metrics | P2/P4 | HOME_METRICS (from contentInventory) | — |
| 皇甫谧 | P1 | HOME_HUANGFU / CORE_PERSON_* | /persons/person-huangfu-mi |
| 《针灸甲乙经》 | P2 | HOME_JIAYI (from jiayiView) + lineage image | /jiayi |
| 文献与史料 | governed | HOME_LITERATURE | /yan · /archive |
| 非遗活态传承 | P3 | HOME_HERITAGE (from heritageView) | /heritage |
| 从资料到研究 | P4 | HOME_RESEARCH_STEPS | /research · /search · /reader |

```text
SECOND_HOMEPAGE_DOMAIN_SOURCE_OF_TRUTH = NO
HOMEPAGE_DATA_TRACEABILITY = PASS
HOMEPAGE_NARRATIVE = PRESENTATION_COMPOSITION
HOMEPAGE_AS_NEW_SOURCE_OF_TRUTH = FORBIDDEN (not done)
NEW_FRONTEND_DOMAIN_REGISTRY = FORBIDDEN (not done)
```

## 4. Implementation

| File | Change |
| --- | --- |
| `views/HomeView.vue` | Applied **P0 state labels** to the two surfaced data states: jiayi lineage figcaption now carries `版本关系整理中` (UNSTRUCTURED_OR_INCOMPLETE) alongside the DATA-GAP caption; heritage section carries `谱系整理中` (UNSTRUCTURED_OR_INCOMPLETE) alongside the PARTIAL lede. Homepage search form landmark named (`aria-label="平台内容检索"`) resolving the pre-existing duplicate-search-landmark axe issue on the home page. Narrative order, hero copy, metrics, CTAs unchanged (already conformant to the frozen grammar). |

## 5. P1–P4 Domain Truth Preservation

```text
P1_SEMANTICS_PRESERVED = YES — no fake media resource-ready/playability claim
P2_SEMANTICS_PRESERVED = YES — editions remain summary-only; no false
                         digitization; DATA-GAP state labeled; chronology ≠ lineage
P3_SEMANTICS_PRESERVED = YES — 第六代名医 exact; PARTIAL lineage labeled
                         谱系整理中; no honor-wall treatment
P4_SEMANTICS_PRESERVED = YES — no fake search counts/full-text claims; counts
                         from governed contentInventory
NARRATIVE_ORDER_CLAIMED_AS_FACTUAL_RELATION = NO
UNSUPPORTED_CROSS_DOMAIN_RELATIONSHIP_CLAIMS = NONE
HERO_COPY = GOVERNED · UNSUPPORTED_SUPERLATIVE = NONE
FALSE_COMPLETION_CLAIM = NONE · FALSE_AUTHORITY_CLAIM = NONE
CARD_DATA_TRACEABLE = YES · CARD_STATE_TRUTHFUL = YES · CARD_CTA_TRUTHFUL = YES
NO_FAKE_READ/PLAY/DOWNLOAD_CTA = YES
```

## 6. State / Media / Provenance / Performance

```text
P0_PRIMITIVE_INTEGRATION = PASS (P0 status vocabulary used; data-status =
                           UNSTRUCTURED_OR_INCOMPLETE)
P0_STATE_MAPPING = PASS · LOCAL_DUPLICATE_PRESENTATION_STATE_LOGIC = NO
MEDIA_SOURCE_TRACEABLE = YES (lineage PNG = JIAYI_LINEAGE_IMAGE_SRC governed asset)
PUBLIC_MEDIA_ONLY = YES · NO_FAKE_PLAYABILITY = YES
NO_FAKE_MEDIA_ADMISSION = YES · NO_FIXTURE_AS_PRODUCTION_MEDIA = YES
NO_INTERNAL_REGISTER_KEY_PUBLICLY_RENDERED = YES (no hfmzl/zzcl)
PROVENANCE = PASS · FALSE_ATTRIBUTION = NO · INTERNAL_IDENTIFIER_LEAK = NONE
NEW_HEAVY_VISUAL_DEPENDENCY = NO · UNBOUNDED_MEDIA_PRELOAD = NO
BLOCKING_AUTOPLAY_MEDIA = NO · UNAUTHORIZED_WEBGL/THREE/XR = NO
```

## 7. Negative Boundary Results

```text
NB-01 = PASS — no fabricated historical/promotional content
NB-05 = PASS — no clinical content
N-09 = PASS — no unverified marketing copy
N-13 = PASS — no news-portal homepage layout
SECOND_DOMAIN_SOURCE_OF_TRUTH = NO · FAKE_CTA = NO
UNSUPPORTED_CROSS_DOMAIN_CLAIMS = NONE · HONOR_WALL = NO
```

## 8. Test / Quality Results (independently reproduced)

```text
TARGETED_TESTS      = 12/12 PASS (ux2_p5_home.spec.ts)
P0_REGRESSION_TESTS = 58/58 PASS (P0_REGRESSION = NONE)
P1_REGRESSION_TESTS = 19/19 PASS (P1_REGRESSION = NONE)
P2_REGRESSION_TESTS = 11/11 PASS (P2_REGRESSION = NONE)
P3_REGRESSION_TESTS = 12/12 PASS (P3_REGRESSION = NONE)
P4_REGRESSION_TESTS = 13/13 PASS (P4_REGRESSION = NONE)
FULL_VITEST         = 324/324 PASS (34 files)
VUE_TSC             = PASS (0 errors)
ESLINT              = 0_ERRORS_963_WARNINGS (actual reproduction; repo-wide
                      pre-existing style-warning baseline; gate is errors)
VITE_BUILD          = PASS
PLAYWRIGHT          = 90/90 PASS (85 existing incl. ui03 + 5 UX2-P5)
BROWSER_AXE         = 0 (real browser, full rule set)
RESPONSIVE_375/1280/1920 = PASS · HORIZONTAL_OVERFLOW = NONE
NAVIGATION = PASS · NO_DEAD_ROUTE = YES · KEYBOARD = PASS · FOCUS = PASS
HEADING_HIERARCHY = PASS · LANDMARKS = PASS
```

## 9. Scope Audit

```text
AUTHORIZED_PRODUCTION_DELTA = apps/frontend/src/views/HomeView.vue
AUTHORIZED_TEST_DELTA = ux2_p5_home.spec.ts · e2e/ux2-p5-home.spec.ts
AUTHORIZED_EVIDENCE_DELTA = HFM-UX2-P5-IMPLEMENTATION-EVIDENCE-v1.md
FORBIDDEN_PRODUCTION_PATH_DELTA = ZERO
DATA/SERVICES/BACKEND/TYPES/ROUTER_DELTA = ZERO
P0_PRIMITIVE_IMPLEMENTATION_DELTA = ZERO
P1/P2/P3/P4_ACCEPTED_IMPLEMENTATION_DELTA = ZERO
P6/P7_DELTA = ZERO · UNRELATED_DELTA = ZERO
```

## 10. Worktree & Rollback

```text
WORKTREE = authorized delta only (staged for candidate commit)
ROLLBACK_TARGET = 6e77f2b6697f2e17f48b53910ddfeae051c3571b (PRE_WP_BASELINE)
Rollback boundary = view-only; revert = restore HomeView + drop P5 test files
P0-1 = OPEN_P2_NON_BLOCKING_REVERIFY_AT_P6 (untouched — no DHObjectLayout change)
```

## 11. Commit

```text
UX2_P5_IMPLEMENTATION_CANDIDATE = <commit SHA recorded at delivery>
CANDIDATE_PARENT = 6e77f2b6697f2e17f48b53910ddfeae051c3571b
```
