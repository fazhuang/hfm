# HFM Homepage — WP-03 Visual System Foundation

Work package: `WP-03` · Role: Implementation · Acceptance authority: Codex.
Objective: establish the minimal shared **homepage visual-system foundation** (reusable container/width, section rhythm, typography roles, border/surface, responsive foundation) that the later Section visual WPs (WP-04/05) inherit. **Does NOT implement final Section pixel/geometry/material fidelity.**

Baseline reference: `HFM_HOMEPAGE_STEP2_VISUAL_BASELINE_FINAL` + accepted Section 01–08 artifacts (isolated in `/tmp/hfm-wp03-isolation/`). Existing tokens: `apps/frontend/src/styles/tokens.css`.

---

## 1. What was established

A homepage-scoped shared foundation, added as a clearly-namespaced block in `apps/frontend/src/styles/foundations.css` (the authorized file), reusing **existing HFM tokens** for color / font / spacing where the shared roles need them. A small number of role-local geometry/tracking values (e.g. 44px rule width, 1px hairline, 2px underline offset, 70ch lede max-width, 0.32em eyebrow tracking) are intentional constants on the roles; these are not a parallel token system, but the doc's "token-only" phrasing is slightly overstated — recorded as a P2 contract-wording observation.

Rules (all `.home`-descendant so they are scoped to homepage content — `HomeView` renders `<div class="home">`):

| role | rule | token basis |
| --- | --- | --- |
| section container | `.home .home-section` — centre to `--hfm-content-max`, no horizontal overflow | `--hfm-content-max` |
| chapter eyebrow | `.home .home-eyebrow` (+ `__no`) — small caps, wide tracking, heritage-accent number, hairline `::before` | `--hfm-color-heritage`, `--hfm-color-border-strong` |
| homepage serif heading | `.home .home-section__title` — serif heading role for sections 02–07 | `--hfm-font-heading`, `--hfm-text-2xl` |
| lede / intro | `.home .home-section__lede` — secondary tone, reading leading | `--hfm-color-text-secondary`, `--hfm-leading-reading` |
| editorial action | `.home .home-cta-row` + `.home .home-cta` — real link, accent, underline, visible focus | `--hfm-color-interactive`, `--hfm-color-border-strong` |
| responsive foundation | `@media (max-width: 640px)` `.home`-scoped adjustments (no overflow) | tokens only |

These roles were previously **unstyled** (the WP-02 structural shells used the classes in templates but no CSS defined them) — WP-03 closes that gap once, namespaced, so the visual WPs inherit a consistent foundation instead of each section re-styling.

## 2. Foundation → frozen-artifact mapping

| role | frozen-artifact intent (Section 01–08 authority) | WP-03 foundation |
| --- | --- | --- |
| section rhythm / content column | accepted 8-section white column (captioned content on warm canvas) | `.home .home-section` (content-max, centred, no overflow) |
| chapter marker | 眉题 (eyebrow) at each section head, accent number | `.home .home-eyebrow` |
| serif title hierarchy | Chinese serif-led section headings | `.home .home-section__title` |
| editorial copy tone | secondary muted lede/prose | `.home .home-section__lede` |
| editorial CTA | restrained editorial action, accent arrow, no button chrome | `.home .home-cta` |

The foundation encodes the **shared grammar**; per-section final geometry (fixed artboard heights, manuscript/photography placement, absolute coords) is intentionally NOT in WP-03 (belongs to WP-04/05).

## 3. Files / scope classification

| file | scope | class |
| --- | --- | --- |
| `apps/frontend/src/styles/foundations.css` | homepage-scoped foundation rules (`.home`-namespaced, token-only) | WP-03 CHANGE |
| `apps/frontend/src/__tests__/wp03_foundation.spec.ts` | WP-03 foundation verification (roles present, `.home`-scoped, single-H1, data-status, axe) | WP-03 NEW TEST |
| `apps/frontend/e2e/ui03-home.spec.ts` | added WP-03 scope regression test (foundation on `/`, absent on `/about`) | WP-03 E2E |
| `docs/audit/evidence/homepage-step3-wp03-1440.png`, `-375.png` | browser evidence | WP-03 EVIDENCE |

Read-only / untouched: `tokens.css`, `router`, `PublicLayout`/`AppFooter`, `homeProjection.ts`, canonical domain data, `presentation/`, the 8 `Home*Section.vue` shells (= frozen `2880d11`), prototype.

## 4. Verification (raw results)

| command | result |
| --- | --- |
| `vue-tsc --noEmit` | PASS (rc=0) |
| WP-02 targeted homepage tests (`ui03`,`ux2_p5`,`app.smoke`) | 35/35 PASS |
| WP-03 foundation unit test | 6/6 PASS (roles, `.home`-scope, single-H1, data-status, axe) |
| full `vitest run` | **36 files / 343 tests / all PASS** |
| `vite build` | rc=0 (201 modules) |
| ESLint (foundations + home + tests) | **0 errors** (113 Prettier-style warnings only) |
| Playwright (full suite) | **98/98 PASS** |
| browser axe on homepage | 0 violations (in `ux2-p5-home` + `ui03-home` + `ux2-responsive-a11y`) |
| representative widths | 375 / 768 / 1024 / 1440 / 1920 + 200% zoom — **no horizontal overflow** |

### Browser evidence

- `docs/audit/evidence/homepage-step3-wp03-1440.png` — desktop 1440: h1=1, 8 `.home-eyebrow`, 8 `.home-section`, sw=cw=1440 (no overflow).
- `docs/audit/evidence/homepage-step3-wp03-375.png` — mobile 375: overflow=0 (sw=cw=375).
- Playwright scope test: `/` has `.home-eyebrow`/`.home-section`; `/about` has **0** (no leakage to unrelated public route).

## 5. Correctness / regression contracts preserved

- single H1 (hero) + heading hierarchy (02–07 h2) — PASS.
- Footer ownership: AppFooter remains the only semantic `<footer>` (via PublicLayout) — unchanged.
- Search ownership: HomeView page-level state; `#home-search-input` — preserved (E2E `ui03-home` + P5 pass).
- data-status / provenance / no-fabrication: `UNSTRUCTURED_OR_INCOMPLETE`, `DATA-GAP`, `PARTIAL` intact (unit + E2E pass).
- HomeView + 8 section shells **unchanged** from frozen `2880d11` (no diff).

## 6. P2 observations

- **P2**: ESLint emits Prettier-style `vue/*-attributes-per-line`/`singleline` warnings (103 fixable, repo convention; 0 errors). Non-blocking.
- **P2**: `ui13-polish` heading-scale test previously expected 56px hero (`text-4xl`); that is a WP-03+ **visual** value — not implemented in WP-03 (foundation keeps base serif heading scale); the test was aligned to the structural 28px in the WP-02A correction. Recorded, not a WP-03 regression.
- **P2**: no new production image/video/material added (foundation is CSS-only + tests).

---

## 7. Candidate

| field | value |
| --- | --- |
| CANDIDATE_SHA | (set on commit below) |
| CANDIDATE_PARENT | `2880d119894c263867393d42722b1fe66a1ecadf` (frozen WP-02 candidate) |
| Worktree | WP-03 changes only: `foundations.css`, `wp03_foundation.spec.ts`, `e2e/ui03-home.spec.ts`, `docs/audit/evidence/*` |

*WP-03 established the homepage visual-system foundation (scoped, token-only, no final Section visuals/geometry/assets). Waits for Codex independent acceptance; WP-04 (Sections 01–04 visual fidelity) NOT begun.*
