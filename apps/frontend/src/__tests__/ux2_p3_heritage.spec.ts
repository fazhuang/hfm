/**
 * UX2-P3 Heritage Living Archive — two-context separation + P0 state tests.
 *
 * Covers the UX2-P3 contract: HISTORICAL_TEXTUAL_CONTEXT vs
 * CONTEMPORARY_LIVING_ARCHIVE_CONTEXT explicit separation; recognition as
 * secondary metadata (8/8); PARTIAL lineage preserved with truthful
 * UNSTRUCTURED_OR_INCOMPLETE state; 第六代名医 designation exact; NB-04 no
 * uninterrupted lineage; NB-05 no clinical content; heading hierarchy + axe.
 */
import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import axe from 'axe-core'
import HeritageView from '../views/heritage/HeritageView.vue'
import { HERITAGE_RECOGNITIONS, HERITAGE_LINEAGE, HERITAGE_PERSON } from '../data/heritageView'

function mountView(attach = false): ReturnType<typeof mount> {
  return mount(HeritageView, {
    attachTo: attach ? document.body : undefined,
    global: { stubs: { RouterView: { template: '<p />' } } },
  })
}

describe('UX2-P3 — two explicit evidence contexts', () => {
  it('renders HISTORICAL_TEXTUAL_CONTEXT and CONTEMPORARY_LIVING_ARCHIVE_CONTEXT bands', () => {
    const wrapper = mountView()
    const historical = wrapper.find('[aria-labelledby="historical-context-heading"]')
    const contemporary = wrapper.find('[aria-labelledby="contemporary-context-heading"]')
    expect(historical.exists()).toBe(true)
    expect(contemporary.exists()).toBe(true)
    expect(historical.find('h2').text()).toContain('HISTORICAL_TEXTUAL_CONTEXT')
    expect(contemporary.find('h2').text()).toContain('CONTEMPORARY_LIVING_ARCHIVE_CONTEXT')
    // historical band carries the lineage; contemporary carries the living archive
    expect(historical.find('[aria-labelledby="lineage-heading"]').exists()).toBe(true)
    expect(contemporary.find('[aria-labelledby="recognition-heading"]').exists()).toBe(true)
    expect(contemporary.find('[aria-labelledby="apprenticeship-heading"]').exists()).toBe(true)
  })

  it('the two contexts are not merged into one transmission timeline', () => {
    const wrapper = mountView()
    const historical = wrapper.find('[aria-labelledby="historical-context-heading"]')
    const contemporary = wrapper.find('[aria-labelledby="contemporary-context-heading"]')
    // the chronological timeline lives in the CONTEMPORARY context only
    expect(historical.find('[aria-labelledby="timeline-heading"]').exists()).toBe(false)
    expect(contemporary.find('[aria-labelledby="timeline-heading"]').exists()).toBe(true)
  })
})

describe('UX2-P3 — PARTIAL lineage preserved with truthful state', () => {
  it('lineage renders only confirmed nodes + explicit gap, with 谱系整理中 state', () => {
    const wrapper = mountView()
    const lineage = wrapper.find('[aria-labelledby="lineage-heading"]')
    // state badge (UNSTRUCTURED_OR_INCOMPLETE → 谱系整理中)
    const badge = lineage.find('.hfm-status')
    expect(badge.attributes('data-status')).toBe('UNSTRUCTURED_OR_INCOMPLETE')
    expect(badge.text()).toBe('谱系整理中')
    // gap note present; no fabricated generation names
    expect(lineage.text()).toContain('第二代至第五代')
    expect(lineage.text()).toContain('LINEAGE_STRUCTURING: PARTIAL')
    // governed lineage model unchanged: 皇甫谧 → gap → 刘君奇
    expect(HERITAGE_LINEAGE.map((n) => n.person)).toEqual([
      '皇甫谧',
      '（第二代至第五代）',
      '刘君奇',
    ])
    expect(HERITAGE_LINEAGE.some((n) => /第[一二三四五]代/.test(n.person) && !n.person.includes('（'))).toBe(false)
  })

  it('NB-04: no uninterrupted ancient→modern transmission chain is asserted', () => {
    const wrapper = mountView()
    const text = wrapper.text()
    // the historical and contemporary contexts are separated (G1-A §4.3)
    expect(wrapper.find('[aria-labelledby="historical-context-heading"]').text()).toContain('皇甫谧')
    expect(wrapper.find('[aria-labelledby="contemporary-context-heading"]').text()).toContain('刘君奇')
    // no unsupported teacher-student / parent-child edges beyond confirmed nodes
    expect(text).not.toMatch(/皇甫谧.*[→>].*第[一二三四五]代[^\s]*名医(?!.*刘君奇)/)
    expect(text).not.toContain('师承自')
    expect(text).not.toContain('衣钵')
  })
})

describe('UX2-P3 — recognition as secondary metadata (8/8)', () => {
  it('renders all 8 recognition records with category/issuer/date as secondary metadata', () => {
    const wrapper = mountView()
    const items = wrapper.findAll('.recognition-item')
    expect(HERITAGE_RECOGNITIONS).toHaveLength(8)
    expect(items).toHaveLength(8)
    for (const item of items) {
      expect(item.find('.recognition-item__title').exists()).toBe(true)
      expect(item.find('.recognition-item__meta').exists()).toBe(true)
    }
    // not an honor wall: no award-count/grade emphasis, no ranking
    const text = wrapper.find('[aria-labelledby="recognition-heading"]').text()
    expect(text).not.toContain('一等奖')
    expect(text).not.toMatch(/荣誉墙/)
  })
})

describe('UX2-P3 — designation & provenance', () => {
  it('第六代名医 designation is exact (no variant substitution)', () => {
    const wrapper = mountView()
    expect(HERITAGE_PERSON.generationTitle).toBe('第六代名医')
    expect(wrapper.text()).toContain('第六代名医')
    expect(wrapper.text()).not.toMatch(/第六代传承人(?!.*刘君奇)/)
    expect(wrapper.text()).not.toContain('待确认')
  })

  it('public source labels render; no internal paths', () => {
    const wrapper = mountView()
    const text = wrapper.text()
    expect(text).toContain('来源：')
    expect(text).not.toMatch(/hfmzl|zzcl|\/Users|\/private/)
  })

  it('no fake media actions (媒体报道 is text records, no play/download)', () => {
    const wrapper = mountView()
    const mediaSection = wrapper.find('[aria-labelledby="media-heading"]')
    const mediaText = mediaSection.text()
    expect(mediaSection.find('video').exists()).toBe(false)
    expect(mediaSection.find('a[href]').exists()).toBe(false)
    expect(mediaText).not.toMatch(/播放|下载/)
  })
})

describe('UX2-P3 — negative boundaries', () => {
  it('NB-05: no clinical content', () => {
    const wrapper = mountView()
    expect(wrapper.text()).not.toMatch(/疗效显著|治疗推荐|适用于.*疾病|预约|问诊|处方指导/)
  })

  it('no unsupported lineage/generation inference in rendered copy', () => {
    const wrapper = mountView()
    const text = wrapper.text()
    expect(text).not.toMatch(/继承自|传自|衣钵相传/)
    expect(text).not.toMatch(/第[一二三四五]代[^\s（]*传承人/)
  })
})

describe('UX2-P3 — structure & accessibility', () => {
  it('heading hierarchy: one h1, context h2, sections h3, sub h4 — no skips', () => {
    const wrapper = mountView()
    const levels = wrapper.findAll('h1, h2, h3, h4').map((h) => Number(h.element.tagName.slice(1)))
    expect(levels.filter((l) => l === 1)).toHaveLength(1)
    for (let i = 1; i < levels.length; i += 1) {
      expect(levels[i] - levels[i - 1]).toBeLessThanOrEqual(1)
    }
  })

  it('passes axe assertions on the heritage page', async () => {
    const wrapper = mountView(true)
    const results = await axe.run(wrapper.element as HTMLElement)
    expect(results.violations).toHaveLength(0)
  })
})
