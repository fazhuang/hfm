/**
 * UX2-G2 prototype verification — runs PT-NB-01..12 + responsive + axe.
 * Playwright is resolved from the frozen frontend toolchain (read-only use).
 */
import { createRequire } from 'module'
import { fileURLToPath } from 'url'
import { dirname, join, resolve } from 'path'
import { readFileSync } from 'fs'

const here = dirname(fileURLToPath(import.meta.url))
const repo = resolve(here, '..', '..')
const require = createRequire(join(repo, 'apps/frontend/package.json'))
const { chromium } = require('@playwright/test')

const PAGES = ['index.html', 'p01-person.html', 'p02-jiayi.html', 'p03-heritage.html', 'p04-discovery.html', 'p05-home.html']
const base = 'file://' + here + '/'

const results = { pages: {}, nb: {}, responsive: {}, axe: {} }
const textAssertions = {
  'PT-NB-01 unsupported historical facts': [
    { bad: /生于\d{4}年|卒于\d{4}年/, pages: PAGES },
  ],
  'PT-NB-02/03/04 no implied lineage': [
    { bad: /继承自|源自.*本|传自|第[一二三四五]代[^\s]*名医(?!·)/, pages: ['index.html', 'p02-jiayi.html', 'p03-heritage.html'] },
  ],
  'PT-NB-05 clinical': [
    { bad: /疗效显著|治疗推荐|适用于.*疾病|预约|问诊|处方指导|穴位推荐/, pages: PAGES },
  ],
  'PT-NB-06 no synthesized citation page/volume': [
    { bad: /卷\d+|页\d+/, pages: ['p04-discovery.html', 'index.html'] },
  ],
  'PT-NB-07 no historical absence from data absence': [
    { bad: /已佚|亡佚/, pages: PAGES },
  ],
  'PT-NB-08 no empty placeholder shell': [
    { bad: /暂无内容|敬请期待|即将上线/, pages: PAGES },
  ],
}

const browser = await chromium.launch()
for (const page of PAGES) {
  const p = await browser.newPage({ viewport: { width: 1280, height: 900 } })
  await p.goto(base + page)
  await p.waitForSelector('[data-primitive="dh-object"], body')
  const text = await p.locator('body').innerText()
  const pageKey = page
  results.pages[pageKey] = { loaded: true }

  for (const [name, spec] of Object.entries(textAssertions)) {
    const hit = spec.flatMap((s) =>
      s.bad.test(text) ? [`${pageKey}: ${name}`] : [],
    )
    results.nb[name] = results.nb[name] || []
    if (hit.length) results.nb[name].push(...hit)
  }

  // responsive: no horizontal scroll at 375 / 1920
  for (const width of [375, 1920]) {
    await p.setViewportSize({ width, height: 900 })
    await p.waitForTimeout(60)
    const overflow = await p.evaluate(
      () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
    )
    results.responsive[`${pageKey}@${width}`] = overflow
  }
  await p.close()
}

// slot-presence assertions on the primitive page
{
  const p = await browser.newPage({ viewport: { width: 1280, height: 900 } })
  await p.goto(base + 'index.html')
  await p.waitForSelector('[data-primitive="dh-object"]')
  const slots = await p.$$eval('[data-slot]', (els) => els.map((e) => e.getAttribute('data-slot-state')))
  const absent = await p.locator('.dh-object[data-primitive="dh-object"]').count()
  const bibCount = await p.$$eval('[data-primitive="bib-record"]', (els) => els.length)
  results.pages.primitives = { slotStates: slots, dhObjects: absent, bibRecords: bibCount }
  // PT-NB-02: index relations carry explicit semantics only
  const semLabels = await p.$$eval('.relation-item .sem', (els) => els.map((e) => e.textContent))
  results.nb['PT-NB-02 relation semantics explicit'] = semLabels.every((s) =>
    ['EXPLICIT_RELATION', 'ASSOCIATED_CONTEXT', 'CO_PRESENTED_ONLY'].includes(s.trim()),
  )
    ? []
    : semLabels
  await p.close()
}

// axe on EVERY prototype page (corrective-pass requirement: G2 F-1 regression
// check must prove 0 heading-order / a11y violations across all 6 surfaces,
// not only the hub page).
for (const page of PAGES) {
  const p = await browser.newPage({ viewport: { width: 1280, height: 900 } })
  await p.goto(base + page)
  await p.waitForSelector('body')
  const axePath = join(repo, 'apps/frontend/node_modules/axe-core/axe.min.js')
  await p.addScriptTag({ path: axePath })
  const v = await p.evaluate(async () => {
    const r = await window.axe.run(document)
    return { violations: r.violations.map((x) => x.id) }
  })
  results.axe[page] = v
  await p.close()
}
await browser.close()

console.log(JSON.stringify(results, null, 1))
