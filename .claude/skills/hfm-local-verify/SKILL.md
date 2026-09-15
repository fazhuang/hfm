---
name: hfm-local-verify
description: Run the HFM app and see it render in a real browser — start the Vite frontend, capture a screenshot of a page, and run the Playwright e2e suite. Use whenever a UI change needs visual confirmation, a page must be checked against a design reference, or the e2e suite must be run.
---

# HFM local run and visual verification

Two different jobs, two different ports. Mixing them up breaks the e2e harness.

## Port contract

| Port | Owner | Rule |
| --- | --- | --- |
| 5199 | `apps/frontend/playwright.config.ts` (`HFM_E2E_PORT`) | Reserved. The harness starts its own Vite here with `--strictPort` and `reuseExistingServer: false`, so it fails closed if anything else holds the port. Never start your own server here. |
| 5198 | ad-hoc dev server | Use this for browsing and screenshots. |
| 8000 | FastAPI backend | Vite proxies `/api` here (`vite.config.ts`). No frontend config needed. |

## Look at a page

```bash
cd apps/frontend
pnpm dev --port 5198 --strictPort        # background; wait for the ready line
npx playwright screenshot --wait-for-timeout 1500 \
  --viewport-size "1280,720" \
  http://localhost:5198/ /tmp/hfm-home.png
```

Then open the PNG with the Read tool — it renders images. Add `--full-page` for a
whole scroll height, `--device "iPhone 13"` for a mobile view, `--color-scheme dark`
for the dark theme.

Screenshots on 5198 hit the **live backend** on :8000, so they show real data.
Stop the 5198 server when done; leaving it running is what breaks a later
`pnpm e2e` if it ever drifts onto a reserved port.

## Check behaviour

```bash
cd apps/frontend
pnpm e2e                                  # Playwright, real Chromium, self-managed server
pnpm e2e e2e/ui03-home.spec.ts            # one spec
pnpm --filter @hfm/frontend run e2e -- --grep "hero"
```

The e2e suite mocks the public API routes, so the backend does not need to be
running. It asserts in the real browser DOM, not jsdom.

`HFM_E2E_TARGET_SHA` is optional. When set, the config aborts before starting any
server unless the checkout HEAD matches that SHA. Use it when a result must be
tied to an exact revision.

## Before calling UI work done

```bash
pnpm check                                # lint + typecheck + test + build, all workspaces
```

Report the command and its real output. A screenshot proves the page rendered;
it does not prove the behaviour is correct — run the e2e spec for that.
