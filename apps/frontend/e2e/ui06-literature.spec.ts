/**
 * UI-06 Literature / Qiyan / Archive — browser E2E.
 *
 *  - /yan /works /archive render their core headings;
 *  - 其言 content comes from the customer docx (visible real text);
 *  - 375px renders without horizontal overflow on all three surfaces;
 *  - dark mode keeps long-form reading surfaces sane.
 */
import { expect, test } from '@playwright/test'

const SURFACES = [
  { path: '/yan', heading: '其言' },
  { path: '/works', heading: '论著 / 研究' },
  { path: '/archive', heading: '数字档案' },
]

for (const surface of SURFACES) {
  test(`UI-06 ${surface.path}: heading renders and 375px has no overflow`, async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 })
    await page.goto(surface.path)
    await expect(page.getByRole('heading', { name: surface.heading })).toBeVisible()
    const overflow = await page.evaluate(
      () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
    )
    expect(overflow).toBeLessThanOrEqual(0)
  })
}

test('UI-06 其言: customer docx content is visible (real material, not placeholder)', async ({
  page,
}) => {
  await page.goto('/yan')
  await expect(page.getByText('皇甫谧本人存世文章、序跋、著作序言')).toBeVisible()
  await expect(page.getByRole('heading', { name: '《三都赋》序' })).toBeVisible()
  await expect(page.getByRole('heading', { name: '《笃终论》' })).toBeVisible()
  // No invented full text: DATA_GAP status shown honestly.
  await expect(page.getByText('全文整理中（客户文稿为整理说明，未含全文）').first()).toBeVisible()
})

test('UI-06 archive: no internal file-system paths are exposed publicly', async ({ page }) => {
  await page.goto('/archive')
  const body = await page.locator('body').innerText()
  expect(body).not.toContain('hfmzl/')
  expect(body).not.toContain('zzcl/')
  expect(body).toContain('皇甫谧人物资料')
  expect(body).toContain('皇甫谧针灸非遗传承')
})

test('UI-06 dark mode: long-form reading surface stays readable', async ({ page }) => {
  await page.goto('/yan')
  await page.evaluate(() => document.documentElement.classList.add('dark'))
  const textColor = await page
    .locator('.quotation__text')
    .first()
    .evaluate((el) => getComputedStyle(el).color)
  expect(textColor).not.toBe('rgb(0, 0, 0)')
  await expect(page.getByRole('heading', { name: '其言' })).toBeVisible()
})
