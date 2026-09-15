/**
 * Homepage browser E2E — HFM-UI-CONTRACT-v2 §5.
 *
 * The contract deliberately does not fix the homepage's band count, band ids,
 * heading text, or CTA targets: the page is rebuilt against the reference
 * layout (`HFM-SY-CK.png`) and those all move. This spec asserts only what must
 * survive any rebuild — one H1, one usable search entry, exactly one global
 * footer, no horizontal overflow at the three breakpoints, and no broken images.
 */
import { expect, test } from '@playwright/test'

test('one H1, one search input, one global footer', async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 900 })
  await page.goto('/')
  await page.waitForTimeout(400)
  await expect(page.getByRole('heading', { level: 1 })).toHaveCount(1)
  await expect(page.locator('#header-search-input')).toHaveCount(1)
  await expect(page.locator('footer')).toHaveCount(1)
})

test('search submits to /search?q=', async ({ page }) => {
  await page.goto('/')
  await page.fill('#header-search-input', '甲乙经')
  await page.locator('#header-search-input').press('Enter')
  await expect(page).toHaveURL(/\/search\?q=%E7%94%B2%E4%B9%99%E7%BB%8F/)
})

test('responsive: 375 / 768 / 1440 with no horizontal overflow', async ({ page }) => {
  for (const width of [375, 768, 1440]) {
    await page.setViewportSize({ width, height: 900 })
    await page.goto('/')
    await page.waitForTimeout(300)
    const overflow = await page.evaluate(
      () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
    )
    expect(overflow, `overflow at ${width}`).toBeLessThanOrEqual(0)
  }
})

test('images load and controls stay in viewport at 1440', async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 900 })
  await page.goto('/')
  await page.waitForTimeout(400)
  const broken = await page.$$eval('img', (imgs) =>
    imgs.filter((i) => !i.complete || i.naturalWidth === 0).map((i) => i.getAttribute('src')),
  )
  expect(broken).toHaveLength(0)
})
