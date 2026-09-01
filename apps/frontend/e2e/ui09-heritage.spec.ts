/**
 * UI-09 Heritage — browser E2E.
 *
 *  - /heritage renders the flagship: 第六代名医·刘君奇, recognition,
 *    2023-09-26 apprenticeship, CCTV《陇脉医承》;
 *  - search integration: 刘君奇 reachable via the unified search;
 *  - 375 no overflow; dark mode readable; no clinical surface.
 */
import { expect, test } from '@playwright/test'

test('UI-09 /heritage renders the flagship content', async ({ page }) => {
  await page.goto('/heritage')
  await expect(page.getByRole('heading', { name: /皇甫谧针灸非遗/ })).toBeVisible()
  await expect(page.getByText('第六代名医').first()).toBeVisible()
  await expect(page.getByRole('heading', { name: '认定与荣誉' })).toBeVisible()
  await expect(page.getByText('2023-09-26').first()).toBeVisible()
  await expect(page.getByText('陇脉医承').first()).toBeVisible()
  await expect(page.getByRole('heading', { name: '传承谱系' })).toBeVisible()
})

test('UI-09 lineage shows confirmed nodes with PARTIAL note (no fabricated generations)', async ({
  page,
}) => {
  await page.goto('/heritage')
  await expect(page.locator('.lineage__person').first()).toHaveText('皇甫谧')
  await expect(page.getByText('第六代', { exact: false }).first()).toBeVisible()
  await expect(page.getByText(/第二代至第五代/).first()).toBeVisible()
  await expect(page.getByText('LINEAGE_STRUCTURING: PARTIAL').first()).toBeVisible()
})

test('UI-09 search integration: 刘君奇 findable via unified search', async ({ page }) => {
  await page.goto('/search?q=刘君奇')
  await expect(page.getByText(/找到 \d+ 条结果/)).toBeVisible()
  await expect(page.getByRole('link', { name: '刘君奇', exact: true }).first()).toBeVisible()
})

test('UI-09 responsive: 375 no overflow, dark mode readable, no clinical surface', async ({
  page,
}) => {
  await page.setViewportSize({ width: 375, height: 812 })
  await page.goto('/heritage')
  const overflow = await page.evaluate(
    () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
  )
  expect(overflow).toBeLessThanOrEqual(0)

  await page.evaluate(() => document.documentElement.classList.add('dark'))
  await page.waitForTimeout(200)
  const bodyColor = await page.evaluate(() => getComputedStyle(document.body).color)
  expect(bodyColor).not.toBe('rgb(0, 0, 0)')

  const body = await page.locator('body').innerText()
  expect(body).not.toMatch(/疗效显著|治疗推荐|预约|问诊/)
})
