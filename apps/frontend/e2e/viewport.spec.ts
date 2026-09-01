/**
 * P2-01 real viewport rendering verification (P1-02 correction).
 *
 * Renders the public portal in real Chromium at the frozen breakpoint
 * matrix (sm 480 / md 768 / lg 1024) and proves: the layout renders, no
 * critical horizontal overflow, navigation stays usable, and content
 * remains accessible — not just the breakpoint helper return value.
 */
import { expect, test } from '@playwright/test'

const PROJECTION = {
  items: [
    { id: 'pub-1', title: '已发布内容', publicationState: 'published' },
    { id: 'pub-2', title: '针灸甲乙经·校勘', publicationState: 'published' },
  ],
}

const VIEWPORTS = [
  { name: 'sm', width: 375, height: 812 }, // iPhone-class mobile (UI-02 matrix)
  { name: 'sm', width: 480, height: 800 }, // --hfm-bp-sm
  { name: 'md', width: 768, height: 900 }, // --hfm-bp-md
  { name: 'lg', width: 1024, height: 800 }, // --hfm-bp-lg
  { name: 'xl', width: 1440, height: 900 }, // --hfm-bp-xl
  { name: '2xl', width: 1920, height: 1080 }, // --hfm-bp-2xl
] as const

for (const vp of VIEWPORTS) {
  test(`viewport ${vp.name} (${vp.width}px): layout renders without overflow, nav usable`, async ({
    page,
  }) => {
    await page.setViewportSize({ width: vp.width, height: vp.height })
    await page.route('**/api/v1/public/home', (route) =>
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(PROJECTION),
      }),
    )
    await page.goto('/')

    // Layout renders: brand, main content.
    await expect(page.getByRole('banner')).toBeVisible()
    await expect(page.getByRole('main')).toBeVisible()
    await expect(page.getByRole('heading', { name: '皇甫谧人文数字平台' })).toBeVisible()

    // No critical horizontal overflow.
    const overflow = await page.evaluate(
      () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
    )
    expect(overflow).toBeLessThanOrEqual(0)

    // Navigation stays usable: drawer toggle at <768px, inline nav at >=768px
    // (UI-02 mobile drawer — P2-01-AC-05 responsive matrix preserved).
    const nav = page.getByRole('navigation', { name: 'Public navigation' })
    if (vp.width < 768) {
      const toggle = page.getByRole('button', { name: '打开导航菜单' })
      await expect(toggle).toBeVisible()
      // Closed drawer: main-nav links hidden.
      await expect(nav.getByRole('link').first()).toBeHidden()
      await toggle.click()
      await expect(nav.getByRole('link').first()).toBeVisible()
      await nav.getByRole('link').first().click()
    } else {
      await expect(nav).toBeVisible()
      await expect(nav.getByRole('link').first()).toBeVisible()
      await nav.getByRole('link').first().click()
    }
    await expect(page.getByRole('heading', { name: /皇甫谧人文数字平台/ })).toBeVisible()
  })
}
