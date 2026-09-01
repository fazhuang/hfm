# HFM-UX2 G2 Corrective Pass v1

Status: `UX2_G2_CORRECTED_CANDIDATE_READY_FOR_REAUDIT` · PENDING_REAUDIT
Frozen UI Baseline: `ae55abc606c419f27259fc80bb8bee258d595ce9` (unchanged)
Corrective inputs: Claude Independent Audit findings F-1…F-5 (sole correction source)
Corrective scope: `prototype/ux2/**` + `docs/ux2/g2/**` only
Original records: NOT deleted — see Audit Chain (§11). v1 artifacts remain the
"Original G2" layer; this document is the correction overlay.

## 0. Governance State

```text
UX2-G0 = ACCEPTED
UX2-G1 = ACCEPTED
UX2-G2 = CORRECTION_REQUIRED  →  CORRECTED_CANDIDATE / PENDING_REAUDIT
UX2-G3 = NOT_AUTHORIZED
UX2-G4 = NOT_AUTHORIZED
PRODUCTION_IMPLEMENTATION = LOCKED
```

No G2 scope expansion. No new design phase. F-5 is explicitly deferred
(NON_BLOCKING), not implemented.

## 1. Correction Record — F-1 (P1 BLOCKING) — CORRECTED

| Field | Value |
| --- | --- |
| Original Claude Finding | `p01-person.html` renders heading order `H1 → H3 → H2`. Root cause: DHObjectLayout object title uses a fixed `<h3>`. Violates G1 §8 heading hierarchy and G2-AC-12 (accessibility PASS claim). |
| Required Fix Principle | Keep DHObjectLayout reusable; no p01-only hardcoded patch; make the object-title semantic level adapt to document context; presentation-only solution (no domain field / API / schema / production component / route change). |
| Chosen Mechanism | Option A — `renderDHObjectLayout` accepts a presentation-only `header.titleTag` parameter ('h1'..'h6' / 1..6 / 'p' / 0 / 'none'); the renderer deterministically re-tags any built `.dh-object__title` node to the declared level. A reusable factory `dhObjectTitle(tagOrLevel, text)` is the single creation point for object titles. Default (no `titleTag`) preserves the surface-built tag for backward compatibility. |
| Changed Files | `prototype/ux2/assets/js/ux2.js` (titleTag support + `dhObjectTitle` factory + contract docs); `prototype/ux2/p01-person.html` (header slot `titleTag: 2`, title built via `dhObjectTitle(2, …)`); `prototype/ux2/index.html` (demo slot `titleTag: 3`, `headerRow` via `dhObjectTitle(3, …)`). |
| Resulting Outline | p01: `H1 皇甫谧人物档案 → H2 皇甫谧 → H2 语境·证据·关联` (no skip). index: `H1 → H2 → H3 (demo object) → H2 …` (no skip). Other surfaces unchanged. |
| Verification Command | `node prototype/ux2/verify.mjs` (axe-core over all 6 pages) + Playwright outline dump of `main h1..h4`. |
| Verification Result | axe `heading-order` violations: p01 `1 → 0`; all other pages `0` (unchanged). `AXE_VIOLATIONS = 0` across all six pages. |
| Regression Result | PT-NB-01…12 all PASS; responsive 0 overflow @375/1920 all pages; primitives slot states unchanged (7 PRESENT + 1 INCOMPLETE_WITH_EVIDENCE_STATE); DHObjectLayout still renders 3 demo layouts on the hub. No new heading-order violation introduced on any surface. |

## 2. Correction Record — F-2 (P2) — CORRECTED

| Field | Value |
| --- | --- |
| Original Claude Finding | Prototype token file is not a byte-for-byte copy of the frozen token file (original comments stripped), yet provenance text said "byte-copied". |
| Correction | Provenance wording corrected to the true semantics — `VALUE-IDENTICAL TOKEN PROJECTION`: same 35 values as the frozen source, file organization/comments not reproduced byte-for-byte. Token VALUES untouched. |
| Changed Files | `prototype/ux2/assets/css/tokens.css` (provenance header); `docs/ux2/g2/HFM-UX2-G2-PROTOTYPE-PLAN-v1.md` (2× "byte-copy" → "value-identical projection"). |
| Verification Command | hex scan: `node` set-diff of `prototype/ux2` hex values vs `apps/frontend/src/styles/tokens.css`. |
| Verification Result | prototype unique hex 35, all 35 present in frozen set; `NEW_PALETTE = ZERO`; `TOKEN_DRIFT = ZERO`; 35/35 values match. |

## 3. Correction Record — F-3 (P2) — CLARIFIED

| Field | Value |
| --- | --- |
| Original Claude Finding | Facet "档案 8" sourced from `ARCHIVE_RECORDS.length = 8` (archiveInventory.ts) while the full searchIndex archive-type count is 16; provenance claimed searchIndex type counts — semantic ambiguity. |
| Chosen Authoritative Semantic | Option B — **搜索索引 archive-type 结果数** (search-index type count). Rationale: the P4 surface is a search/discovery page; every other facet (人物 2 / 作品 8 / 版本 19 / 论文题录 5 / 文本 6) exactly matches the deterministic SEARCH_INDEX type counts; the facet labels are the SEARCH_INDEX `TYPE_LABELS`; the fixture provenance header already named `searchIndex.ts`. The archive facet therefore reports the 16 archive-type index entries, NOT the 8 inventory objects. |
| Consistency Applied | UI label (`档案 16` + explicit count-basis note on the page) · fixture provenance (per-facet semantic documented in `fixtures.js`) · data-binding ledger (Facets row restated with the 16-entry derivation) — all three now state the same single semantic. |
| Derivation (16) | heritage-project 1 + HERITAGE_APPRENTICESHIPS 1 + HERITAGE_STUDIOS 2 + HERITAGE_MEDIA 4 + ARCHIVE_RECORDS 8 = 16. |
| Changed Files | `prototype/ux2/assets/data/fixtures.js` (档案 8 → 16 + provenance); `prototype/ux2/p04-discovery.html` (H2 "Facets（搜索索引类型计数）" + count-basis note); `docs/ux2/g2/HFM-UX2-G2-PROTOTYPE-DATA-BINDING-v1.md` (Facets row). |
| Verification Command | Playwright DOM dump of `#facets li` text; source cross-check of `searchIndex.ts` entry construction. |
| Verification Result | Rendered facets: `人物 2 / 作品 8 / 版本 19 / 档案 16 / 论文题录 5 / 文本 6`. No number changed arbitrarily — the 档案 value follows the same search-index semantic as the other five facets. |

## 4. Correction Record — F-4 (P2) — CORRECTED

| Field | Value |
| --- | --- |
| Original Claude Finding | Data ledger claimed 8 recognition records; fixture rendered 4 condensed strings covering only 7/8; `首届平凉名医` missing. |
| Correction | Option A — full coverage of all 8 verified `HERITAGE_RECOGNITIONS` records. `首届平凉名医` (r-pl-my) added to the grouped string `甘肃省名中医 · 平凉市名中医 · 首届平凉名医 · 崆峒工匠`. Recognition stays secondary metadata — compact grouped strings, no honor wall. |
| Coverage Now | r-fy / r-gs-mzy / r-pl-mzy / r-pl-my / r-kt-gj / r-gs-xjj / r-gs-rc / r-yz-2016 → 8/8, presented as 4 grouped display strings. |
| Changed Files | `prototype/ux2/assets/data/fixtures.js` (recognition array + provenance mapping each string to record ids); `docs/ux2/g2/HFM-UX2-G2-PROTOTYPE-DATA-BINDING-v1.md` (Recognition row: 8/8 coverage, grouped display). |
| Verification Command | Playwright DOM dump of `#recognition li`; record-id mapping cross-check against `heritageView.ts HERITAGE_RECOGNITIONS`. |
| Verification Result | All 8 verified records present in rendered output; ledger and fixture now agree on 8/8 with no ambiguity. |

## 5. Correction Record — F-5 (P2) — DEFERRED_NON_BLOCKING

| Field | Value |
| --- | --- |
| Original Claude Finding | P1 Person prototype does not cover Life Events / Historical Assessments / Later Scholarship / Archival Media. |
| Disposition | `DEFERRED_COVERAGE` · `NON_BLOCKING` · `NO_G2_SCOPE_EXPANSION`. Not implemented in this corrective pass; whether these enter production scope is decided by G3/G4. No code change was made for F-5. |

## 6. Re-Verification (post-correction)

| Check | Command | Result |
| --- | --- | --- |
| axe, all 6 pages | `node prototype/ux2/verify.mjs` (axe-core 4.x over index/p01/p02/p03/p04/p05) | 0 violations on every page → `AXE_VIOLATIONS = 0` |
| heading-order regression | same run, rule-level inspect | p01 fixed (H1→H2→H2); no new violation on any surface |
| responsive | verify.mjs @375 / @1920 | 0 horizontal scroll on all 6 pages |
| token scan | hex set-diff vs frozen `tokens.css` | 35/35 match · `NEW_PALETTE = ZERO` · `TOKEN_DRIFT = ZERO` |
| PT-NB-01…12 | verify.mjs text + slot assertions | all PASS (empty violation arrays) |
| production delta | `git rev-parse HEAD` · `git diff -- apps packages` · `git diff --stat` · `git status --short` | HEAD `ae55abc…` unchanged · apps/packages diff empty · stat empty · status = same untracked dirs only → `PRODUCTION_IMPLEMENTATION_DELTA = ZERO` |

## 7. G2-AC-12 Re-Adjudication

G2-AC-12 (accessibility PASS) was the criterion violated by the F-1 heading-order
defect. After the corrective pass:

```text
G2-AC-12 = PASS
```

Evidence: axe `heading-order` clean on all six surfaces; object-title level now
declared per surface via the reusable `titleTag` mechanism; status text labels,
keyboard/focus, reduced-motion, semantic landmarks unchanged from v1.

## 8. Changed Files (corrective pass)

```text
prototype/ux2/assets/js/ux2.js            — titleTag contract + dhObjectTitle factory
prototype/ux2/assets/css/tokens.css       — F-2 provenance wording (values untouched)
prototype/ux2/assets/data/fixtures.js     — F-3 facet semantic + 档案 16; F-4 recognition 8/8
prototype/ux2/p01-person.html             — F-1 object title H2 (titleTag: 2)
prototype/ux2/index.html                  — F-1 demo object title via shared mechanism (titleTag: 3)
prototype/ux2/p04-discovery.html          — F-3 facet count-basis note + heading
prototype/ux2/verify.mjs                  — axe now runs on all 6 pages (was hub-only)
docs/ux2/g2/HFM-UX2-G2-PROTOTYPE-PLAN-v1.md            — F-2 wording
docs/ux2/g2/HFM-UX2-G2-PROTOTYPE-DATA-BINDING-v1.md    — F-3 / F-4 ledger accuracy
docs/ux2/g2/HFM-UX2-G2-CORRECTIVE-PASS-v1.md           — this record
```

No file outside `prototype/ux2/**` and `docs/ux2/g2/**` was modified.

## 9. Disposition Summary

```text
F-1 = CORRECTED            (P1 BLOCKING → resolved, re-verified)
F-2 = CORRECTED
F-3 = CLARIFIED            (single authoritative semantic: search-index type count)
F-4 = CORRECTED            (8/8 verified recognition coverage)
F-5 = DEFERRED_NON_BLOCKING
```

## 10. Audit Chain (preserved in full)

```text
Original G2            → HFM-UX2-G2-PROTOTYPE-*-v1.md (plan / data-binding ledger /
                          acceptance matrix / audit report) — original records kept,
                          not deleted; the audit report's v1 claims remain the
                          pre-audit state of record.
Claude Independent Audit → findings F-1…F-5 (P1×1 BLOCKING, P2×4) — the sole
                          correction input for this pass.
Corrective Pass        → this document (F-1…F-5 dispositions + re-verification).
Claude Re-Audit        → PENDING — acceptance authority belongs to the independent
                          auditor, not to Pi.
```

## 11. End State Declaration

```text
UX2_G2_CORRECTED_CANDIDATE_READY_FOR_REAUDIT
```

Pi does not declare `UX2_G2_ACCEPTED`. Acceptance authority remains with the
independent auditor.

## 12. Hard Stop

This corrective pass is complete and stops here:

```text
NO_G3 · NO_G4 · NO_PROTOTYPE_MERGE · NO_PRODUCTION_UI_CHANGE
NO_PRODUCTION_ROUTE_REPLACEMENT · NO_UX2_PRODUCTION_IMPLEMENTATION
```

Awaiting Claude directed re-audit.
