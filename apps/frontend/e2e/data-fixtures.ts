/**
 * WR00-B2-E2E-R1 — deterministic public-data fixtures for browser E2E.
 *
 * Test-owned data contract only: the fixtures are served at the network
 * boundary (Playwright route.fulfill) so data-flow journeys (person page,
 * search results) never depend on pre-existing rows in the runtime database.
 * The canonical production database (hfm_prod) is never read as a fixture
 * source and never written by E2E.
 *
 * Payloads mirror the documented product response envelope and projection
 * shapes (see ui10-search.spec.ts / ui12-correction.spec.ts for the same
 * conventions). These fixtures are NOT product proof — full-chain coverage
 * lives in the CF-01 golden gate (e2e/golden-runtime.spec.ts keeps the real
 * chain under CF01_GATE=1 with its seeded disposable database).
 */
import type { Page } from '@playwright/test'

/** Deterministic search hit (person) matching the public search projection. */
export const PERSON_HIT = {
  kind: 'person',
  id: 'ENT-PERSON-HFM-HUANGFUMI',
  title: '皇甫谧',
  snippet: '',
  version_id: null,
  publication_status: 'PUBLISHED',
} as const

/** Deterministic public person projection matching GET /public/persons/:id. */
export const PERSON_PROJECTION = {
  entity_id: 'ENT-PERSON-HFM-HUANGFUMI',
  name_zh: '皇甫谧',
  name_pinyin: null,
  courtesy_name: null,
  pseudonym: null,
  dynasty: '西晋',
  publication_status: 'published',
  assertions: [],
  events: [],
} as const

function fulfillJson(route: Parameters<Parameters<Page['route']>[1]>[0], body: unknown): void {
  void route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify(body),
  })
}

/** Stub the public search endpoint with one deterministic person hit. */
export function stubPublicSearch(page: Page): void {
  void page.route('**/api/v1/public/search*', (route) =>
    fulfillJson(route, {
      success: true,
      data: { hits: [PERSON_HIT], total: 1, page: 1, page_size: 20 },
    }),
  )
}

/** Stub the public person endpoint with the deterministic Huangfu Mi record. */
export function stubPublicPerson(page: Page): void {
  void page.route('**/api/v1/public/persons/**', (route) =>
    fulfillJson(route, { success: true, data: PERSON_PROJECTION }),
  )
}
