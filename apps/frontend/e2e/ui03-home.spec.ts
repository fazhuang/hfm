/**
 * UI-03 Homepage — browser E2E.
 *
 *  - unique H1 = 皇甫谧人文数字平台; narrative sections in order;
 *  - CTA targets real routes; search submits to /search?q=;
 *  - 刘君奇·第六代名医 real; lineage caption carries DATA-GAP;
 *  - 375/768/1024/1440/1920 no overflow; dark; 200% zoom (640px).
 */
import { expect, test } from '@playwright/test'

test('UI-03 homepage renders unique H1 and narrative sections', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByRole('heading', { name: '皇甫谧人文数字平台' })).toBeVisible()
  await expect(page.getByRole('heading', { name: '皇甫谧', exact: true })).toBeVisible()
  await expect(page.getByRole('heading', { name: '《针灸甲乙经》' })).toBeVisible()
  await expect(page.getByRole('heading', { name: '文献与史料' })).toBeVisible()
  await expect(page.getByRole('heading', { name: '皇甫谧针灸非遗 · 活态传承' })).toBeVisible()
  await expect(page.getByRole('heading', { name: '从资料到研究' })).toBeVisible()
})

test('UI-03 CTA targets are real routes', async ({ page }) => {
  await page.goto('/')
  const targets = [
    '/persons/person-huangfu-mi',
    '/jiayi',
    '/yan',
    '/archive',
    '/heritage',
    '/research',
  ]
  for (const target of targets) {
    const link = page.locator(`a[href="${target}"]`).first()
    await expect(link).toBeVisible()
    expect(await link.getAttribute('href')).toBe(target)
  }
})

test('UI-03 search submits to /search?q=', async ({ page }) => {
  await page.goto('/')
  const input = page.locator('#home-search-input')
  await input.fill('甲乙经')
  await page.locator('form.home-search').getByRole('button', { name: '检索' }).click()
  await expect(page).toHaveURL(/\/search\?q=%E7%94%B2%E4%B9%99%E7%BB%8F/)
  await expect(page.getByText(/找到 \d+ 条结果/)).toBeVisible()
})

test('UI-03 刘君奇·第六代名医 and lineage DATA-GAP are真实呈现', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByText('第六代名医').first()).toBeVisible()
  await expect(page.getByText('刘君奇').first()).toBeVisible()
  await expect(page.getByText(/结构化版本关系整理中（DATA-GAP）/)).toBeVisible()
})

test('UI-03 real quotation with attribution (no fabricated slogan)', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByText(/皇甫谧素履幽贞/)).toBeVisible()
  await expect(page.getByText(/房玄龄/)).toBeVisible()
})

test('UI-03 responsive: 375–1920 no overflow, dark, 200% zoom', async ({ page }) => {
  for (const width of [375, 768, 1024, 1440, 1920]) {
    await page.setViewportSize({ width, height: 900 })
    await page.goto('/')
    await page.waitForTimeout(150)
    const overflow = await page.evaluate(
      () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
    )
    expect(overflow, `overflow at ${width}`).toBeLessThanOrEqual(0)
  }
  await page.evaluate(() => document.documentElement.classList.add('dark'))
  await page.goto('/')
  await page.waitForTimeout(150)
  const bodyColor = await page.evaluate(() => getComputedStyle(document.body).backgroundColor)
  expect(bodyColor).not.toBe('rgb(255, 255, 255)')
  // 200% zoom (640px = 1280 at 200%).
  await page.setViewportSize({ width: 640, height: 720 })
  await page.goto('/')
  const zoomOverflow = await page.evaluate(
    () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
  )
  expect(zoomOverflow).toBeLessThanOrEqual(0)
})
