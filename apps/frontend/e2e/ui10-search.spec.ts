/**
 * UI-10 / Search — auxiliary browser UI tests (CF-06).
 *
 * The PUBLIC surface is wired to the real /api/v1/public/search endpoint;
 * its full-chain acceptance is the golden real-runtime journey + the CF-06
 * real browser gate (no network interception there). This file covers the
 * UI states deterministically by stubbing the search transport with the
 * documented response envelope (same pattern as other auxiliary e2e specs
 * that stub their public-API routes). Never used as production proof.
 */
import { expect, test } from '@playwright/test'

const PERSON_HIT = {
  kind: 'person',
  id: 'ENT-PERSON-HFM-HUANGFUMI',
  title: '皇甫谧',
  snippet: '',
  version_id: null,
  publication_status: 'PUBLISHED',
}

function stubSearch(page: import('@playwright/test').Page, data: unknown): void {
  void page.route('**/api/v1/public/search*', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ success: true, data }),
    }),
  )
}

test('UI-10 /search accessible; idle shows scope + static entry points', async ({ page }) => {
  await page.goto('/search')
  await expect(page.getByRole('heading', { name: '检索', exact: true })).toBeVisible()
  await expect(page.getByRole('heading', { name: '检索范围' })).toBeVisible()
  await expect(page.getByRole('link', { name: '皇甫谧' }).first()).toBeVisible()
})

test('UI-10 query renders real-projection rows; person result navigates canonically', async ({
  page,
}) => {
  stubSearch(page, { hits: [PERSON_HIT], total: 1, page: 1, page_size: 20 })
  await page.goto('/search?q=皇甫谧')
  await expect(page.getByText('找到 1 条结果')).toBeVisible()
  await expect(page.locator('.result-row__type').first()).toHaveText('人物')
  const link = page.locator('.result-row__link').first()
  await expect(link).toHaveAttribute('href', '/persons/ENT-PERSON-HFM-HUANGFUMI')
})

test('UI-10 empty (0 total) is distinct from error', async ({ page }) => {
  stubSearch(page, { hits: [], total: 0, page: 1, page_size: 20 })
  await page.goto('/search?q=完全不存在的词xyz')
  await expect(page.locator('[data-search-state="empty"]')).toBeVisible()
  await expect(page.locator('[data-search-state="error"]')).toHaveCount(0)
})

test('UI-10 API failure (500) shows an error state, never 暂无结果', async ({ page }) => {
  await page.route('**/api/v1/public/search*', (route) =>
    route.fulfill({ status: 500, contentType: 'application/json', body: '{"success":false}' }),
  )
  await page.goto('/search?q=皇甫谧')
  await expect(page.locator('[data-search-state="error"]')).toBeVisible()
  await expect(page.getByText(/检索服务暂时不可用/)).toBeVisible()
  await expect(page.locator('[data-search-state="empty"]')).toHaveCount(0)
})

test('UI-10 keyboard: Enter submits and the URL carries q (state round-trip)', async ({ page }) => {
  stubSearch(page, { hits: [PERSON_HIT], total: 1, page: 1, page_size: 20 })
  await page.goto('/search')
  const input = page.locator('.search-form input')
  await input.fill('皇甫谧')
  await input.press('Enter')
  await expect(page).toHaveURL(/q=%E7%9A%87%E7%94%AB%E8%B0%A7/)
  await expect(page.getByText('找到 1 条结果')).toBeVisible()
  // Refresh recovers the same state from the URL.
  await page.reload()
  await expect(page.getByText('找到 1 条结果')).toBeVisible()
})

test('UI-10 responsive: no overflow at 375 / 1440 in results; dark mode readable', async ({
  page,
}) => {
  stubSearch(page, { hits: [PERSON_HIT], total: 1, page: 1, page_size: 20 })
  for (const width of [375, 1440]) {
    await page.setViewportSize({ width, height: 900 })
    await page.goto('/search?q=皇甫谧')
    await expect(page.getByText('找到 1 条结果')).toBeVisible()
    const overflow = await page.evaluate(
      () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
    )
    expect(overflow, `overflow at ${width}`).toBeLessThanOrEqual(0)
  }
  await page.evaluate(() => document.documentElement.classList.add('dark'))
  const title = page.locator('.result-row__title').first()
  await expect(title).toBeVisible()
})
