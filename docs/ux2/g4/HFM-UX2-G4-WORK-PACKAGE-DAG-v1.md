# HFM-UX2 G4 Work Package DAG v1

Status: UX2-G4 NORMATIVE ARTIFACT · Package-ready for independent review
Binding: Production Implementation Contract v1 (§14 file allowlist governs each
WP's files). Dependencies derived from the actual Vue 3 architecture
(shared primitives must exist before surfaces consume them; surfaces must
exist before cross-surface verification; verification before acceptance).

## 1. Work Package Graph

```text
UX2-P0 (shared presentation primitives + state mapping)
  ├─→ UX2-P1 (Person Archive)
  ├─→ UX2-P2 (Jiayi Work / Edition)
  ├─→ UX2-P3 (Heritage Living Archive)
  ├─→ UX2-P4 (Scholarly Discovery)
  └─→ UX2-P5 (Homepage Exhibition Narrative)

UX2-P1,P2,P3,P4 → UX2-P5          (home narrative links to and reflects the surfaces)

UX2-P1,P2,P3,P4,P5 → UX2-P6       (cross-surface responsive/accessibility verification)

UX2-P6 → UX2-P7                   (final production UX2 integration acceptance)
```

```text
Dependencies (mathematical):
P0 → P1 ; P0 → P2 ; P0 → P3 ; P0 → P4 ; P0 → P5
P1 → P5 ; P2 → P5 ; P3 → P5 ; P4 → P5
P1 → P6 ; P2 → P6 ; P3 → P6 ; P4 → P6 ; P5 → P6
P6 → P7
```

Rationale (from repository architecture): P0 must land first because every
surface consumes the shared primitives and the state mapping. P5 (home) depends
on P1–P4 because its narrative sections cross-link to `/persons/…`, `/jiayi`,
`/heritage`, `/search` and reflect their state labels. P6 verifies the composed
surfaces; P7 accepts the integration as a whole.

## 2. Work Package Definitions

### UX2-P0 — Shared Presentation Primitives

| Field | Value |
| --- | --- |
| WP ID | UX2-P0 |
| Objective | Ship the two shared primitives (DHObjectLayout, BibliographicRecord) + deterministic presentation-state mapping + extended `hfm-status` vocabulary. |
| Production Files Allowed | CREATE: `components/primitives/DHObjectLayout.vue`, `components/primitives/BibliographicRecord.vue`, `presentation/stateMapping.ts`, `__tests__/ux2_p0_*.spec.ts`. MODIFY: `styles/foundations.css` (status vocabulary + token-role application). |
| Production Files Forbidden | anything outside the contract §14 allowlist; `data/**`, `types/**`, `router/**`, `tokens.css`, package.json |
| Dependencies | none (foundation) |
| Data Inputs | existing projections via props only (no new data read) |
| Presentation States | full G1-C vocabulary incl. SCHOLARLY_UNCERTAIN / HISTORICAL_ABSENCE / UNSTRUCTURED_OR_INCOMPLETE; fail-closed default |
| Negative Boundaries | NB-02 (relations semantics), NB-08 (no empty shells), NB-06 (no citation synthesis), N-F-1 (titleTag fail-closed) |
| Tests | unit (slot states ×3, record kinds ×5, state mapping rows 1–13 + precedence, titleTag contract), component, token scan |
| Definition of Done | both primitives + mapping util + status vocabulary in place; unit suites green; axe clean on primitive usage |
| Rollback Boundary | create-only additions + foundations.css class additions; reversible independently |
| Expected Evidence | changed-file list, unit results, axe result, token scan, baseline parent |

### UX2-P1 — Person Archive

| Field | Value |
| --- | --- |
| WP ID | UX2-P1 |
| Objective | Adopt DHObjectLayout + G1-C states on PersonDetailView; F-5 Life Events / Historical Assessments / Archival Media; correct heading hierarchy. |
| Production Files Allowed | MODIFY: `views/persons/PersonDetailView.vue`. CREATE: `__tests__/ux2_p1_*.spec.ts`, `e2e/ux2-p1-*.spec.ts`. |
| Production Files Forbidden | data/types/router/services/api modifications; Later Scholarship section (DEFERRED); new fields |
| Dependencies | UX2-P0 |
| Data Inputs | `config/corePerson.ts`, `services/api.ts` (read-only), `data/readerDocuments.ts` (后论), `data/archiveInventory.ts` (其传/后论 evidence), `services/media.ts` (movies) |
| Presentation States | RESOURCE_READY (identities/definition), SCHOLARLY_UNCERTAIN (生卒年 dispute note), METADATA_ONLY (其传/后论 文稿), ABSENT_OPTIONAL (portrait/holding) |
| Negative Boundaries | NB-01 (no fabrication), NB-07 (uncertainty ≠ incompleteness), NB-05 (clinical), F-5 Later Scholarship NOT added |
| Tests | unit/component per ui04 style; NB patterns; axe; responsive |
| Definition of Done | person page renders DHObjectLayout regions + states; heading order correct; F-5 authorized sections from real data; suite green |
| Rollback Boundary | view-only change; route unchanged; revert = restore view |
| Expected Evidence | changed-file list, test results, axe result, data provenance samples |

### UX2-P2 — Jiayi Work / Edition

| Field | Value |
| --- | --- |
| WP ID | UX2-P2 |
| Objective | Render edition records via BibliographicRecord (存目 per U-05); align work-profile; keep chronology ≠ lineage + DATA-GAP. |
| Production Files Allowed | MODIFY: `views/jiayi/JiayiView.vue`. CREATE: `__tests__/ux2_p2_*.spec.ts`, `e2e/ux2-p2-*.spec.ts`. |
| Production Files Forbidden | data/types/router changes; digitization flags (U-05); genealogy edges |
| Dependencies | UX2-P0 |
| Data Inputs | `data/jiayiView.ts` (19 editions, scholars, papers, sources, lineage asset) |
| Presentation States | METADATA_ONLY (存目 for all 19 editions), UNSTRUCTURED_OR_INCOMPLETE (DATA-GAP caption) |
| Negative Boundaries | NB-03 (no edition genealogy), NB-08, NB-06, NB-05 |
| Tests | ui08-style suite; NB-03 assertions; axe; responsive |
| Definition of Done | 19 editions render via BibliographicRecord with 存目; DATA-GAP + chronology ≠ lineage captions intact; suite green |
| Rollback Boundary | view-only; revert = restore view |
| Expected Evidence | changed-file list, test results, axe result |

### UX2-P3 — Heritage Living Archive

| Field | Value |
| --- | --- |
| WP ID | UX2-P3 |
| Objective | Make historical vs contemporary evidence-context separation explicit; recognition as secondary metadata (8/8); PARTIAL lineage preserved. |
| Production Files Allowed | MODIFY: `views/heritage/HeritageView.vue`. CREATE: `__tests__/ux2_p3_*.spec.ts`, `e2e/ux2-p3-*.spec.ts`. |
| Production Files Forbidden | data/types/router changes; honor-wall treatment; lineage inference; clinical content |
| Dependencies | UX2-P0 |
| Data Inputs | `data/heritageView.ts` (project/person/recognitions 8/academic/technical/apprenticeships/studios/media/lineage/timeline) |
| Presentation States | RESOURCE_READY (confirmed nodes/events), UNSTRUCTURED_OR_INCOMPLETE (PARTIAL lineage), METADATA_ONLY where applicable |
| Negative Boundaries | NB-04 (no uninterrupted lineage), NB-05 (clinical), NB-01, honor-wall prohibition (N-14) |
| Tests | ui09-style suite; NB-04 assertions; axe; responsive |
| Definition of Done | two contexts explicit; recognition stays secondary; PARTIAL gap explicit; suite green |
| Rollback Boundary | view-only; revert = restore view |
| Expected Evidence | changed-file list, test results, axe result |

### UX2-P4 — Scholarly Discovery

| Field | Value |
| --- | --- |
| WP ID | UX2-P4 |
| Objective | Results via BibliographicRecord; document-level CitationLocator; 515/5 shown separately; facet semantic stays search-index type counts. |
| Production Files Allowed | MODIFY: `views/search/SearchView.vue`, `views/research/ResearchSearchView.vue`, `components/search/BibliographyEntry.vue` (alignment only). CREATE: `__tests__/ux2_p4_*.spec.ts`, `e2e/ux2-p4-*.spec.ts`. |
| Production Files Forbidden | data/searchIndex.ts modification; new index; synthesized page/volume (U-04); UI re-classification |
| Dependencies | UX2-P0 |
| Data Inputs | `data/searchIndex.ts` (SEARCH_INDEX, facetCounts, AUDITED 515 / SEARCHABLE 5), `data/jiayiView.ts` (paper previews), `data/readerDocuments.ts` (citations) |
| Presentation States | RESOURCE_READY (searchable 5), METADATA_ONLY (仅题录), UNSTRUCTURED_OR_INCOMPLETE (rest of 515) |
| Negative Boundaries | NB-06 (no citation fabrication), NB-07 (515 ≠ searchable), NB-05 |
| Tests | ui10/ui11-style suites; NB-06 assertions; axe; responsive |
| Definition of Done | results render via BibliographicRecord; locator at document level; 515/5 distinct; suite green |
| Rollback Boundary | view/component-only; revert = restore |
| Expected Evidence | changed-file list, test results, axe result |

### UX2-P5 — Homepage Exhibition Narrative

| Field | Value |
| --- | --- |
| WP ID | UX2-P5 |
| Objective | Align HomeView to frozen narrative grammar (already matching); apply state labels; verify cross-links to implemented surfaces. |
| Production Files Allowed | MODIFY: `views/HomeView.vue`. CREATE: `__tests__/ux2_p5_*.spec.ts`, `e2e/ux2-p5-*.spec.ts`. |
| Production Files Forbidden | new promotional/historical copy; news-portal layout; data/homeProjection.ts modification |
| Dependencies | UX2-P0, UX2-P1, UX2-P2, UX2-P3, UX2-P4 |
| Data Inputs | `data/homeProjection.ts` (frozen), `data/researchProjection.ts` |
| Presentation States | labels via P0 state mapping where surfaced |
| Negative Boundaries | NB-01, NB-05, G1-A §9 homepage boundary (N-09/N-13) |
| Tests | ui03-style suite; axe; responsive |
| Definition of Done | narrative order/grammar conform; links resolve to implemented surfaces; suite green |
| Rollback Boundary | view-only |
| Expected Evidence | changed-file list, test results, axe result |

### UX2-P6 — Cross-Surface Responsive & Accessibility Verification

| Field | Value |
| --- | --- |
| WP ID | UX2-P6 |
| Objective | Machine-verified responsive (375/768/1440/1920) and accessibility (axe 0) across all authorized surfaces. |
| Production Files Allowed | CREATE: `e2e/ux2-responsive-a11y.spec.ts`, `__tests__/ux2_*.spec.ts` (verification). MODIFY: authorized surface styles only if a defect is proven. |
| Production Files Forbidden | behavior/feature changes; data/types/router changes |
| Dependencies | UX2-P1…UX2-P5 |
| Data Inputs | n/a (rendered surfaces) |
| Presentation States | n/a (verification of all) |
| Negative Boundaries | NB-10 (responsive semantics), NB-11 (a11y), heading-order regression (F-1), N-F-1 contract |
| Tests | responsive matrix (375/768/1440/1920: no horizontal overflow, semantic order, evidence access, heritage context separation, relation semantics); axe on all authorized surfaces; keyboard/focus/reduced-motion |
| Definition of Done | all assertions green; 0 violations; no regression on existing ui02–ui13 suites |
| Rollback Boundary | test-only additions unless a style defect fix is authorized (per-surface revert) |
| Expected Evidence | responsive matrix results, axe results, full test run |

### UX2-P7 — Final Production UX2 Integration Acceptance

| Field | Value |
| --- | --- |
| WP ID | UX2-P7 |
| Objective | Collect the full acceptance evidence set; confirm boundaries; produce the integration acceptance record for independent review. |
| Production Files Allowed | CREATE: `docs/ux2/g4/` acceptance evidence artifacts (governance only). NO production source change. |
| Production Files Forbidden | all production source (no code change in P7) |
| Dependencies | UX2-P6 |
| Data Inputs | evidence from P0–P6 |
| Presentation States | n/a |
| Negative Boundaries | full negative matrix re-check; clinical P0; production delta ZERO at handover |
| Tests | full Vitest + Playwright run; production delta (`git diff -- apps packages` empty) |
| Definition of Done | acceptance evidence package complete; boundaries verified; verdict issued |
| Rollback Boundary | n/a (no code) |
| Expected Evidence | production diff, test results, negative-boundary results, responsive + a11y results, data provenance samples, baseline parent, worktree status |

## 3. Sequencing Rules

- Each WP is independently reversible (rollback contract); a later WP never
  destroys the ability to return to the previous accepted baseline.
- P0 is the only WP with no dependencies and must complete first.
- P5 may begin only after P1–P4 land (cross-link integrity).
- P6/P7 are verification-only; they change no behavior.
- No WP introduces a new UI framework, a new test framework, or a production
  runtime dependency.

## 4. Exit State

```text
WP_DAG_FINITE = TRUE (UX2-P0…P7, 8 work packages)
WP_DAG_ROLLBACK_SAFE = TRUE (per-WP reversible; no destroy of prior baseline)
UX2_G4 = PACKAGE_READY / PENDING_INDEPENDENT_REVIEW
```
