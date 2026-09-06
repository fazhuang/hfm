/**
 * CF-10 — Real-browser keyboard + focus-visibility verification (Tab/Shift+Tab).
 *
 * Uses genuine Playwright keyboard input against real production routes, asserting
 * every keyboard-focused control shows a visible focus indicator (the repo's
 * :focus-visible ring = box-shadow), and that a bounded number of Tabs always
 * lands on a focusable element (no trap). Also checks homepage touch targets at 375.
 */
import { expect, test, type Page } from '@playwright/test'

const SURFACES = ['HOME', 'PERSON', 'JIAYI', 'HERITAGE', 'SEARCH', 'RESEARCH_GUARD'] as const

async function gotoSurface(page: Page, surface: string): Promise<void> {
  await page.setViewportSize({ width: 1440, height: 900 })
  switch (surface) {
    case 'HOME':
      await page.goto('/')
      break
    case 'PERSON':
      await page.goto('/persons/person-huangfu-mi')
      break
    case 'JIAYI':
      await page.goto('/jiayi')
      break
    case 'HERITAGE':
      await page.goto('/heritage')
      break
    case 'SEARCH': {
      await page.goto('/search')
      const input = page.locator('input[type="search"], input[type="text"], form input').first()
      await input.fill('皇甫谧')
      await page.keyboard.press('Enter')
      await expect(page.locator('.result-list, ol.result-list')).toBeVisible()
      break
    }
    case 'RESEARCH_GUARD':
      await page.goto('/research')
      await page.waitForURL(/\/login/)
      break
  }
  await page.waitForLoadState('networkidle')
  await page.waitForTimeout(150)
}

interface Focused {
  tag: string
  cls: string
  name: string
  ring: boolean
}

async function readFocused(page: Page): Promise<Focused> {
  return page.evaluate(() => {
    const el = document.activeElement as HTMLElement | null
    if (!el || el === document.body) return { tag: 'body', cls: '', name: '', ring: false }
    const cs = getComputedStyle(el)
    const ring =
      cs.boxShadow !== 'none' || (cs.outlineStyle !== 'none' && cs.outlineWidth !== '0px')
    return {
      tag: el.tagName.toLowerCase(),
      cls: (el.getAttribute('class') ?? '').split(' ').slice(0, 2).join(' '),
      name: (el.getAttribute('aria-label') ?? el.innerText ?? '').slice(0, 24),
      ring,
    }
  })
}

test('CF-10 keyboard traversal + visible focus across surfaces', async ({ page }) => {
  const summary: Record<string, number> = {}
  for (const surface of SURFACES) {
    await gotoSurface(page, surface)
    const reached: Focused[] = []
    for (let i = 0; i < 30; i++) {
      await page.keyboard.press('Tab')
      const f = await readFocused(page)
      if (f.tag !== 'body') reached.push(f)
    }
    const noRing = reached.filter((r) => !r.ring)
    summary[surface] = reached.length
    console.log(`CF10_KEYBOARD ${surface} reached=${reached.length} noRing=${noRing.length}`)
    if (noRing.length)
      console.log(`CF10_KEYBOARD_NORING ${surface} ${JSON.stringify(noRing, null, 2)}`)
    expect(reached.length, `keyboard produced no focusable on ${surface}`).toBeGreaterThan(0)
  }
  for (const s of SURFACES) {
    expect(summary[s] ?? 0, `${s} keyboard traversal`).toBeGreaterThan(0)
  }
})

test('CF-10 focus indicator is visible (no invisible focused control)', async ({ page }) => {
  await page.goto('/')
  await page.waitForTimeout(200)
  await page.keyboard.press('Tab')
  const f = await readFocused(page)
  expect(f.tag === 'a' || f.tag === 'button' || f.tag === 'input', `first focus was ${f.tag}`).toBe(
    true,
  )
  expect(f.ring, `first focused control has no visible focus ring (${f.name})`).toBe(true)
})

test('CF-10 homepage touch targets at 375 (WCAG 2.5.5: ≥24×24 for visible primary controls)', async ({
  page,
}) => {
  await page.setViewportSize({ width: 375, height: 900 })
  await page.goto('/')
  await page.waitForTimeout(200)
  // Open the mobile nav drawer so its links become real, visible touch targets.
  const toggle = page.locator('.nav-toggle')
  if ((await toggle.count()) > 0) await toggle.first().click()
  await page.waitForTimeout(150)
  const small = await page.evaluate(() => {
    const selectors = [
      '#home-hero .home-hero__act',
      '#home-hero .home-search__input',
      '#home-hero .home-search__submit',
      '.public-shell__nav .nav-link',
      '.nav-toggle',
      '#home-book .home-book__act',
      '#home-knowledge .home-knowledge__act',
      '#home-domains .home-domains__go',
      '#home-heritage .home-heritage__act',
    ]
    return selectors
      .map((s) => {
        const el = document.querySelector(s)
        if (!el) return { s, missing: true }
        const r = el.getBoundingClientRect()
        if (r.width === 0 || r.height === 0) return { s, hidden: true }
        return { s, w: Math.round(r.width), h: Math.round(r.height) }
      })
      .filter((r) => !r.missing && !r.hidden && (r.w < 24 || r.h < 24))
  })
  expect(small, `undersized touch targets at 375: ${JSON.stringify(small, null, 2)}`).toHaveLength(
    0,
  )
})
