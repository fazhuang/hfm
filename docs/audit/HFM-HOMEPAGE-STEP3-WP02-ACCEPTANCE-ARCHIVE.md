# HFM Homepage — WP-02 Structural Shell Acceptance Archive / Freeze

Work package: `WP-02A` · Verdict: **`WP02_ACCEPTED`** · State: **`ACCEPTANCE_ARCHIVE = FROZEN`** · `WP03_DISPATCH = BLOCKED_PENDING_ARCHIVE_FREEZE` (Codex to lift).

---

## 1. Candidate (frozen)

| field | value |
| --- | --- |
| **CANDIDATE_SHA** | `2880d119894c263867393d42722b1fe66a1ecadf` |
| **CANDIDATE_PARENT** | `6dcf75dd90887dec0a8243e9f655241c88511db9` |
| **Branch** | `phase1/frontier-6-integration` |
| **Files changed** | 17 (8 Home*Section structural shells + HomeView orchestrator + homeProjection additive projections + 3 unit tests + 3 E2E aligned to structural contract + WP-02 evidence doc) |

No `router` / `backend` / `services` / `types` / `PublicLayout` / `AppFooter` / P0 shared primitive modified. Candidate does not reference prototype assets or WP-03+ production material. `homeProjection.ts` is additive projection only (single domain data source).

## 2. Independent verification results

| check | result |
| --- | --- |
| targeted homepage tests | 35/35 PASS |
| full Vitest (`vitest run`) | 35 files / 337 tests PASS |
| `vue-tsc --noEmit` | PASS |
| production build | PASS (201 modules) |
| ESLint | 0 errors (Prettier-style warnings only) |
| Playwright (full) | **97/97 PASS** |
| browser heading / search / viewport regression | PASS |
| single H1; HomeClosingSection no duplicate platform-heading | PASS |
| `#home-search-input` search flow (Enter / click → /search) | PASS |
| AppFooter single semantic footer | PASS |
| responsive no-overflow (375/768/1024/1440/1920 / 200% zoom) | PASS |
| browser-level axe = 0 on homepage + cross-surface | PASS |

P0 = 0 · P1 = 0 · P2 = 1 (see §3).

## 3. P2-01 — non-blocking worktree observation (now CLOSED)

**Observation:** the repository root held 8 untracked user-media files (image + video). Their attribution was undetermined and they predated this WP-02A session; they were never part of the candidate and never modified.

**Disposition (per user confirmation, option A — non-destructive, recoverable):** the 8 media files were moved **out of the audit worktree** to `/tmp/hfm-user-media-isolation/` (exact filenames preserved, `mtime` unchanged, **not deleted**). The git working tree is now fully clean.

Recorded media (all in `/tmp/hfm-user-media-isolation/`):

| file | real type | dims | size |
| --- | --- | --- | --- |
| `皇甫谧学院宣传视频.mp4` | MP4 (ISO 14496-12) | — | 56.66 MB |
| `d8e66448207df5d23b84876511c78739.png` | PNG RGB | 736×781 | 817 KB |
| `dfjsyyfd.png` | PNG RGB | 1254×1254 | 3.81 MB |
| `hfm-fdx_副本.jpeg` | PNG RGBA (suffix `.jpeg`) | 2048×2048 | 9.05 MB |
| `hfm-yz.png` | PNG RGB | 1254×1254 | 1.81 MB |
| `hfm_副本.jpeg` | JPEG | 965×1024 | 210 KB |
| `rwjhqfd.png` | PNG RGB | 1254×1254 | 3.19 MB |
| `ylmlt_副本.png` | PNG RGB | 1672×941 | 1.99 MB |

These are recoverable at any time (restore = `mv` back to repo root). If their ownership/attribution is later confirmed, document accordingly; they are NOT part of the WP-02 archive scope.

## 4. Archive / freeze state

- **`ACCEPTANCE_ARCHIVE = FROZEN`** — the WP-02 structural shell candidate `2880d11` is accepted and archived; the working tree is clean and archivable.
- **`WP03_DISPATCH = BLOCKED_PENDING_ARCHIVE_FREEZE`** — per verdict, WP-03 dispatch remains gated until the archive freeze (this record) is complete. Codex is the acceptance authority to lift the block and dispatch WP-03.

## 5. Ready-to-restore WP-03+ isolation (not part of WP-02)

Visual implementation work for Sections 01–03 / 04–06 and their assets, plus the WP-01/03/03C/04/04C audit docs, remain isolated (non-destructive) in:

- `/tmp/hfm-wp03-isolation/` — production assets (book-siku-leaf.jpg, frag-band1.jpg, frag-macro.jpg, heritage/), WP-01/03/03C/04/04C docs, `prototype/ux2/visual/`.

These must be re-consulted when WP-03 resumes. The accepted Hero H3 / Life L2 / Book B1 / Knowledge S4-B / Evidence S5-C / Heritage S6-B visual baselines live there and remain authoritative for the subsequent visual WPs.

---

*WP-02 structural shell accepted and frozen. Working tree clean; P2-01 closed via non-destructive, recoverable media isolation. Awaiting Codex to lift `WP03_DISPATCH` and authorize WP-03.*
