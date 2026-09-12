/**
 * UI-02 Global Shell — browser E2E.
 *
 *  - the five customer-mandated main-nav targets are reachable;
 *  - real keyboard path: Tab → toggle, Enter opens the drawer, Escape
 *    closes it and focus returns to the trigger (mobile nav semantics);
 *  - skip link is keyboard-activatable and lands in #main-content.
 */
import { expect, test } from '@playwright/test'

const NAV_TARGETS = [
  { label: '首页', href: '/' },
  { label: '人物（皇甫谧）', href: '/persons/person-huangfu-mi' },
  { label: '其言', href: '/yan' },
  { label: '《针灸甲乙经》', href: '/jiayi' },
  { label: '皇甫谧针灸非遗的传承', href: '/heritage' },
]

async function mockPublicApi(page: import('@playwright/test').Page): Promise<void> {
  await page.route('**/api/v1/public/**', (route) => {
    const url = route.request().url()
    let body: unknown = null
    if (url.includes('/home')) {
      body = { works: [], counts: { works: 0, persons: 0, heritage_projects: 0, c_terms: 0 } }
    } else if (url.includes('/persons/')) {
      body = {
        entity_id: 'person-huangfu-mi',
        name_zh: '皇甫谧',
        name_pinyin: null,
        courtesy_name: null,
        pseudonym: null,
        dynasty: '西晋',
        publication_status: 'published',
        assertions: [],
        events: [],
      }
    } else if (url.includes('/heritage')) {
      body = { projects: [] }
    } else if (url.includes('/media')) {
      body = { items: [], total: 0 }
    } else if (url.includes('/search')) {
      body = { hits: [], total: 0 }
    }
    void route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ success: true, data: body }),
    })
  })
}

test.describe('UI-02 five main-nav targets', () => {
  for (const target of NAV_TARGETS) {
    test(`target "${target.label}" (${target.href}) is reachable and renders main content`, async ({
      page,
    }) => {
      await mockPublicApi(page)
      await page.goto(target.href)
      await expect(page.getByRole('main')).toBeVisible()
      // No crash: at least the shell footer renders.
      await expect(page.getByRole('contentinfo')).toBeVisible()
      expect(new URL(page.url()).pathname).toBe(target.href)
    })
  }
})

test.describe('UI-02 keyboard navigation (mobile drawer)', () => {
  test.beforeEach(async ({ page }) => {
    await mockPublicApi(page)
    await page.setViewportSize({ width: 375, height: 812 })
    await page.goto('/')
  })

  test('Tab reaches toggle, Enter opens drawer, Escape closes, focus returns', async ({ page }) => {
    const toggle = page.getByRole('button', { name: '打开导航菜单' })
    const nav = page.getByRole('navigation', { name: 'Public navigation' })

    // Tab through skip link → brand → toggle (3rd tab stop; drawer links are
    // display:none while closed, so they are skipped).
    await page.keyboard.press('Tab')
    await page.keyboard.press('Tab')
    await page.keyboard.press('Tab')
    await expect(toggle).toBeFocused()

    // Enter opens the drawer; first nav link becomes visible + focusable.
    await page.keyboard.press('Enter')
    await expect(nav.getByRole('link').first()).toBeVisible()
    await expect(toggle).toHaveAttribute('aria-expanded', 'true')

    // Escape closes and focus returns to the trigger.
    await page.keyboard.press('Escape')
    await expect(nav.getByRole('link').first()).toBeHidden()
    await expect(toggle).toBeFocused()
    await expect(toggle).toHaveAttribute('aria-expanded', 'false')
  })
})

test.describe('UI-02 skip link', () => {
  test('keyboard activation moves focus into #main-content', async ({ page }) => {
    await mockPublicApi(page)
    await page.goto('/')
    const skip = page.getByRole('link', { name: '跳到主内容' })

    // Visually-hidden-but-focusable pattern: off-canvas until focused.
    const before = await skip.boundingBox()
    expect(before !== null && before.y < 0).toBe(true)

    await page.keyboard.press('Tab')
    await expect(skip).toBeFocused()
    const after = await skip.boundingBox()
    expect(after !== null && after.y >= 0).toBe(true)

    await page.keyboard.press('Enter')
    await expect(page.locator('#main-content')).toBeFocused()
  })
})
