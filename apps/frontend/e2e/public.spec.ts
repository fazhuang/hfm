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
    await expect(page.getByRole('heading', { name: /公开门户/ })).toBeVisible()
    // No login wall: the page stays at home.
    expect(new URL(page.url()).pathname).toBe('/')
  })
})

test.describe('P2-01-AC-02 published projection only', () => {
  test('published content is visible', async ({ page }) => {
    await mockPublicHome(page)
    await page.goto('/')
    await expect(page.getByText('已发布内容', { exact: true })).toBeVisible()
  })

  test('draft content is not visible', async ({ page }) => {
    await mockPublicHome(page)
    await page.goto('/')
    await expect(page.getByText('未发布草稿', { exact: true })).not.toBeVisible()
  })

  test('withdrawn content is not visible', async ({ page }) => {
    await mockPublicHome(page)
    await page.goto('/')
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
