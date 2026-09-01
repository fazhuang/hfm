# HFM-UX2 G4 Production Implementation Contract v1

Status: UX2-G4 NORMATIVE ARTIFACT · Package-ready for independent review
Authoritative baselines:

```text
PRE_UX2_PRODUCTION_UI_BASELINE   = ae55abc606c419f27259fc80bb8bee258d595ce9
UX2_G0_G3_ACCEPTANCE_ARCHIVE_BASELINE = e8593ffc7eec98584b3d69207a9bcd95e1698f8d
UX2-G0 = ACCEPTED_AND_ARCHIVED
UX2-G1 = ACCEPTED_AND_ARCHIVED
UX2-G2 = ACCEPTED_AND_ARCHIVED
UX2-G3 = ACCEPTED_AND_ARCHIVED
CURRENT_GATE = UX2-G4_IMPLEMENTATION_AUTHORIZATION_REVIEW
PRODUCTION_IMPLEMENTATION = LOCKED
```

This contract answers: exactly which accepted UX2 design requirements may be
implemented in HFM production, where, what existing data/contracts they may
consume, what they may not change, and how implementation will be accepted.
G4 preparation does NOT unlock implementation.

## 1. Source Precedence

```text
1. Existing frozen HFM domain/API/data contracts   (authoritative, read-only)
2. Accepted UX2 G1 contracts
3. Accepted UX2 G2 evidence
4. Accepted UX2 G3 implementation-scope decisions
5. G2 prototype as IMPLEMENTATION_REFERENCE_ONLY where classified
```

Prototype behavior never overrides accepted production/domain contracts.

## 2. Authorization Candidates (12, from G3)

All 12 accepted G3 candidates are mapped independently. Recommendations use
only: `AUTHORIZE | DEFER | EXCLUDE | BLOCKED`.

| # | Candidate | Recommendation | Production Target | Route/API/Schema Change |
| --- | --- | --- | --- | --- |
| 01 | DHObjectLayout | AUTHORIZE | `apps/frontend/src/components/primitives/DHObjectLayout.vue` (CREATE) | NO / NO / NO |
| 02 | BibliographicRecord | AUTHORIZE | `apps/frontend/src/components/primitives/BibliographicRecord.vue` (CREATE) | NO / NO / NO |
| 03 | Person surface | AUTHORIZE | `apps/frontend/src/views/persons/PersonDetailView.vue` (MODIFY) | NO / NO / NO |
| 04 | Jiayi surface | AUTHORIZE | `apps/frontend/src/views/jiayi/JiayiView.vue` (MODIFY) | NO / NO / NO |
| 05 | Heritage surface | AUTHORIZE | `apps/frontend/src/views/heritage/HeritageView.vue` (MODIFY) | NO / NO / NO |
| 06 | Scholarly Discovery | AUTHORIZE | `apps/frontend/src/views/search/SearchView.vue` + `apps/frontend/src/views/research/ResearchSearchView.vue` (MODIFY) | NO / NO / NO |
| 07 | Homepage Exhibition Narrative | AUTHORIZE | `apps/frontend/src/views/HomeView.vue` (MODIFY) | NO / NO / NO |
| 08 | Presentation-state mapping | AUTHORIZE | `apps/frontend/src/presentation/stateMapping.ts` (CREATE) + `apps/frontend/src/styles/foundations.css` (MODIFY) | NO / NO / NO |
| 09 | Semantic token roles | AUTHORIZE | role application in `foundations.css` + consuming components; `tokens.css` READ_ONLY | NO / NO / NO |
| 10 | Responsive semantics | AUTHORIZE | styles + surface views above + tests | NO / NO / NO |
| 11 | Accessibility requirements | AUTHORIZE | surface views above + tests (axe/heading/keyboard/focus) | NO / NO / NO |
| 12 | CitationLocator | AUTHORIZE | reuse `apps/frontend/src/components/reader/CitationBlock.vue` (READ_ONLY reuse) in surfaces | NO / NO / NO |

### Candidate Detail Records

**01 DHObjectLayout**

- Accepted Design Source: G1-A §1 (regions, slot presence, relations semantics) + G2 P1/index evidence + G3 scope item 1
- Production Target: new shared presentation primitive `apps/frontend/src/components/primitives/DHObjectLayout.vue`
- Existing Data Source: none new — consumes existing projections via props (corePerson, workCollection, readerDocuments, archiveInventory, heritageView, searchIndex)
- Existing Component/Primitive Reuse: `EmptyState`/`ErrorState`/`LoadingState`, `.hfm-status`, tokens
- Allowed Change: create primitive; render Header/Context/Evidence/Relations regions; slot presence contract (PRESENT/ABSENT_OPTIONAL/INCOMPLETE_WITH_EVIDENCE_STATE); relations semantics labels; presentation-only `titleTag` per N-F-1 contract (§6)
- Forbidden Change: any domain type/API/schema change; relation inference; new tokens
- Dependencies: none (foundation; P0)
- Acceptance Tests: unit (slot states ×3, relations semantics, titleTag contract incl. fail-closed), component, axe
- Rollback Boundary: component create-only; removable without touching routes/data
- Authorization Recommendation: AUTHORIZE

**02 BibliographicRecord**

- Accepted Design Source: G1-A §2 + G2 P2/P4 evidence + G3 scope item 2
- Production Target: new shared primitive `apps/frontend/src/components/primitives/BibliographicRecord.vue`
- Existing Data Source: searchIndex entries, jiayiView editions, workCollection, readerDocuments (via props)
- Existing Component/Primitive Reuse: `BibliographyEntry.vue` (search result kind — align in P4), `hfm-status`
- Allowed Change: create generalized record primitive (work/edition/paper/search-result/source-reference kinds); field-hierarchy degradation (absent fields collapse)
- Forbidden Change: synthesized fields (卷/页/版本号/馆藏); marketing-card treatment
- Dependencies: P0 (with DHObjectLayout)
- Acceptance Tests: unit (5 kinds, degradation), component, route render
- Rollback Boundary: component create-only
- Authorization Recommendation: AUTHORIZE

**03 Person surface**

- Accepted Design Source: G1-A §1/§6, G1-C + G2 P1 + G3 scope item 3 + F-5 determinations (§7)
- Production Target: `apps/frontend/src/views/persons/PersonDetailView.vue`
- Existing Data Source: `src/config/corePerson.ts`, `services/api.ts` (`fetchPublicPerson`, `fetchPublicMedia`), `readerDocuments.ts`, `archiveInventory.ts`
- Existing Component/Primitive Reuse: Timeline, EmptyState, CitationBlock, DHObjectLayout (P0)
- Allowed Change: adopt DHObjectLayout header/context/evidence/relations; presentation states per G1-C (scholarly-uncertain from verified 其传 text; metadata-only for 后论/其传); heading hierarchy; F-5 Life Events / Historical Assessments / Archival Media sections (§7)
- Forbidden Change: new fields; invented biography content; clinical content; Later Scholarship section (DEFERRED)
- Dependencies: P0
- Acceptance Tests: ui04-person-style suite extended; negative boundary (no fabrication); axe; responsive
- Rollback Boundary: view-only change; route unchanged
- Authorization Recommendation: AUTHORIZE

**04 Jiayi surface**

- Accepted Design Source: G1-A §2/§6 + G2 P2 + G3 scope item 4
- Production Target: `apps/frontend/src/views/jiayi/JiayiView.vue`
- Existing Data Source: `src/data/jiayiView.ts` (19 editions, scholars, papers, sources)
- Existing Component/Primitive Reuse: Timeline, EditionLineageImage, BibliographicRecord (P0)
- Allowed Change: render edition records via BibliographicRecord (存目 state per U-05 disposition); work-profile/hero alignment; chronology ≠ lineage preserved; DATA-GAP caption
- Forbidden Change: edition genealogy inference; digitization flags (U-05); clinical content
- Dependencies: P0
- Acceptance Tests: ui08-jiayi-style suite; NB-03; axe; responsive
- Rollback Boundary: view-only
- Authorization Recommendation: AUTHORIZE

**05 Heritage surface**

- Accepted Design Source: G1-A §4 + G2 P3 + G3 scope item 5
- Production Target: `apps/frontend/src/views/heritage/HeritageView.vue`
- Existing Data Source: `src/data/heritageView.ts` (project/person/recognitions 8/academic/technical/apprenticeships/studios/media/lineage/timeline)
- Existing Component/Primitive Reuse: LineageGraph, Timeline, DHObjectLayout (P0)
- Allowed Change: make HISTORICAL_TEXTUAL_CONTEXT vs CONTEMPORARY_LIVING_ARCHIVE_CONTEXT separation explicit; recognition remains secondary metadata (8/8); PARTIAL lineage gap preserved
- Forbidden Change: honor-wall treatment; lineage inference; clinical content
- Dependencies: P0
- Acceptance Tests: ui09-heritage-style suite; NB-04; axe; responsive
- Rollback Boundary: view-only
- Authorization Recommendation: AUTHORIZE

**06 Scholarly Discovery**

- Accepted Design Source: G1-A §2/§3 + G2 P4 + G3 scope item 6
- Production Target: `apps/frontend/src/views/search/SearchView.vue` + `apps/frontend/src/views/research/ResearchSearchView.vue` + `apps/frontend/src/components/search/BibliographyEntry.vue`
- Existing Data Source: `src/data/searchIndex.ts` (SEARCH_INDEX, facetCounts, 515/5) — facet semantic is search-index type counts (F-3 resolution, already the production behavior)
- Existing Component/Primitive Reuse: BibliographyEntry, SearchHighlight, BibliographicRecord (P0), CitationBlock
- Allowed Change: results via BibliographicRecord; CitationLocator at document level; 515/5 shown separately; no UI re-classification
- Forbidden Change: synthesized page/volume; claiming 515 searchable; new index
- Dependencies: P0
- Acceptance Tests: ui10/ui11-style suites; NB-06; axe; responsive
- Rollback Boundary: view/component-only
- Authorization Recommendation: AUTHORIZE

**07 Homepage Exhibition Narrative**

- Accepted Design Source: G1-A §9 + G2 P5 + G3 scope item 7
- Production Target: `apps/frontend/src/views/HomeView.vue`
- Existing Data Source: `src/data/homeProjection.ts` (frozen narrative)
- Existing Component/Primitive Reuse: existing home sections; state labels from P0
- Allowed Change: align to frozen narrative order/grammar (already matches); apply state labels; verification
- Forbidden Change: new promotional/historical copy; news-portal layout
- Dependencies: P0, P1, P2, P3 (cross-links to person/jiayi/heritage surfaces)
- Acceptance Tests: ui03-home-style suite; axe; responsive
- Rollback Boundary: view-only
- Authorization Recommendation: AUTHORIZE

**08 Presentation-state mapping**

- Accepted Design Source: G1-C (deterministic mapping, precedence, fail-closed) + G3 scope item 8
- Production Target: `apps/frontend/src/presentation/stateMapping.ts` (CREATE) + `apps/frontend/src/styles/foundations.css` (extend `.hfm-status` vocabulary)
- Existing Data Source: existing ContentStatus/ReadingAvailability + verified-text predicates (DERIVED_PRESENTATION_ONLY)
- Existing Component/Primitive Reuse: `.hfm-status` (AVAILABLE/METADATA_ONLY/DATA_GAP today)
- Allowed Change: add presentation states SCHOLARLY_UNCERTAIN / HISTORICAL_ABSENCE / UNSTRUCTURED_OR_INCOMPLETE + public labels per G1-C; deterministic priority; fail-closed default
- Forbidden Change: new domain states; synthetic flags (is_gap/is_uncertain/…); hidden production-only states
- Dependencies: none (P0 foundation)
- Acceptance Tests: unit tests per G1-C matrix rows 1–13; conflict-precedence tests
- Rollback Boundary: util + CSS class additions
- Authorization Recommendation: AUTHORIZE

**09 Semantic token roles**

- Accepted Design Source: G1-B + G3 scope item 9
- Production Target: role application (`surface-paper`/`surface-archive`/`surface-evidence`) in foundations.css + consuming components; `tokens.css` READ_ONLY
- Existing Data Source: existing frozen tokens
- Existing Component/Primitive Reuse: tokens.css semantic layer
- Allowed Change: apply documented role→token mapping; no value changes
- Forbidden Change: new palette; arbitrary hex; one-off tokens; parallel token system
- Dependencies: none
- Acceptance Tests: token scan (NB-09 style, ui13-polish)
- Rollback Boundary: role-class additions
- Authorization Recommendation: AUTHORIZE

**10 Responsive semantics**

- Accepted Design Source: G1-A §7 + G2 + G3 scope item 10
- Production Target: styles in authorized views + verification suite
- Existing Data Source: n/a (presentation)
- Existing Component/Primitive Reuse: existing 375/768/1024/1440/1920 verification
- Allowed Change: reflow/stack adjustments in authorized surfaces only
- Forbidden Change: semantics encoded in position/hover/connectors
- Dependencies: P1–P5
- Acceptance Tests: 375/768/1440/1920, no horizontal overflow, semantic order, evidence access, heritage context separation, relation semantics (acceptance contract)
- Rollback Boundary: per-surface style changes
- Authorization Recommendation: AUTHORIZE

**11 Accessibility requirements**

- Accepted Design Source: G1-A §8 + G2 F-1 + G3 scope item 11
- Production Target: authorized surface views + verification suite
- Existing Data Source: n/a
- Existing Component/Primitive Reuse: axe-core (project standard), focus ring, reduced-motion rule, AppSkipLink
- Allowed Change: heading hierarchy (titleTag semantics per §6), status text+color, keyboard, focus, reduced-motion conformance on authorized surfaces
- Forbidden Change: new project-wide a11y standard; color-only status
- Dependencies: P1–P5
- Acceptance Tests: axe = 0 on authorized surfaces; heading-order assertions
- Rollback Boundary: per-surface changes
- Authorization Recommendation: AUTHORIZE

**12 CitationLocator**

- Accepted Design Source: G1-A §3.1 + G2 P4 + G3 scope item 12
- Production Target: reuse `apps/frontend/src/components/reader/CitationBlock.vue` in person/jiayi/discovery evidence sections
- Existing Data Source: `readerDocuments.ts` citations (document/section level)
- Existing Component/Primitive Reuse: CitationBlock (READ_ONLY reuse)
- Allowed Change: surface integration only
- Forbidden Change: invented 卷/页/版本号 (U-04); new locator fields
- Dependencies: P1/P2/P4
- Acceptance Tests: NB-06; citation determinism tests
- Rollback Boundary: view integration
- Authorization Recommendation: AUTHORIZE

## 3. CitationExport — DEFER

CitationExport remains `DEFER` (G3 decision; unchanged unless authoritative
production data changed — it has not). Production already ships an
`ExportPanel` (`apps/frontend/src/components/ExportPanel.vue`, markdown/print
for reader records, `services/export.ts`); UX2 adds NO export formats and NO
fields to enable export. Prohibited for UX2:

```text
synthetic page number · synthetic holding institution
synthetic edition identifier · synthetic bibliographic fact
```

## 4. U-01…U-05 Carry-Forward

```text
U-01 scholarly uncertainty field      UNRESOLVED / NO_IMPLEMENTATION_ASSUMPTION
U-02 historical-loss field            UNRESOLVED / NO_IMPLEMENTATION_ASSUMPTION
U-03 holding institution              UNRESOLVED / NO_IMPLEMENTATION_ASSUMPTION
U-04 page-level citation locator      UNRESOLVED / NO_IMPLEMENTATION_ASSUMPTION
U-05 per-edition digitization flag    UNRESOLVED / NO_IMPLEMENTATION_ASSUMPTION
```

Production UI degrades per accepted G1 rules (collapse or meaningful
incomplete state). G4 does not solve these by schema invention.

## 5. N-F-1 Resolution — Production `titleTag` Semantics (contract resolution, no code change)

The accepted P2 observation (prototype `titleTag:0` truthiness ambiguity) is
resolved contractually for production. Production DHObjectLayout `titleTag`
MUST implement:

```text
titleTag ∈ {1,2,3,4,5,6}
→ semantic heading h1..h6

titleTag ∈ {null, undefined, 'none'}
→ non-heading title (<p class="dh-object__title">), heading semantics deferred
  to the surface

any other value (including 0)
→ FAIL_CLOSED: non-heading <p> + deterministic developer warning
```

`0` is NOT a valid production value; the prototype's documented `'0'`
vocabulary is withdrawn in production. No falsy-value ambiguity is preserved.
This is a contract decision in G4 preparation only; it grants no permission to
modify production code yet.

## 6. F-5 Deferred Person Coverage — Determinations (AMENDED — F-5 Reconciliation OPTION_C)

Authorization requires existing authoritative production data. No section is
created for visual completeness.

| F-5 item | Determination | Data basis |
| --- | --- | --- |
| Life Events | AUTHORIZE | `CORE_PERSON_LIFE_PHASES` (config/corePerson.ts) + `PersonEvent[]` via `fetchPublicPerson` — production already renders 生平 timeline |
| Historical Assessments | AUTHORIZE | `readerDocuments.ts` 后论 FULL_TEXT + 12 citations — existing authoritative content |
| Later Scholarship | DEFER | no confirmed person-scholarship authoritative projection (`JIAYI_MODERN_SCHOLARS` is edition-collation-focused, not person scholarship) |
| Archival Media | AUTHORIZE — presentation contract + truthful production empty state (F-5A/B/C below) | `fetchPublicMedia('movie')` + `archiveInventory.ts` a-movies — production renders 影像资料; runtime currently returns `[]` (no admitted MediaAsset records) |

### F-5 Amended Semantics (Reconciliation OPTION_C · BLOCKER UX2-P1-F5-CONTRACT-CAPABILITY-MISMATCH)

UX2-P1 is a PRESENTATION CONTRACT. The real customer media end-to-end
admission chain is explicitly out of UX2-P1 scope. Three independent
responsibilities:

**F-5A — Production truth / empty-state behavior**

Given the existing production runtime returns `fetchPublicMedia('movie')` = `[]`
(no admitted MediaAsset records exist), UX2-P1 acceptance requires
PersonDetailView to render a truthful compliant empty/degraded state:

```text
NO_FAKE_MEDIA = YES
NO_FALSE_RESOURCE_READY = YES
EMPTY_STATE = 暂无影像资料。 (or equivalent already-authorized wording)
```

The UI must not imply that NOT_ADMITTED / absent runtime media are playable or
published.

**F-5B — Presentation capability contract**

UX2-P1 must prove PersonDetailView can correctly render valid media objects
conforming to the frozen `MediaAssetItem` / public-media contract. A controlled
deterministic test fixture is permitted and is explicitly a
PRESENTATION-CONTRACT fixture — NOT evidence that the two customer movies have
been admitted to production. Required proof areas:

```text
media item rendering · metadata rendering · format/state labels
player/link DOM where contractually applicable · accessibility · responsive
```

**F-5C — Explicit deferred integration guarantee**

```text
REAL_CUSTOMER_MEDIA_END_TO_END_ADMISSION = DEFERRED
OWNER = Phase 2 Content Admission / P2-05 Media & Rights domain
```

Deferred capability: customer media bytes → governed per-media admission →
`MediaAsset` → publication/import lifecycle → public API projection → runtime
retrieval → streaming/distribution. UX2-P1 acceptance MUST NOT claim this
end-to-end chain exists.

### Reconciliation rationale

```text
CONTRACT_CAPABILITY_MISMATCH = CONFIRMED
F5_CURRENT_REQUIREMENT_CROSSED_WP_BOUNDARY = YES
RESOLUTION = PRESENTATION_ACCEPTANCE_AND_RUNTIME_TRUTH_SEPARATED_FROM_MEDIA_ADMISSION
```

The prior requirement — real customer file → admitted MediaAsset → real
production API result → runtime media render — is REMOVED from UX2-P1 scope
because the frozen P1 allowlist forbids creating that capability
(`data/**`, `services/**`, `backend/**`). F-5 end-to-end media admission is
owned by Phase 2 Content Admission / P2-05 (external/deferred; not in the UX2
DAG; not a new UX2 WP).

## 7. Implementation Strategy

```text
REUSE     → existing production components/tokens/data/services (primary)
ADAPT     → existing section/hero patterns, BibliographyEntry, hfm-status
MINIMAL NEW PRESENTATION PRIMITIVE → DHObjectLayout + BibliographicRecord only
```

Rejected:

```text
REWRITE · NEW UI FRAMEWORK · PARALLEL DESIGN SYSTEM · PROTOTYPE COPY-IN
```

Production implementation uses the existing HFM Vue 3 architecture.

## 8. Prototype Status

```text
prototype/ux2/** = REFERENCE / ACCEPTANCE EVIDENCE (never bulk-copied)
```

| Prototype concept | Production treatment |
| --- | --- |
| Slot presence semantics (PRESENT/ABSENT_OPTIONAL/INCOMPLETE_WITH_EVIDENCE_STATE) | PORT_SEMANTICS (into DHObjectLayout) |
| Object-title level adaptation (titleTag) | PORT_SEMANTICS (production contract §5) |
| Relations semantics vocabulary (EXPLICIT_RELATION/ASSOCIATED_CONTEXT/CO_PRESENTED_ONLY) | PORT_SEMANTICS |
| Status badge pattern (`.hfm-status` + data-status) | ADAPT_PATTERN (extend existing production pattern) |
| DOM construction via createElement/textContent (no innerHTML) | REFERENCE_ONLY (production uses Vue SFC) |
| verify.mjs Playwright+axe harness | REFERENCE_ONLY (production re-implements in Vitest + Playwright e2e) |
| Fixtures / prototype HTML / prototype CSS composition | DO_NOT_PORT (production reads authoritative data) |

## 9. Hard Architecture Boundaries

```text
NO_DATABASE_CHANGE · NO_SCHEMA_CHANGE · NO_DOMAIN_MODEL_CHANGE
NO_API_CONTRACT_CHANGE · NO_AUTH_CHANGE · NO_RBAC_CHANGE
NO_GRAPH_DATABASE · NO_HFB_RUNTIME_DEPENDENCY · NO_NEW_LARGE_UI_FRAMEWORK
```

Violation at any point is automatic acceptance failure.

## 10. Content / Historical Boundaries

```text
NO_HISTORICAL_FABRICATION · NO_RELATION_INFERENCE
NO_EDITION_GENEALOGY_INFERENCE · NO_HERITAGE_LINEAGE_INFERENCE
NO_UNVERIFIED_PUBLIC_COPY
```

Production UI displays only facts traceable to accepted HFM data.

## 11. Clinical Boundary

```text
CLINICAL = REJECTED
```

No UX2 work package may introduce diagnosis, treatment recommendation, clinical
acupoint recommendation, efficacy claim, prescription guidance, or clinical
decision support. Violation → `P0`.

## 12. Presentation State Contract

```text
SOURCE FACT → PRESENTATION STATE → PUBLIC LABEL
```

Supported states remain the accepted G1 set; no hidden production-only states;
missing data never automatically becomes historical absence (G1-C precedence +
fail-closed).

## 13. Token Contract

Production uses the existing frozen token architecture (`apps/frontend/src/styles/tokens.css`,
READ_ONLY). Required semantic roles: `surface-paper`, `surface-archive`,
`surface-evidence` (G1-B mappings to existing tokens). Prohibited: new palette,
arbitrary hex, one-off design token, parallel token system.

## 14. File-Level Change Allowlist

Default rule: `NOT_EXPLICITLY_ALLOWED = FORBIDDEN`.

### ALLOW_CREATE

```text
apps/frontend/src/components/primitives/DHObjectLayout.vue
apps/frontend/src/components/primitives/BibliographicRecord.vue
apps/frontend/src/presentation/stateMapping.ts
apps/frontend/src/__tests__/ux2_*.spec.ts
apps/frontend/e2e/ux2-*.spec.ts
```

### ALLOW_MODIFY

```text
apps/frontend/src/views/persons/PersonDetailView.vue
apps/frontend/src/views/jiayi/JiayiView.vue
apps/frontend/src/views/heritage/HeritageView.vue
apps/frontend/src/views/search/SearchView.vue
apps/frontend/src/views/research/ResearchSearchView.vue
apps/frontend/src/views/HomeView.vue
apps/frontend/src/styles/foundations.css                        (hfm-status vocabulary + token-role application)
```

### READ_ONLY

```text
apps/frontend/src/styles/tokens.css
apps/frontend/src/data/**            (authoritative data sources)
apps/frontend/src/config/**          (corePerson, navigation)
apps/frontend/src/services/**        (api, reader, export, heritage, media)
apps/frontend/src/types/**           (domain types)
apps/frontend/src/router/**          (no route change)
apps/frontend/src/stores/**          (auth)
apps/frontend/src/components/reader/CitationBlock.vue
apps/frontend/src/components/states/**, Timeline.vue, LineageGraph.vue, EditionLineageImage.vue,
apps/frontend/src/components/research/**, SearchHighlight.vue, AppSkipLink.vue, AppFooter.vue
```

### FORBIDDEN

```text
backend/** · packages/** · migrations/** · schema/** · server/** 
apps/frontend/src/router/** (modification) · services/api.ts (modification) · stores/auth.ts
apps/frontend/src/types/** (modification) · apps/frontend/src/data/** (modification)
apps/frontend/package.json (dependencies) · apps/frontend/vite.config.ts · playwright.config.ts (modification)
prototype/ux2/** (copy into apps — DO_NOT_PORT)
```

### Special Rule — `components/search/BibliographyEntry.vue` (G4-O-1 closure)

Normalized deterministic rule (replaces the former dual ALLOW_MODIFY / READ_ONLY
wording). One rule, no conditionals:

```text
components/search/BibliographyEntry.vue =
  ALLOW_MODIFY_ONLY_IN_UX2-P4

outside UX2-P4 =
  FORBIDDEN_TO_MODIFY
```

Implementation scope and allowlist are NOT widened by this rule. This is a
documentation-only normalization.

```text
G4-O-1 = CLOSED_DOCUMENTATION_ONLY
```

## 15. Exit State

```text
UX2_G4 = PACKAGE_READY / PENDING_INDEPENDENT_REVIEW
PRODUCTION_IMPLEMENTATION = LOCKED
```
