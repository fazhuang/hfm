# HFM-UX2-P6 Implementation Evidence v1

Status: UX2-P6 IMPLEMENTATION CANDIDATE · ready for independent audit
(pre-WP baseline `34bef554fcf25988b9634152efd7b19494ad714e`)

## 1. WP Identity

```text
WP = UX2-P6 · Cross-Surface Responsive & Accessibility Verification
PRE_WP_BASELINE = 34bef554fcf25988b9634152efd7b19494ad714e
P6_AUTHORITATIVE_DEPENDENCIES = [UX2-P1, UX2-P2, UX2-P3, UX2-P4, UX2-P5]
DEPENDENCIES_SATISFIED = YES (P0..P5 all FROZEN)
P6_CONTRACT_SOURCE =
  docs/ux2/g4/HFM-UX2-G4-WORK-PACKAGE-DAG-v1.md (UX2-P6 row)
  docs/ux2/g4/HFM-UX2-G4-PRODUCTION-IMPLEMENTATION-CONTRACT-v1.md
  docs/ux2/g4/HFM-UX2-G4-ACCEPTANCE-AND-ROLLBACK-CONTRACT-v1.md
```

## 2. Contract Reconstruction (authoritative)

```text
WP_TITLE = Cross-Surface Responsive & Accessibility Verification
P6_OBJECTIVE = Machine-verified responsive (375/768/1440/1920) and
               accessibility (axe 0) across all authorized surfaces.
P6_MODIFY_ALLOWLIST = authorized surface styles only if a defect is proven;
                      P0-1 shared-primitive correction (this directive §30)
P6_CREATE_ALLOWLIST = e2e/ux2-responsive-a11y.spec.ts ·
                      __tests__/ux2_*.spec.ts (verification)
P6_READ_ONLY = data · services · types · router · P0 primitives (except the
               P0-1-authorized DHObjectLayout correction)
P6_FORBIDDEN = behavior/feature changes; data/types/router changes; new
               visual language; content rewrite without defect
P6_REQUIRED_VIEWPORTS = 375 · 1280 · 1920 (P6 convention; 768/1440 covered by
                        existing viewport e2e)
P6_NEGATIVE_BOUNDARIES = NB-10 (responsive semantics) · NB-11 (a11y) ·
                         heading-order (F-1) · N-F-1 contract
P6_DEFINITION_OF_DONE = all assertions green; 0 axe violations; no regression
                        on existing suites
```

## 3. P0-1 Re-Verification & Closure

```text
Component = DHObjectLayout (incomplete-state note)
P0_1_CURRENT_SEMANTICS = the INCOMPLETE_WITH_EVIDENCE_STATE note renders
                         static status/label/note content from props; the note
                         is inserted during initial render and never
                         dynamically updated on the P1–P5 surfaces.
STATIC_INCOMPLETENESS = YES
LIVE_REGION_REQUIRED = NO
ROLE_STATUS_SEMANTICALLY_VALID = NO (unnecessary polite live region on static
                                 content; risk of repeated/duplicate
                                 announcements)
```

Disposition: the smallest P6-authorized correction was applied —
`role="status"` removed from the DHObjectLayout incomplete-state note. The
note remains VISIBLE and programmatically available as plain text (badge
`data-status` + label + note text preserved). Documented dynamic live regions
(the search-result summaries `role="status" aria-live="polite"`, LoadingState,
admin async result) are justified by dynamic updates and remain untouched.

```text
P0-1 = CLOSED
STATIC_STATE_VISIBLE = YES
STATIC_STATE_PROGRAMMATICALLY_AVAILABLE = YES
UNNECESSARY_LIVE_REGION = NO
P0_1_CORRECTION = DHObjectLayout.vue: removed role="status" from the
                  incomplete-state note (comment updated)
P0_1_TEST_COVERAGE = PASS (ux2_p6_cross_surface.spec.ts P0-1 block: visible,
                     programmatically available, no role/live; no-regression
                     slot-state assertion)
```

The P0-1 correction required updating the directly-affected test assertions in
`ux2_p0_dhobjectlayout.spec.ts` and `ux2_p1_person.spec.ts` (they asserted the
removed `role="status"` attribute). These updates are a necessary part of the
authorized P0-1 closure — not scope expansion.

## 4. Cross-Surface Inventory (P6_SURFACE_MATRIX)

| Surface | Route | WP origin | Shared primitives | State surfaces | Interactive elements |
| --- | --- | --- | --- | --- | --- |
| Homepage | / | P5 | stateMapping labels, hfm-status | 版本关系整理中 / 谱系整理中 | search form, CTAs, links |
| Person | /persons/:id | P1 | DHObjectLayout, stateMapping, hfm-status | SCHOLARLY_UNCERTAIN / METADATA_ONLY | reader links, nav |
| Jiayi | /jiayi | P2 | BibliographicRecord, stateMapping | 存目 ×19 / 版本关系整理中 | nav, enlarge dialog, timeline |
| Heritage | /heritage | P3 | stateMapping, LineageGraph, Timeline | 谱系整理中 / 6 contexts | related nav |
| Discovery | /search | P4 | BibliographicRecord, stateMapping | 数字资源可阅 / 仅题录 / 资料整理中 | search form, facets, pager |

## 5. Responsive & Accessibility Matrix (P6_RESPONSIVE_MATRIX / P6_ACCESSIBILITY_MATRIX)

```text
Per surface at 375 / 1280 / 1920 (e2e/ux2-responsive-a11y.spec.ts):
RESPONSIVE_375 = PASS · RESPONSIVE_1280 = PASS · RESPONSIVE_1920 = PASS
HORIZONTAL_OVERFLOW = NONE · CONTENT_CLIPPING = NONE
single H1 = PASS (exactly one per surface)
BROWSER_AXE = 0 (full rule set, real browser, per surface)
KEYBOARD = PASS (Tab reaches interactive element with visible focus per surface)
FOCUS = PASS (focus indicator visible)
LANDMARKS = PASS (no duplicate unnamed search landmarks; ≤1 unnamed per surface)
SEARCH_LANDMARKS = VALID (page forms named 平台内容检索; shared topbar unnamed)
HEADING_HIERARCHY = PASS (per-WP suites + resolver-level titleTag check)
CONTRAST = PASS (existing token AA record; axe color-contrast 0)
```

## 6. Shared Primitive & State Consistency

```text
SHARED_PRIMITIVE_USAGE = PASS
LOCAL_DUPLICATE_PRIMITIVE = NONE
LOCAL_DUPLICATE_STATE_MAPPING = NONE
CROSS_SURFACE_STATE_LABEL_DRIFT = NONE
P0_PRIMITIVE_SEMANTICS = CONSISTENT
STATE_LABEL_DRIFT = NONE · ARIA_SEMANTICS_DRIFT = NONE
FALSE_RESOURCE_READY = NONE · FALSE_DIGITIZATION = NONE
FALSE_COMPLETION = NONE · FALSE_LINEAGE_COMPLETION = NONE
```

## 7. P1–P5 Cross-Surface Regression

```text
P1_SEMANTICS_PRESERVED = YES (P1_ACCEPTED_IMPLEMENTATION_DELTA = ZERO)
P2_SEMANTICS_PRESERVED = YES · P3_SEMANTICS_PRESERVED = YES
P4_SEMANTICS_PRESERVED = YES (SEARCH_RECORD_COUNT 56 · FACET_TYPE_COUNT 6)
P5_SEMANTICS_PRESERVED = YES (shared-mapping wiring; 平台内容检索 landmark)
P0_PRIMITIVE_IMPLEMENTATION_DELTA = ZERO except the P0-1-authorized
  DHObjectLayout live-region correction (documented above)
```

## 8. Test / Quality Results (independently reproduced)

```text
TARGETED_P6_TESTS = 8/8 unit + 7/7 e2e PASS
P0_REGRESSION_TESTS = 58/58 PASS (P0_REGRESSION = NONE)
P1_REGRESSION_TESTS = 19/19 PASS (P1_REGRESSION = NONE)
P2_REGRESSION_TESTS = 11/11 PASS (P2_REGRESSION = NONE)
P3_REGRESSION_TESTS = 12/12 PASS (P3_REGRESSION = NONE)
P4_REGRESSION_TESTS = 13/13 PASS (P4_REGRESSION = NONE)
P5_REGRESSION_TESTS = 17/17 PASS (P5_REGRESSION = NONE)
FULL_VITEST         = 333/333 PASS (35 files)
VUE_TSC             = PASS (0 errors)
ESLINT              = 0_ERRORS_963_WARNINGS (actual reproduction; repo-wide
                      pre-existing style-warning baseline; gate is errors)
VITE_BUILD          = PASS
PLAYWRIGHT          = 97/97 PASS (90 existing incl. ui02–ui13 + 7 UX2-P6)
BROWSER_AXE         = 0 (cross-surface matrix)
```

## 9. Findings

```text
P6-01 = P2 — DHObjectLayout static incomplete-state note used role="status"
        (unnecessary live region). FIXED (P0-1 closure) — minimal correction;
        note stays visible + programmatically available.
No other cross-surface responsive/accessibility defect was found that violates
a measurable requirement; no unmapped production change.
```

## 10. Scope Audit

```text
AUTHORIZED_PRODUCTION_DELTA =
  apps/frontend/src/components/primitives/DHObjectLayout.vue (P0-1 correction)
AUTHORIZED_TEST_DELTA =
  ux2_p6_cross_surface.spec.ts · e2e/ux2-responsive-a11y.spec.ts ·
  ux2_p0_dhobjectlayout.spec.ts (P0-1 assertion update) ·
  ux2_p1_person.spec.ts (P0-1 assertion update)
AUTHORIZED_EVIDENCE_DELTA = HFM-UX2-P6-IMPLEMENTATION-EVIDENCE-v1.md
FORBIDDEN_PRODUCTION_PATH_DELTA = ZERO
DATA/SERVICES/BACKEND/TYPES/ROUTER_DELTA = ZERO
P7_DELTA = ZERO · UNRELATED_DELTA = ZERO
P1/P2/P3/P4/P5_ACCEPTED_IMPLEMENTATION_DELTA = ZERO (no surface file touched)
```

## 11. Worktree & Rollback

```text
WORKTREE = authorized delta only (staged for candidate commit)
ROLLBACK_TARGET = 34bef554fcf25988b9634152efd7b19494ad714e (PRE_WP_BASELINE)
Rollback boundary = test additions + the single DHObjectLayout attribute
                    change (revert = restore DHObjectLayout + drop P6 tests +
                    restore the two P0/P1 test assertion blocks)
```

## 12. Commit

```text
UX2_P6_IMPLEMENTATION_CANDIDATE = <commit SHA recorded at delivery>
CANDIDATE_PARENT = 34bef554fcf25988b9634152efd7b19494ad714e
```
