# HFM Homepage — WP-05 Sections 05–08 Production Fidelity

Work package: `WP-05` · Role: Implementation · Acceptance authority: Codex.
Objective: implement **production visual fidelity** for Sections 05–08 (Evidence, Heritage, Domains, Closing) against the frozen visual authorities (S5-C Refined / S6-B Corrected / S7-A Refined / S8-A), keeping content hierarchy / provenance / data-status semantics true, single H1, heading no-skip, AppFooter footer ownership, real-route CTAs. **Does not** implement Sections 01–04 (WP-04, frozen) and does **not** touch shared foundation / HomeView / homeProjection / router / backend / prototype.

Authoritative inputs: WP-04 acceptance archive (`ab7b978`), WP-02 structural shell, WP-03 visual foundation (`e30a0da`), frozen Section 05–08 artifacts (S5-C-final / S6-B-final / S7-A-final / S8-A html, isolated in `/tmp/hfm-wp03-isolation/visual/section0[5-8]/`), tokens/foundations, `homeProjection.ts`, WP-04 Sections 01–04 layout & accessibility patterns.

Frozen heights (authority): 05 Evidence **1240** · 06 Heritage **1240** · 07 Domains **1240** · 08 Closing **900**.

## 1. Implementation summary

Each section was reconstructed from its accepted standalone artboard composition, mapping production-derived content (`homeProjection.ts` — read-only, untouched) into the accepted structure. No prototype CSS bulk-copy, no prototype runtime path, no fabricated history/facts.

| Section | authority | fidelity added | data source |
| --- | --- | --- | --- |
| 05 Evidence | S5-C Refined | **ONE scholarly argument held open**: 01 结论 `生卒年 215—282` (reduced authority) → 02 出处 (`《晋书》等本源史料`, 32px editorial witness = the FULL verified quotation, attribution) → 03 争议 `建安 / 正始 两说` nested as qualification — indentation only, no arrows/boxes; **provenance register** (quiet marginalia, six source types) | `HOME_EVIDENCE`, `HOME_QUOTATION` |
| 06 Heritage | S6-B Corrected | **ONE continuous editorial field**: documentary act (authentic 2023-09-26 拜师大会 photo, materially embedded, dissolved edges) + factual caption → **transmission records** (师承教育 principal; 央视《陇脉医承》 / 名中医工作室 quieter) → **刘君奇 present carrier** (continuous register, no cards/chips) → **PARTIAL lineage as quiet provenance** (shared resolver + label chip) | `HOME_HERITAGE_LIVING` (+`HERITAGE_PERSON`), `HOME_HERITAGE.items`, shared `presentation/stateMapping` |
| 07 Domains | S7-A Refined | **Four editorial thresholds** (not content columns): full-height thin vertical rules, asymmetric first threshold, holdings rows per door (person/archive from `HOME_HUANGFU`/`HOME_LITERATURE`; medicine = 19/92/515 **scholarly bibliographic register**, not KPI; heritage rows from `HOME_HERITAGE`), ONE navigation grammar with CTAs anchored to a shared terminal baseline (measured 1116px), bottom register 四域 · 四入口 · 一平台 | `HOME_DOMAINS` (+ `HOME_HUANGFU`/`HOME_LITERATURE`/`HOME_KNOWLEDGE`/`HOME_HERITAGE`) |
| 08 Closing | S8-A | Quiet institutional close: single thin rule announces the end of the narrative, then large platform identity (68px serif, NON-heading `<p>`) + approved subtitle; strong negative space | `HOME_CLOSING` |

### Production mapping decisions (documented, no content invented)

- **S5-C extended-reading collapse**: `HOME_QUOTATION` holds the full verified witness once; the artboard's duplicate "extended reading" repetition of the same quote is intentionally **not** duplicated in production (no two equal repetitions of the same evidence). The full quote is the single primary witness.
- **P1-01 (a11y) applied to every visible caption**: Heritage documentary figure/caption carry **no** `aria-hidden`; the photograph is decorative-hidden on the `img` only (`alt=""` + `aria-hidden="true"`) while the visible provenance figcaption stays in the accessibility tree.
- **S7-A removed-copy discipline**: the removed "NARRATIVE → USABLE ARCHIVE" line is **not** reintroduced (no `NARRATIVE`/`USABLE ARCHIVE`/`叙事之后` copy anywhere in Section 07); the four thresholds read as entrances only.
- **S7-A doors are link-free compositions**: each door is a `<div role="listitem">` whose real CTA is a single anchor (`role="list"` on the container) — no whole-door links, no hidden-holdings `aria-hidden` (visible holdings stay readable to AT).
- **S8-A footer boundary (WP-01/02)**: Closing renders identity + subtitle only — no nav, no ©, no legal links; AppFooter remains the single semantic `<footer>` (measured exactly 1 in E2E).

### Asset intake (SHA-verified, traceable)

| asset | source (frozen artifact, isolated) | destination | SHA-256 (verified) |
| --- | --- | --- | --- |
| `heritage-baishi-ceremony.jpg` (2023-09-26 拜师大会; customer-supplied, 客户实拍) | `/tmp/hfm-wp03-isolation/visual/assets/heritage-baishi-ceremony.jpg` (= `/tmp/hfm-wp03-isolation/heritage/baishi-ceremony.jpg`, byte-identical) | `apps/frontend/public/assets/heritage/heritage-baishi-ceremony.jpg` | `b83d4d48be05dad98ef4def4da5cb97c14e69d730f310389216e6df0247a8d7c` |

Documentary photo is illustrative presentation material beside its factual caption → decorative `img` treatment (empty `alt` + `aria-hidden`), consistent with the accepted image treatment and the P1-01 rule.

## 2. Browser geometry (measured at 1440, dev server)

| section | section height (target) | content column | right-edge overflow | note |
| --- | --- | --- | --- | --- |
| 05 Evidence | 1240 (1240) | 1200 | none | argument bottom 1148; register right 884–1130; CTA bottom 52 — no overlaps |
| 06 Heritage | 1240 (1240) | 1200 | none | field 470–950, carrier 962–1162, CTA 1161–1188 right — no overlaps; figcaption bottom 949 |
| 07 Domains | 1240 (1240) | 1200 | none | four CTAs share terminal baseline 1116; foot register at 1185 |
| 08 Closing | 900 (900) | 1200 (centered) | none | identity + subtitle vertically centered |

Horizontal overflow = 0 at 375 / 768 / 1440 / 1920 (E2E). Browser evidence: `docs/audit/evidence/homepage-step3-wp05-{05-evidence,06-heritage,07-domains,08-closing}-{1440,375,768}.png` + `homepage-step3-wp05-full-{1440,375,768}.png`.

### Mobile visibility repair (acceptance BLOCK response — surgical, ≤1199px only)

The initial candidate reused the WP-04 family's fixed ~1200px internal geometry; at <1200px viewports that geometry relies on `overflow: hidden` and hides readable content (`scrollWidth == clientWidth` only proves no scrollbar). **Root-cause fix**: scoped `@media (max-width: 1199px)` flow layouts were added **inside each Section 05–08 component** (no shared CSS touched) that stack the exact same content in DOM order — absolute artboard coordinates become static flow, fixed heights become auto, headline/witness sizes clamp, imagery flows full-width with natural aspect. Desktop ≥1200px geometry and the frozen 1440px composition are byte-identical in markup/CSS (media block cannot match ≥1200px).

DOM-rect evidence (Playwright, measured): at **375px** and **768px**, all four Section 07 CTAs (`/persons/person-huangfu-mi`, `/archive`, `/jiayi`, `/heritage`) scroll into the viewport (`scrollIntoView block:center`) and intersect it — `left≥48`, `right≤viewport`, `top<800`, `bottom>0`, `visible`, non-zero size (recorded as an E2E regression test `WP-05 mobile repair: four domain CTAs reach the viewport`); document overflow = 0 and **no element bottom exceeds its section box** (no internal `overflow:hidden` clipping) for Sections 05–07 at 375/768/1024. The mobile repair changed no data, copy, routes, status semantics or desktop composition; Section 08 footer boundary unchanged.

## 3. Correctness / regression contracts preserved

- **Single H1** = `皇甫谧人文数字平台` (hero); h2 sequence 02–07 unchanged (Evidence/Heritage/Domains headlines verbatim from projection); Closing identity is a NON-heading `<p>` (no duplicate accessible heading name).
- **Heading no-skip** (h1→h2→h3, Heritage carrier name as h3) — axe clean.
- **Footer**: AppFooter remains the only semantic `<footer>`; Closing has no links/legal content.
- **CTAs real routes**: Evidence `/reader/houlun`; Heritage `/heritage`; Domains `/persons/person-huangfu-mi`, `/archive`, `/jiayi`, `/heritage` — unchanged from data.
- **data-status / provenance / no-fabrication**: Heritage PARTIAL chip still routes `resolvePresentationState` + `presentationStatusLabel` (spy-wired contract) with data-status `UNSTRUCTURED_OR_INCOMPLETE` and label `谱系整理中`; `PARTIAL` / `整理中` / `不虚构` / `第六代名医` / `刘君奇` visible; no intermediate-generation titles, no honor-wall, no full-lineage claim, no clinical advice anywhere in 05–08.
- **No hardcoded hex color** (token/`color-mix` only; mask `#000` gradients follow the accepted WP-04 pattern); no `v-html` (all interpolation).
- **HomeProjection / foundations / tokens / router / HomeView / Sections 01–04 / prototype**: read-only, untouched.

## 4. Verification (raw results)

| command | result |
| --- | --- |
| `vue-tsc --noEmit` | PASS (rc=0) |
| WP-05 targeted Vitest (`wp05_sections`) | 13/13 PASS |
| WP-02/03/04 regression targets (`ui03_home`,`ux2_p5_home`,`wp03_foundation`,`ui13` deps) | 55/55 PASS |
| full `vitest run` | **37 files / 358 tests / all PASS** |
| `vite build` | rc=0 (204 modules) |
| ESLint (4 sections + 2 test files) | 0 errors (105 Prettier-style warnings; repo default formatter used) |
| Playwright (full suite) | **105/105 PASS** (100 + 6 WP-05 incl. mobile-repair DOM-rect proof) |
| browser-level axe on homepage | 0 violations (`ux2-responsive-a11y` matrix 375/1280/1920) |
| widths 375 / 768 / 1024 / 1440 / 1920 | no horizontal overflow; no internal section clipping at <1200px (flow regime) |
| scope & worktree audit | PASS (only WP-05 files below) |
| `git diff --check` | PASS |

## 5. Files / scope

| file | scope | class |
| --- | --- | --- |
| `apps/frontend/src/components/home/HomeEvidenceSection.vue` | WP-05 (05 Evidence visual) | CHANGE |
| `apps/frontend/src/components/home/HomeHeritageSection.vue` | WP-05 (06 Heritage visual) | CHANGE |
| `apps/frontend/src/components/home/HomeDomainsSection.vue` | WP-05 (07 Domains visual) | CHANGE |
| `apps/frontend/src/components/home/HomeClosingSection.vue` | WP-05 (08 Closing visual) | CHANGE |
| `apps/frontend/public/assets/heritage/heritage-baishi-ceremony.jpg` | WP-05 asset intake (customer-supplied) | NEW |
| `apps/frontend/src/__tests__/wp05_sections.spec.ts` | WP-05 targeted unit tests | NEW |
| `apps/frontend/e2e/wp05-home-sections.spec.ts` | WP-05 targeted E2E | NEW |
| `docs/audit/evidence/homepage-step3-wp05-*.png` (15: 4 sections × 1440/375/768 + full 1440/375/768) | WP-05 browser evidence | NEW |

Read-only / untouched: `HomeView.vue`, `homeProjection.ts`, `foundations.css`, `tokens.css`, `router/`, `services/`, `types/`, `PublicLayout.vue`, `AppFooter.vue`, Sections 01–04, `prototype/`, backend.

## 6. P2 observations

- **P2**: ESLint Prettier-style warnings (105, 97 fixable) — repo formatting convention; 0 errors.
- **P2**: below 1200px viewports Sections 05–08 render as component-scoped flow layouts (see §2 mobile repair); Sections 01–04 retain their accepted desktop geometry per their own WP (mobile-composition deferral is recorded in WP-02 P2, unchanged by WP-05).
- **P2**: heritage photo caption and Section 07 leads are frozen-authority editorial microcopy derived from data semantics; the ceremony photo caption includes provenance `客户实拍`.

## 7. Candidate

| field | value |
| --- | --- |
| CANDIDATE_SHA | (set on commit below — no commit performed; waits acceptance) |
| CANDIDATE_PARENT | `99c5709dad167cabca57a307088bacd2eef0cba8` (SG-02 current-state corrections) |
| Worktree | WP-05 changes only (4 sections + 1 asset + 2 test files + 6 evidence) |

*WP-05 Sections 05–08 production fidelity implemented and verified locally; Sections 01–04 untouched; no WP-06; no commit made (implementation/verification only per task boundary). Waits for Codex independent acceptance; commit authorization to follow separately.*
