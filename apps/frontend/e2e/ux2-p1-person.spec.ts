/**
 * UX2-P1 browser E2E — person archive surface (real Chromium, mocked public API).
 *
 * Proves in the real browser DOM:
 *  - /persons/person-huangfu-mi renders the DHObjectLayout (语境·证据·关联)
 *    with G1-C presentation states;
 *  - F-5 Historical Assessments (后论) renders real houlun content;
 *  - 其传 renders real qichuan content;
 *  - heading hierarchy: exactly one h1;
 *  - no horizontal overflow at mobile width.
 */
import { expect, test, type Page } from '@playwright/test'

async function mockPublicApi(page: Page): Promise<void> {
  await page.route('**/api/v1/public/**', (route) => {
    const url = route.request().url()
    let body: unknown = null
    if (url.includes('/persons/')) {
      body = {
        entity_id: 'person-huangfu-mi',
        name_zh: '皇甫谧',
        name_pinyin: 'Huángfǔ Mì',
        courtesy_name: '士安',
        pseudonym: '玄晏先生',
        dynasty: '西晋',
        publication_status: 'published',
        assertions: [],
        events: [],
      }
    } else if (url.includes('/media')) {
      body = { items: [], total: 0 }
    }
    void route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(body) })
  })
}

test.describe('UX2-P1 person archive surface', () => {
  test('renders DHObjectLayout with presentation states and F-5 后论 content', async ({ page }) => {
    await mockPublicApi(page)
    const response = await page.goto('/persons/person-huangfu-mi')
    expect(response?.status()).toBe(200)

    await expect(page.getByRole('heading', { name: '皇甫谧' })).toBeVisible()
    await expect(page.getByRole('heading', { name: '语境 · 证据 · 关联' })).toBeVisible()

    // DHObjectLayout regions render (header ABSENT_OPTIONAL collapses)
    await expect(page.locator('[data-primitive="dh-object"]')).toBeVisible()
    await expect(page.locator('[data-slot="context"][data-slot-state="INCOMPLETE_WITH_EVIDENCE_STATE"]')).toBeVisible()
    await expect(page.locator('[data-slot="evidence"][data-slot-state="INCOMPLETE_WITH_EVIDENCE_STATE"]')).toBeVisible()
    await expect(page.locator('[data-slot="relations"][data-slot-state="PRESENT"]')).toBeVisible()
    await expect(page.locator('[data-slot="header"]')).toHaveCount(0)

    // G1-C states visible as text + color (not color-only)
    await expect(page.locator('.hfm-status[data-status="SCHOLARLY_UNCERTAIN"]')).toHaveText('尚有争议')
    await expect(page.locator('.hfm-status[data-status="METADATA_ONLY"]')).toContainText('原典全文未收录')

    // F-5 Historical Assessments: 后论 real content + reader link
    await expect(page.locator('[aria-labelledby="afterwords-heading"]')).toContainText('后论 · 历史评价汇编')
    await expect(page.locator('[aria-labelledby="afterwords-heading"] .hfm-status')).toHaveText('全文已整理')
    await expect(page.locator('[aria-labelledby="afterwords-heading"] a[href="/reader/houlun"]')).toBeVisible()

    // 其传 real content
    await expect(page.locator('[aria-labelledby="biography-heading"]')).toContainText('其传 · 史料来源整理')
    await expect(page.locator('[aria-labelledby="biography-heading"] a[href="/reader/qichuan"]')).toBeVisible()

    // heading hierarchy: exactly one h1
    await expect(page.locator('h1')).toHaveCount(1)

    // no horizontal overflow at mobile width
    await page.setViewportSize({ width: 375, height: 800 })
    const overflow = await page.evaluate(
      () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
    )
    expect(overflow).toBeLessThanOrEqual(0)
  })
})
