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
  { name: 'sm', width: 390, height: 844 }, // below --hfm-bp-sm? no: sm covers >=480; 390 exercises <sm fallback
  { name: 'sm', width: 480, height: 800 }, // --hfm-bp-sm
  { name: 'md', width: 768, height: 900 }, // --hfm-bp-md
  { name: 'lg', width: 1280, height: 800 }, // >= --hfm-bp-lg
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

    // Layout renders: brand, nav, main content.
    await expect(page.getByRole('banner')).toBeVisible()
    await expect(page.getByRole('navigation', { name: 'Public navigation' })).toBeVisible()
    await expect(page.getByRole('main')).toBeVisible()
    await expect(page.getByText('已发布内容')).toBeVisible()

    // No critical horizontal overflow.
    const overflow = await page.evaluate(
      () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
    )
    expect(overflow).toBeLessThanOrEqual(0)

    // Navigation remains usable.
    const homeLink = page.getByRole('navigation', { name: 'Public navigation' }).getByRole('link')
    await expect(homeLink.first()).toBeVisible()
    await homeLink.first().click()
    await expect(page.getByRole('heading', { name: /公开门户/ })).toBeVisible()
  })
}
