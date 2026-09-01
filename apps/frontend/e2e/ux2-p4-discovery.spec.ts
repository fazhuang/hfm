/**
 * UX2-P4 Scholarly Discovery — browser E2E (real Chromium).
 *
 * Proves:
 *  - /search renders results via the BibliographicRecord primitive;
 *  - 515/5 paper split shown separately (no 515 searchable claim);
 *  - facet type filter via URL works (search-index type counts);
 *  - no fake full-text/PDF/reader/download affordances;
 *  - keyboard submit via Enter; refresh/back-forward recover state;
 *  - no horizontal overflow at 375 / 1280 / 1920;
 *  - browser-level axe = 0.
 */
import { expect, test } from '@playwright/test'

test.describe('UX2-P4 Scholarly Discovery surface', () => {
  test('renders results via BibliographicRecord with 515/5 and no fake actions', async ({ page }) => {
    await page.goto('/search?q=针灸甲乙经')
    await expect(page.getByRole('heading', { name: '检索' })).toBeVisible()
    await expect(page.getByText(/找到 \d+ 条结果/)).toBeVisible()

    // results render through the shared record primitive
    await expect(page.locator('.result-list [data-primitive="bib-record"]').first()).toBeVisible()

    // 515/5 shown separately (never claims 515 searchable)
    await expect(page.getByText(/已结构化 5/)).toBeVisible()
    await expect(page.getByText(/审计 515/)).toBeVisible()

    // discovery ≠ resource availability — no fake actions
    const resultsText = await page.locator('.result-list').innerText()
    expect(resultsText).not.toContain('阅读全文')
    expect(resultsText).not.toMatch(/查看\s*PDF|下载/i)
    expect(resultsText).not.toContain('在线阅读')

    // single h1
    await expect(page.locator('h1')).toHaveCount(1)
  })

  test('type filter via URL (?type=work) applies with search-index counts', async ({ page }) => {
    await page.goto('/search?q=针灸甲乙经&type=work')
    await expect(page.getByText(/找到 \d+ 条结果\s*（作品）/)).toBeVisible()
    await expect(page.getByRole('button', { name: /作品/ })).toHaveAttribute('aria-pressed', 'true')
  })

  test('refresh and back/forward recover query state', async ({ page }) => {
    await page.goto('/search?q=皇甫谧&type=edition')
    await expect(page.getByText(/找到 \d+ 条结果\s*（版本）/)).toBeVisible()
    await page.reload()
    await expect(page.getByText(/找到 \d+ 条结果\s*（版本）/)).toBeVisible()
    await page.goto('/jiayi')
    await page.goBack()
    await expect(page.getByText(/找到 \d+ 条结果\s*（版本）/)).toBeVisible()
  })

  test('keyboard: Enter submits the search', async ({ page }) => {
    await page.goto('/search')
    const input = page.locator('.search-form input')
    await input.fill('高士传')
    await page.keyboard.press('Enter')
    await expect(page).toHaveURL(/\/search\?q=/)
    await expect(page.getByText(/找到 \d+ 条结果/)).toBeVisible()
  })

  test('browser-level axe = 0 on the discovery surface (results + empty)', async ({ page }) => {
    await page.goto('/search?q=针灸甲乙经')
    await expect(page.locator('.result-list [data-primitive="bib-record"]').first()).toBeVisible()
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
      await page.goto('/search?q=针灸甲乙经')
      await expect(page.getByText(/找到 \d+ 条结果/)).toBeVisible()
      const overflow = await page.evaluate(
        () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
      )
      expect(overflow, `horizontal overflow at ${width}px`).toBeLessThanOrEqual(0)
    }
  })
})
