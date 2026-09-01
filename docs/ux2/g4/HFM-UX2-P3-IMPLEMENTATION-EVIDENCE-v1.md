# HFM-UX2-P3 Implementation Evidence v1

Status: UX2-P3 IMPLEMENTATION CANDIDATE · ready for independent audit
(pre-WP baseline `dba82e2aeaed31a815178a2745ffe484d249c7d3`)

## 1. WP Identity

```text
WP = UX2-P3 · Heritage Living Archive
PRE_WP_BASELINE = dba82e2aeaed31a815178a2745ffe484d249c7d3
P3_AUTHORITATIVE_DEPENDENCIES = [UX2-P0]  (WP DAG: P3 ← P0 only)
DEPENDENCIES_SATISFIED = YES (P0/P1/P2 all FROZEN)
P3_CONTRACT_SOURCE =
  docs/ux2/g4/HFM-UX2-G4-WORK-PACKAGE-DAG-v1.md (UX2-P3 row)
  docs/ux2/g4/HFM-UX2-G4-PRODUCTION-IMPLEMENTATION-CONTRACT-v1.md (candidate 05)
  docs/ux2/g4/HFM-UX2-G4-ACCEPTANCE-AND-ROLLBACK-CONTRACT-v1.md
```

## 2. Contract Reconstruction (authoritative)

```text
WP_TITLE = Heritage Living Archive
OBJECTIVE = Make historical vs contemporary evidence-context separation
            explicit; recognition as secondary metadata (8/8); PARTIAL
            lineage preserved.
MODIFY_ALLOWLIST = apps/frontend/src/views/heritage/HeritageView.vue
CREATE_ALLOWLIST = apps/frontend/src/__tests__/ux2_p3_*.spec.ts
                  apps/frontend/e2e/ux2-p3-*.spec.ts
READ_ONLY = data/heritageView.ts · types · P0 primitives · LineageGraph ·
            Timeline · services · router
FORBIDDEN = data/types/router changes; honor-wall treatment; lineage
            inference; clinical content
NEGATIVE_BOUNDARIES = NB-04 (no uninterrupted lineage) · NB-05 (clinical) ·
                      NB-01 · honor-wall prohibition (N-14)
PRESENTATION_STATES = RESOURCE_READY (confirmed nodes/events) ·
                      UNSTRUCTURED_OR_INCOMPLETE (PARTIAL lineage 谱系整理中)
DEFINITION_OF_DONE = two contexts explicit; recognition stays secondary;
                     PARTIAL gap explicit; suite green
ROLLBACK_BOUNDARY = view-only; revert = restore view
```

## 3. Implementation

| File | Change |
| --- | --- |
| `apps/frontend/src/views/heritage/HeritageView.vue` | Explicit **HISTORICAL_TEXTUAL_CONTEXT** (历史文献语境) and **CONTEMPORARY_LIVING_ARCHIVE_CONTEXT** (当代活态档案语境) evidence-context bands (G1-A §4); 传承谱系 (confirmed nodes + PARTIAL gap) moved into the historical band with a truthful `谱系整理中` state badge (UNSTRUCTURED_OR_INCOMPLETE); recognition remains secondary metadata (8/8, no honor wall); heading hierarchy H1 → H2 (context) → H3 (sections) → H4 (sub); 第六代名医 designation exact; removed the internal register key `zzcl` from the public evidence note (PUBLIC_SOURCE_ONLY) |

## 4. Data Truth / Source of Truth

```text
SOURCE_OF_TRUTH = apps/frontend/src/data/heritageView.ts (single source;
                  no second heritage registry)
SECOND_HERITAGE_SOURCE_OF_TRUTH = NO
RUNTIME_STATE = static governed data (no API dependency on the heritage page)
PUBLICATION_STATE = governed (public labels only; internal paths never rendered)
MEDIA_AVAILABLE = N/A — 媒体报道 is a TEXT record list (no media files)
DIGITIZED_RESOURCE_AVAILABLE = N/A (no digitized cert/media claims; 证书图像整理中)
```

## 5. P3 State Matrix

```text
source/runtime condition                → presentation state       → UI rendering
HERITAGE_LINEAGE (confirmed nodes)      → RESOURCE_READY           → LineageGraph nodes
LINEAGE_STRUCTURING PARTIAL (gap)       → UNSTRUCTURED_OR_INCOMPLETE → 谱系整理中 badge + gap note
HERITAGE_RECOGNITIONS (8 records)       → RESOURCE_READY           → 认定与荣誉 list (secondary)
certificate images (not digitized)      → METADATA_ONLY (note)     → 证书图像整理中 note
NO_FALSE_RESOURCE_READY = YES · NO_FAKE_DIGITIZED_STATUS = YES
NO_FALSE_PLAYABILITY = YES · NO_FALSE_DOWNLOADABILITY = YES
```

## 6. Designation & Lineage Integrity

```text
第六代名医 designation = EXACT (HERITAGE_PERSON.generationTitle; hero + profile;
                          no unsupported 第六代传承人 variant)
UNSUPPORTED_HERITAGE_LINEAGE_CLAIMS = NONE
UNSUPPORTED_PARENT_CHILD_EDGES = NONE
UNSUPPORTED_TEACHER_STUDENT_EDGES = NONE
UNSUPPORTED_GENERATION_INFERENCE = NONE
chronology ≠ lineage preserved (timeline in contemporary band only)
```

## 7. Provenance

```text
SOURCE_IDENTITY = TRACEABLE (public sourceName per record)
SOURCE_TITLE = TRACEABLE
CITATION_OR_REFERENCE = TRACEABLE (公开来源名 per record)
FALSE_SINGLE_SOURCE_ATTRIBUTION = NO
PUBLIC_SOURCE_ONLY = YES (register key zzcl removed from public note)
```

## 8. Acceptance Criteria Results

```text
P3 DoD:
  two contexts explicit                       PASS (labeled bands)
  recognition stays secondary (8/8)           PASS
  PARTIAL gap explicit                        PASS (谱系整理中 badge + note)
  suite green                                 PASS
```

## 9. Test / Quality Results (independently reproduced)

```text
TARGETED_TESTS      = 12/12 PASS (ux2_p3_heritage.spec.ts)
P0_REGRESSION_TESTS = 58/58 PASS (P0_REGRESSION = NONE)
P1_REGRESSION_TESTS = 19/19 PASS (P1_REGRESSION = NONE)
P2_REGRESSION_TESTS = 11/11 PASS (P2_REGRESSION = NONE)
FULL_VITEST         = 295/295 PASS (32 files)
VUE_TSC             = PASS (0 errors)
ESLINT              = 0_ERRORS_953_WARNINGS (actual reproduction; repo-wide
                      pre-existing style-warning baseline; gate is errors)
VITE_BUILD          = PASS
PLAYWRIGHT          = 79/79 PASS (75 existing + 4 UX2-P3)
BROWSER_AXE         = 0 (real browser, full rule set)
RESPONSIVE_375/1280/1920 = PASS · HORIZONTAL_OVERFLOW = NONE
NAVIGATION = PASS · KEYBOARD = PASS · FOCUS = PASS · NO_DEAD_ROUTE = YES
```

## 10. Scope Audit

```text
AUTHORIZED_PRODUCTION_DELTA = apps/frontend/src/views/heritage/HeritageView.vue
AUTHORIZED_TEST_DELTA = ux2_p3_heritage.spec.ts · e2e/ux2-p3-heritage.spec.ts
AUTHORIZED_EVIDENCE_DELTA = HFM-UX2-P2-IMPLEMENTATION-EVIDENCE-v1.md
FORBIDDEN_PRODUCTION_PATH_DELTA = ZERO
DATA/SERVICES/BACKEND/TYPES/ROUTER_DELTA = ZERO
P0_PRIMITIVE_IMPLEMENTATION_DELTA = ZERO
P1_ACCEPTED_IMPLEMENTATION_DELTA = ZERO
P2_ACCEPTED_IMPLEMENTATION_DELTA = ZERO
P4/P5/P6/P7_DELTA = ZERO · UNRELATED_DELTA = ZERO
```

## 11. Worktree & Rollback

```text
WORKTREE = authorized delta only (staged for candidate commit)
ROLLBACK_TARGET = dba82e2aeaed31a815178a2745ffe484d249c7d3 (PRE_WP_BASELINE)
Rollback boundary = view-only; revert = restore HeritageView + drop P3 test files
P0-1 = OPEN_P2_NON_BLOCKING_REVERIFY_AT_P6 (untouched — no DHObjectLayout change)
```

## 12. Commit

```text
UX2_P3_IMPLEMENTATION_CANDIDATE = <commit SHA recorded at delivery>
CANDIDATE_PARENT = dba82e2aeaed31a815178a2745ffe484d249c7d3
```
