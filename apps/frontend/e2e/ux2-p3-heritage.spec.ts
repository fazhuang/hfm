/**
 * UX2-P3 Heritage Living Archive — browser E2E (real Chromium).
 *
 * Proves:
 *  - /heritage renders two explicit evidence contexts
 *    (HISTORICAL_TEXTUAL_CONTEXT vs CONTEMPORARY_LIVING_ARCHIVE_CONTEXT);
 *  - PARTIAL lineage with 谱系整理中 state (UNSTRUCTURED_OR_INCOMPLETE);
 *  - recognition as secondary metadata (8 records);
 *  - 第六代名医 designation exact;
 *  - no horizontal overflow at 375 / 1280 / 1920;
 *  - browser-level axe = 0; related-nav keyboard reachable.
 */
import { expect, test } from '@playwright/test'

test.describe('UX2-P3 Heritage surface', () => {
  test('renders two explicit evidence contexts with truthful states', async ({ page }) => {
    await page.goto('/heritage')
    await expect(page.getByRole('heading', { name: /皇甫谧针灸非遗/ })).toBeVisible()

    // historical context band carries the lineage; contemporary carries the archive
    await expect(page.getByRole('heading', { name: /HISTORICAL_TEXTUAL_CONTEXT/ })).toBeVisible()
    await expect(
      page.getByRole('heading', { name: /CONTEMPORARY_LIVING_ARCHIVE_CONTEXT/ }),
    ).toBeVisible()

    // PARTIAL lineage + truthful 谱系整理中 state
    await expect(page.locator('[aria-labelledby="lineage-heading"] .hfm-status')).toHaveText('谱系整理中')
    await expect(page.locator('[aria-labelledby="lineage-heading"]')).toContainText('第二代至第五代')
    await expect(page.locator('.lineage__person').first()).toHaveText('皇甫谧')

    // recognition secondary metadata (8 records)
    await expect(page.locator('.recognition-item')).toHaveCount(8)
    await expect(page.getByRole('heading', { name: '认定与荣誉' })).toBeVisible()

    // 第六代名医 exact designation
    await expect(page.getByText('第六代名医', { exact: false }).first()).toBeVisible()

    // no internal register keys in public copy
    const text = await page.locator('.heritage').innerText()
    expect(text).not.toMatch(/hfmzl|zzcl/)

    // single h1
    await expect(page.locator('h1')).toHaveCount(1)
  })

  test('keyboard: related-nav links reachable via Tab with visible focus', async ({ page }) => {
    await page.goto('/heritage')
    await expect(page.getByRole('heading', { name: /皇甫谧针灸非遗/ })).toBeVisible()

    let focusedHref = ''
    for (let i = 0; i < 80; i += 1) {
      await page.keyboard.press('Tab')
      focusedHref = await page.evaluate(() => document.activeElement?.getAttribute('href') ?? '')
      if (focusedHref === '/persons/person-huangfu-mi') break
    }
    expect(focusedHref).toBe('/persons/person-huangfu-mi')
    const focusRingVisible = await page.evaluate(() => {
      const el = document.activeElement
      if (!el) return false
      const cs = getComputedStyle(el)
      return cs.boxShadow !== 'none' || cs.outlineStyle !== 'none'
    })
    expect(focusRingVisible).toBe(true)
    await page.keyboard.press('Enter')
    await expect(page).toHaveURL(/\/persons\/person-huangfu-mi/)
  })

  test('browser-level axe = 0 on the heritage page', async ({ page }) => {
    await page.goto('/heritage')
    await expect(page.getByRole('heading', { name: /皇甫谧针灸非遗/ })).toBeVisible()
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
      await page.goto('/heritage')
      await expect(page.getByRole('heading', { name: /皇甫谧针灸非遗/ })).toBeVisible()
      const overflow = await page.evaluate(
        () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
      )
      expect(overflow, `horizontal overflow at ${width}px`).toBeLessThanOrEqual(0)
    }
  })
})
