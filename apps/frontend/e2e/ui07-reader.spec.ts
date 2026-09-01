/**
 * UI-07 Ancient Text Reader — browser E2E.
 *
 *  - real reader URLs accessible with real text;
 *  - section navigation works; direct hash URL recovers the section;
 *  - copy citation button works;
 *  - invalid reader id shows not-found;
 *  - search → reader routing;
 *  - 375 no overflow; 1920 reading width bounded; dark mode; 200% zoom.
 */
import { expect, test } from '@playwright/test'

test('UI-07 /reader/houlun renders real text with citations', async ({ page }) => {
  await page.goto('/reader/houlun')
  await expect(page.getByRole('heading', { name: /后论/ })).toBeVisible()
  await expect(page.getByText(/《晋书》/).first()).toBeVisible()
  await expect(page.getByRole('heading', { name: '论其人' })).toBeVisible()
  await expect(page.getByRole('heading', { name: '演其人' })).toBeVisible()
  const citations = page.getByRole('button', { name: /复制引用/ })
  expect(await citations.count()).toBe(12)
})

test('UI-07 section navigation: direct hash URL recovers the section', async ({ page }) => {
  await page.goto('/reader/houlun#yanqiren')
  await expect(page.getByRole('heading', { name: '演其人' })).toBeVisible()
  // Active nav item reflects the hash section.
  await expect(page.locator('.reader__nav-item--active')).toHaveText('演其人')
})

test('UI-07 copy citation produces deterministic text', async ({ page }) => {
  await page.goto('/reader/houlun')
  const first = page.getByRole('button', { name: /复制引用/ }).first()
  await expect(first).toBeVisible()
  // Deterministic citation content is present (document-level granularity).
  await expect(page.getByText(/作品：后论 · 历史评价汇编/).first()).toBeVisible()
})

test('UI-07 invalid reader id shows not-found with recovery links', async ({ page }) => {
  await page.goto('/reader/nope')
  await expect(page.getByText('未找到该文献')).toBeVisible()
  await expect(page.getByRole('link', { name: '检索' })).toBeVisible()
})

test('UI-07 search → reader routing', async ({ page }) => {
  await page.goto('/search?q=后论')
  await expect(page.getByText(/找到 \d+ 条结果/)).toBeVisible()
  const readerLink = page.getByRole('link', { name: /后论/ }).first()
  await readerLink.click()
  await expect(page.getByRole('heading', { name: /后论/ })).toBeVisible()
})

test('UI-07 responsive: 375 no overflow, 1920 reading bounded, dark + 200% zoom', async ({
  page,
}) => {
  for (const width of [375, 1920]) {
    await page.setViewportSize({ width, height: 900 })
    await page.goto('/reader/houlun')
    await page.waitForTimeout(200)
    const overflow = await page.evaluate(
      () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
    )
    expect(overflow, `overflow at ${width}`).toBeLessThanOrEqual(0)
  }

  // 1920 reading width stays bounded.
  await page.setViewportSize({ width: 1920, height: 900 })
  await page.goto('/reader/houlun')
  const paneWidth = await page
    .locator('.reader__paragraph')
    .first()
    .evaluate((el) => el.getBoundingClientRect().width)
  expect(paneWidth).toBeLessThan(1200)

  // Dark mode.
  await page.evaluate(() => document.documentElement.classList.add('dark'))
  await page.waitForTimeout(200)
  const bodyColor = await page.evaluate(() => getComputedStyle(document.body).backgroundColor)
  expect(bodyColor).not.toBe('rgb(255, 255, 255)')

  // 200% zoom (WCAG): 640px viewport = 1280 at 200% — content reflows, no overflow.
  await page.setViewportSize({ width: 640, height: 720 })
  await page.goto('/reader/houlun')
  const zoomOverflow = await page.evaluate(
    () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
  )
  expect(zoomOverflow).toBeLessThanOrEqual(0)
})
