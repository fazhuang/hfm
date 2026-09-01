/**
 * UI-12 correction — browser E2E.
 *
 *  - PATH D: main nav 人物（皇甫谧） → canonical person page (desktop + mobile);
 *  - PATH E: /jiayi DOM contains no internal provenance, source labels readable.
 */
import { expect, test } from '@playwright/test'

async function mockPersonApi(page: import('@playwright/test').Page): Promise<void> {
  await page.route('**/api/v1/public/persons/**', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        success: true,
        data: {
          entity_id: 'person-huangfu-mi',
          name_zh: '皇甫谧',
          name_pinyin: null,
          courtesy_name: null,
          pseudonym: null,
          dynasty: '西晋',
          publication_status: 'published',
          assertions: [],
          events: [],
        },
      }),
    }),
  )
  await page.route('**/api/v1/public/media**', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ success: true, data: { items: [], total: 0 } }),
    }),
  )
}

test('UI-12 PATH D: main nav 人物（皇甫谧） reaches the canonical person page (desktop)', async ({
  page,
}) => {
  await mockPersonApi(page)
  await page.setViewportSize({ width: 1280, height: 800 })
  await page.goto('/')
  const personLink = page.getByRole('link', { name: '皇甫谧人物档案' })
  await expect(personLink).toHaveAttribute('href', '/persons/person-huangfu-mi')
  await personLink.click()
  await expect(page).toHaveURL(/\/persons\/person-huangfu-mi$/)
  await expect(page.getByRole('heading', { name: '皇甫谧' })).toBeVisible()
})

test('UI-12 PATH D: mobile drawer nav reaches the canonical person page', async ({ page }) => {
  await mockPersonApi(page)
  await page.setViewportSize({ width: 375, height: 812 })
  await page.goto('/')
  await page.getByRole('button', { name: '打开导航菜单' }).click()
  const personLink = page
    .getByRole('navigation', { name: 'Public navigation' })
    .getByRole('link', { name: '皇甫谧人物档案' })
  await expect(personLink).toHaveAttribute('href', '/persons/person-huangfu-mi')
  await personLink.click()
  await expect(page).toHaveURL(/\/persons\/person-huangfu-mi$/)
  await expect(page.getByRole('heading', { name: '皇甫谧' })).toBeVisible()
})

test('UI-12 direct canonical person URL works (no not-found)', async ({ page }) => {
  await mockPersonApi(page)
  await page.goto('/persons/person-huangfu-mi')
  await expect(page.getByRole('heading', { name: '皇甫谧' })).toBeVisible()
  await expect(page.getByText('人物不存在或未发布')).not.toBeVisible()
})

test('UI-12 PATH E: /jiayi DOM contains no internal provenance, labels readable', async ({
  page,
}) => {
  await page.goto('/jiayi')
  const body = await page.locator('body').innerText()
  expect(body).not.toContain('hfmzl/')
  expect(body).not.toContain('zzcl/')
  expect(body).not.toContain('registerKey')
  // Public source labels remain readable.
  await expect(page.getByText('客户提供《针灸甲乙经》学术论文资料')).toBeVisible()
  await expect(page.getByText('客户提供《针灸甲乙经》资料').first()).toBeVisible()
})
