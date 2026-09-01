/**
 * UX2-P2 Jiayi Work / Edition — browser E2E (real Chromium).
 *
 * Proves:
 *  - /jiayi renders 19 edition records via the BibliographicRecord primitive
 *    with 存目 (METADATA_ONLY) — no fake digitized-resource state;
 *  - DATA-GAP state (版本关系整理中) renders; chronology ≠ lineage caption;
 *  - no horizontal overflow at 375 / 1280 / 1920;
 *  - browser-level axe = 0.
 */
import { expect, test } from '@playwright/test'

test.describe('UX2-P2 Jiayi surface', () => {
  test('renders 19 editions via BibliographicRecord with 存目 and DATA-GAP state', async ({ page }) => {
    await page.goto('/jiayi')
    await expect(page.getByRole('heading', { name: '《针灸甲乙经》' })).toBeVisible()

    // all 19 editions render through the shared primitive with 存目
    await expect(page.locator('[data-primitive="bib-record"]')).toHaveCount(19)
    await expect(page.locator('.edition-card .hfm-status[data-status="METADATA_ONLY"]')).toHaveCount(19)
    await expect(page.locator('.edition-card .hfm-status').first()).toHaveText('存目')
    await expect(page.locator('.edition-card .hfm-status').last()).toHaveText('存目')

    // U-05: no fake digitized-resource state (no play/read CTA on editions)
    const editionText = await page.locator('#editions').innerText()
    expect(editionText).not.toContain('阅读全文')
    expect(editionText).not.toContain('可阅读')

    // DATA-GAP state + chronology ≠ lineage caption
    await expect(page.locator('.lineage-state .hfm-status')).toHaveText('版本关系整理中')
    await expect(page.locator('#edition-timeline')).toContainText('chronology ≠ lineage')

    // NB-03: no genealogy claims
    await expect(page.locator('#editions')).not.toContainText('继承自')

    // exactly one h1
    await expect(page.locator('h1')).toHaveCount(1)
  })

  test('browser-level axe = 0 on the jiayi page', async ({ page }) => {
    await page.goto('/jiayi')
    await expect(page.getByRole('heading', { name: '《针灸甲乙经》' })).toBeVisible()
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
      await page.goto('/jiayi')
      await expect(page.getByRole('heading', { name: '《针灸甲乙经》' })).toBeVisible()
      const overflow = await page.evaluate(
        () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
      )
      expect(overflow, `horizontal overflow at ${width}px`).toBeLessThanOrEqual(0)
    }
  })
})
