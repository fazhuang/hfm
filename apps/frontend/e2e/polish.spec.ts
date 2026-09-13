/**
 * CF-11 — Final visual polish verification (real browser).
 *
 * Locks the CF-11 micro-interaction polish:
 *   every homepage editorial CTA arrow carries a transform transition (consistent
 *   hover affordance), and the global link colour transition is active, in real
 *   Chromium. Also captures evidence screenshots under docs/audit/evidence/cf11/.
 *
 * WR00-B2-E2E-R1 data isolation: the evidence pass renders the data-flow
 * surfaces (person page, search results) from a deterministic test-owned data
 * contract (see data-fixtures.ts) instead of depending on pre-existing
 * business data in the runtime database; no writes are made.
 */
import { expect, test } from '@playwright/test'
import { mkdirSync } from 'node:fs'
import { resolve } from 'node:path'

import { stubPublicPerson, stubPublicSearch } from './data-fixtures'

const EVIDENCE_DIR = resolve(process.cwd(), '../../docs/audit/evidence/cf11')

const CTA_ARROWS = [
  '.home-hero__act-arr',
  '.home-person__act-arr',
  '.home-yan__act-arr',
  '.home-book__act-arr',
  '.home-heritage__act-arr',
  '.home-closing__act-arr',
]

test('CF-11 editorial CTA arrows all carry the transform transition (consistent hover affordance)', async ({
  page,
}) => {
  await page.setViewportSize({ width: 1440, height: 900 })
  await page.goto('/')
  await page.waitForTimeout(200)
  for (const sel of CTA_ARROWS) {
    const prop = await page
      .locator(sel)
      .first()
      .evaluate((el) => getComputedStyle(el).transitionProperty)
    expect(prop, `${sel} should have a transform transition`).toContain('transform')
  }
})

test('CF-11 global link colour transition is active (subtle, non-blocking feedback)', async ({
  page,
}) => {
  await page.goto('/')
  const prop = await page
    .locator('a')
    .first()
    .evaluate((el) => getComputedStyle(el).transitionProperty)
  expect(prop).toContain('color')
})

test('CF-11 link/arrow transitions respect prefers-reduced-motion', async ({ page }) => {
  await page.emulateMedia({ reducedMotion: 'reduce' })
  await page.goto('/')
  await page.waitForTimeout(200)
  const dur = await page
    .locator('#home-hero .home-hero__act-arr')
    .first()
    .evaluate((el) => parseFloat(getComputedStyle(el).transitionDuration))
  // The global reduced-motion rule forces transition-duration to ~0 (0.01ms).
  expect(dur).toBeLessThanOrEqual(0.00002)
})

test('CF-11 evidence screenshots (375 / 768 / 1440 + public surfaces)', async ({ page }) => {
  // WR00-B2-E2E-R1: this evidence pass navigates 13 surfaces and captures
  // screenshots; under a loaded parallel dev server it can exceed the global
  // 30s timeout, so the runner tears the page down mid-pass. Per-test
  // runner-lifecycle ceiling only — no assertion or product change.
  test.setTimeout(180_000)
  mkdirSync(EVIDENCE_DIR, { recursive: true })
  // Data-flow surfaces (person page + search results) render deterministic
  // test-owned content for the evidence pass.
  stubPublicPerson(page)
  stubPublicSearch(page)
  const shots: Array<[string, number]> = [
    ['home', 375],
    ['home', 768],
    ['home', 1440],
    ['person', 375],
    ['person', 1440],
    ['jiayi', 375],
    ['jiayi', 1440],
    ['heritage', 375],
    ['heritage', 1440],
    ['search', 375],
    ['search', 1440],
    ['research_guard', 375],
    ['research_guard', 1440],
  ]
  for (const [name, width] of shots) {
    await page.setViewportSize({ width, height: 900 })
    const path =
      name === 'home'
        ? '/'
        : name === 'person'
          ? '/persons/ENT-PERSON-HFM-HUANGFUMI'
          : name === 'jiayi'
            ? '/jiayi'
            : name === 'heritage'
              ? '/heritage'
              : name === 'search'
                ? '/search'
                : '/research' // guard → /login
    await page.goto(path)
    if (name === 'research_guard') await page.waitForURL(/\/login/)
    if (name === 'search') {
      const input = page.locator('input[type="search"], input[type="text"], form input').first()
      await input.fill('皇甫谧')
      await page.keyboard.press('Enter')
      await expect(page.locator('.result-list, ol.result-list')).toBeVisible()
    }
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(150)
    await page.screenshot({ path: `${EVIDENCE_DIR}/${name}-${width}.png` })
  }
})
