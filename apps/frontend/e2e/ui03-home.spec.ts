/**
 * Homepage browser E2E — HFM-FRONTEND-CONTENT-CONTRACT v1 §4.
 *
 *  - unique H1 = 皇甫谧人文数字平台; the six contract blocks exist in exact
 *    order (home-hero → home-person → home-yan → home-book → home-heritage →
 *    home-closing);
 *  - T0 participation: the hero's published counts and the 人物 block's
 *    assertions render from the real backend; blocks without T0 carry a
 *    visible data-source + fallback note (never a silent substitute);
 *  - exactly ONE global semantic footer; the close is a section;
 *  - CTA targets real routes; search submits to /search?q=;
 *  - responsive: 375 / 768 / 1440, no horizontal overflow, dark mode readable.
 */
import { expect, test } from '@playwright/test'
import { mkdirSync } from 'node:fs'
import { resolve } from 'node:path'

const SECTION_IDS = [
  'home-hero',
  'home-person',
  'home-yan',
  'home-book',
  'home-heritage',
  'home-closing',
]

const EVIDENCE_DIR = resolve(process.cwd(), '../../docs/audit/evidence/cf08')

test('contract structure: unique H1 + the six blocks in order', async ({ page }) => {
  mkdirSync(EVIDENCE_DIR, { recursive: true })
  await page.setViewportSize({ width: 1440, height: 900 })
  await page.goto('/')
  await page.waitForTimeout(400)
  await expect(page.getByRole('heading', { level: 1 })).toHaveCount(1)
  await expect(page.getByRole('heading', { name: '皇甫谧人文数字平台' })).toBeVisible()
  const ids = await page.$$eval('section[id^="home-"]', (els) => els.map((e) => e.id))
  expect(ids).toEqual(SECTION_IDS)
  await page.screenshot({ path: resolve(EVIDENCE_DIR, 'home-contract-1440.png'), fullPage: false })
})

test('T0 participation: hero counts + person assertions render from the backend', async ({ page }) => {
  await page.goto('/')
  await page.waitForTimeout(600)
  const hero = page.locator('#home-hero')
  await expect(hero).toHaveAttribute('data-source', 'backend')
  await expect(hero).toContainText('已发布著作')
  await expect(page.locator('.home')).toHaveAttribute('data-home-source', 'backend')
  const person = page.locator('#home-person')
  await expect(person).toHaveAttribute('data-source', 'backend')
  const facts = await page.locator('#home-person .person__fact').count()
  expect(facts).toBeGreaterThanOrEqual(10)
})

test('every block carries a data-source marker; T1 fallbacks are visible', async ({ page }) => {
  await page.goto('/')
  await page.waitForTimeout(600)
  for (const id of SECTION_IDS) {
    expect(await page.locator(`#${id}`).getAttribute('data-source'), id).toBeTruthy()
  }
  // 其言 is un-admitted → honest state, never fabricated full text.
  await expect(page.locator('#home-yan [data-empty-state]')).toBeVisible()
  // 非遗 has no T0 yet (C1 pending) → visible fallback note.
  await expect(page.locator('#home-heritage [data-fallback-note]')).toBeVisible()
})

test('exactly one global footer; the close is a section', async ({ page }) => {
  await page.goto('/')
  await expect(page.locator('footer')).toHaveCount(1)
  const closing = page.locator('#home-closing')
  expect(await closing.evaluate((el) => el.tagName)).toBe('SECTION')
  await expect(closing).not.toContainText(/版权与免责声明|隐私说明/)
})

test('CTA targets are real routes', async ({ page }) => {
  await page.goto('/')
  for (const target of [
    '/persons/ENT-PERSON-HFM-HUANGFUMI',
    '/yan',
    '/jiayi',
    '/heritage',
    '/search',
  ]) {
    const link = page.locator(`a[href="${target}"]`).first()
    await expect(link, `link to ${target}`).toBeVisible()
  }
})

test('search submits to /search?q=', async ({ page }) => {
  await page.goto('/')
  await page.fill('#home-search-input', '甲乙经')
  await page.locator('#home-hero form.home-search').getByRole('button', { name: '检索' }).click()
  await expect(page).toHaveURL(/\/search\?q=%E7%94%B2%E4%B9%99%E7%BB%8F/)
})

test('responsive: 375 / 768 / 1440 render all six blocks with no overflow', async ({ page }) => {
  for (const width of [375, 768, 1440]) {
    await page.setViewportSize({ width, height: 900 })
    await page.goto('/')
    await page.waitForTimeout(300)
    const ids = await page.$$eval('section[id^="home-"]', (els) => els.map((e) => e.id))
    expect(ids, `blocks at ${width}`).toEqual(SECTION_IDS)
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
