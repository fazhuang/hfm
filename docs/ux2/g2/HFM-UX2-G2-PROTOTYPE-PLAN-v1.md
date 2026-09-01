# HFM-UX2 G2 Prototype Plan v1

Status: UX2-G2 NORMATIVE ARTIFACT · Binds to UX2-G1 (ACCEPTED) and frozen UI
baseline `ae55abc606c419f27259fc80bb8bee258d595ce9`
Goal: build a limited, auditable, real-data representative prototype proving the
UX2 presentation language holds **without modifying Domain/API/DB**.
Implementation: NOT_AUTHORIZED · Production code change: PROHIBITED.

## 1. Isolation Model

```text
prototype/ux2/          — isolated prototype (new directory, no production route)
  ├── index.html        — core primitive demos (DHObjectLayout ×3 slot states, BibliographicRecord ×5 kinds)
  ├── p01-person.html   — P-G2-01 Huangfu Mi Person Archive
  ├── p02-jiayi.html    — P-G2-02 Jiayi Work / Edition Experience
  ├── p03-heritage.html — P-G2-03 Heritage Living Archive (two evidence contexts)
  ├── p04-discovery.html— P-G2-04 Scholarly Discovery (515/5)
  ├── p05-home.html     — P-G2-05 Homepage Exhibition Narrative (01–05)
  └── assets/
      ├── css/tokens.css  — value-identical token projection of the frozen
      │                     semantic tokens (provenance header; 35/35 values)
      ├── css/ux2.css     — prototype composition/editorial styles (tokens only)
      ├── data/fixtures.js— fixtures derived from frozen baseline data (provenance per object)
      └── js/ux2.js       — renderers: DHObjectLayout, BibliographicRecord (DOM, no innerHTML)
```

Isolation guarantees:

```text
NO_PRODUCTION_ROUTE_REPLACEMENT   — no production view/router touched
NO_DATABASE_CHANGE · NO_SCHEMA_CHANGE · NO_API_CHANGE · NO_MIGRATION
NO_AUTH_CHANGE · NO_RBAC_CHANGE
NO_HFB_RUNTIME_DEPENDENCY
NO_PRODUCTION_CONTENT_MUTATION    — fixtures are read-only copies with provenance
```

## 2. Reuse Matrix

| Reused from frozen baseline | Prototype usage |
| --- | --- |
| Semantic tokens (tokens.css values) | assets/css/tokens.css (value-identical projection; 35/35 values) |
| `hfm-reading` / `hfm-eyebrow` / `hfm-status` conventions | assets/css/ux2.css equivalents |
| corePerson data | P1 header/context |
| jiayiView editions (19) + DATA-GAP + FULL_TEXT 2 | P2 |
| heritageView (project/person/events/lineage PARTIAL) | P3 |
| searchIndex invariants (515/5) + paper previews | P4 |
| homeProjection narrative (01–05) | P5 |
| readerDocuments citation (《晋书》房玄龄) | P4 CitationLocator |

## 3. Core Primitives Under Test

### DHObjectLayout

Slot presence states verified on pages:

```text
PRESENT                       — person header/context/evidence/relations (P1, index)
ABSENT_OPTIONAL               — portrait / holding-institution / unused slots collapse fully (index, P1)
INCOMPLETE_WITH_EVIDENCE_STATE— 四论全文未收录（METADATA_ONLY）；生卒年学术争议（SCHOLARLY_UNCERTAIN）
                                ；版本关系 DATA-GAP（P2）
```

### BibliographicRecord

Kinds verified: classical work (P2 work header), edition (P2 ×19, P4), paper
(P4), search result (P4), source reference (P4 citation). Hanging indent,
metadata hierarchy, compact density, no SaaS card styling; narrow-viewport
degradation verified in the responsive audit.

## 4. Five Unresolved Source Fields (U-01…U-05)

Handling rule: DO_NOT_INVENT · DO_NOT_ADD_SCHEMA · DO_NOT_ADD_MOCK_HISTORICAL_FACT.
Real field → show; no field → collapse; meaningful absence → allowed incomplete
presentation state. Prototype-specific dispositions:

| Item | Prototype disposition |
| --- | --- |
| U-01 scholarly uncertainty | derived from verified 其传 text (建安/正始 两说) → SCHOLARLY_UNCERTAIN note; no new field |
| U-02 historical loss | 逸士传/列女传 辑佚 note present in verified text; no loss flag invented |
| U-03 holding institution | slot ABSENT_OPTIONAL (collapses) |
| U-04 page-level citation locator | CitationLocator renders document-level only; page slot collapses (P4) |
| U-05 per-edition digitization | all 19 editions render METADATA_ONLY 存目; no fake digitized state |

## 5. Verification Runs (see audit report)

- Token scan: `rg -n '#[0-9A-Fa-f]{3,8}' prototype/ux2` → every hex must equal a
  frozen tokens.css value (no palette drift).
- PT-NB-01…12 assertions over rendered DOM (Playwright, file:// pages).
- Responsive: 375 / 768 / 1280 / 1920 semantic integrity + no horizontal scroll.
- Accessibility: axe-clean (project standard), keyboard, focus, reduced motion.
- Production delta: `git status --short` / `git diff -- apps packages` → no
  production implementation delta.
