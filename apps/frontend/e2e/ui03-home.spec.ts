/**
 * UI-03 Homepage — browser E2E (CF-07 8-section structural shell).
 *
 *  - unique H1 = 皇甫谧人文数字平台; the eight accepted homepage sections
 *    exist in exact order with stable ids (home-hero → home-closing);
 *  - exactly ONE global semantic footer (AppFooter); Section 08 is a
 *    narrative closing section, never a second footer;
 *  - CTA targets real routes; search submits to /search?q=;
 *  - 刘君奇·第六代名医 real; book lineage caption carries DATA-GAP; heritage
 *    lineage state is PARTIAL;
 *  - viewport structural smoke at 375 / 768 / 1440 (all sections render in
 *    order, no catastrophic horizontal overflow, no fatal errors);
 *  - dark + 200% zoom no overflow.
 */
import { expect, test } from '@playwright/test'

const SECTION_IDS = [
  'home-hero',
  'home-life',
  'home-book',
  'home-knowledge',
  'home-evidence',
  'home-heritage',
  'home-domains',
  'home-closing',
]

test('UI-03 homepage renders the unique H1 and the accepted eight sections in order', async ({
  page,
}) => {
  await page.goto('/')
  await expect(page.getByRole('heading', { level: 1 })).toHaveCount(1)
  await expect(page.getByRole('heading', { name: '皇甫谧人文数字平台' })).toBeVisible()

  const sections = page.locator('#main-content section[id^="home-"], main section[id^="home-"]')
  await expect(sections).toHaveCount(8)
  const ids = await sections.evaluateAll((els) => els.map((el) => el.id))
  expect(ids).toEqual(SECTION_IDS)

  // Section H2 set follows the accepted chapter headlines.
  for (const name of [
    '从带经而农，到著书传世。',
    '一部书，成为历史中的物。',
    '从古籍文字，到可探索的知识。',
    '每一个结论，都回到它的出处。',
    '一千七百年之后，传承仍在继续。',
    '四域探索',
  ]) {
    await expect(page.getByRole('heading', { name, exact: true })).toBeVisible()
  }
})

test('UI-03 exactly one global footer — Section 08 is a closing section, not a second footer', async ({
  page,
}) => {
  await page.goto('/')
  await expect(page.locator('footer')).toHaveCount(1)
  // The closing section is a <section> landmarked via aria-label, and it must
  // contain no footer-level content (legal nav / copyright / co-construction).
  const closing = page.locator('#home-closing')
  await expect(closing).toBeVisible()
  expect(await closing.evaluate((el) => el.tagName)).toBe('SECTION')
  await expect(
    closing.locator('footer, nav, [aria-label*="版权"], [aria-label*="隐私"]'),
  ).toHaveCount(0)
  await expect(closing).not.toContainText(/版权与免责声明|隐私说明|仅供皇甫谧学术研究/)
})

test('UI-03 CTA targets are real routes', async ({ page }) => {
  await page.goto('/')
  const targets = [
    '/persons/person-huangfu-mi',
    '/reader/qichuan',
    '/yan',
    '/reader/houlun',
    '/jiayi',
    '/archive',
    '/heritage',
    '/research/search',
  ]
  for (const target of targets) {
    const link = page.locator(`a[href="${target}"]`).first()
    await expect(link, `link to ${target}`).toBeVisible()
    expect(await link.getAttribute('href')).toBe(target)
  }
})

test('UI-03 search submits to /search?q= (real CF-06 transport stubbed here)', async ({ page }) => {
  // Public search is the real /api/v1/public/search endpoint (CF-06); this
  // auxiliary spec stubs the transport so the homepage CTA round-trip is
  // deterministic. Real-chain proof lives in the golden runtime journey.
  await page.route('**/api/v1/public/search*', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        success: true,
        data: {
          hits: [
            {
              kind: 'work',
              id: 'w-jiayi',
              title: '《针灸甲乙经》',
              snippet: '',
              version_id: null,
              publication_status: 'PUBLISHED',
            },
          ],
          total: 1,
          page: 1,
          page_size: 20,
        },
      }),
    }),
  )
  await page.goto('/')
  const input = page.locator('#home-search-input')
  await input.fill('甲乙经')
  await page.locator('#home-hero form.home-search').getByRole('button', { name: '检索' }).click()
  await expect(page).toHaveURL(/\/search\?q=%E7%94%B2%E4%B9%99%E7%BB%8F/)
  await expect(page.getByText(/找到 \d+ 条结果/)).toBeVisible()
})

test('UI-03 刘君奇·第六代名医, PARTIAL lineage and book lineage DATA-GAP are real', async ({
  page,
}) => {
  await page.goto('/')
  const heritage = page.locator('#home-heritage')
  await expect(heritage.getByText('刘君奇').first()).toBeVisible()
  await expect(heritage.getByText('第六代名医').first()).toBeVisible()
  await expect(page.locator('#home-heritage .hfm-status')).toHaveAttribute('data-status', 'PARTIAL')
  // Book lineage caption: the accepted homepage transparency line (unchanged).
  await expect(
    page.locator('#home-book').getByText(/结构化版本关系整理中（DATA-GAP）/),
  ).toBeVisible()
  await expect(page.locator('#home-book').getByText(/版本记录 \d+ 条/)).toBeVisible()
})

test('UI-03 real quotation with attribution (no fabricated slogan)', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByText(/皇甫谧素履幽贞/)).toBeVisible()
  await expect(page.getByText(/房玄龄/)).toBeVisible()
})

test('UI-03 structural smoke: 375 / 768 / 1440 — all sections render in order, no overflow', async ({
  page,
}) => {
  const fatal: string[] = []
  page.on('pageerror', (e) => fatal.push(String(e)))
  page.on('console', (m) => {
    if (m.type() === 'error') fatal.push(m.text())
  })
  for (const width of [375, 768, 1440]) {
    await page.setViewportSize({ width, height: 900 })
    await page.goto('/')
    await page.waitForTimeout(150)
    const sections = page.locator('#main-content section[id^="home-"], main section[id^="home-"]')
    await expect(sections, `eight sections at ${width}`).toHaveCount(8)
    const ids = await sections.evaluateAll((els) => els.map((el) => el.id))
    expect(ids, `section order at ${width}`).toEqual(SECTION_IDS)
    const overflow = await page.evaluate(
      () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
    )
    expect(overflow, `overflow at ${width}`).toBeLessThanOrEqual(0)
    await expect(page.getByRole('heading', { level: 1 })).toBeVisible()
  }
  expect(fatal, 'fatal browser errors during viewport smoke').toHaveLength(0)
})

test('UI-03 responsive: dark theme and 200% zoom do not overflow', async ({ page }) => {
  await page.evaluate(() => document.documentElement.classList.add('dark'))
  await page.goto('/')
  await page.waitForTimeout(150)
  const bodyColor = await page.evaluate(() => getComputedStyle(document.body).backgroundColor)
  expect(bodyColor).not.toBe('rgb(255, 255, 255)')
  // 200% zoom (640px = 1280 at 200%).
  await page.setViewportSize({ width: 640, height: 720 })
  await page.goto('/')
  const zoomOverflow = await page.evaluate(
    () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
  )
  expect(zoomOverflow).toBeLessThanOrEqual(0)
})
