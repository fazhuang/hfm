/**
 * UX2-P2 Jiayi Work / Edition — BibliographicRecord + G1-C states tests.
 *
 * Covers the UX2-P2 contract: 19 edition records render via the shared
 * BibliographicRecord primitive with 存目 (METADATA_ONLY per U-05); edition
 * metadata renders from the audited register; DATA-GAP state (版本关系整理中)
 * and chronology ≠ lineage captions intact; NB-03 no genealogy inference;
 * U-05 no digitization flags; heading hierarchy + axe.
 */
import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import axe from 'axe-core'
import JiayiView from '../views/jiayi/JiayiView.vue'
import { JIAYI_ANCIENT_EDITIONS, JIAYI_MODERN_EDITIONS } from '../data/jiayiView'

function mountView(attach = false): ReturnType<typeof mount> {
  return mount(JiayiView, {
    attachTo: attach ? document.body : undefined,
    global: { stubs: { RouterView: { template: '<p />' } } },
  })
}

const TOTAL_EDITIONS = JIAYI_ANCIENT_EDITIONS.length + JIAYI_MODERN_EDITIONS.length

describe('UX2-P2 — edition records via BibliographicRecord', () => {
  it('renders all 19 editions as BibliographicRecord primitives (存目 / METADATA_ONLY)', () => {
    const wrapper = mountView()
    expect(TOTAL_EDITIONS).toBe(19)
    expect(wrapper.findAll('.edition-card')).toHaveLength(TOTAL_EDITIONS)
    const records = wrapper.findAll('[data-primitive="bib-record"]')
    expect(records).toHaveLength(TOTAL_EDITIONS)
    const badges = wrapper.findAll('.edition-card .hfm-status[data-status="METADATA_ONLY"]')
    expect(badges).toHaveLength(TOTAL_EDITIONS)
    for (const badge of badges) {
      expect(badge.text()).toBe('存目')
    }
  })

  it('renders edition metadata from the audited register (period/imprint/type/source)', () => {
    const wrapper = mountView()
    const firstAncient = wrapper.find('.edition-card [data-primitive="bib-record"]')
    const meta = firstAncient.findAll('.bib-record__meta dd').map((n) => n.text())
    expect(meta).toContain('明万历 29 年（1601）') // period
    expect(meta).toContain('吴勉学刊') // imprint
    expect(meta).toContain('古代版本') // type
    expect(meta.some((m) => m.includes('客户提供《针灸甲乙经》论著资料'))).toBe(true) // public source
    expect(firstAncient.find('.bib-record__title').text()).toContain('医统正脉全书本')
  })

  it('modern group renders 近现代整理 type with 存目', () => {
    const wrapper = mountView()
    const groups = wrapper.findAll('.edition-group-title')
    expect(groups[0]?.text()).toBe('古代版本')
    expect(groups[1]?.text()).toBe('近现代整理版本')
    const modernMeta = wrapper
      .findAll('.edition-card [data-primitive="bib-record"]')
      .slice(JIAYI_ANCIENT_EDITIONS.length)
    expect(modernMeta.length).toBe(JIAYI_MODERN_EDITIONS.length)
    expect(modernMeta[0].text()).toContain('近现代整理')
    expect(modernMeta[0].find('.hfm-status').text()).toBe('存目')
  })
})

describe('UX2-P2 — negative boundaries', () => {
  it('U-05: no digitized-resource flag / no fake 阅读 CTA on editions', () => {
    const wrapper = mountView()
    const editionText = wrapper
      .findAll('.edition-card [data-primitive="bib-record"]')
      .map((r) => r.text())
      .join(' ')
    expect(editionText).not.toContain('阅读全文')
    expect(editionText).not.toContain('可阅读')
    expect(editionText).not.toContain('数字资源可阅')
  })

  it('NB-03: no edition genealogy inference', () => {
    const wrapper = mountView()
    const text = wrapper.text()
    expect(text).not.toMatch(/继承自/)
    expect(text).not.toMatch(/源自.*本/)
    expect(text).not.toMatch(/传自/)
  })

  it('NB-06: no synthesized page/volume citations', () => {
    const wrapper = mountView()
    const text = wrapper.text()
    expect(text).not.toMatch(/第\s*\d+\s*页/)
    expect(text).not.toMatch(/第\s*\d+\s*卷/)
  })

  it('NB-05: no clinical content', () => {
    const wrapper = mountView()
    expect(wrapper.text()).not.toContain('疗效')
    expect(wrapper.text()).not.toContain('治疗推荐')
  })
})

describe('UX2-P2 — presentation states & captions', () => {
  it('DATA-GAP state renders 版本关系整理中 (UNSTRUCTURED_OR_INCOMPLETE)', () => {
    const wrapper = mountView()
    const badge = wrapper.find('.lineage-state .hfm-status')
    expect(badge.exists()).toBe(true)
    expect(badge.attributes('data-status')).toBe('UNSTRUCTURED_OR_INCOMPLETE')
    expect(badge.text()).toBe('版本关系整理中')
    expect(wrapper.text()).toContain('DATA-GAP')
  })

  it('chronology ≠ lineage caption intact (year-sorted timeline, no edges)', () => {
    const wrapper = mountView()
    expect(wrapper.find('#edition-timeline').text()).toContain('chronology ≠ lineage')
    const dates = wrapper
      .findAll('.timeline__date')
      .map((d) => Number(d.text()))
      .filter((n) => !Number.isNaN(n))
    const sorted = [...dates].sort((a, b) => a - b)
    expect(dates.length).toBeGreaterThan(0)
    expect(dates).toEqual(sorted)
  })
})

describe('UX2-P2 — structure & accessibility', () => {
  it('heading hierarchy: exactly one h1, no level skips', () => {
    const wrapper = mountView()
    const headings = wrapper.findAll('h1, h2, h3').map((h) => Number(h.element.tagName.slice(1)))
    expect(headings.filter((l) => l === 1)).toHaveLength(1)
    for (let i = 1; i < headings.length; i += 1) {
      expect(headings[i] - headings[i - 1]).toBeLessThanOrEqual(1)
    }
  })

  it('passes axe assertions on the jiayi page', async () => {
    const wrapper = mountView(true)
    const results = await axe.run(wrapper.element as HTMLElement)
    expect(results.violations).toHaveLength(0)
  })
})
