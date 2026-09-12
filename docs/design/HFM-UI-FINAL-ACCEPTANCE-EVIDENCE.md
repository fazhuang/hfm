# HFM UI Final Acceptance Evidence

Audit: UI-14 Final UI Acceptance & Freeze Candidate
Date: 2026-09-01
HEAD: `094713bd06c56ef67499724925cb8a2219e1b4c8`

## Scope

Accepted UI optimization scope: UI-01, UI-02, UI-03, UI-04, UI-06, UI-07,
UI-08, UI-09, UI-10, UI-11, UI-12, and UI-13. UI-05 is the Timeline dependency
absorbed by UI-03/UI-04. The DAG's later Exhibition Readiness and Visual QA
entries are not implementation WPs in this scope; this document records the
final acceptance checks over the implemented surfaces.

## Surface and route evidence

20 registered leaf routes were inspected: public core (`/`, `/persons/person-huangfu-mi`,
`/yan`, `/works`, `/archive`, `/jiayi`, `/heritage`, `/search`, `/reader/:id`,
`/about`), supporting public routes (`/reader`, `/library`, `/works/:id`,
`/login`, `/denied`), research routes (`/research`, `/research/search`,
`/research/entity/:type/:id`), and admin routes (`/admin`, `/admin/audit`).

The primary navigation has exactly five items and uses
`/persons/person-huangfu-mi` as the canonical person route. Route, query, hash,
back/forward, invalid-reader, drawer, and public/research round-trip coverage
passed in the final Playwright run.

## Content invariants

| Invariant | Result |
| --- | --- |
| Audited papers | 515 |
| Searchable paper records | 5 |
| Jiayi edition records | 19 |
| Full-text reader documents | 2 (`后论`, `其传`) |
| Search index | 1 |
| Jiayi lineage | `DATA-GAP`; chronology remains separate |
| Heritage lineage | `PARTIAL` |
| 刘君奇 | `第六代名医` |
| Internal paths in rendered UI | 0 |
| Clinical recommendation surface | 0 |
| Sensitive public data | 0 |

Public/research projections preserve domain boundaries, status semantics,
source/evidence presentation, and the 515/5 distinction. No fabricated ancient
full text, lineage edge, citation metadata, or customer path is rendered.

## Commands and results

| Check | Result |
| --- | --- |
| `pnpm typecheck` | PASS |
| `pnpm lint` | PASS; 0 errors, historical warnings only |
| `apps/frontend: pnpm format:check` | PASS |
| `apps/frontend: pnpm test` | 195/195 PASS |
| `pnpm build` | PASS |
| `apps/frontend: pnpm e2e` | 67/67 PASS |
| `git diff --check` | PASS |

The E2E run used the repository Playwright command and exercised Vite on port
5199 in an approved execution context. Responsive coverage includes 375, 768,
1024, 1440, and 1920 widths; dark mode, focus, keyboard, drawer, reader hash,
200% zoom, and no-overflow assertions passed. Component axe checks passed;
jsdom Canvas warnings are tooling observations, not axe violations.

## Integrity

No governance path, formal Phase-2 baseline, migration, or customer source
asset was modified by this audit. No UI dependency delta was found. `hfmzl/`
and `zzcl/` remain untracked customer source directories with no audit writes.
The worktree contains the existing uncommitted UI implementation and test
changes; this evidence file is not a formal acceptance archive or baseline.

## Non-blocking observations

- Historical ESLint warnings remain with zero errors.
- jsdom Canvas `getContext` not-implemented warnings appear during axe tests.
- The previously reported lens-guard `session_mismatch` remains a tooling note;
  equivalent `git diff --check` passed.
- The previously observed UI-03 parallel flake was not reproduced in the final
  67-test run.

Result: P0 = 0, P1 = 0. This evidence supports UI-14 freeze-candidate
readiness; it does not itself create an archive, commit, tag, or formal UI
baseline.
