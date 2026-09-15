/**
 * CF-01 Golden Runtime Regression — real chain, NO mock (CF01_GATE mode).
 *
 * Executed by `infra/scripts/golden-runtime-gate.sh` (FULL_GOLDEN_GATE) after
 * a fresh PostgreSQL + alembic upgrade head + deterministic bootstrap, with
 * CF01_GATE=1: the full real chain is exercised with zero network interception:
 *   Browser → Vite /api proxy → FastAPI :8000 → PostgreSQL → JSON → page.
 *
 * WR00-B2-E2E-R1 data isolation: when the spec runs OUTSIDE the golden gate
 * (no CF01_GATE marker — e.g. the standard acceptance E2E suite against the
 * canonical runtime database, which contains no demo content), the two
 * data-flow journeys (PERSON, SEARCH) use a deterministic test-owned data
 * contract served at the network boundary. They never depend on pre-existing
 * business data in hfm_prod and never write to it. Their UI intent is
 * unchanged: a known person page renders its structured fields and a search
 * query renders real result rows that navigate canonically.
 *
 * Hard invariants enforced here (CF-01 acceptance):
 *   - every core route is served HTTP 200 (no 404 shell);
 *   - every /api answer carries JSON (no SPA HTML fallback);
 *   - zero failed requests, fatal browser errors, unexpected /api 4xx/5xx;
 *   - the /research anonymous route guard → /login is correct behaviour
 *     (401 on that guarded path is the ONLY tolerated non-2xx /api status).
 */
import { expect, test } from '@playwright/test'

import { stubPublicPerson, stubPublicSearch } from './data-fixtures'

// ND-1 H01: the spec honours the same explicit-port override as the Playwright
// config (HFM_E2E_BASE) in addition to the CF01_BASE the gate scripts set.
const BASE = process.env.CF01_BASE || process.env.HFM_E2E_BASE || 'http://localhost:5199'

// Set by infra/scripts/golden-runtime-gate.sh (disposable seeded DB): the
// PERSON/SEARCH journeys run against the REAL chain. Absent (standard E2E
// suite, canonical runtime DB) they use deterministic network fixtures.
const CF01_GATE = process.env.CF01_GATE === '1'

const captured = {
  consoleErrors: [] as string[],
  pageErrors: [] as string[],
  requestFailed: [] as string[],
  htmlFallback: [] as string[],
  unexpectedHttp: [] as string[],
}

function recordApi(path: string, status: number, contentType: string): void {
  // Any /api answered with HTML = failure (the SPA shell must never leak to /api).
  const ct = (contentType || '').toLowerCase()
  if (path.includes('/api/') && (ct.includes('text/html') || ct.includes('text/plain'))) {
    captured.htmlFallback.push(`${status} ${path}`)
  }
  // Core /api must not 4xx/5xx. The ONLY tolerated non-2xx is the 401 produced
  // by the anonymous /research route guard (a correct product behaviour),
  // and the 404 thrown by the real "entity not found yet" read paths that are
  // part of the bootstrap contract are still recorded — do NOT whitelist 404.
  if (path.includes('/api/') && status >= 400 && !(status === 401)) {
    captured.unexpectedHttp.push(`${status} ${path}`)
  }
}

function attach(page: import('@playwright/test').Page): void {
  page.on('console', (m) => {
    if (m.type() === 'error') captured.consoleErrors.push(m.text().slice(0, 200))
  })
  page.on('pageerror', (e) => captured.pageErrors.push(String(e).slice(0, 200)))
  page.on('requestfailed', (r) =>
    captured.requestFailed.push(`${r.url()} :: ${r.failure()?.errorText}`),
  )
  page.on('response', (r) => recordApi(r.url(), r.status(), r.headers()['content-type'] || ''))
}

async function goto200(page: import('@playwright/test').Page, path: string): Promise<void> {
  const resp = await page.goto(BASE + path)
  expect(resp?.status(), `${path} must be 200`).toBe(200)
  await page.waitForLoadState('networkidle')
}

test('HOME — / served 200 + platform heading', async ({ page }) => {
  attach(page)
  await goto200(page, '/')
  await expect(page.getByRole('heading', { level: 1 })).toBeVisible()
  await expect(page.getByRole('heading', { level: 1 })).not.toBeEmpty()
})

test('PERSON — known person page renders structured fields (data fixture unless CF01 gate)', async ({
  page,
}) => {
  attach(page)
  // Standard suite: deterministic person projection (test-owned data). The
  // CF-01 gate keeps the REAL Browser→/api→FastAPI→PG chain under CF01_GATE=1.
  if (!CF01_GATE) {
    stubPublicPerson(page)
  }
  await goto200(page, '/persons/ENT-PERSON-HFM-HUANGFUMI')
  await expect(page.locator('h1')).toBeVisible()
  await expect(page.locator('h1').first()).toContainText('皇甫谧')
  await expect(page.locator('body')).toBeVisible()
})

test('JIAYI — /jiayi served 200 + heading', async ({ page }) => {
  attach(page)
  await goto200(page, '/jiayi')
  await expect(page.getByRole('heading', { level: 1 }).first()).toBeVisible()
})

test('HERITAGE — /heritage served 200 + heading', async ({ page }) => {
  attach(page)
  await goto200(page, '/heritage')
  await expect(page.getByRole('heading', { level: 1 }).first()).toBeVisible()
})

test('SEARCH — search renders deterministic result rows and navigates canonically', async ({
  page,
}) => {
  attach(page)
  // Standard suite: deterministic public-search fixture (test-owned data).
  // The CF-01 gate keeps the REAL search chain under CF01_GATE=1 (typed query
  // runs the real published-content search against the seeded database).
  if (!CF01_GATE) {
    stubPublicSearch(page)
    stubPublicPerson(page) // result click lands on the deterministic person page
  }
  await goto200(page, '/search')
  const input = page.locator('input[type="search"], input[type="text"], form input').first()
  await input.fill('皇甫谧')
  await page.keyboard.press('Enter')
  const list = page.locator('.result-list, ol.result-list')
  await expect(list).toBeVisible()
  const rows = page.locator(
    '.result-list .result-row, ol.result-list .result-row, .result-list li, ol.result-list li',
  )
  await expect(rows.first()).toBeVisible()
  await expect(list).toContainText('皇甫谧')
  const rowLink = page.locator('.result-row a.result-row__link').first()
  await expect(rowLink).toHaveAttribute('href', '/persons/ENT-PERSON-HFM-HUANGFUMI')
  await rowLink.click()
  await expect(page.getByRole('heading', { level: 1 }).first()).toContainText('皇甫谧')
})

test('RESEARCH — anonymous route guard → login (correct)', async ({ page }) => {
  attach(page)
  const resp = await page.goto(BASE + '/research')
  expect(resp?.status()).toBe(200)
  await page.waitForURL(/\/login/)
  await expect(page.getByRole('heading', { name: '登录' })).toBeVisible()
})

test('final invariants: 0 fallback / 0 fatal / 0 failed network / 0 unexpected 4xx-5xx', async () => {
  waitForMonitors()
  const fatal = [...captured.pageErrors, ...captured.consoleErrors]
  expect(captured.htmlFallback, 'an /api request was answered with SPA HTML').toHaveLength(0)
  expect(captured.requestFailed, 'a browser request failed (network/abort)').toHaveLength(0)
  expect(
    captured.unexpectedHttp,
    'an /api request returned unexpected 4xx/5xx (incl. 404)',
  ).toHaveLength(0)
  expect(fatal, 'fatal browser errors (console.error / pageerror)').toHaveLength(0)
  console.log(
    `CF01_MONITOR htmlFallback=${captured.htmlFallback.length} ` +
      `fatal=${fatal.length} requestFailed=${captured.requestFailed.length} ` +
      `unexpectedHttp=${captured.unexpectedHttp.length}`,
  )
})

function waitForMonitors(): void {
  // no-op hook for clarity; events are gathered via the streamed listeners.
}
