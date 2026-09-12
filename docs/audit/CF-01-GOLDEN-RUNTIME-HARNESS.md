# HFM CLEAN FORWARD — CF-01 Golden Runtime Regression Harness

Status: CF-01 implementation · Branch: `recovery/hfm-foundation` · Baseline `f81f4e8`

## Purpose

CF-01 establishes the permanent real-runtime regression gate for the HFM
recovery foundation. It does not modify product behavior — it only adds the
test orchestration that proves the live chain:

```text
fresh PostgreSQL → Alembic upgrade head → deterministic bootstrap
  → FastAPI (:8000) → Vite /api proxy (:5199 / :8000) → real Chromium
```

No mocked API, no Playwright route fulfillment, no fixture backend, no
network interception. Every journey hits the real backend / real database.

## What was added (test-only)

| file | role |
| --- | --- |
| `apps/frontend/e2e/golden-runtime.spec.ts` | Real-chain browser journeys (HOME/PERSON/JIAYI/HERITAGE/SEARCH/RESEARCH guard) + failure monitoring |
| `infra/scripts/golden-runtime-gate.sh` | `FULL_GOLDEN_GATE` — fresh disposable PG → alembic → bootstrap → backend → frontend → browser → build → typecheck |
| `infra/scripts/fast-runtime-gate.sh` | `FAST_RUNTIME_GATE` — real backend+frontend+browser on an existing DB (daily regression) |
| `docs/audit/CF-01-GOLDEN-RUNTIME-HARNESS.md` | this document |

## Gate semantics

- `FAST_RUNTIME_GATE`: real DB (existing) + real `/api` proxy + real Chromium.
  No mock. No fresh-DB / migration step. For daily WP regression.
- `FULL_GOLDEN_GATE`: fresh disposable PostgreSQL → migrations → bootstrap →
  backend → frontend → real browser journeys → build → typecheck. Required for
  CF/milestone acceptance.

## Monitored invariants (every run)

```text
API_HTML_FALLBACK          = 0   (no /api request answered with SPA HTML)
FATAL_BROWSER_ERRORS       = 0   (no console.error / pageerror)
UNEXPECTED_FAILED_NETWORK  = 0   (no unexpected /api 4xx/5xx; route guards excluded)
```

The `/research` anonymous route guard → `/login` is the correct product
behavior and is asserted as such (not treated as failure).

## Real API assertion (PERSON end-to-end)

The PERSON test proves the browser request flows through the Vite `/api` proxy
→ FastAPI → PostgreSQL and returns JSON (not an HTML shell) which renders the
person page. This is a real-runtime proof, not a DOM-shell check.
