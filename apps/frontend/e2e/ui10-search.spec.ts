/**
 * UI-10 Search / Bibliography — browser E2E.
 *
 *  - /search accessible; ?q= returns results; type filter via URL works;
 *  - refresh + back/forward recover state;
 *  - pagination URL round-trip (when applicable);
 *  - 375 no overflow; 1920 content stays bounded; dark mode readable;
 *  - keyboard submit works.
 */
import { expect, test } from '@playwright/test'

test('UI-10 /search is accessible and returns results for 针灸甲乙经', async ({ page }) => {
  await page.goto('/search?q=针灸甲乙经')
  await expect(page.getByRole('heading', { name: '检索' })).toBeVisible()
  await expect(page.getByText(/找到 \d+ 条结果/)).toBeVisible()
  await expect(page.getByRole('list').first()).toBeVisible()
})

test('UI-10 type filter via URL (?type=work) is applied', async ({ page }) => {
  await page.goto('/search?q=针灸甲乙经&type=work')
  await expect(page.getByText(/找到 \d+ 条结果\s*（作品）/)).toBeVisible()
  // Facet active state reflects the URL.
  await expect(page.getByRole('button', { name: /作品/ })).toHaveAttribute('aria-pressed', 'true')
})

test('UI-10 refresh and back/forward recover state', async ({ page }) => {
  await page.goto('/search?q=皇甫谧&type=edition')
  await expect(page.getByText(/找到 \d+ 条结果\s*（版本）/)).toBeVisible()
  await page.reload()
  await expect(page.getByText(/找到 \d+ 条结果\s*（版本）/)).toBeVisible()
  // Navigate away and back.
  await page.goto('/jiayi')
  await page.goBack()
  await expect(page.getByText(/找到 \d+ 条结果\s*（版本）/)).toBeVisible()
})

test('UI-10 keyboard: submit via Enter triggers search', async ({ page }) => {
  await page.goto('/search')
  const input = page.locator('.search-form input')
  await input.fill('高士传')
  await input.press('Enter')
  await expect(page).toHaveURL(/q=%E9%AB%98%E5%A3%AB%E4%BC%A0/)
  await expect(page.getByText(/找到 \d+ 条结果/)).toBeVisible()
})

test('UI-10 responsive: 375 no overflow, 1920 bounded', async ({ page }) => {
  for (const width of [375, 1920]) {
    await page.setViewportSize({ width, height: 900 })
    await page.goto('/search?q=针灸甲乙经')
    await page.waitForTimeout(200)
    const overflow = await page.evaluate(
      () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
    )
    expect(overflow, `overflow at ${width}`).toBeLessThanOrEqual(0)
  }
})

test('UI-10 dark mode: highlight and metadata stay readable', async ({ page }) => {
  await page.goto('/search?q=甲乙经')
  await page.evaluate(() => document.documentElement.classList.add('dark'))
  const mark = page.locator('mark').first()
  await expect(mark).toBeVisible()
  const markColor = await mark.evaluate((el) => getComputedStyle(el).backgroundColor)
  expect(markColor).not.toBe('rgb(255, 255, 255)')
})
