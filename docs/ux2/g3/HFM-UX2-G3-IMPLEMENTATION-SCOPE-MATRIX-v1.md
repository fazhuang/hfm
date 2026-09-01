# HFM-UX2 G3 Implementation Scope Matrix v1

Status: UX2-G3 NORMATIVE ARTIFACT · Package-ready for independent audit
Frozen UI Baseline: `ae55abc606c419f27259fc80bb8bee258d595ce9`
Binding: G1 contracts (ACCEPTED) + G2 evidence (ACCEPTED) +
`UX2_G2_ACCEPTED` + `HFM-UX2-G3-DESIGN-ACCEPTANCE-PACKAGE-v1.md`.

Purpose: classify every candidate implementation item for a FUTURE G4
deliberation. **A G2 prototype proving a design does NOT auto-authorize
implementation.** Each item below is a candidate until G4 decides.

## 0. Classification Vocabulary

```text
AUTHORIZED_CANDIDATE — proven by G1+G2; implementable without domain/API/DB
                       expansion; ready for G4 consideration as-is.
DEFERRED             — recognized requirement; not implementable now because
                       an authoritative data capability or contract condition
                       is not yet met.
EXCLUDED             — permanently outside UX2 scope (negative authorization);
                       see RISK-AND-DEFERRED-ITEMS §4.
UNRESOLVED           — required data/field is SOURCE_FIELD_UNRESOLVED; item
                       cannot be implemented without either resolving the
                       field or re-scoping.
```

## 1. Implementation Scope Matrix

| # | Item | Classification | G2 evidence | G4 condition / note |
| --- | --- | --- | --- | --- |
| 1 | DHObjectLayout | AUTHORIZED_CANDIDATE | index.html + P1/P3/P5: 3 slot states, object-title level adaptation (titleTag), relations semantics | Implement against frozen G1-A §1; reuse titleTag contract; resolve N-F-1 truthiness ambiguity BEFORE API reuse (see RISK register §3) |
| 2 | BibliographicRecord | AUTHORIZED_CANDIDATE | index.html + P2/P4: 5 kinds, field hierarchy, degradation | Implement against frozen G1-A §2; absent fields degrade per NB-06 |
| 3 | Person surface | AUTHORIZED_CANDIDATE | P1 `p01-person.html` | Header/Context/Evidence/Relations + incomplete states; Life Events / Historical Assessments / Later Scholarship / Archival Media are DEFERRED (F-5) |
| 4 | Jiayi surface | AUTHORIZED_CANDIDATE | P2 `p02-jiayi.html` | 19 editions 存目; 2 FULL_TEXT; edition-relations DATA-GAP; chronology ≠ lineage |
| 5 | Heritage surface | AUTHORIZED_CANDIDATE | P3 `p03-heritage.html` | Two-context separation; PARTIAL gap; recognition secondary metadata (no honor wall) |
| 6 | Scholarly Discovery | AUTHORIZED_CANDIDATE | P4 `p04-discovery.html` | Facets = search-index type counts (F-3 semantic fixed); 515/5 shown separately; no UI re-classification |
| 7 | Homepage narrative | AUTHORIZED_CANDIDATE | P5 `p05-home.html` | Frozen copy + five-part order; approved copy only; no new promotional content |
| 8 | Presentation-state mapping | AUTHORIZED_CANDIDATE | G1-C matrix; P1/P2/P3/P4 statuses | Deterministic mapping + precedence + fail-closed; labels per G1-C; no synthetic flags |
| 9 | Token semantic roles | AUTHORIZED_CANDIDATE | G1-B spec; tokens.css projection 35/35 | Production consumes EXISTING frozen tokens; no new palette; new-token justification rule holds |
| 10 | Responsive behavior | AUTHORIZED_CANDIDATE | 0 overflow @375/1920 all 6 pages | Semantic preservation; meaning never encoded in position/hover/connectors |
| 11 | Accessibility requirements | AUTHORIZED_CANDIDATE | axe 0 on all 6 pages; heading hierarchy (F-1); focus ring; reduced motion; status text + color | Production-testable via axe-core + keyboard/focus/reduced-motion checks (G3-AC-10) |
| 12 | CitationLocator | AUTHORIZED_CANDIDATE | P4 document-level locator; G1-A §3.1 | Renders ONLY existing fields; page/volume-level remains collapsed (U-04 → UNRESOLVED sub-item) |
| 13 | CitationExport | DEFERRED | G1-A §3.2 capability gate | Format (plain / GB/T 7714 / BibTeX) MAY enable only when all required source fields exist AND transformation is deterministic; authoritative data at required granularity not yet confirmed; no format forces domain expansion |

## 2. CitationExport — DEFERRED Rationale

CitationExport is capability-gated by G1-A §3.2. The G2 prototype demonstrated
only CitationLocator at document level; it did not demonstrate export fields
(complete citation field set per format) because the authoritative data
capability is not yet confirmed (U-04 page-level locator unresolved; export
field completeness unverified). Per the directive: "不得因 G2 prototype 成立
自动授权" — the design proof does not carry CitationExport into G4 scope.
Classification: DEFERRED.

## 3. Production Mapping — Design Proof vs Implementation Requirement

G3 answers: which prototype outputs are design proof, and which may become
production implementation requirements. **The equivalence
`prototype code = production code` is explicitly rejected.**

| Prototype artifact | Classification | G4 treatment |
| --- | --- | --- |
| `assets/data/fixtures.js` | PROTOTYPE_ONLY | Never promoted. Production reads its own authoritative frozen data sources (`apps/frontend/src/data/*`). Fixtures exist only to isolate the prototype. |
| `index.html` + `p01…p05.html` | PROTOTYPE_ONLY | Never promoted. Pages are isolation vehicles; their copy/behavior becomes DESIGN_REQUIREMENT statements, not HTML to copy. |
| `assets/css/ux2.css` (composition) | PROTOTYPE_ONLY | Never promoted as a file. Its token usage rules (tokens-only, no hex) become DESIGN_REQUIREMENT; production composition is re-implemented against production tokens. |
| `assets/css/tokens.css` | PROTOTYPE_ONLY (file) / DESIGN_REQUIREMENT (values) | File is a prototype projection. The 35 VALUES are the frozen production tokens already owned by `apps/frontend/src/styles/tokens.css`; production uses its own file. |
| `assets/js/ux2.js` (renderers) | IMPLEMENTATION_REFERENCE_ONLY | Reference for behavior: createElement/textContent DOM (no innerHTML), status badge pattern, titleTag level-adaptation mechanism, slot presence rendering. Production re-implements; do not copy verbatim (framework/stack differs). |
| `verify.mjs` | IMPLEMENTATION_REFERENCE_ONLY | Reference for verification approach: Playwright + axe-core over all surfaces, PT-NB assertions, responsive overflow checks. Production test suite re-implements against production stack. |
| G1-C state mapping / G1-B token roles / G1-A slot contract | DESIGN_REQUIREMENT | These are the normative requirements G4 implements. |

Explicit principle:

```text
DESIGN_REQUIREMENT          — normative behavior production must satisfy.
IMPLEMENTATION_REFERENCE_ONLY — technique/approach to reference, re-implemented
                                in the production stack.
PROTOTYPE_ONLY              — never auto-promoted; exists for evidence only.
```

## 4. No Auto-Authorization Statement

The G2 prototype acceptance proves the DESIGN. It does not authorize code
promotion, route replacement, dependency adoption, or production changes of
any kind. G4, if authorized, starts from the DESIGN_REQUIREMENT set in §3 and
the frozen contracts — not from prototype files.

## 5. Exit State

```text
G4 CANDIDATE SCOPE = DETERMINISTIC (AUTHORIZED_CANDIDATE × 12 + DEFERRED × 1)
NO_HIDDEN_IMPLEMENTATION_AUTHORIZATION = TRUE
UX2_G4 = NOT_AUTHORIZED
PRODUCTION_IMPLEMENTATION = LOCKED
```
