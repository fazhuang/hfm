# HFM-UX2 G4 Production Surface Mapping v1

Status: UX2-G4 NORMATIVE ARTIFACT · Package-ready for independent review
Binding: authoritative baselines (G0–G3 archive `e8593ff…`); production
routes/components inspected from `apps/frontend` at preparation time.

Purpose: exact mapping from accepted UX2 surfaces to current production
routes/components, with the route/API/schema-change invariant.

## 1. Surface → Production Mapping

| UX2 Surface | Current Route | Current Entry Component | Current Data Source | Existing Reusable Components | UX2 Change Boundary | Route Change Required? | API Change Required? | Schema Change Required? |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P1 Person Archive | `/persons/:id` (canonical `/persons/person-huangfu-mi`) | `views/persons/PersonDetailView.vue` | `config/corePerson.ts`, `services/api.ts` (`fetchPublicPerson`, `fetchPublicMedia`), `data/readerDocuments.ts`, `data/archiveInventory.ts` | Timeline, EmptyState/ErrorState/LoadingState, CitationBlock, states | adopt DHObjectLayout regions + G1-C states; F-5 Life Events / Historical Assessments / Archival Media sections; heading hierarchy | NO | NO | NO |
| P2 Jiayi Work / Edition | `/jiayi` | `views/jiayi/JiayiView.vue` | `data/jiayiView.ts` (19 editions, scholars, papers, sources), `data/workCollection.ts` | Timeline, EditionLineageImage, BibliographicRecord (P0) | edition records via BibliographicRecord (存目); work-profile alignment; DATA-GAP caption | NO | NO | NO |
| P3 Heritage Living Archive | `/heritage` | `views/heritage/HeritageView.vue` | `data/heritageView.ts` (project/person/recognitions 8/academic/technical/apprenticeships/studios/media/lineage/timeline) | LineageGraph, Timeline, DHObjectLayout (P0) | explicit HISTORICAL_TEXTUAL_CONTEXT vs CONTEMPORARY_LIVING_ARCHIVE_CONTEXT separation; recognition secondary metadata; PARTIAL gap | NO | NO | NO |
| P4 Scholarly Discovery | `/search` + `/research/search` (+ `/research`) | `views/search/SearchView.vue`, `views/research/ResearchSearchView.vue`, `views/research/ResearchHomeView.vue` | `data/searchIndex.ts` (SEARCH_INDEX, facetCounts, 515/5), `data/jiayiView.ts` (papers) | BibliographyEntry, SearchHighlight, BibliographicRecord (P0), CitationBlock | results via BibliographicRecord; document-level CitationLocator; 515/5 separation; facet semantic already search-index type counts (F-3) | NO | NO | NO |
| P5 Homepage Exhibition Narrative | `/` | `views/HomeView.vue` | `data/homeProjection.ts` (frozen narrative), `data/researchProjection.ts` | existing home sections; state labels (P0) | frozen narrative order/grammar alignment; state labels; verification | NO | NO | NO |
| Primitive hub (index.html) | — (no production route; prototype-only) | — | — | — | DO_NOT_PORT; primitives ship via P0 components | — | — | — |

Related production surfaces consumed by UX2 surfaces (READ_ONLY): `/reader`,
`/reader/:id` (`views/reader/ReaderView.vue`, `ReaderDocView.vue`), `/yan`
(`views/yan/YanView.vue`), `/works`, `/works/:id`, `/archive`
(`views/archive/ArchiveView.vue`), `/library`.

## 2. Invariant Verification

```text
API_CHANGE_REQUIRED   = NO    (all candidates)
SCHEMA_CHANGE_REQUIRED = NO   (all candidates)
ROUTE_CHANGE_REQUIRED  = NO   (all candidates — surfaces map to existing routes)
```

Any candidate requiring API/schema change is BLOCKED unless separately
authorized outside UX2. No candidate does; no route names are invented; all
routes above are existing production routes.

## 3. Existing Production Reuse Inventory

Components (reused, not rewritten): `Timeline.vue`, `LineageGraph.vue`,
`EditionLineageImage.vue`, `CitationBlock.vue`, `BibliographyEntry.vue`,
`SearchHighlight.vue`, `EvidenceExplorer.vue`, `RelatedEntityLinks.vue`,
states (`EmptyState`/`ErrorState`/`LoadingState`), `AppSkipLink.vue`,
`AppFooter.vue`.

Patterns (adapted): `.hfm-status` status badges (foundations.css), hero/section
composition, chronology ≠ lineage captions, clinical-boundary disclaimers,
`hfm-eyebrow` / `hfm-reading` conventions.

Data/services (read-only): `data/searchIndex.ts`, `heritageView.ts`,
`jiayiView.ts`, `homeProjection.ts`, `archiveInventory.ts`,
`workCollection.ts`, `readerDocuments.ts`, `yanCollection.ts`,
`researchProjection.ts`, `contentInventory.ts`, `config/corePerson.ts`,
`config/navigation.ts`, `services/api.ts`, `services/reader.ts`,
`services/export.ts`, `services/heritage.ts`, `services/media.ts`.

## 4. Architecture Integrity Notes

- Search facets in production are computed by `facetCounts(results)` over the
  current result set (`searchIndex.ts`) — the F-3 "search-index type count"
  semantic is already the production behavior; no change required.
- Reader citations render at document/section level only (`CitationBlock.vue`)
  — U-04 page-level locator stays collapsed; no change required.
- All 19 editions render 元数据已录 (METADATA_ONLY) — U-05 stays unresolved;
  UX2 renders via BibliographicRecord 存目 state without new flags.
- `hfm-status` currently supports AVAILABLE / METADATA_ONLY / DATA_GAP;
  candidate 08 extends the vocabulary with the accepted G1-C presentation
  states and public labels (presentation-only, no domain change).

## 5. Exit State

```text
SURFACE_MAPPING_COMPLETE = TRUE (5 UX2 surfaces → existing production routes)
ROUTE_CHANGE_REQUIRED = NO · API_CHANGE_REQUIRED = NO · SCHEMA_CHANGE_REQUIRED = NO
UX2_G4 = PACKAGE_READY / PENDING_INDEPENDENT_REVIEW
```
