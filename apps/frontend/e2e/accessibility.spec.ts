/**
 * CF-10 — Cross-surface browser accessibility audit (REAL Chromium + axe-core).
 *
 * Mandatory browser-level accessibility execution (CF-10 §4/§28/§29):
 *   real rendered routes in real Chromium, axe-core from node_modules.
 *
 * WR00-B2-E2E-R1 data isolation: the two data-flow surfaces (PERSON, SEARCH)
 * receive a deterministic test-owned data contract at the network boundary
 * (see data-fixtures.ts) so the audit never depends on pre-existing business
 * data in the runtime database and never writes to it. Structural surfaces
 * (HOME / JIAYI / HERITAGE / RESEARCH_GUARD) keep their real rendered routes.
 *
 * Matrix: HOME / PERSON / JIAYI / HERITAGE / SEARCH / RESEARCH_GUARD × 375 / 1440.
 * Blocking = axe 'critical' + 'serious'. Moderate/minor are surfaced, non-blocking.
 */
import { expect, test, type Page } from '@playwright/test'
import { mkdirSync } from 'node:fs'
import { resolve } from 'node:path'

import { stubPublicPerson, stubPublicSearch } from './data-fixtures'

const AXE_PATH = resolve(process.cwd(), 'node_modules/axe-core/axe.min.js')
const EVIDENCE_DIR = resolve(process.cwd(), '../../docs/audit/evidence/cf10')

const SURFACES = ['HOME', 'PERSON', 'JIAYI', 'HERITAGE', 'SEARCH', 'RESEARCH_GUARD'] as const
const VIEWPORTS = [375, 1440] as const

interface AxeNode {
  impact: string
  id: string
  help: string
  nodes: number
}

type AxeViolation = Omit<AxeNode, 'impact' | 'nodes'> & {
  impact: string
  nodes: Array<{ target: string[]; html: string }>
}

interface SurfaceResult {
  surface: string
  viewport: number
  critical: string[]
  serious: string[]
  moderate: string[]
  minor: string[]
  overflow: number
  broken: boolean
}

async function runAxe(page: Page): Promise<AxeViolation[]> {
  await page.addScriptTag({ path: AXE_PATH })
  return page.evaluate(async () => {
    const axe = (
      window as unknown as { axe?: { run: () => Promise<{ violations: AxeViolation[] }> } }
    ).axe
    if (!axe) throw new Error('axe-core not injected')
    const res = await axe.run()
    return res.violations
  })
}

function ids(v: AxeViolation[], impact: string): string[] {
  return v.filter((x) => x.impact === impact).map((x) => x.id)
}

async function gotoSurface(page: Page, surface: string, viewport: number): Promise<void> {
  await page.setViewportSize({ width: viewport, height: 900 })
  switch (surface) {
    case 'HOME':
      await page.goto('/')
      break
    case 'PERSON':
      await page.goto('/persons/ENT-PERSON-HFM-HUANGFUMI')
      // Deterministic readiness: the fixture person page must render its title
      // before the audit runs (replaces a networkidle dependency).
      await expect(page.locator('h1').first()).toBeVisible()
      break
    case 'JIAYI':
      await page.goto('/jiayi')
      break
    case 'HERITAGE':
      await page.goto('/heritage')
      break
    case 'SEARCH': {
      await page.goto('/search')
      const input = page.locator('input[type="search"], input[type="text"], form input').first()
      await input.fill('皇甫谧')
      await page.keyboard.press('Enter')
      await expect(page.locator('.result-list, ol.result-list')).toBeVisible()
      break
    }
    case 'RESEARCH_GUARD': {
      const resp = await page.goto('/research')
      expect(resp?.status()).toBe(200)
      await page.waitForURL(/\/login/)
      await expect(page.locator('#main-content, main')).toBeVisible()
      break
    }
  }
  // WR00-B2-E2E-R1: deterministic settle instead of waitForLoadState
  // 'networkidle', which stalls under a loaded parallel dev server (the
  // matrix previously hit its own timeout waiting for the network to idle).
  await page.waitForLoadState('load')
  await page.waitForTimeout(250)
}

test('CF-10 browser accessibility matrix (axe-core, real runtime, 375 + 1440)', async ({
  page,
}) => {
  test.setTimeout(300000)
  // Data-flow surfaces get deterministic test-owned data (person + search
  // fixtures); structural surfaces keep their real rendered routes.
  stubPublicPerson(page)
  stubPublicSearch(page)
  const results: SurfaceResult[] = []
  for (const surface of SURFACES) {
    for (const viewport of VIEWPORTS) {
      await gotoSurface(page, surface, viewport)
      const violations = await runAxe(page)
      const critical = ids(violations, 'critical')
      const serious = ids(violations, 'serious')
      const moderate = ids(violations, 'moderate')
      const minor = ids(violations, 'minor')
      const overflow = await page.evaluate(
        () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
      )
      mkdirSync(EVIDENCE_DIR, { recursive: true })
      await page.screenshot({ path: `${EVIDENCE_DIR}/${surface.toLowerCase()}-${viewport}.png` })
      const broken = critical.length > 0 || serious.length > 0 || overflow > 0
      results.push({ surface, viewport, critical, serious, moderate, minor, overflow, broken })
      if (broken) {
        const contrastNodes = violations
          .filter((v) => v.id === 'color-contrast')
          .flatMap((v) => v.nodes)
          .slice(0, 6)
          .map((n) => `[${n.target.join(' ')}] ${n.html.replace(/\s+/g, ' ').slice(0, 140)}`)
        console.log(
          `CF10_FINDING ${surface}@${viewport} crit=${critical.join(',')} ser=${serious.join(',')} overflow=${overflow}\n` +
            contrastNodes.join('\n'),
        )
      }
      if (moderate.length > 0) {
        const modNodes = violations
          .filter((v) => moderate.includes(v.id))
          .flatMap((v) => v.nodes)
          .slice(0, 4)
          .map((n) => `[${n.target.join(' ')}] ${n.html.replace(/\s+/g, ' ').slice(0, 120)}`)
        console.log(
          `CF10_MODERATE ${surface}@${viewport} rule=${moderate.join(',')}\n  ${modNodes.join('\n  ')}`,
        )
      }
    }
  }
  const blocking = results.filter((r) => r.broken)
  expect(
    blocking,
    `blocking axe/overflow findings:\n${JSON.stringify(blocking, null, 2)}`,
  ).toHaveLength(0)
  for (const r of results) {
    console.log(
      `CF10_MATRIX ${r.surface}@${r.viewport} crit=${r.critical.length} ser=${r.serious.length} ` +
        `mod=${r.moderate.length} min=${r.minor.length} overflow=${r.overflow}`,
    )
  }
})
