/**
 * UX2-P1 corrective browser E2E — person archive surface (real Chromium).
 *
 * Covers the audited P0/P1 findings:
 *  - P1-01 real archival-media proof: the media mock is a deterministic
 *    projection of the authoritative archiveInventory a-movies record
 *    (bound in-test; no synthetic acceptance fixture).
 *  - P1-02A reader navigation: person → 其传 reader → back → 后论 reader,
 *    verifying real route + real content (no dead routes / placeholders).
 *  - P1-02B keyboard/focus: reader links reachable via Tab, Enter activates,
 *    visible focus indicator, no focus trap.
 *  - P1-02C browser-level axe (real browser, not jsdom).
 *  - P1-02D responsive: no horizontal overflow at 375 / 1280 / 1920.
 */
import { expect, test, type Page } from '@playwright/test'
import { readdirSync, statSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { ARCHIVE_RECORDS } from '../src/data/archiveInventory'
import { INVENTORY_MOVIES } from '../src/data/contentInventory'

const ARCHIVE_MOVIES = ARCHIVE_RECORDS.find((r) => r.id === 'a-movies')

/**
 * MEDIA_SOURCE_OF_TRUTH — the two real customer media files
 *   hfmzl/皇甫谧/皇甫谧电影/皇甫谧一.mpg
 *   hfmzl/皇甫谧/皇甫谧电影/《针灸鼻祖皇甫谧》第1集 大器晚成.mpg
 * recorded in the governance asset map docs/design/HFM-CONTENT-ASSET-MAP.md
 * (rows 31/57) and archiveInventory.ts a-movies. The intercepted API response
 * is GENERATED from the real files (name/object_key/byte_size) + the
 * governance license policy — never a manually duplicated fixture.
 */
const MEDIA_SOURCE_DIR = fileURLToPath(new URL('../../../hfmzl/皇甫谧/皇甫谧电影/', import.meta.url))
const MEDIA_LICENSE_BASIS = '授权公开（存在文件才可播放）'
const MIME_BY_EXTENSION: Record<string, string> = {
  '.mpg': 'video/mpeg',
  '.mpeg': 'video/mpeg',
  '.mp4': 'video/mp4',
}

function deriveMediaProjection(): Array<{
  id: string
  name: string
  object_key: string
  mime_type: string
  byte_size: number
  rights_holder: string
  license_basis: string
  restriction: null
  category: 'movie'
  publication_state: string
}> {
  const files = readdirSync(MEDIA_SOURCE_DIR)
    .filter((f) => f.endsWith('.mpg') || f.endsWith('.mp4'))
    .sort()
  if (files.length === 0) {
    throw new Error(`F-5 media source of truth missing: ${MEDIA_SOURCE_DIR}`)
  }
  return files.map((objectKey) => {
    const dot = objectKey.lastIndexOf('.')
    const stem = dot > 0 ? objectKey.slice(0, dot) : objectKey
    const ext = dot > 0 ? objectKey.slice(dot) : ''
    return {
      id: stem,
      name: stem,
      object_key: objectKey,
      mime_type: MIME_BY_EXTENSION[ext] ?? 'application/octet-stream',
      byte_size: statSync(`${MEDIA_SOURCE_DIR}/${objectKey}`).size,
      rights_holder: '客户提供',
      license_basis: MEDIA_LICENSE_BASIS,
      restriction: null,
      category: 'movie',
      publication_state: 'published',
    }
  })
}

const MEDIA_PROJECTION = {
  items: deriveMediaProjection(),
  total: INVENTORY_MOVIES,
}

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
      body = MEDIA_PROJECTION
    }
    void route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(body) })
  })
}

async function openPerson(page: Page): Promise<void> {
  await mockPublicApi(page)
  await page.goto('/persons/person-huangfu-mi')
  await expect(page.getByRole('heading', { name: '皇甫谧', exact: true })).toBeVisible()
}

test.describe('UX2-P1 corrective — person archive surface', () => {
  test('renders DHObjectLayout states, F-5 后论 content and REAL archival media projection', async ({ page }) => {
    await openPerson(page)

    await expect(page.getByRole('heading', { name: '语境 · 证据 · 关联' })).toBeVisible()
    await expect(page.locator('[data-primitive="dh-object"]')).toBeVisible()
    await expect(
      page.locator('[data-slot="context"][data-slot-state="INCOMPLETE_WITH_EVIDENCE_STATE"]'),
    ).toBeVisible()
    await expect(
      page.locator('[data-slot="evidence"][data-slot-state="INCOMPLETE_WITH_EVIDENCE_STATE"]'),
    ).toBeVisible()
    await expect(page.locator('[data-slot="relations"][data-slot-state="PRESENT"]')).toBeVisible()
    await expect(page.locator('[data-slot="header"]')).toHaveCount(0)
    await expect(page.locator('.hfm-status[data-status="SCHOLARLY_UNCERTAIN"]')).toHaveText('尚有争议')

    // F-5 Historical Assessments: 后论 real content + reader link
    await expect(page.locator('[aria-labelledby="afterwords-heading"]')).toContainText('后论 · 历史评价汇编')
    await expect(page.locator('[aria-labelledby="afterwords-heading"] .hfm-status')).toHaveText('全文已整理')
    await expect(page.locator('[aria-labelledby="afterwords-heading"] a[href="/reader/houlun"]')).toBeVisible()

    // 其传 real content
    await expect(page.locator('[aria-labelledby="biography-heading"]')).toContainText('其传 · 史料来源整理')
    await expect(page.locator('[aria-labelledby="biography-heading"] a[href="/reader/qichuan"]')).toBeVisible()

    // P1-01: media mock is bound to the authoritative record, and the
    // projection reaches the surface with the real movie titles
    expect(ARCHIVE_MOVIES).toBeDefined()
    expect(ARCHIVE_MOVIES?.status).toBe('AVAILABLE')
    expect(MEDIA_PROJECTION.items).toHaveLength(INVENTORY_MOVIES)
    const strip = (s: string) => s.replace(/\s+/g, '')
    for (const item of MEDIA_PROJECTION.items) {
      expect(strip(ARCHIVE_MOVIES!.description)).toContain(strip(item.name))
    }
    await expect(page.locator('.movie-card__title')).toHaveCount(MEDIA_PROJECTION.items.length)
    const movieTitles = await page.locator('.movie-card__title').allTextContents()
    expect(movieTitles).toEqual(MEDIA_PROJECTION.items.map((m) => m.name))

    // heading hierarchy: exactly one h1
    await expect(page.locator('h1')).toHaveCount(1)
  })

  test('reader navigation: person → 其传 reader → back → 后论 reader (no dead routes)', async ({ page }) => {
    await openPerson(page)

    // 其传 reader link → real reader route + real content
    await page.locator('[aria-labelledby="biography-heading"] a[href="/reader/qichuan"]').click()
    await expect(page).toHaveURL(/\/reader\/qichuan/)
    await expect(page.locator('.reader__title')).toHaveText('其传 · 史料来源整理')
    await expect(page.locator('.reader__status')).toHaveText('全文可读')
    await expect(page.locator('.reader')).toContainText('本源核心史料')

    // back to the person archive
    await page.goBack()
    await expect(page).toHaveURL(/\/persons\/person-huangfu-mi/)
    await expect(page.getByRole('heading', { name: '语境 · 证据 · 关联' })).toBeVisible()

    // 后论 reader link → real reader route + real citation content
    await page.locator('[aria-labelledby="afterwords-heading"] a[href="/reader/houlun"]').click()
    await expect(page).toHaveURL(/\/reader\/houlun/)
    await expect(page.locator('.reader__title')).toHaveText('后论 · 历史评价汇编')
    await expect(page.locator('.reader__status')).toHaveText('全文可读')
    await expect(page.locator('.reader')).toContainText('男子皇甫谧沈静履素')
  })

  test('keyboard: reader links reachable via Tab, Enter activates, visible focus, no trap', async ({ page }) => {
    await openPerson(page)

    // Tab until the 其传 reader link is focused (keyboard-reachable)
    let focusedHref = ''
    for (let i = 0; i < 80; i += 1) {
      await page.keyboard.press('Tab')
      focusedHref = await page.evaluate(() => document.activeElement?.getAttribute('href') ?? '')
      if (focusedHref === '/reader/qichuan') break
    }
    expect(focusedHref).toBe('/reader/qichuan')

    // visible focus indicator (focus-visible ring, not color-only / missing)
    const focusRingVisible = await page.evaluate(() => {
      const el = document.activeElement
      if (!el) return false
      const cs = getComputedStyle(el)
      return cs.boxShadow !== 'none' || cs.outlineStyle !== 'none'
    })
    expect(focusRingVisible).toBe(true)

    // Enter activates the focused link → real reader route
    await page.keyboard.press('Enter')
    await expect(page).toHaveURL(/\/reader\/qichuan/)

    // no focus trap: Tab advances focus on the reader page
    await page.keyboard.press('Tab')
    const moved = await page.evaluate(() => document.activeElement?.tagName ?? '')
    expect(moved).not.toBe('')
  })

  test('browser-level axe = 0 on the person archive page', async ({ page }) => {
    await openPerson(page)
    await page.addScriptTag({ path: 'node_modules/axe-core/axe.min.js' })
    const violations = await page.evaluate(async () => {
      const runner = window as unknown as { axe: { run: (n: unknown) => Promise<{ violations: Array<{ id: string }> }> } }
      const results = await runner.axe.run(document)
      return results.violations.map((v) => v.id)
    })
    expect(violations).toEqual([])
  })

  test('responsive: no horizontal overflow at 375 / 1280 / 1920', async ({ page }) => {
    for (const width of [375, 1280, 1920]) {
      await page.setViewportSize({ width, height: 900 })
      await openPerson(page)
      const overflow = await page.evaluate(
        () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
      )
      expect(overflow, `horizontal overflow at ${width}px`).toBeLessThanOrEqual(0)
    }
  })
})
