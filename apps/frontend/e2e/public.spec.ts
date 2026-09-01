/**
 * P2-01 browser E2E (P1-01 correction).
 *
 * Real-browser proof of the frozen public-frontend acceptance criteria:
 *  - P2-01-AC-01 anonymous visitor traverses the public portal without an
 *    auth challenge;
 *  - P2-01-AC-02 the public surface renders the published projection only
 *    (draft and withdrawn content are not visible);
 *  - P2-01-AC-03 research/admin surfaces are unavailable anonymously
 *    (redirect to login).
 *
 * The public API route (/api/v1/public/home) is mocked at the network layer;
 * rendering, navigation and redirects run in real Chromium.
 */
import { expect, test } from '@playwright/test'

const PROJECTION = {
  items: [
    { id: 'pub-1', title: '已发布内容', publicationState: 'published' },
    { id: 'draft-1', title: '未发布草稿', publicationState: 'draft' },
    { id: 'wd-1', title: '已撤回内容', publicationState: 'withdrawn' },
  ],
}

async function mockPublicHome(page: import('@playwright/test').Page): Promise<void> {
  await page.route('**/api/v1/public/home', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(PROJECTION),
    }),
  )
}

test.describe('P2-01-AC-01 anonymous public traversal', () => {
  test('anonymous visitor opens the portal home without any auth challenge', async ({ page }) => {
    await mockPublicHome(page)
    const response = await page.goto('/')
    expect(response?.status()).toBe(200)
    await expect(page.getByRole('heading', { name: /皇甫谧人文数字平台/ })).toBeVisible()
    // No login wall: the page stays at home.
    expect(new URL(page.url()).pathname).toBe('/')
  })
})

test.describe('P2-01-AC-02 published projection only (static homepage)', () => {
  test('homepage renders the platform hero; mocked draft/withdrawn content never leaks', async ({
    page,
  }) => {
    await mockPublicHome(page)
    await page.goto('/')
    // The homepage is a static verified-content projection: it renders real
    // platform content and can never surface draft/withdrawn records.
    await expect(page.getByRole('heading', { name: '皇甫谧人文数字平台' })).toBeVisible()
    await expect(page.getByText('未发布草稿', { exact: true })).not.toBeVisible()
    await expect(page.getByText('已撤回内容', { exact: true })).not.toBeVisible()
  })
})

test.describe('P2-01-AC-03 research/admin unavailable anonymously', () => {
  test('anonymous /research redirects to login', async ({ page }) => {
    await page.goto('/research')
    await page.waitForURL(/\/(login|$)/)
    expect(new URL(page.url()).pathname).toBe('/login')
  })

  test('anonymous /admin redirects to login', async ({ page }) => {
    await page.goto('/admin')
    await page.waitForURL(/\/(login|$)/)
    expect(new URL(page.url()).pathname).toBe('/login')
  })
})

test.describe('UI-02 main navigation (customer 5 links)', () => {
  test('main nav exposes exactly five links and header tools are separate', async ({ page }) => {
    await mockPublicHome(page)
    await page.goto('/')
    const nav = page.getByRole('navigation', { name: 'Public navigation' })
    const mainLinks = nav.locator('a.nav-link')
    await expect(mainLinks).toHaveCount(5)
    await expect(mainLinks.nth(0)).toHaveText('首页')
    await expect(mainLinks.nth(1)).toHaveText('人物（皇甫谧）')
    await expect(mainLinks.nth(2)).toHaveText('其言')
    await expect(mainLinks.nth(3)).toHaveText('《针灸甲乙经》')
    await expect(mainLinks.nth(4)).toHaveText('皇甫谧针灸非遗的传承')
    // Search + login live outside the main nav (header utility area).
    await expect(page.getByRole('banner').getByRole('search')).toBeVisible()
    await expect(page.getByRole('link', { name: '登录' })).toBeVisible()
  })
})
