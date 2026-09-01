# HFM-UX2-P2 Implementation Evidence v1

Status: UX2-P2 IMPLEMENTATION CANDIDATE · ready for independent audit
(pre-WP baseline `8b1bd83adc4a478c3e6f848ba9a67a412dd13d0c`)

## 1. WP Identity

```text
WP = UX2-P2 · Jiayi Work / Edition
PRE_WP_BASELINE = 8b1bd83adc4a478c3e6f848ba9a67a412dd13d0c
P2_AUTHORITATIVE_DEPENDENCIES = [UX2-P0]  (WP DAG: P2 ← P0 only)
DEPENDENCIES_SATISFIED = YES (P0 FROZEN 2b315795… · P1 FROZEN 8b1bd83…)
P2_CONTRACT_SOURCE =
  docs/ux2/g4/HFM-UX2-G4-WORK-PACKAGE-DAG-v1.md (UX2-P2 row)
  docs/ux2/g4/HFM-UX2-G4-PRODUCTION-IMPLEMENTATION-CONTRACT-v1.md (candidate 04)
  docs/ux2/g4/HFM-UX2-G4-ACCEPTANCE-AND-ROLLBACK-CONTRACT-v1.md
```

## 2. Contract Reconstruction (authoritative)

```text
OBJECTIVE = Render edition records via BibliographicRecord (存目 per U-05);
            align work-profile; keep chronology ≠ lineage + DATA-GAP.
MODIFY_ALLOWLIST = apps/frontend/src/views/jiayi/JiayiView.vue
CREATE_ALLOWLIST = apps/frontend/src/__tests__/ux2_p2_*.spec.ts
                  apps/frontend/e2e/ux2-p2-*.spec.ts
READ_ONLY = data/jiayiView.ts · types · P0 primitives · Timeline ·
            EditionLineageImage · services · router
FORBIDDEN = data/types/router changes · digitization flags (U-05) ·
            genealogy edges · backend · clinical content
AUTHORIZED_PRESENTATION_STATES =
  METADATA_ONLY (存目 for all 19 editions) · UNSTRUCTURED_OR_INCOMPLETE
  (DATA-GAP 版本关系整理中)
NEGATIVE_BOUNDARIES = NB-03 (no edition genealogy) · NB-08 · NB-06 · NB-05
ACCEPTANCE_CRITERIA = ui08-style suite; NB-03 assertions; axe; responsive
ROLLBACK_BOUNDARY = view-only; revert = restore view
DEFINITION_OF_DONE = 19 editions render via BibliographicRecord with 存目;
                     DATA-GAP + chronology ≠ lineage captions intact; suite green
```

## 3. Implementation

| File | Change |
| --- | --- |
| `apps/frontend/src/views/jiayi/JiayiView.vue` | Edition collection now renders each of the 19 audited edition records through the shared **BibliographicRecord** primitive with `METADATA_ONLY 存目` (via the P0 `resolvePresentationState` / `presentationLabel` mapping); public source label only (`JIAYI_PUBLIC_SOURCES.lunzhu`); added `版本关系整理中` state badge (UNSTRUCTURED_OR_INCOMPLETE) above the lineage visual; `.edition-card` restyled as a plain list wrapper; no digitized-resource flag (U-05), no genealogy edges (NB-03), chronology ≠ lineage + DATA-GAP captions intact |
| `apps/frontend/src/__tests__/ux2_p2_jiayi.spec.ts` | 11 tests — 19 primitives/存目, metadata, U-05 no fake CTA, NB-03/06/05, DATA-GAP state, chronology ≠ lineage, heading, axe |
| `apps/frontend/e2e/ux2-p2-jiayi.spec.ts` | 3 tests — 19 records + 存目 in browser, browser axe 0, responsive 375/1280/1920 |

## 4. P2 State Matrix

```text
source/runtime condition            → presentation state       → UI rendering
19 × edition status METADATA_ONLY   → METADATA_ONLY            → 存目 badge + record
JIAYI_EDITION_RELATIONS DATA-GAP    → UNSTRUCTURED_OR_INCOMPLETE → 版本关系整理中 badge
year-sorted editions                → chronology (≠ lineage)  → timeline + caption
digitized-resource flag (U-05)      → ABSENT (no field)       → never rendered
NO_FALSE_RESOURCE_READY = YES · NO_FAKE_COMPLETION = YES · NO_HIDDEN_DATA_GAP = YES
```

## 5. Provenance

```text
SOURCE_IDENTITY = TRACEABLE (every edition from jiayiView.ts audited register)
SOURCE_TITLE = TRACEABLE (edition.title / period / imprint)
CITATION = TRACEABLE (public source label JIAYI_PUBLIC_SOURCES.lunzhu)
AGGREGATE_FALSE_ATTRIBUTION = NONE
TEST_AUTHORED_PROVENANCE_AS_PRODUCTION_EVIDENCE = NO
```

## 6. Navigation / Interaction

Editions are non-interactive records (no fake CTAs); page navigation (hero jump
links, enlarge-dialog) unchanged and already keyboard-operable (ui08 e2e).
`NAVIGATION = PASS · KEYBOARD = PASS · FOCUS = PASS · NO_DEAD_ROUTE = YES`.

## 7. Acceptance Criteria Results

```text
P2 DoD:
  19 editions via BibliographicRecord with 存目      PASS
  DATA-GAP + chronology ≠ lineage captions intact   PASS
  suite green                                       PASS
```

## 8. Test / Quality Results (independently reproduced)

```text
TARGETED_TESTS      = 11/11 PASS (ux2_p2_jiayi.spec.ts)
P0_REGRESSION_TESTS = 58/58 PASS (P0_REGRESSION = NONE)
P1_REGRESSION_TESTS = 19/19 PASS (ux2_p1_person.spec.ts — P1_REGRESSION = NONE)
FULL_VITEST         = 283/283 PASS (31 files)
VUE_TSC             = PASS (0 errors)
ESLINT              = 0_ERRORS_950_WARNINGS (actual reproduction; repo-wide
                      pre-existing style-warning baseline; gate is errors)
VITE_BUILD          = PASS
PLAYWRIGHT          = 75/75 PASS (72 existing + 3 UX2-P2)
BROWSER_AXE         = 0 (real browser, full rule set)
RESPONSIVE_375/1280/1920 = PASS · HORIZONTAL_OVERFLOW = NONE
```

## 9. Scope Audit

```text
AUTHORIZED_DELTA = JiayiView.vue · ux2_p2_jiayi.spec.ts · e2e/ux2-p2-jiayi.spec.ts
FORBIDDEN_PRODUCTION_PATH_DELTA = ZERO
P0_PRIMITIVE_IMPLEMENTATION_DELTA = ZERO
P1_ACCEPTED_IMPLEMENTATION_DELTA = ZERO
P3/P4/P5/P6/P7_DELTA = ZERO · UNRELATED_DELTA = ZERO
```

## 10. Worktree & Rollback

```text
WORKTREE = authorized delta only (staged for candidate commit)
ROLLBACK_TARGET = 8b1bd83adc4a478c3e6f848ba9a67a412dd13d0c (PRE_WP_BASELINE)
Rollback boundary = view-only; revert = restore JiayiView + drop P2 test files
```

## 11. Commit

```text
UX2_P2_IMPLEMENTATION_CANDIDATE = f973412629edd34e37b74a02e8aaa5a003bb6074 (ACCEPTED)
CANDIDATE_PARENT = 8b1bd83adc4a478c3e6f848ba9a67a412dd13d0c
P0-1 = OPEN_P2_NON_BLOCKING_REVERIFY_AT_P6 (untouched — no DHObjectLayout change)
```
