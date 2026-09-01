# HFM-UX2 G2 Prototype Audit Report v1

Status: UX2-G2 FINAL REPORT · Independent-audit-ready
Frozen UI Baseline: `ae55abc606c419f27259fc80bb8bee258d595ce9`
G1 Contract Binding: HFM-UX2-PRESENTATION-CONTRACT-v1 / DESIGN-TOKEN-MAPPING-SPEC-v1 /
PRESENTATION-STATE-MATRIX-v1 / NEGATIVE-BOUNDARY-VERIFICATION-MATRIX-v1 (docs/ux2)
Prototype Paths: `prototype/ux2/` (isolated; no production route touched)

## 1. Prototype Surface Results

| Surface | Path | Result |
| --- | --- | --- |
| P-G2-01 Huangfu Mi Person Archive | `p01-person.html` | PASS — DHObjectLayout Header/Context/Evidence/Relations PRESENT; optional slots (portrait/holding) collapse; incomplete states (四论全文未收录 METADATA_ONLY；生卒年争议 SCHOLARLY_UNCERTAIN) rendered |
| P-G2-02 Jiayi Work/Edition | `p02-jiayi.html` | PASS — Work header (19/2/DATA-GAP invariants as badges); 19 editions as BibliographicRecord 存目; FULL_TEXT 2; DATA-GAP note; no genealogy inferred |
| P-G2-03 Heritage Living Archive | `p03-heritage.html` | PASS — HISTORICAL_TEXTUAL_CONTEXT and CONTEMPORARY_LIVING_ARCHIVE_CONTEXT rendered as two semantic bands; PARTIAL gap explicit; 2007 / 2023-09-26 / 2025-04-25 events from verified data; 第六代名医 as metadata, not an honor badge |
| P-G2-04 Scholarly Discovery | `p04-discovery.html` | PASS — 515/5 presented unmodified; facets from existing taxonomy; BibliographicRecord results (work/edition/paper/search-result); CitationLocator at document level; page-level locator collapsed (U-04) |
| P-G2-05 Homepage Exhibition Narrative | `p05-home.html` | PASS — hero (approved copy) + dual primary + weak research entry; narrative 01→05 in frozen order; editorial rhythm, no card grid |

Core primitives (index.html): DHObjectLayout verified with PRESENT (7 slots across
demos), ABSENT_OPTIONAL (collapse, no empty shells), INCOMPLETE_WITH_EVIDENCE_STATE
(1 verified on hub); BibliographicRecord verified across classical work, edition,
paper, search result, and source reference kinds across surfaces.

## 2. Data Binding Result

Every visible fact traces to the frozen baseline (full ledger:
HFM-UX2-G2-PROTOTYPE-DATA-BINDING-v1.md). Status distribution per surface:
all UI fields `EXISTING` or explicitly `DERIVED_PRESENTATION_ONLY`; optional
absent fields `OPTIONAL_COLLAPSED`; no string outside the four-class vocabulary.

## 3. SOURCE_FIELD_UNRESOLVED Status

| Item | Prototype disposition | Status |
| --- | --- | --- |
| U-01 scholarly uncertainty | derived from verified 其传 text → SCHOLARLY_UNCERTAIN note | DERIVED_PRESENTATION_ONLY |
| U-02 historical loss | 辑佚 note from verified text; no flag | DERIVED_PRESENTATION_ONLY |
| U-03 holding institution | slot ABSENT_OPTIONAL (collapses) | OPTIONAL_COLLAPSED |
| U-04 page-level citation locator | document-level only; page slot collapsed | OPTIONAL_COLLAPSED |
| U-05 per-edition digitization | all 19 editions render METADATA_ONLY 存目 | OPTIONAL_COLLAPSED (no fake digitized state) |

No synthesized museum, page, digitization, loss, or uncertainty data.

## 4. Token Audit (G1-B)

`prototype/ux2` unique hex = 35; all 35 present in frozen `tokens.css` →
**ZERO DRIFT**. No new palette, no arbitrary one-off tokens, no library.

## 5. Responsive Audit

Verified at 375 and 1920 across all 6 pages: **0 horizontal scroll everywhere**
(after adding `overflow-wrap: anywhere` for long evidence-context tokens).
Meaning preservation: relations readable without connectors; heritage two
contexts remain two semantic bands when stacked; BibliographicRecord hanging
indent wraps without overflow; metadata does not crowd titles.

## 6. Accessibility Audit

- axe (project axe-clean standard, axe-core 4.x): **0 violations** on the
  primitive hub (representative surface).
- Status conveyed by text label + token color (not color-only).
- DOM built via createElement/textContent — no innerHTML, no XSS surface.
- Keyboard/focus: native anchors/buttons focusable; `:focus-visible` ring.
- Reduced motion: global `prefers-reduced-motion` guard.
- Semantic structure: `article/section/header/main`, headings ordered, `role=status`
  on incomplete-state notes.

## 7. Negative Boundary Audit (G1-D → PT-NB-01…12)

| PT-NB | Assertion | Result |
| --- | --- | --- |
| 01 unsupported historical facts | no invented years/roles | PASS |
| 02 relation inference | no connector implies lineage; relation semantics explicit (EXPLICIT_RELATION/ASSOCIATED_CONTEXT) | PASS |
| 03 edition genealogy | no 继承自/源自 claims; DATA-GAP only | PASS |
| 04 uninterrupted heritage lineage | no ancient→modern single chain; PARTIAL gap | PASS |
| 05 clinical guidance | zero clinical patterns | PASS |
| 06 synthesized citation page/volume | none | PASS |
| 07 historical absence from data absence | no 已佚/亡佚 inference | PASS |
| 08 empty placeholder shell | no 暂无内容/即将上线 shells | PASS |
| 09 hard-coded palette | 35/35 in frozen set — zero drift | PASS |
| 10 responsive semantics | 0 overflow @375/1920; meaning preserved | PASS |
| 11 color-only status | labels carry text | PASS |
| 12 production change | none (see §8) | PASS |

## 8. Production Delta Audit

```text
git status --short          → only untracked: prototype/ux2/, docs/ux2/g2/, plus
                              pre-existing untracked docs/research/, hfmzl/, zzcl/
git diff --stat -- apps packages → EMPTY
HEAD                        → ae55abc606c419f27259fc80bb8bee258d595ce9 (unchanged)
```

**NO_PRODUCTION_IMPLEMENTATION_DELTA.**

## 9. G2 Acceptance Matrix Result

| ID | Criterion | Result |
| --- | --- | --- |
| G2-AC-01 | 5 surfaces + primitive hub exist | PASS |
| G2-AC-02 | both core primitives reusable | PASS |
| G2-AC-03 | all facts trace to authoritative data | PASS |
| G2-AC-04 | U-01…U-05 remain unresolved, never synthesized | PASS |
| G2-AC-05 | no domain/API/DB expansion | PASS |
| G2-AC-06 | no unsupported relation inference | PASS |
| G2-AC-07 | heritage contexts separated | PASS |
| G2-AC-08 | clinical zero-tolerance | PASS |
| G2-AC-09 | presentation states conform to G1-C | PASS |
| G2-AC-10 | tokens conform to G1-B | PASS |
| G2-AC-11 | responsive semantics | PASS |
| G2-AC-12 | accessibility | PASS |
| G2-AC-13 | G1-D negative matrix | PASS |
| G2-AC-14 | frozen production unchanged | PASS |
| G2-AC-15 | sufficient to decide future authorization | PASS |

## 10. Visual Quality

Scholarly, restrained, object-first, evidence-first, editorial, contemporary
oriental. Not a SaaS dashboard, government portal, marketing landing, news
aggregation, museum gimmick, or AI product interface.

## Final Verdict

```text
UX2_G2_PROTOTYPE_READY_FOR_INDEPENDENT_AUDIT
```
