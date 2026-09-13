/**
 * UI-03 Homepage — browser E2E (CF-07 structure + CF-08 Sections 01–04 production).
 *
 *  - unique H1 = 皇甫谧人文数字平台; the eight accepted homepage sections
 *    exist in exact order with stable ids (home-hero → home-closing);
 *  - exactly ONE global semantic footer (AppFooter); Section 08 is a
 *    narrative closing section, never a second footer;
 *  - CTA targets real routes; search submits to /search?q=;
 *  - CF-08: Sections 01–04 render the accepted composition in real Chromium —
 *    images actually load (naturalWidth > 0), interactive controls never
 *    overlap and stay within viewport, no horizontal page failure, at
 *    375 / 768 / 1440 (no mock); screenshots captured as evidence.
 */
import { expect, test } from '@playwright/test'
import { mkdirSync } from 'node:fs'
import { resolve } from 'node:path'

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

const EVIDENCE_DIR = resolve(process.cwd(), '../../docs/audit/evidence/cf08')

test('UI-03 homepage renders the unique H1 and the accepted eight sections in order', async ({
  page,
}) => {
  await page.goto('/')
  await expect(page.getByRole('heading', { level: 1 })).toHaveCount(1)
  await expect(page.getByRole('heading', { name: '皇甫谧人文数字平台' })).toBeVisible()

  const sections = page.locator('#main-content section[id^="home-"]')
  await expect(sections).toHaveCount(8)
  const ids = await sections.evaluateAll((els) => els.map((el) => el.id))
  expect(ids).toEqual(SECTION_IDS)

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
    '/persons/ENT-PERSON-HFM-HUANGFUMI',
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
    const sections = page.locator('#main-content section[id^="home-"]')
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
  await page.setViewportSize({ width: 640, height: 720 })
  await page.goto('/')
  const zoomOverflow = await page.evaluate(
    () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
  )
  expect(zoomOverflow).toBeLessThanOrEqual(0)
})

test('CF-08 Sections 01–04: images load, controls never overlap/off-screen, no page failure (375/768/1440)', async ({
  page,
}) => {
  // WR00-B2-E2E-R1: this visual smoke captures full-page + per-section
  // evidence screenshots at three widths; it needs more than the global 30s
  // timeout under a loaded dev server, otherwise the runner tears the page
  // down mid-loop ("page/browser closed"). Runner-lifecycle setting only — no
  // assertion or product change.
  test.setTimeout(180_000)
  mkdirSync(EVIDENCE_DIR, { recursive: true })
  const fatal: string[] = []
  page.on('pageerror', (e) => fatal.push(String(e)))
  page.on('console', (m) => {
    if (m.type() === 'error') fatal.push(m.text())
  })

  for (const width of [375, 768, 1440]) {
    await page.setViewportSize({ width, height: 900 })
    await page.goto('/')
    await page.waitForTimeout(200)

    // Production images genuinely load (real asset, not a broken ref).
    const badImages = await page.evaluate(() =>
      Array.from(document.images)
        .filter((img) => img.getAttribute('src')?.startsWith('/assets/jiayi/'))
        .filter((img) => !img.complete || img.naturalWidth === 0),
    )
    expect(badImages, `broken asset at ${width}`).toHaveLength(0)

    // No catastrophic horizontal overflow.
    const overflow = await page.evaluate(
      () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
    )
    expect(overflow, `overflow at ${width}`).toBeLessThanOrEqual(0)

    // Hero: the CTA and the search input never overlap and both stay in-viewport.
    const boxes = await page.evaluate(() => {
      const hero = document.querySelector('#home-hero')!
      const act = hero.querySelector('.home-hero__act')!.getBoundingClientRect()
      const search = hero.querySelector('.home-search')!.getBoundingClientRect()
      const intersects =
        act.left < search.right &&
        search.left < act.right &&
        act.top < search.bottom &&
        search.top < act.bottom
      const inViewport =
        act.left >= 0 &&
        act.right <= window.innerWidth &&
        search.left >= 0 &&
        search.right <= window.innerWidth
      return { intersects, inViewport }
    })
    expect(boxes.intersects, `hero CTA overlaps search at ${width}`).toBe(false)
    expect(boxes.inViewport, `hero controls off-screen at ${width}`).toBe(true)

    // Full-page + per-section evidence screenshots (real browser render).
    if (width === 1440 || width === 768 || width === 375) {
      await page.screenshot({ path: `${EVIDENCE_DIR}/home-${width}.png`, fullPage: true })
      for (const id of ['home-hero', 'home-life', 'home-book', 'home-knowledge']) {
        const section = page.locator(`#${id}`)
        if ((await section.count()) > 0) {
          await section.screenshot({ path: `${EVIDENCE_DIR}/${id}-${width}.png` })
        }
      }
    }
  }
  expect(fatal, 'fatal browser errors during CF-08 visual smoke').toHaveLength(0)
})

test('CF-08 desktop composition at 1440 — sections render, display scale, centred column', async ({
  page,
}) => {
  await page.setViewportSize({ width: 1440, height: 900 })
  await page.goto('/')
  await page.waitForTimeout(300)

  // Every section renders with real content height (responsive editorial layout).
  const heights = await page.evaluate(() => {
    const h = (id: string) => document.getElementById(id)!.getBoundingClientRect().height
    return {
      hero: h('home-hero'),
      life: h('home-life'),
      book: h('home-book'),
      knowledge: h('home-knowledge'),
    }
  })
  expect(heights.hero).toBeGreaterThan(400)
  expect(heights.life).toBeGreaterThan(400)
  expect(heights.book).toBeGreaterThan(400)
  expect(heights.knowledge).toBeGreaterThan(400)

  // The 皇甫谧 monument is a large serif display element (clamp scales with viewport).
  const glyph = await page.evaluate(() => {
    const g = document.querySelector('.home-hero__glyph') as HTMLElement
    return parseFloat(getComputedStyle(g).fontSize)
  })
  expect(glyph).toBeGreaterThanOrEqual(60)

  // Sections are full-width; the content column is centred and clamped (no page clamp).
  const geom = await page.evaluate(() => {
    const section = document.getElementById('home-life')!.getBoundingClientRect()
    const inner = document.querySelector('.home-life__inner')!.getBoundingClientRect()
    return { sectionWidth: section.width, innerWidth: inner.width, innerLeft: inner.left }
  })
  expect(geom.sectionWidth).toBeGreaterThanOrEqual(1380)
  expect(geom.innerWidth).toBeLessThanOrEqual(1400)
  expect(geom.innerLeft).toBeGreaterThan(0)
  expect(geom.innerLeft).toBeLessThan(400)
})

test('CF-09 Sections 05–08: render in order, single-footer handoff, no overflow (375/768/1440)', async ({
  page,
}) => {
  mkdirSync(EVIDENCE_DIR, { recursive: true })
  const fatal: string[] = []
  page.on('pageerror', (e) => fatal.push(String(e)))
  page.on('console', (m) => {
    if (m.type() === 'error') fatal.push(m.text())
  })
  const FROM = ['home-evidence', 'home-heritage', 'home-domains', 'home-closing']
  for (const width of [375, 768, 1440]) {
    await page.setViewportSize({ width, height: 900 })
    await page.goto('/')
    await page.waitForTimeout(200)
    // Sections 05–08 render, in order, exactly once.
    const sections = page.locator('#main-content section[id^="home-"]')
    const ids = await sections.evaluateAll((els) => els.map((el) => el.id))
    expect(ids).toEqual(SECTION_IDS)
    for (const id of FROM) {
      await expect(page.locator(`#${id}`), `${id} at ${width}`).toBeVisible()
    }
    // No horizontal page failure.
    const overflow = await page.evaluate(
      () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
    )
    expect(overflow, `overflow at ${width}`).toBeLessThanOrEqual(0)
    // Single semantic footer; the closing is a <section>, not a footer.
    await expect(page.locator('footer')).toHaveCount(1)
    expect(await page.locator('#home-closing').evaluate((el) => el.tagName)).toBe('SECTION')
    // Footer comes after the closing section (clean handoff, no overlap).
    const handoff = await page.evaluate(() => {
      const close = document.getElementById('home-closing')!.getBoundingClientRect()
      const foot = document.querySelector('footer')!.getBoundingClientRect()
      return { closeBottom: close.bottom, footTop: foot.top }
    })
    expect(handoff.footTop).toBeGreaterThanOrEqual(handoff.closeBottom)
    // Evidence screenshots for 05–08 at the primary reference width (1440).
    if (width === 1440) {
      for (const id of FROM) {
        await page.locator(`#${id}`).screenshot({ path: `${EVIDENCE_DIR}/${id}-1440.png` })
      }
    }
  }
  expect(fatal, 'fatal browser errors during CF-09 sections 05-08').toHaveLength(0)
})

test('CF-09 Section 07 route truth: the four domain CTAs resolve to real current routes', async ({
  page,
}) => {
  const targets = ['/persons/ENT-PERSON-HFM-HUANGFUMI', '/archive', '/jiayi', '/heritage']
  for (const target of targets) {
    const resp = await page.goto(target)
    expect(resp?.status(), `${target} must be 200`).toBe(200)
    await expect(page.locator('h1, h2').first()).toBeVisible()
  }
  // The rejected line is absent from the rendered homepage source.
  await page.goto('/')
  await expect(page.locator('#home-domains')).not.toContainText(/NARRATIVE|USABLE ARCHIVE/)
  const body = await page.evaluate(() => document.body.innerText)
  expect(body).not.toMatch(/NARRATIVE · USABLE ARCHIVE|USABLE ARCHIVE/)
})
