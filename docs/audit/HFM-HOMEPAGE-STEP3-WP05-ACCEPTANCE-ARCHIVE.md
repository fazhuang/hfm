# HFM Homepage — WP-05 Sections 05–08 Acceptance Archive

Work package: `WP-05` · Verdict: **`WP05_IMPLEMENTATION = VERIFIED`** · State: **`ACCEPTANCE_ARCHIVE = COMMITTED`** · **`WP05_ACCEPTED = ACCEPTED`**

## 1. Candidate

| field | value |
| --- | --- |
| **branch** | `phase1/frontier-6-integration` |
| **HEAD** | `fa41d22fce270090d52c069929de99fae066dac0` |
| **CANDIDATE_PARENT** | `99c5709dad167cabca57a307088bacd2eef0cba8` (SG-02 current-state corrections) |
| **commit subject** | `feat(home): implement WP-05 sections 05-08 fidelity` |
| **worktree** | clean |
| **changed files** | 23 (WP-05 file set; no out-of-scope file) |

## 2. Scope

- **Implemented**: Sections 05–08 production visual fidelity (Evidence S5-C Refined, Heritage S6-B Corrected, Domains S7-A Refined, Closing S8-A) + a **surgical mobile repair** (component-scoped `@media (max-width: 1199px)` flow layouts) so no readable content is hidden by `overflow: hidden` below the 1200px content column.
- **Not touched**: Sections 01–04 (WP-04, frozen), `HomeView.vue`, `homeProjection.ts`, `foundations.css`, `tokens.css`, `router/`, `services/`, `types/`, `PublicLayout.vue`, `AppFooter.vue`, `prototype/`, backend.
- **Not started**: WP-06 (Sections 05–08 beyond the immediate fidelity/mobile repair are not in process), Phase 3, production HFB import, any other product task.

## 3. Changed files (23)

| type | files |
| --- | --- |
| Components | `apps/frontend/src/components/home/HomeEvidenceSection.vue` · `HomeHeritageSection.vue` · `HomeDomainsSection.vue` · `HomeClosingSection.vue` |
| Asset | `apps/frontend/public/assets/heritage/heritage-baishi-ceremony.jpg` (customer-supplied; SHA `b83d4d48be05dad98ef4def4da5cb97c14e69d730f310389216e6df0247a8d7c`, byte-identical to isolated source) |
| Tests | `apps/frontend/src/__tests__/wp05_sections.spec.ts` (13 tests) · `apps/frontend/e2e/wp05-home-sections.spec.ts` (6 tests incl. mobile DOM-rect proof) |
| Evidence doc | `docs/audit/HFM-HOMEPAGE-STEP3-WP05-SECTIONS05-08-PRODUCTION-FIDELITY.md` |
| Browser evidence | `docs/audit/evidence/homepage-step3-wp05-{05-evidence,06-heritage,07-domains,08-closing}-{1440,375,768}.png` (12) + `homepage-step3-wp05-full-{1440,375,768}.png` (3) |

## 4. Frozen authorities & boundaries

- Section authorities: `HFM_HOMEPAGE_SECTION05_VISUAL_BASELINE_S5C_REFINED` · `…SECTION06_VISUAL_BASELINE_S6B_CORRECTED` · `…SECTION07_VISUAL_BASELINE_S7A_REFINED` · `…SECTION08_VISUAL_BASELINE_S8A`; overall `HFM_HOMEPAGE_STEP2_VISUAL_BASELINE_FINAL`.
- Heights (authority) confirmed via browser probe: 05/06/07 = 1240, 08 = 900; content column 1200px; desktop ≥1200px geometry unchanged by the mobile repair.
- WP-02 structural shell, WP-03 visual foundation (`e30a0da`), WP-04 sections 01–04 (`a3f3ec0…` frozen) — all read-only, untouched.

## 5. Semantic contracts preserved

- **Single H1** = `皇甫谧人文数字平台` (hero); h2 sequence 02–07; Closing identity is a NON-heading `<p>` (no duplicate accessible heading name); heading no-skip (h1→h2→h3).
- **Evidence visibility / provenance**: quotation witness (房玄龄《晋书》) visible in the accessibility tree; Heritage documentary figcaption visible & accessible (no `aria-hidden` on visible captions — WP-04 P1-01 rule); decorative images hidden on the `img` only (`alt=""` + `aria-hidden="true"`).
- **PARTIAL / DATA-GAP / no fabrication**: Heritage PARTIAL chip routes `resolvePresentationState` + `presentationStatusLabel` (data-status `UNSTRUCTURED_OR_INCOMPLETE`, label `谱系整理中`); `PARTIAL` / `整理中` / `不虚构` / `第六代名医` / `刘君奇` preserved; no invented intermediate-generation titles, no honor-wall, no full-lineage claim, no invented counts — medical numbers (19/92/515) and all holdings derive from existing projections.
- **Four real domain routes**: `/persons/person-huangfu-mi`, `/archive`, `/jiayi`, `/heritage` (Sections 07 CTAs), plus Evidence `/reader/houlun`, Heritage `/heritage`.
- **AppFooter remains the only semantic `<footer>`** (measured exactly 1 in E2E); Closing renders no © / legal nav / links.
- **No clinical recommendation** anywhere in 05–08.

## 6. Mobile proof

- **375px / 768px** (Playwright, DOM-rect): document overflow = **0**; Sections 05–07 show **no internal clipping** (no element bottom exceeds its section box — content is not hidden by `overflow: hidden`).
- **Section 07 four CTAs** all scroll into the viewport (`scrollIntoView block:center`) and intersect it at 375px and 768px: `left 48`, `right ≤ viewport`, `top 387`, `bottom 413/414`, non-zero size, `visible`; each `href` = the four real routes. Recorded as the E2E regression `WP-05 mobile repair: four domain CTAs reach the viewport`.
- Evidence images: `homepage-step3-wp05-*-{375,768}.png` + `homepage-step3-wp05-full-{375,768}.png`.

## 7. Verification (recorded in the implementation evidence doc; summarized)

| check | result |
| --- | --- |
| full Vitest | **37 files / 358 tests PASS** |
| WP-05 targeted Playwright | 6/6 PASS |
| full Playwright | **105/105 PASS** |
| `vue-tsc --noEmit` | PASS (rc=0) |
| `vite build` | PASS (rc=0) |
| browser-level axe (homepage) | **0 violations** (375/1280/1920) |
| `git diff --check` | PASS |
| ESLint (targeted, repo formatter) | **0 errors** (105 Prettier-style warnings recorded) |

## 8. P2 / deferred

- **P2**: ESLint Prettier-style warnings (105, 97 fixable) — repo formatting convention; 0 errors.
- **P2**: desktop fixed-geometry composition is retained at ≥1200px (frozen); Sections 01–04 retain their accepted desktop composition per their own WP (mobile-composition deferral is recorded in WP-02 P2, unchanged by WP-05).
- **Deferred / not auto-authorized**: WP-06 and any later work are not authorized by this archive; nothing beyond WP-05 may be dispatched without a separate instruction.

## 9. Final state

```text
WP05_IMPLEMENTATION          = VERIFIED
WP05_ACCEPTANCE_ARCHIVE      = COMMITTED
WP05_ACCEPTED                = ACCEPTED
```

*WP-05 accepted. This acceptance archive was committed at `2266c227bb43ba2fd66e38586b20b27d83376777`; the Independent Archive Review is recorded below. No work beyond WP-05 is authorized by this archive.*

## 10. Independent Archive Review

| field | value |
| --- | --- |
| reviewed HEAD | `2266c227bb43ba2fd66e38586b20b27d83376777` |
| verdict | **PASS** |
| scope | archive content · candidate binding (HEAD `fa41d22…`, parent `99c5709…`) · file scope (23-file WP-05 set, no out-of-scope file) · evidence (15 browser PNGs + implementation evidence doc) · boundary (Sections 01–04 / shared foundation / `AppFooter` / backend untouched) |

Status drift resolved: the archive body now reflects `WP05_ACCEPTED = ACCEPTED`, consistent with the independent review result.
