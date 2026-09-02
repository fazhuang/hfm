# HFM Homepage — STEP 3.0 WP-02 Structural Shell

Work package: `WP = UX2-HOMEPAGE-STEP3-WP02`
Authoritative visual baseline: `HFM_HOMEPAGE_STEP2_VISUAL_BASELINE_FINAL` (`STEP2_VISUAL_DESIGN = COMPLETE`).
WP-02 establishes the production **structural architecture** for the accepted 8-section homepage — section ownership, component boundaries, data flow, semantic section order, AppFooter integration boundary, safe HomeView orchestration. **NOT visual-completion work**; no final Section visuals, no prototype CSS migration, no pixel parity, no asset copy.

---

## 1. Repository state

- Branch: `phase1/frontier-6-integration`; HEAD `6dcf75dd90887dec0a8243e9f655241c88511db9`.
- `WP02_PRE_HOMEVIEW_DIFF_SHA256 = b120a1b38584687231dd5af8b1145f92687b16b9a120774fcd163374726ad79c` — recorded before any WP-02 edit, identical to WP-01 (confirming no prior edit).
- After WP-02: `HomeView.vue` cumulative diff = 49 insertions / 541 deletions (monolithic view → thin orchestrator); STEP-1 superseded **in place** (not reset, not stashed, not reverted from HEAD).

## 2. STEP-1 supersession (HomeView)

The prior monolithic `HomeView.vue` (813 lines: STEP-1 hero + metrics + person/jiayi/literature/heritage/research sections) was replaced by a thin orchestrator. Per the WP-01 reconciliation rule ("preserve intent/history, not obsolete implementation"):

- **Superseded in place**, no `git checkout`/`reset`/`clean`.
- **Preserved behavior**: page-level search state + `/search` submit (search capability survives); data-honesty state mapping re-homed to the owning sections (HomeBookSection / HomeHeritageSection) so the `ux2_p5` P1-01 contract (data-status via shared resolver, label via shared helper) still holds.
- **Removed**: obsolete hero plate/lineage markup, old metrics block, and the old inner sections (their content is re-homed into the 8 accepted sections).
- The STEP-1 history/intent is captured in `docs/audit/HFM-HOMEPAGE-STEP3-WP01-PRODUCTION-STATE-RECONCILIATION.md` (§2, §3).

## 3. Structure delivered

```
HomeView.vue                     (thin orchestrator — page-level search state)
  ├─ HomeHeroSection.vue         #home-hero      (01, holds the single H1 + search interface)
  ├─ HomeLifeSection.vue         #home-life      (02)
  ├─ HomeBookSection.vue         #home-book      (03)
  ├─ HomeKnowledgeSection.vue    #home-knowledge (04)
  ├─ HomeEvidenceSection.vue     #home-evidence  (05)
  ├─ HomeHeritageSection.vue     #home-heritage  (06)
  ├─ HomeDomainsSection.vue      #home-domains   (07)
  └─ HomeClosingSection.vue      #home-closing   (08)
```

- **8 production section components** exist under `apps/frontend/src/components/home/`.
- Each has a semantic root `<section id="home-*">`, a stable id, and receives/derives data via the additive projection.
- Section order = 01→08 (verified by `ui03` test asserting the id list in order).
- **Exactly one H1** (HomeHeroSection) = `皇甫谧人文数字平台`; sections 02–08 use `h2` (and `h3` for sub-elements) — heading hierarchy has no skips (verified by axe heading/no-skips tests).
- **One semantic footer**: `AppFooter` is rendered by `PublicLayout` (which wraps `<main><RouterView/></main>`), NOT by HomeView. So there is exactly one footer, no duplication. `HomeClosingSection` owns only the accepted closing composition (platform identity + subtitle + quiet transition); it does NOT render copyright / legal nav / co-construction signature / positioning statement.

## 4. Search ownership

- `HomeView` owns **page-level search state** (`searchInput` ref) and the submit handler (`onSearch` → `/search?q=`).
- `HomeHeroSection` receives `search-value` (v-model) + `on-search` + `search-label` props and renders the visible search interface — it does NOT import or duplicate `SEARCH_INDEX` or search logic.
- (Note: `PublicLayout` separately owns the global header-search; both push to `/search` as before. This is unchanged existing behavior.)

## 5. Data projection changes (homeProjection.ts — ADDITIVE only)

Added presentation projections selecting/deriving existing authoritative data (no new domain facts, no fabricated counts):

| Export | Derivation | Verified |
| --- | --- | --- |
| `HOME_CHAPTERS` | chapter eyebrows/labels (presentation microcopy) | — |
| `HOME_LIFE` | `CORE_PERSON_LIFE_PHASES` + `CORE_PERSON_DATES` + approved headline | 4 stages |
| `HOME_BOOK` | `HOME_JIAYI` (editions + lineage + cta) | — |
| `HOME_KNOWLEDGE` | `SEARCH_INDEX.length`(56), 6 types, `INVENTORY_EDITION_RECORDS`(19), `INVENTORY_LUNZHU_FILES`(92), `INVENTORY_LUNWEN_FILES`(515), `SEARCHABLE_PAPER_TOTAL`(5) | 56 / 6 / 19 / 92 / 515 / 5 |
| `HOME_EVIDENCE` | `HOME_QUOTATION` (房玄龄《晋书》) + source register + claim/dispute | 6 sources |
| `HOME_HERITAGE_LIVING` | `HERITAGE_PERSON` + project + PARTIAL lineage note | 刘君奇 / 第六代名医 / PARTIAL |
| `HOME_DOMAINS` | four domain entries → existing routes | 4 valid routes |
| `HOME_CLOSING` | `HOME_HERO.title` + `subtitle` | — |

No authoritative domain semantics mutated; no existing export removed; counts derived from the single source (contentInventory / searchIndex / jiayiView / heritageView). Verified at runtime: `SEARCH_INDEX.length = 56`, `edition:19`, `paper:5`, 92/515 inventory.

## 6. AppFooter / closing boundary

- `PublicLayout.vue` renders `<AppFooter />` after `<main>` (single global `<footer>`).
- `HomeClosingSection` = accepted close (identity + subtitle + quiet transition) only. It does **not** duplicate © / legal nav / co-construction / positioning statement.
- Architecture is WP-02 (final visual reconciliation deferred to WP-05 as designed); ownership is now unambiguous — no second footer.

## 7. CSS scope (WP-02)

Minimal structural shell only: container/root class names, section wrappers, basic flex flow, and a scoped `.visually-hidden` utility on HomeHeroSection (matching the project's per-component convention). **No** prototype pixel coords, no absolute-position migration, no final typography scale, no final section heights, no grain/halo textural recreation, no final grids, no responsive compositions.

## 8. Assets / routes

- **No prototype-only asset copied**; components use only existing production assets (`HOME_BOOK.book.lineage.src` = `/assets/jiayi/edition-lineage.png`, already shipped).
- **No production code references `prototype/ux2/visual/assets/*`** (verified: no leak).
- All CTA links resolve to existing valid routes (`/persons/person-huangfu-mi`, `/archive`, `/jiayi`, `/heritage`, `/research/search`, `/reader/houlun`). No `#` / `javascript:` / fake interactive controls. Router config NOT modified.

## 9. Tests

Updated to structural architecture: `ui03_home.spec.ts`, `ux2_p5_home.spec.ts`. `app.smoke.spec.ts` unchanged (route smoke).

- **TARGETED**: `ui03_home.spec.ts` (17 tests), `ux2_p5_home.spec.ts` (17 tests), `app.smoke.spec.ts` (1 test).
- **FULL_RELEVANT**: full `vitest run` = **35 files / 337 tests / all pass**.
- Structural tests added: 8 section roots render in order; exactly one H1; exactly one semantic footer (AppFooter via layout, not duplicated); 8-section heading set; real CTA route targets; data-status honesty (`UNSTRUCTURED_OR_INCOMPLETE` on book + heritage) + `DATA-GAP`/`PARTIAL`/`第六代名医`/`刘君奇` preserved; search form wiring; no prototype path; heading no-skips; axe passes.
- Kept Must-Not-Regress contracts: axe, single H1/no-skip heading hierarchy, `HOME_METRICS`-from-inventory, `HOME_JIAYI` DATA-GAP, `HOME_HERITAGE` PARTIAL, `HOME_QUOTATION` 房玄龄·《晋书》, no-fabrication/no-clinical/no-internal-register-keys.

## 10. Risks / P0 / P1 / P2

- **P0**: none.
  - P0-01 STEP-1 HomeView preserved (fingerprinted, not reset; superseded in place per WP-01).
  - P0-02 Search behavior survives (orchestrator owns state; hero receives props; test green).
  - P0-03 Data-honesty/no-fabrication contract preserved (data-status + PARTIAL/DATA-GAP tests green).
  - P0-04 Accessibility semantics preserved (single H1, heading no-skips, one `<footer>` via layout; axe passes).
  - P0-05 No prototype asset path leaked (verified).
- **P1**: none blocking.
  - P1-01 HomeView is now a thin orchestrator (monolith replaced).
  - P1-02 Section components use the additive projection (no authoritative-data duplication).
  - P1-03 AppFooter/HomeClosingSection responsibilities are distinct (no overlap).
  - P1-04 Structural tests updated to the 8-section structure (old 7-block assumptions removed).
  - P1-05 Component boundaries are clean — WP-03–05 can implement visual fidelity per section without touching the orchestrator.
- **P2**: carried forward (font fallback, desktop-only coords → WP-06, clipping margins, English microcopy KEEP, S07 removed line not reintroduced). No new P2 introduced.

## 11. Acceptance result

WP-02 criteria — all PASS:

- [x] 8 production section components exist
- [x] HomeView is a thin orchestrator
- [x] section order = 01→08
- [x] exactly one H1
- [x] exactly one semantic footer (via layout; no duplication)
- [x] HomeClosingSection does not duplicate AppFooter responsibilities
- [x] search capability survives
- [x] no fabricated authoritative data (all counts derived)
- [x] homeProjection changes are additive only
- [x] no prototype path used by production
- [x] no broken routes (existing valid routes only)
- [x] structural homepage tests pass (17 + 17 + 1)
- [x] existing required smoke/accessibility/data-honesty tests remain green (full suite 337/337)
- [x] no visual fidelity claim made (structural only)
- [x] git diff contains only explained WP-02 changes + preserved prior the STEP-1 supersession (recorded)

**`WP02_ACCEPTANCE = PASS`**

---

## Final report

```
WP = UX2-HOMEPAGE-STEP3-WP02
PRE_WP_HEAD = 6dcf75dd90887dec0a8243e9f655241c88511db9
WP02_PRE_HOMEVIEW_DIFF_SHA256 = b120a1b38584687231dd5af8b1145f92687b16b9a120774fcd163374726ad79c
STRUCTURE =
  HOMEVIEW = thin orchestrator (page-level search state + 8-section composition; no footer, no monolithic markup)
  SECTIONS = 8 components under src/components/home/: HomeHero(01, H1+search)/HomeLife(02)/HomeBook(03)/HomeKnowledge(04)/HomeEvidence(05)/HomeHeritage(06)/HomeDomains(07)/HomeClosing(08), each with #home-* root + h2 (sub h3)
  FOOTER = AppFooter via PublicLayout (single global <footer>); HomeClosingSection owns closing composition only (no ©/legal/co-construction)
SEARCH_OWNERSHIP = HomeView owns page-level search state + /search submit; HomeHeroSection receives search-value/on-search/search-label props (no SEARCH_INDEX duplication); PublicLayout header-search unchanged
DATA_PROJECTION_CHANGES = ADDITIVE only: HOME_CHAPTERS, HOME_LIFE, HOME_BOOK, HOME_KNOWLEDGE (56/6/19/92/515/5 derived), HOME_EVIDENCE, HOME_HERITAGE_LIVING, HOME_DOMAINS, HOME_CLOSING. No domain semantics mutated, no export removed.
FILES_CHANGED = apps/frontend/src/views/HomeView.vue (49+/541-); new apps/frontend/src/components/home/* (8 files); apps/frontend/src/data/homeProjection.ts (additive); apps/frontend/src/__tests__/ui03_home.spec.ts, ux2_p5_home.spec.ts (updated to 8-section structure); docs/audit/HFM-HOMEPAGE-STEP3-WP02-STRUCTURAL-SHELL.md (this).
TESTS =
  TARGETED: ui03_home (17), ux2_p5_home (17), app.smoke (1)
  FULL_RELEVANT: full vitest run = 35 files / 337 tests / all pass
P0 = None (all mitigated: STEP-1 preserved, search survives, honesty preserved, a11y preserved incl. single footer/H1, no prototype path)
P1 = None blocking (thin orchestrator, no data duplication, footer ownership distinct, structural tests updated, clean boundaries)
P2 = font fallback; desktop-only coords (→WP-06); clipping margins (→WP-04); English microcopy KEEP; S07 removed line not reintroduced
WP02_ACCEPTANCE = PASS
NEXT_FRONTIER = WP-03
```

*WP-02 produced as the structural shell. No final Section visuals, no prototype CSS migration, no final typography heights, no asset copy, no responsive fidelity work. Awaiting independent WP-02 acceptance before WP-03 (Sections 01–03 visual implementation).*
