# HFM-UX2-P4 Implementation Evidence v1

Status: UX2-P4 IMPLEMENTATION CANDIDATE · ready for independent audit
(pre-WP baseline `4b31de15bd3488a537e65cc5b6dd4df478f02700`)

## 1. WP Identity

```text
WP = UX2-P4 · Scholarly Discovery
PRE_WP_BASELINE = 4b31de15bd3488a537e65cc5b6dd4df478f02700
P4_AUTHORITATIVE_DEPENDENCIES = [UX2-P0]  (WP DAG: P4 ← P0 only)
DEPENDENCIES_SATISFIED = YES (P0/P1/P2/P3 all FROZEN)
P4_CONTRACT_SOURCE =
  docs/ux2/g4/HFM-UX2-G4-WORK-PACKAGE-DAG-v1.md (UX2-P4 row)
  docs/ux2/g4/HFM-UX2-G4-PRODUCTION-IMPLEMENTATION-CONTRACT-v1.md
    (candidate 06 + G4-O-1 BibliographyEntry special rule)
  docs/ux2/g4/HFM-UX2-G4-ACCEPTANCE-AND-ROLLBACK-CONTRACT-v1.md
```

## 2. Contract Reconstruction (authoritative)

```text
WP_TITLE = Scholarly Discovery
P4_OBJECTIVE = Results via BibliographicRecord; document-level CitationLocator;
               515/5 shown separately; facet semantic stays search-index type
               counts.
P4_MODIFY_ALLOWLIST = views/search/SearchView.vue ·
                      views/research/ResearchSearchView.vue ·
                      components/search/BibliographyEntry.vue
                      (alignment only — G4-O-1 ALLOW_MODIFY_ONLY_IN_UX2-P4)
P4_CREATE_ALLOWLIST = __tests__/ux2_p4_*.spec.ts · e2e/ux2-p4-*.spec.ts
P4_READ_ONLY = data/searchIndex.ts · data/jiayiView.ts · data/readerDocuments.ts ·
               types · P0 primitives · CitationBlock · SearchHighlight
P4_FORBIDDEN = data/searchIndex.ts modification · new index · synthesized
               page/volume (U-04) · UI re-classification · backend/services/
               router/types changes
P4_NEGATIVE_BOUNDARIES = NB-06 (no citation fabrication) · NB-07 (515 ≠
                         searchable) · NB-05 (clinical)
P4_PRESENTATION_STATES = RESOURCE_READY (searchable 5) · METADATA_ONLY (仅题录)
                         · UNSTRUCTURED_OR_INCOMPLETE (rest of 515)
P4_DEFINITION_OF_DONE = results render via BibliographicRecord; locator at
                        document level; 515/5 distinct; suite green
P4_ROLLBACK_BOUNDARY = view/component-only; revert = restore
```

## 3. Implementation

| File | Change |
| --- | --- |
| `views/search/SearchView.vue` | Results render through the shared **BibliographicRecord** primitive: presentation state derived from the entry's governed ContentStatus via the P0 G1-C mapping (`resolvePresentationState`/`presentationLabel` → RESOURCE_READY 数字资源可阅 / METADATA_ONLY 仅题录 / UNSTRUCTURED_OR_INCOMPLETE 资料整理中); the highlighted result title (SearchHighlight `<mark>`) is preserved as the interactive title above each record (frozen ui10 dark-mode highlight test stays green); search form landmark named (`aria-label="平台内容检索"`) resolving a pre-existing duplicate-search-landmark axe issue surfaced by full-document axe on /search; 515/5 summary and facet type-count semantics unchanged |
| `components/search/BibliographyEntry.vue` | **Aligned to BibliographicRecord (G4-O-1)**: the paper-result adapter now renders the shared record primitive internally (title/badge/metadata via the P0 mapping; kind=论文); no fake full-text/PDF/reader/download affordance |
| `views/research/ResearchSearchView.vue` | Removed the local status ternary (已展示/元数据已录/整理中) — status labels now derive from the shared P0 G1-C mapping (`entryStateLabel`); `LOCAL_DUPLICATE_PRESENTATION_STATE_LOGIC = NO` |

## 4. Discovery Behavior

```text
DISCOVERY_BEHAVIOR = real governed dataset (searchIndex) end-to-end:
  query → searchIndex() → facetCounts (type counts) → paged results →
  BibliographicRecord rendering
FAKE_SEARCH_CAPABILITY = NO · FAKE_FILTER_CAPABILITY = NO
SEARCH_RESULT_SCOPE_OVERSTATEMENT = NO
CONTROL = query (input)  — DATA_SCOPE = SEARCH_INDEX  — BEHAVIOR = URL-driven
CONTROL = type filter  — DATA_SCOPE = facetCounts(qResults)  — BEHAVIOR = URL type
CONTROL = pagination   — DATA_SCOPE = filteredResults/PAGE_SIZE
CONTROL = clear filter — BEHAVIOR = type reset to all
EMPTY_RESULT_BEHAVIOR = truthful 未找到匹配 + count 0 (no fake success)
KEYBOARD_BEHAVIOR = Enter submits; facet/pager buttons focusable
```

## 5. Presentation State Matrix (P4)

```text
entry.status AVAILABLE     → RESOURCE_READY     → 数字资源可阅
entry.status METADATA_ONLY → METADATA_ONLY      → 仅题录
entry.status DATA_GAP      → UNSTRUCTURED_OR_INCOMPLETE → 资料整理中
SEARCHABLE_PAPER_TOTAL 5   → shown separately   → 已结构化 5
AUDITED_PAPER_TOTAL 515    → shown separately   → 审计 515 (never 515 searchable)
NO_FALSE_RESOURCE_READY = YES · NO_FAKE_FULL_TEXT = YES · NO_FAKE_PDF = YES
NO_FAKE_READER = YES · NO_FAKE_DOWNLOAD = YES · NO_FAKE_EXTERNAL_LINK = YES
```

## 6. Count Integrity & Provenance

```text
HARDCODED_FALSE_COUNTS = NONE
COUNT_SOURCE = searchIndex facetCounts + SEARCHABLE/AUDITED_PAPER_TOTAL
FILTERED_COUNT_MATCH = YES (facet counts = facetCounts(qResults))
EMPTY_RESULT_COUNT = 0
PROVENANCE = PASS · FALSE_ATTRIBUTION = NO · AGGREGATE_FALSE_ATTRIBUTION = NO
PUBLIC_SOURCE_ONLY = YES · INTERNAL_IDENTIFIER_LEAK = NONE
UNSUPPORTED_SCHOLAR_RELATIONSHIP_CLAIMS = NONE
UNSUPPORTED_AUTHORSHIP_CLAIMS = NONE · UNSUPPORTED_CITATION_EDGES = NONE
```

## 7. Negative Boundary Results

```text
NB-06 = PASS  — no synthesized page/volume citation (U-04 page-level collapsed)
NB-07 = PASS  — 515 audited ≠ 5 searchable (shown separately)
NB-05 = PASS  — no clinical content on the discovery surface
NO_FAKE_ACTIONS = PASS (no 阅读全文/PDF/下载/在线阅读 on results)
```

## 8. Test / Quality Results (independently reproduced)

```text
TARGETED_TESTS      = 13/13 PASS (ux2_p4_discovery.spec.ts)
P0_REGRESSION_TESTS = 58/58 PASS (P0_REGRESSION = NONE)
P1_REGRESSION_TESTS = 19/19 PASS (P1_REGRESSION = NONE)
P2_REGRESSION_TESTS = 11/11 PASS (P2_REGRESSION = NONE)
P3_REGRESSION_TESTS = 12/12 PASS (P3_REGRESSION = NONE)
FULL_VITEST         = 308/308 PASS (33 files)
VUE_TSC             = PASS (0 errors)
ESLINT              = 0_ERRORS_960_WARNINGS (actual reproduction; repo-wide
                      pre-existing style-warning baseline; gate is errors)
VITE_BUILD          = PASS
PLAYWRIGHT          = 85/85 PASS (79 existing incl. ui10/ui11 + 6 UX2-P4)
BROWSER_AXE         = 0 (real browser, full rule set)
RESPONSIVE_375/1280/1920 = PASS · HORIZONTAL_OVERFLOW = NONE
NAVIGATION = PASS · NO_DEAD_ROUTE = YES · KEYBOARD = PASS · FOCUS = PASS
QUERY_STATE = PASS (refresh + back/forward recover; invalid query → 0 results)
```

## 9. Scope Audit

```text
AUTHORIZED_PRODUCTION_DELTA = SearchView.vue · ResearchSearchView.vue ·
                              BibliographyEntry.vue (G4-O-1 alignment)
AUTHORIZED_TEST_DELTA = ux2_p4_discovery.spec.ts · e2e/ux2-p4-discovery.spec.ts
AUTHORIZED_EVIDENCE_DELTA = HFM-UX2-P4-IMPLEMENTATION-EVIDENCE-v1.md
FORBIDDEN_PRODUCTION_PATH_DELTA = ZERO · DATA/SERVICES/BACKEND/TYPES/ROUTER_DELTA = ZERO
P0_PRIMITIVE_IMPLEMENTATION_DELTA = ZERO
P1/P2/P3_ACCEPTED_IMPLEMENTATION_DELTA = ZERO
P5/P6/P7_DELTA = ZERO · UNRELATED_DELTA = ZERO
```

## 10. Worktree & Rollback

```text
WORKTREE = authorized delta only (staged for candidate commit)
ROLLBACK_TARGET = 4b31de15bd3488a537e65cc5b6dd4df478f02700 (PRE_WP_BASELINE)
Rollback boundary = view/component-only; revert = restore the three views +
                    drop P4 test files
P0-1 = OPEN_P2_NON_BLOCKING_REVERIFY_AT_P6 (untouched — no DHObjectLayout change)
```

## 11. Commit

```text
UX2_P4_IMPLEMENTATION_CANDIDATE = 9b4adcbf7441c3ec9ac0cbab5fcd8d21598d677f (ACCEPTED)
CANDIDATE_PARENT = 4b31de15bd3488a537e65cc5b6dd4df478f02700
P2-01 = CLOSED_AT_ACCEPTANCE_ARCHIVE
```
