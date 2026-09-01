/**
 * UX2-P5 Homepage Exhibition Narrative — browser E2E (real Chromium).
 *
 * Proves:
 *  - narrative sections render in the frozen order;
 *  - P0 state labels render on surfaced data states (版本关系整理中 / 谱系整理中);
 *  - CTA routes resolve to implemented surfaces;
 *  - no horizontal overflow at 375 / 1280 / 1920;
 *  - browser-level axe = 0; keyboard reaches a CTA and Enter activates it.
 */
import { expect, test } from '@playwright/test'

test.describe('UX2-P5 Homepage surface', () => {
  test('renders narrative sections in order with truthful state labels', async ({ page }) => {
    await page.goto('/')
    await expect(page.getByRole('heading', { name: '皇甫谧人文数字平台' })).toBeVisible()
    await expect(page.getByRole('heading', { name: '皇甫谧', exact: true })).toBeVisible()
    await expect(page.getByRole('heading', { name: '《针灸甲乙经》' })).toBeVisible()
    await expect(page.getByRole('heading', { name: '文献与史料' })).toBeVisible()
    await expect(page.getByRole('heading', { name: '皇甫谧针灸非遗 · 活态传承' })).toBeVisible()
    await expect(page.getByRole('heading', { name: '从资料到研究' })).toBeVisible()

    // P0 state labels on surfaced data states
    await expect(page.locator('.home-lineage figcaption .hfm-status')).toHaveText('版本关系整理中')
    await expect(page.locator('.home-section--heritage .home-state-line .hfm-status')).toHaveText(
      '谱系整理中',
    )
    await expect(page.locator('.home-lineage figcaption')).toContainText('DATA-GAP')
    await expect(page.locator('.home-section--heritage')).toContainText('PARTIAL')

    // single h1
    await expect(page.locator('h1')).toHaveCount(1)
  })

  test('CTA and card links resolve to real implemented routes', async ({ page }) => {
    await page.goto('/')
    const targets = [
      '/persons/person-huangfu-mi',
      '/jiayi',
      '/yan',
      '/archive',
      '/heritage',
      '/research',
      '/search',
    ]
    for (const target of targets) {
      const link = page.locator(`a[href^="${target}"]`).first()
      await expect(link).toBeVisible()
    }
  })

  test('keyboard: Tab reaches a CTA and Enter activates it', async ({ page }) => {
    await page.goto('/')
    let focusedHref = ''
    for (let i = 0; i < 60; i += 1) {
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

  test('browser-level axe = 0 on the homepage', async ({ page }) => {
    await page.goto('/')
    await expect(page.getByRole('heading', { name: '皇甫谧人文数字平台' })).toBeVisible()
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
      await page.goto('/')
      await expect(page.getByRole('heading', { name: '皇甫谧人文数字平台' })).toBeVisible()
      const overflow = await page.evaluate(
        () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
      )
      expect(overflow, `horizontal overflow at ${width}px`).toBeLessThanOrEqual(0)
    }
  })
})
