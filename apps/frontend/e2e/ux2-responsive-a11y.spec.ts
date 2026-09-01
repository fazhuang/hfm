/**
 * UX2-P6 Cross-Surface Responsive & Accessibility — browser E2E matrix.
 *
 * For every governed production surface (/ · /persons/person-huangfu-mi ·
 * /jiayi · /heritage · /search) at 375 / 1280 / 1920:
 *  - no horizontal overflow;
 *  - exactly one H1;
 *  - browser-level axe = 0 (full rule set);
 *  - no duplicate unnamed search landmarks.
 */
import { expect, test, type Page } from '@playwright/test'

/** Person page requires the public API mock (same shape as the P1 e2e). */
async function mockPublicApi(page: Page): Promise<void> {
  await page.route('**/api/v1/public/**', (route) => {
    const url = route.request().url()
    let body: unknown = null
    if (url.includes('/persons/')) {
      body = {
        entity_id: 'person-huangfu-mi',
        name_zh: '皇甫谧',
        name_pinyin: 'Huángfǔ Mì',
        courtesy_name: '士安',
        pseudonym: '玄晏先生',
        dynasty: '西晋',
        publication_status: 'published',
        assertions: [],
        events: [],
      }
    } else if (url.includes('/media')) {
      body = { items: [], total: 0 }
    }
    void route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(body) })
  })
}

const SURFACES = [
  { name: 'home', path: '/', mock: false },
  { name: 'person', path: '/persons/person-huangfu-mi', mock: true },
  { name: 'jiayi', path: '/jiayi', mock: false },
  { name: 'heritage', path: '/heritage', mock: false },
  { name: 'search', path: '/search?q=针灸甲乙经', mock: false },
] as const

test.describe('UX2-P6 cross-surface matrix', () => {
  for (const surface of SURFACES) {
    test(`${surface.name}: no overflow + single H1 + axe 0 at 375 / 1280 / 1920`, async ({ page }) => {
      if (surface.mock) await mockPublicApi(page)
      for (const width of [375, 1280, 1920]) {
        await page.setViewportSize({ width, height: 900 })
        await page.goto(surface.path)
        await page.waitForTimeout(300)
        const overflow = await page.evaluate(
          () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
        )
        expect(overflow, `${surface.name} overflow at ${width}px`).toBeLessThanOrEqual(0)
        const h1Count = await page.locator('h1').count()
        expect(h1Count, `${surface.name} h1 count at ${width}px`).toBe(1)
      }

      // full browser axe on the surface (1280 viewport)
      await page.setViewportSize({ width: 1280, height: 900 })
      await page.goto(surface.path)
      await page.waitForTimeout(300)
      await page.addScriptTag({ path: 'node_modules/axe-core/axe.min.js' })
      const violations = await page.evaluate(async () => {
        const runner = window as unknown as {
          axe: { run: (n: unknown) => Promise<{ violations: Array<{ id: string }> }> }
        }
        const results = await runner.axe.run(document)
        return results.violations.map((v) => v.id)
      })
      expect(violations, `${surface.name} axe`).toEqual([])
    })
  }

  test('no duplicate unnamed search landmarks on any surface', async ({ page }) => {
    for (const surface of SURFACES) {
      if (surface.mock) await mockPublicApi(page)
      await page.goto(surface.path)
      await page.waitForTimeout(300)
      const searchLandmarks = await page.evaluate(() => {
        const found: string[] = []
        for (const el of document.querySelectorAll('form[role="search"], [role="search"]')) {
          found.push(el.getAttribute('aria-label') ?? '')
        }
        return found
      })
      // the shared topbar search form is unnamed; the page form (when present)
      // is named 平台内容检索 — at most ONE unnamed search landmark per surface
      // (no duplicate unnamed collisions; P5/P4 axe landmark-unique already 0)
      const unnamedCount = searchLandmarks.filter((n) => n === '').length
      expect(unnamedCount, `${surface.name} unnamed search landmarks`).toBeLessThanOrEqual(1)
      expect(searchLandmarks.filter((n) => n === '平台内容检索').length).toBeLessThanOrEqual(1)
    }
  })

  test('keyboard: Tab reaches an interactive element with visible focus on each surface', async ({ page }) => {
    for (const surface of SURFACES) {
      if (surface.mock) await mockPublicApi(page)
      await page.goto(surface.path)
      await page.waitForTimeout(300)
      await page.keyboard.press('Tab')
      const focusInfo = await page.evaluate(() => {
        const el = document.activeElement
        if (!el) return { tag: '', focused: false }
        const cs = getComputedStyle(el)
        return {
          tag: el.tagName,
          focused: el !== document.body,
          focusRing: cs.boxShadow !== 'none' || cs.outlineStyle !== 'none',
        }
      })
      expect(focusInfo.focused, `${surface.name} first Tab focus`).toBe(true)
      expect(focusInfo.focusRing, `${surface.name} focus indicator`).toBe(true)
    }
  })
})
