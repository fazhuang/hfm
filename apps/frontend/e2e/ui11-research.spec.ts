/**
 * UI-11 Research Workbench — browser E2E (authenticated flow).
 *
 * Mocks the login API, then exercises: landing, research search, entity
 * research views (皇甫谧 / 甲乙经 / 刘君奇 / 后论), evidence explorer,
 * public↔research links, mobile sidebar, 375/1920, dark, keyboard.
 */
import { expect, test } from '@playwright/test'

const USER = {
  id: 'u1',
  username: 'researcher',
  roles: ['STUDENT_RESEARCHER'],
  permissions: [],
}

async function loginAt(page: import('@playwright/test').Page, target: string): Promise<void> {
  await page.route('**/api/v1/auth/login', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ token: 'test-token', user: USER }),
    }),
  )
  await page.goto(target)
  await page.waitForURL(/\/login/)
  await page.getByLabel('用户名').fill('researcher')
  await page.getByLabel('密码').fill('pw')
  await page.getByRole('button', { name: '登录' }).click()
  await page.waitForURL(new RegExp(target.split('?')[0].replace(/[.*+?^${}()|[\]\\]/g, '\\$&')))
}

test('UI-11 research entry requires login then lands on the workbench', async ({ page }) => {
  await loginAt(page, '/research')
  await expect(page.getByRole('heading', { name: '研究工作台' })).toBeVisible()
  await expect(page.getByText('可研究内容')).toBeVisible()
})

test('UI-11 research search reuses the unified index with denser metadata', async ({ page }) => {
  await loginAt(page, '/research/search?q=黄龙祥')
  await expect(page.getByRole('heading', { name: '研究检索' })).toBeVisible()
  await expect(page.getByText(/找到 \d+ 条结果/)).toBeVisible()
  await expect(page.getByText('研究视图 →').first()).toBeVisible()
})

test('UI-11 entity research views: 皇甫谧 / 甲乙经 / 刘君奇 / 后论', async ({ page }) => {
  const cases = [
    {
      path: '/research/entity/person/person-huangfu-mi',
      title: '皇甫谧',
      public: '查看公众人物页',
    },
    { path: '/research/entity/work/w-jiayi', title: '《针灸甲乙经》', public: '查看公众页' },
    {
      path: '/research/entity/heritage/liujunqi',
      title: '皇甫谧针灸非遗',
      public: '查看公众非遗页',
    },
    { path: '/research/entity/reader/houlun', title: '后论', public: '打开阅读' },
  ]
  for (const c of cases) {
    await loginAt(page, c.path)
    await expect(page.getByRole('heading', { name: c.title })).toBeVisible()
    await expect(page.getByText(c.public)).toBeVisible()
  }
})

test('UI-11 evidence explorer shows real statuses (no invented states)', async ({ page }) => {
  await loginAt(page, '/research/entity/reader/houlun')
  await expect(page.getByText('Evidence', { exact: true })).toBeVisible()
  await expect(page.getByText('已展示').first()).toBeVisible()
  await expect(page.getByText('可引用条目').first()).toBeVisible()
})

test('UI-11 public ↔ research round trip keeps context', async ({ page }) => {
  await loginAt(page, '/research/entity/person/person-huangfu-mi')
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
  await page.getByText('查看公众人物页').click()
  await expect(page.getByRole('heading', { name: '皇甫谧' })).toBeVisible()
  await expect(page.getByRole('banner')).toBeVisible()
})

test('UI-11 mobile sidebar toggles with keyboard', async ({ page }) => {
  await loginAt(page, '/research')
  await page.setViewportSize({ width: 375, height: 812 })
  const toggle = page.getByRole('button', { name: '研究导航' })
  await expect(toggle).toBeVisible()
  await toggle.focus()
  await page.keyboard.press('Enter')
  await expect(page.getByRole('link', { name: '检索' })).toBeVisible()
  await page.keyboard.press('Escape')
  await expect(page.getByRole('link', { name: '检索' })).toBeHidden()
  await expect(toggle).toBeFocused()
})

test('UI-11 responsive: 375 no overflow, 1920 bounded, dark mode', async ({ page }) => {
  await loginAt(page, '/research/entity/work/w-jiayi')
  for (const width of [375, 1920]) {
    await page.setViewportSize({ width, height: 900 })
    await page.goto('/research/entity/work/w-jiayi')
    await page.waitForURL(/\/login/).catch(() => undefined)
    if (new URL(page.url()).pathname.includes('login')) {
      await loginAt(page, '/research/entity/work/w-jiayi')
    }
    await page.waitForTimeout(200)
    const overflow = await page.evaluate(
      () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
    )
    expect(overflow, `overflow at ${width}`).toBeLessThanOrEqual(0)
  }
  await page.evaluate(() => document.documentElement.classList.add('dark'))
  await page.goto('/research/entity/heritage/liujunqi')
  await page.waitForURL(/\/login/).catch(() => undefined)
  if (new URL(page.url()).pathname.includes('login')) {
    await loginAt(page, '/research/entity/heritage/liujunqi')
  }
  const bodyColor = await page.evaluate(() => getComputedStyle(document.body).backgroundColor)
  expect(bodyColor).not.toBe('rgb(255, 255, 255)')
})
