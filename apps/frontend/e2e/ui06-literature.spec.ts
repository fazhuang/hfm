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
  await expect(page.getByRole('heading', { name: '《三都赋》序', exact: true })).toBeVisible()
  await expect(page.getByRole('heading', { name: '《笃终论》', exact: true })).toBeVisible()
  // P-8a supplies the four texts from public-domain editions. The page must
  // show the text AND name its base edition — an unattributed full text is
  // the thing the old DATA_GAP placeholder existed to prevent.
  await expect(page.getByText('玄晏先生曰：古人稱不歌而頌謂之賦').first()).toBeVisible()
  await expect(page.getByText('維基文庫單篇本（繁體）').first()).toBeVisible()
  await expect(page.getByRole('heading', { name: '校勘记' }).first()).toBeVisible()
  await expect(page.getByText('全文整理中').first()).toBeHidden()
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

test('UI-06 其言: 竖排切换生效且跨刷新保持', async ({ page }) => {
  await page.goto('/yan')
  const body = page.locator('.yan-fulltext__body').first()
  expect(await body.evaluate((el) => getComputedStyle(el).writingMode)).toContain('horizontal')

  await page.getByRole('button', { name: '切为竖排' }).click()
  expect(await body.evaluate((el) => getComputedStyle(el).writingMode)).toContain('vertical')
  // 四篇同时切换：版式是全局偏好，不是逐篇设置。
  const modes = await page
    .locator('.yan-fulltext__body')
    .evaluateAll((els) => els.map((el) => getComputedStyle(el).writingMode))
  expect(new Set(modes).size).toBe(1)

  await page.reload()
  await expect(page.getByRole('button', { name: '切为横排' })).toBeVisible()
})

test('UI-06 其言: 生僻字带注音，且只注生僻字', async ({ page }) => {
  await page.goto('/yan')
  const rubies = page.locator('.yan-fulltext__body ruby')
  expect(await rubies.count()).toBeGreaterThan(20)
  // 注音内容非空且为拉丁字母。
  const readings = await rubies.locator('rt').evaluateAll((els) => els.map((e) => e.textContent ?? ''))
  expect(readings.every((r) => /^[a-zāáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜü]+$/i.test(r.replace(/\s/g, '')))).toBe(true)
  // 不注常用字：正文里的「人」「之」等不应产生 ruby。
  const common = await page
    .locator('.yan-fulltext__body p')
    .first()
    .evaluate((el) => Array.from(el.querySelectorAll('ruby')).map((r) => r.firstChild?.textContent ?? ''))
  expect(common).not.toContain('人')
  expect(common).not.toContain('之')
})

test('UI-06 其言: 篇目导航可跳转到各篇', async ({ page }) => {
  await page.goto('/yan')
  const links = page.locator('.yan-nav__link')
  await expect(links).toHaveCount(4)
  await links.nth(3).click()
  await expect(page).toHaveURL(/#duzhong-lun-section$/)
  await expect(page.getByRole('heading', { name: '《笃终论》', exact: true })).toBeVisible()
})
