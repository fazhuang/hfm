/**
 * WP-05 Homepage Sections 05–08 — browser E2E.
 *
 * Real-browser verification of the WP-05 fidelity sections:
 *  - the four sections render in the accepted order under the .home root;
 *  - visible provenance captions (evidence witness, heritage figcaption) stay in
 *    the accessibility tree (no aria-hidden on visible content — P1-01 rule);
 *  - Domains offers exactly four threshold CTAs to the four real routes;
 *  - single H1 + exactly one semantic footer (AppFooter via layout) on '/';
 *  - no horizontal overflow at 375 / 768 / 1440 / 1920 for the homepage.
 */
import { expect, test } from '@playwright/test'

test('WP-05 sections 05–08 render in order with the platform single H1', async ({ page }) => {
  await page.goto('/')
  const ids = await page
    .locator('section[id^="home-"]')
    .evaluateAll((els) => els.map((el) => el.id))
  expect(ids).toEqual([
    'home-hero',
    'home-life',
    'home-book',
    'home-knowledge',
    'home-evidence',
    'home-heritage',
    'home-domains',
    'home-closing',
  ])
  await expect(page.getByRole('heading', { level: 1 })).toHaveCount(1)
  await expect(page.getByRole('heading', { level: 1 })).toContainText('皇甫谧人文数字平台')
  // AppFooter is the only semantic footer (PublicLayout renders it after main).
  await expect(page.locator('footer')).toHaveCount(1)
})

test('WP-05 provenance captions stay in the accessibility tree (P1-01 rule)', async ({ page }) => {
  await page.goto('/')
  // Evidence — the authoritative witness quote is visible text, not aria-hidden.
  const witness = page.locator('.home-evidence__wit-text')
  await expect(witness).toBeVisible()
  expect(await witness.getAttribute('aria-hidden')).toBeNull()
  await expect(witness).toContainText('皇甫谧素履幽贞')
  // Heritage — documentary figcaption visible + accessible; photo hidden on img only.
  const fig = page.locator('.home-heritage__act-pic')
  expect(await fig.getAttribute('aria-hidden')).toBeNull()
  expect(await fig.locator('img').getAttribute('aria-hidden')).toBe('true')
  const cap = fig.locator('figcaption')
  await expect(cap).toBeVisible()
  expect(await cap.getAttribute('aria-hidden')).toBeNull()
  await expect(cap).toContainText('2023-09-26')
  // Heritage PARTIAL chip routes the shared mapping label.
  await expect(page.locator('.home-section--heritage .hfm-status')).toHaveText('谱系整理中')
})

test('WP-05 domains: four threshold CTAs to four real routes', async ({ page }) => {
  await page.goto('/')
  const hrefs = await page
    .locator('#home-domains .home-domains__go')
    .evaluateAll((els) => els.map((el) => el.getAttribute('href')))
  expect(hrefs).toEqual(['/persons/person-huangfu-mi', '/archive', '/jiayi', '/heritage'])
  // no removed "NARRATIVE → USABLE ARCHIVE" copy anywhere on the homepage
  await expect(page.locator('#home-domains')).not.toContainText('NARRATIVE')
  await expect(page.locator('#home-domains')).not.toContainText('USABLE ARCHIVE')
})

test('WP-05 closing: quiet identity, no legal duplication', async ({ page }) => {
  await page.goto('/')
  const closing = page.locator('#home-closing')
  await expect(closing.locator('.home-closing__name')).toHaveText('皇甫谧人文数字平台')
  await expect(closing.locator('.home-closing__subtitle')).toContainText('非遗活态传承')
  // no copyright / legal links inside the closing section (AppFooter owns them)
  expect(await closing.locator('a').count()).toBe(0)
  await expect(closing).not.toContainText('©')
})

test('WP-05 responsive: no horizontal overflow at 375/768/1440/1920', async ({ page }) => {
  for (const width of [375, 768, 1440, 1920]) {
    await page.setViewportSize({ width, height: 900 })
    await page.goto('/')
    await page.waitForTimeout(150)
    const overflow = await page.evaluate(
      () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
    )
    expect(overflow, `${width}px`).toBeLessThanOrEqual(0)
  }
})

test('WP-05 mobile repair: four domain CTAs reach the viewport (DOM rect proof)', async ({
  page,
}) => {
  // Mobile repair evidence: no readable content may be clipped by overflow:hidden;
  // each of the four Section 07 CTAs must enter the viewport and be clickable.
  for (const width of [375, 768]) {
    await page.setViewportSize({ width, height: 800 })
    await page.goto('/')
    await page.waitForTimeout(300)
    await page.addStyleTag({ content: 'html { scroll-behavior: auto !important; }' })
    // no horizontal overflow and no internal clipping inside Sections 05–07
    const noClip = await page.evaluate(() => {
      const overflow =
        document.documentElement.scrollWidth - document.documentElement.clientWidth
      const clips = []
      for (const sel of ['#home-evidence', '#home-heritage', '#home-domains']) {
        const sec = document.querySelector(sel)
        const sr = sec.getBoundingClientRect()
        let maxBottom = 0
        sec.querySelectorAll('*').forEach((n) => {
          const r = n.getBoundingClientRect()
          if (r.width > 0 && r.height > 0 && r.bottom > maxBottom) maxBottom = r.bottom - sr.top
        })
        if (maxBottom > sr.height + 1) clips.push(sel)
      }
      return { overflow, clips }
    })
    expect(noClip.overflow, `${width}px doc overflow`).toBeLessThanOrEqual(0)
    expect(noClip.clips, `${width}px internal clipping`).toEqual([])
    // each CTA scrolls into the viewport and intersects it, horizontally contained
    const hrefs = [
      '/persons/person-huangfu-mi',
      '/archive',
      '/jiayi',
      '/heritage',
    ]
    for (let i = 0; i < 4; i += 1) {
      const rect = await page.evaluate(async (idx) => {
        const el = document.querySelectorAll('#home-domains .home-domains__go')[idx]
        el.scrollIntoView({ block: 'center', behavior: 'instant' })
        await new Promise((res) => requestAnimationFrame(() => requestAnimationFrame(res)))
        const b = el.getBoundingClientRect()
        return {
          href: el.getAttribute('href'),
          left: b.left,
          right: b.right,
          top: b.top,
          bottom: b.bottom,
          width: b.width,
          height: b.height,
        }
      }, i)
      expect(rect.href, `${width}px CTA ${i} href`).toBe(hrefs[i])
      expect(rect.width, `${width}px CTA ${i} width`).toBeGreaterThan(0)
      expect(rect.left, `${width}px CTA ${i} left`).toBeGreaterThanOrEqual(0)
      expect(rect.right, `${width}px CTA ${i} right`).toBeLessThanOrEqual(width)
      expect(rect.bottom, `${width}px CTA ${i} bottom`).toBeGreaterThan(0)
      expect(rect.top, `${width}px CTA ${i} top`).toBeLessThan(800)
    }
  }
})
