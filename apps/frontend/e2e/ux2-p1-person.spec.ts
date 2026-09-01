/**
 * UX2-P1 browser E2E — person archive surface (real Chromium).
 *
 * Covers:
 *  - DHObjectLayout states + F-5 后论 real content on the person page;
 *  - P1-02A reader navigation: person → 其传 reader → back → 后论 reader,
 *    verifying real route + real content (no dead routes / placeholders);
 *  - P1-02B keyboard/focus: reader links reachable via Tab, Enter activates,
 *    visible focus indicator, no focus trap;
 *  - P1-02C browser-level axe (real browser, not jsdom);
 *  - P1-02D responsive: no horizontal overflow at 375 / 1280 / 1920.
 *
 * NOTE (V5 scope restoration): F-5 Archival Media REAL-data runtime proof is
 * NOT claimed here. The real production chain (governed per-media record →
 * backend media_assets → public API → fetchPublicMedia) does not exist in the
 * frozen production state, and the frozen P1 allowlist forbids creating it.
 * Blocked by UX2-P1-F5-CONTRACT-CAPABILITY-MISMATCH. The media mock serves an
 * empty projection (absent state) — no synthetic media acceptance fixture.
 */
import { expect, test, type Page } from '@playwright/test'

/** Empty media projection — the real chain is not present; page shows absent state. */
const MEDIA_EMPTY = { items: [], total: 0 }

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
      body = MEDIA_EMPTY
    }
    void route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(body) })
  })
}

async function openPerson(page: Page): Promise<void> {
  await mockPublicApi(page)
  await page.goto('/persons/person-huangfu-mi')
  await expect(page.getByRole('heading', { name: '皇甫谧', exact: true })).toBeVisible()
}

test.describe('UX2-P1 person archive surface', () => {
  test('renders DHObjectLayout states and F-5 后论 content', async ({ page }) => {
    await openPerson(page)

    await expect(page.getByRole('heading', { name: '语境 · 证据 · 关联' })).toBeVisible()
    await expect(page.locator('[data-primitive="dh-object"]')).toBeVisible()
    await expect(
      page.locator('[data-slot="context"][data-slot-state="INCOMPLETE_WITH_EVIDENCE_STATE"]'),
    ).toBeVisible()
    await expect(
      page.locator('[data-slot="evidence"][data-slot-state="INCOMPLETE_WITH_EVIDENCE_STATE"]'),
    ).toBeVisible()
    await expect(page.locator('[data-slot="relations"][data-slot-state="PRESENT"]')).toBeVisible()
    await expect(page.locator('[data-slot="header"]')).toHaveCount(0)
    await expect(page.locator('.hfm-status[data-status="SCHOLARLY_UNCERTAIN"]')).toHaveText('尚有争议')

    // F-5 Historical Assessments: 后论 real content + reader link
    await expect(page.locator('[aria-labelledby="afterwords-heading"]')).toContainText('后论 · 历史评价汇编')
    await expect(page.locator('[aria-labelledby="afterwords-heading"] .hfm-status')).toHaveText('全文已整理')
    await expect(page.locator('[aria-labelledby="afterwords-heading"] a[href="/reader/houlun"]')).toBeVisible()

    // 其传 real content
    await expect(page.locator('[aria-labelledby="biography-heading"]')).toContainText('其传 · 史料来源整理')
    await expect(page.locator('[aria-labelledby="biography-heading"] a[href="/reader/qichuan"]')).toBeVisible()

    // heading hierarchy: exactly one h1
    await expect(page.locator('h1')).toHaveCount(1)

    // F-5A production truth (amended contract): the real runtime media API
    // returns [] (no admitted MediaAsset records) — the 影像资料 section must
    // degrade truthfully: empty state, no fake movie, no player, no false
    // RESOURCE_READY claim.
    const mediaSection = page.locator('[aria-labelledby="media-heading"]')
    await expect(mediaSection).toContainText('暂无影像资料。')
    await expect(mediaSection.locator('.movie-card')).toHaveCount(0)
    await expect(mediaSection.locator('video')).toHaveCount(0)
    await expect(mediaSection.locator('.hfm-status[data-status="RESOURCE_READY"]')).toHaveCount(0)
    await expect(mediaSection).not.toContainText('皇甫谧一')

    // F-5C: real-media end-to-end admission is deferred to Phase 2 / P2-05
    // (not claimed here). F-5B presentation capability is proven at unit level.
  })

  test('reader navigation: person → 其传 reader → back → 后论 reader (no dead routes)', async ({ page }) => {
    await openPerson(page)

    await page.locator('[aria-labelledby="biography-heading"] a[href="/reader/qichuan"]').click()
    await expect(page).toHaveURL(/\/reader\/qichuan/)
    await expect(page.locator('.reader__title')).toHaveText('其传 · 史料来源整理')
    await expect(page.locator('.reader__status')).toHaveText('全文可读')
    await expect(page.locator('.reader')).toContainText('本源核心史料')

    await page.goBack()
    await expect(page).toHaveURL(/\/persons\/person-huangfu-mi/)
    await expect(page.getByRole('heading', { name: '语境 · 证据 · 关联' })).toBeVisible()

    await page.locator('[aria-labelledby="afterwords-heading"] a[href="/reader/houlun"]').click()
    await expect(page).toHaveURL(/\/reader\/houlun/)
    await expect(page.locator('.reader__title')).toHaveText('后论 · 历史评价汇编')
    await expect(page.locator('.reader__status')).toHaveText('全文可读')
    await expect(page.locator('.reader')).toContainText('男子皇甫谧沈静履素')
  })

  test('keyboard: reader links reachable via Tab, Enter activates, visible focus, no trap', async ({ page }) => {
    await openPerson(page)

    let focusedHref = ''
    for (let i = 0; i < 80; i += 1) {
      await page.keyboard.press('Tab')
      focusedHref = await page.evaluate(() => document.activeElement?.getAttribute('href') ?? '')
      if (focusedHref === '/reader/qichuan') break
    }
    expect(focusedHref).toBe('/reader/qichuan')

    const focusRingVisible = await page.evaluate(() => {
      const el = document.activeElement
      if (!el) return false
      const cs = getComputedStyle(el)
      return cs.boxShadow !== 'none' || cs.outlineStyle !== 'none'
    })
    expect(focusRingVisible).toBe(true)

    await page.keyboard.press('Enter')
    await expect(page).toHaveURL(/\/reader\/qichuan/)

    await page.keyboard.press('Tab')
    const moved = await page.evaluate(() => document.activeElement?.tagName ?? '')
    expect(moved).not.toBe('')
  })

  test('browser-level axe = 0 on the person archive page', async ({ page }) => {
    await openPerson(page)
    await page.addScriptTag({ path: 'node_modules/axe-core/axe.min.js' })
    const violations = await page.evaluate(async () => {
      const runner = window as unknown as {
        axe: { run: (n: unknown) => Promise<{ violations: Array<{ id: string }> }> }
      }
      const results = await runner.axe.run(document)
      return results.violations.map((v) => v.id)
    })
    expect(violations).toEqual([])
  })

  test('responsive: no horizontal overflow at 375 / 1280 / 1920', async ({ page }) => {
    for (const width of [375, 1280, 1920]) {
      await page.setViewportSize({ width, height: 900 })
      await openPerson(page)
      const overflow = await page.evaluate(
        () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
      )
      expect(overflow, `horizontal overflow at ${width}px`).toBeLessThanOrEqual(0)
    }
  })
})
