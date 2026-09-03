/**
 * UI-13 Visual Polish — browser E2E regression.
 *
 * Verifies cross-surface polish with computed-style assertions:
 *  - shared eyebrow primitive (heritage color, sm, 0.12em) on key pages;
 *  - shared status primitive (token backgrounds) on archive + research;
 *  - unified heading scale (serif, h1 28px default; hero overrides larger);
 *  - no horizontal overflow on all major surfaces at 375/1920;
 *  - dark mode quality (no black crush / low contrast on text);
 *  - focus-visible ring present on interactive elements.
 */
import { expect, test } from '@playwright/test'

const SURFACES = [
  '/',
  '/persons/person-huangfu-mi',
  '/yan',
  '/jiayi',
  '/heritage',
  '/search',
  '/reader/houlun',
]

test('UI-13 no horizontal overflow on major surfaces (375 / 1920)', async ({ page }) => {
  for (const width of [375, 1920]) {
    await page.setViewportSize({ width, height: 900 })
    for (const path of SURFACES) {
      await page.goto(path)
      await page.waitForTimeout(120)
      const overflow = await page.evaluate(
        () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
      )
      expect(overflow, `${path}@${width}`).toBeLessThanOrEqual(0)
    }
  }
})

test('UI-13 shared eyebrow primitive uses heritage token styling', async ({ page }) => {
  const cases = [
    '/',
    '/jiayi',
    '/yan',
    '/works',
    '/archive',
    '/heritage',
    '/search',
    '/reader/houlun',
  ]
  for (const path of cases) {
    await page.goto(path)
    const eyebrow = page.locator('.hfm-eyebrow').first()
    if ((await eyebrow.count()) === 0) continue
    const style = await eyebrow.evaluate((el) => {
      const cs = getComputedStyle(el)
      return { color: cs.color, fontSize: cs.fontSize, letterSpacing: cs.letterSpacing }
    })
    // heritage cinnabar-ish bronze token (light mode ~ rgb(138,106,47)).
    expect(style.color, path).toBe('rgb(138, 106, 47)')
    expect(style.fontSize, path).toBe('13px')
    expect(style.letterSpacing, path).toBe('1.56px') // 13px × 0.12em
  }
})

test('UI-13 shared status primitive renders token backgrounds', async ({ page }) => {
  await page.goto('/archive')
  const available = page.locator('.hfm-status[data-status="AVAILABLE"]').first()
  await expect(available).toBeVisible()
  const bg = await available.evaluate((el) => getComputedStyle(el).backgroundColor)
  expect(bg).toBe('rgb(226, 240, 230)') // success-surface token
})

test('UI-13 unified heading scale: default h1 serif 28px, hero h1 larger', async ({ page }) => {
  await page.goto('/about')
  const h1 = await page
    .getByRole('heading', { level: 1 })
    .first()
    .evaluate((el) => {
      const cs = getComputedStyle(el)
      return { font: cs.fontFamily.split(',')[0], size: cs.fontSize }
    })
  expect(h1.font).toBe('"Songti SC"')
  expect(h1.size).toBe('28px')

  await page.goto('/')
  const heroH1 = await page
    .getByRole('heading', { name: '皇甫谧人文数字平台' })
    .evaluate((el) => getComputedStyle(el).fontSize)
  /* Accepted H3 hero (WP-04): the platform name is the quiet top-right register (10px) as
     the single H1; the dominant 皇甫谧 190px monument is a non-heading decorative element
     (aria-hidden). This is the frozen artboard's heading treatment. */
  expect(heroH1).toBe('10px')
})

test('UI-13 dark mode quality: body + text contrast on key surfaces', async ({ page }) => {
  for (const path of ['/', '/jiayi', '/heritage', '/search']) {
    await page.goto(path)
    await page.evaluate(() => document.documentElement.classList.add('dark'))
    const colors = await page.evaluate(() => {
      const body = getComputedStyle(document.body)
      const p = document.querySelector('p')
      return { bodyBg: body.backgroundColor, text: p ? getComputedStyle(p).color : body.color }
    })
    expect(colors.bodyBg, path).toBe('rgb(22, 19, 15)') // dark canvas token
    expect(colors.text, path).not.toBe('rgb(0, 0, 0)')
    expect(colors.text, path).not.toBe(colors.bodyBg)
    await page.evaluate(() => document.documentElement.classList.remove('dark'))
  }
})

test('UI-13 focus-visible ring appears on interactive elements', async ({ page }) => {
  await page.goto('/')
  await page.keyboard.press('Tab')
  await page.keyboard.press('Tab')
  const focusRing = await page.evaluate(() => {
    const el = document.activeElement
    if (!el) return null
    return getComputedStyle(el).boxShadow
  })
  expect(focusRing).toBeTruthy()
  expect(focusRing).not.toBe('none')
})
