# HFM Homepage — WP-04 Sections 01–04 Production Fidelity

Work package: `WP-04` · Role: Implementation · Acceptance authority: Codex.
Objective: implement **production visual fidelity** for Sections 01–04 (Hero, Life, Book, Knowledge) against the frozen visual authorities, keeping content hierarchy / state / source / CTA semantics true, single H1, heading hierarchy, search ownership, footer ownership. **Does not** implement Sections 05–08 (deferred WP-05) and **does not** touch shared foundation / HomeView / homeProjection / router / backend.

Authoritative inputs: WP-03 frozen (`e30a0dad`), frozen Section 01–04 artifacts (isolated in `/tmp/hfm-wp03-isolation/`), existing tokens (`tokens.css`), WP-03 homepage foundation (`foundations.css`, read-only).

---

## 1. Implementation summary

Each section was reconstructed from the **frozen artboard absolute geometry** (1440px; heights 01=900, 02=1240, 03=1200, 04=1240) and reconciled with production semantics/data. No prototype CSS bulk-copy, no prototype runtime path, no fabricated facts.

| Section | artboard | fidelity added | data source |
| --- | --- | --- | --- |
| 01 Hero | H3_REFINED | grain/halo, archive guide-line, kicker `魏晋·公元 215—282`, **190px 皇甫谧 monument (decorative aria-hidden)**, name rule, statement, roles, ONE CTA 进入人物档案 →, bottom note, **manuscript specimen (frag-macro.jpg)** breaking TOP+RIGHT + LEFT dissolve | `HOME_HERO`, `CORE_PERSON_DATES` |
| 02 Life | L2_REFINED | 82px 2-line headline `生于乱世，终于著述。`, intro right (no collision), **descending axis** + 6 junction marks, **104px 215/282 anchors** (derived), 4 narrative-rhythm stages, **manuscript column (frag-band1.jpg)** breaking TOP+page + LEFT dissolve, consolidated scholarly register | `HOME_LIFE` (stages/dates/intro), link `/reader/qichuan` |
| 03 Book | B1_REFINED | **monumental 《针灸甲乙经》 150px**, metadata, narrative block h2, ONE CTA 进入古籍库 →, quiet evidence register (19/92/515 derived), version provenance chain (data-derived), **manuscript counterweight (book-siku-leaf.jpg)** breaking TOP+RIGHT + LEFT dissolve, **DATA-GAP status (ux2_p5 P1-01 `.home-lineage figcaption .hfm-status`)** | `HOME_BOOK`, `HOME_EDITIONS_TOTAL`, `INVENTORY_*`, lineage from `HOME_BOOK.book.lineage` |
| 04 Knowledge | S4-B_REFINED | **manuscript leaf (book-siku-leaf.jpg) dissolving** toward structure + valid figure/figcaption (fixes WP-04C invalid-nesting defect), **taxonomy** (人物/文本/作品 primaries + 版本/档案/论文 layers), scholarly method line (research steps), quiet evidence register (56/6/19/92/515/5 derived), ONE CTA 进入研究工作台 → | `HOME_KNOWLEDGE` (counts), `HOME_RESEARCH_STEPS`, taxonomy = accepted S4-B category vocabulary (presentation-only, no new fact) |

### Asset intake (SHA-verified, traceable)

Three production assets re-intaken from the isolated sources (byte-identical to WP-01-verified values):

| asset | source | destination | SHA-256 (verified) |
| --- | --- | --- | --- |
| `frag-macro.jpg` | `/tmp/hfm-wp03-isolation/frag-macro.jpg` | `apps/frontend/public/assets/jiayi/frag-macro.jpg` | `ce1773089bd144eb560e142f3672e0725b28a8020662c2cb8ccd089f979431b8` |
| `frag-band1.jpg` | `/tmp/hfm-wp03-isolation/frag-band1.jpg` | `apps/frontend/public/assets/jiayi/frag-band1.jpg` | `ec9520f2a36c29a7b61afef585bfba228d68e118bc23ee14084bdb3756d732ad` |
| `book-siku-leaf.jpg` | `/tmp/hfm-wp03-isolation/book-siku-leaf.jpg` | `apps/frontend/public/assets/jiayi/book-siku-leaf.jpg` | `a5a892b63673525ac1e4c4979794483eb839a951a98a92d3c2930d50ba70ab7a` |

`edition-lineage.png` (lineage, tracked) reused. Images are decorative manuscript/specimen material → `alt=""` + `aria-hidden` (or inside `aria-hidden` figure), matching the accepted treatment; no content-bearing alt fabricated.

## 2. Frozen-artifact comparison evidence

- Section heights match artboards: Hero 901 (900) · Life 1241 (1240) · Book 1201 (1200) · Knowledge 1241 (1240).
- Composition verifies against `homepage-step3-wp04-{01,02,03,04}-1440.png` (element renders) and `-01-04-1440.png` (context). `docs/audit/evidence/`.
- Browser probe confirmed: **h1=1** (platform name), 6×h2 (02–07), section heights exact, no horizontal overflow (sw=cw=1440), 375 overflow=0.

## 3. Correctness / regression contracts preserved

- **Single H1** = `皇甫谧人文数字平台` (quiet top-right register, per H3; the 190px 皇甫谧 is a non-heading decorative monument) — heading hierarchy no-skip.
- **Search ownership**: HomeView page-level state; hero presentational; `#home-search-input` + `.home-search` + submit → `/search` (E2E `ui03-home` + P5 pass).
- **Footer**: AppFooter remains the only semantic `<footer>` (via PublicLayout) — unchanged.
- **data-status / provenance / no-fabrication**: `UNSTRUCTURED_OR_INCOMPLETE`, `DATA-GAP`, `PARTIAL` intact (unit + E2E + axe).
- **Homeprojection / HomeView / foundations / tokens / router / PublicLayout / AppFooter / Sections 05–08**: read-only, untouched.

## 4. Verification (raw results)

| command | result |
| --- | --- |
| `vue-tsc --noEmit` | PASS (rc=0) |
| WP-02/03 regression target tests (`ui03`,`ux2_p5`,`app.smoke`,`wp03_foundation`) | 41/41 PASS |
| full `vitest run` | 36 files / 343 tests / all PASS |
| `vite build` | rc=0 (204 modules) |
| ESLint (4 sections + tests) | 0 errors (137 Prettier-style warnings) |
| Playwright (full suite) | **98/98 PASS** |
| browser axe on homepage | 0 violations (`ux2-p5-home` + `ux2-responsive-a11y`) |
| representative widths | 375 / 768 / 1024 / 1440 / 1920 + 200% — no horizontal overflow |
| scope & worktree audit | PASS (only WP-04 files; forbidden read-only untouched) |

## 5. Files / scope

| file | scope | class |
| --- | --- | --- |
| `apps/frontend/src/components/home/HomeHeroSection.vue` | WP-04 (Hero visual) | CHANGE |
| `apps/frontend/src/components/home/HomeLifeSection.vue` | WP-04 (Life visual) | CHANGE |
| `apps/frontend/src/components/home/HomeBookSection.vue` | WP-04 (Book visual) | CHANGE |
| `apps/frontend/src/components/home/HomeKnowledgeSection.vue` | WP-04 (Knowledge visual) | CHANGE |
| `apps/frontend/public/assets/jiayi/{frag-macro,frag-band1,book-siku-leaf}.jpg` | WP-04 asset intake | NEW |
| `apps/frontend/src/__tests__/ui03_home.spec.ts`, `wp03_foundation.spec.ts` | test adjust for visual render | CHANGE |
| `apps/frontend/e2e/ui13-polish.spec.ts` | E2E adjust (hero H1 = accepted 10px register) | CHANGE |
| `docs/audit/evidence/homepage-step3-wp04-*.png` | browser evidence | NEW |

Read-only / untouched: `HomeView.vue`, `homeProjection.ts`, `foundations.css`, `tokens.css`, `router/`, `services/`, `types/`, `PublicLayout.vue`, `AppFooter.vue`, Sections 05–08 `Home*Section.vue`, prototype.

## 6. P2 observations

- **P2**: ESLint Prettier-style warnings (137, 131 fixable) — repo formatting convention; 0 errors.
- **P2**: taxonomy labels in Section 04 are component-local presentation constants mirroring the accepted S4-B category vocabulary (the platform's 6 content types) — not new facts/counts/provenance; documented.
- **P2**: hero H1 rendered at 10px (quiet top-right register per H3); `ui13-polish` assertion was updated to the accepted value. Hero "heading scale" is intentionally subdued in the accepted H3 (the 190px monument is the dominant visual, non-heading).

## 7. Candidate

| field | value |
| --- | --- |
| CANDIDATE_SHA | (set on commit below) |
| CANDIDATE_PARENT | `e30a0dad8a6f85d693504d10d7793d05c26ec5b1` (WP-03 archive/freeze) |
| Worktree | WP-04 changes only (4 sections + 3 assets + 3 tests + 6 evidence) |

*WP-04 Sections 01–04 production fidelity implemented; Sections 05–08 untouched (WP-05); no WP-06. Waits for Codex independent acceptance.*
