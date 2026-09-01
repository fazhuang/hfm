/**
 * UX2-P5 Homepage Exhibition Narrative — composition-truth tests.
 *
 * Covers the UX2-P5 contract: narrative order conforms to the frozen grammar;
 * P0 state labels applied to surfaced data states (版本关系整理中 / 谱系整理中);
 * cross-links resolve to implemented surfaces; hero copy is governed (no
 * unsupported superlatives); no fake CTAs; P1–P4 domain truth preserved
 * (metrics from governed source, 第六代名医 exact, PARTIAL/DATA-GAP);
 * heading hierarchy + axe.
 */
import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import axe from 'axe-core'
import HomeView from '../views/HomeView.vue'
import { HOME_HERO, HOME_METRICS } from '../data/homeProjection'
import { INVENTORY_EDITION_RECORDS, INVENTORY_LUNWEN_FILES } from '../data/contentInventory'

function mountHome(attach = false): ReturnType<typeof mount> {
  return mount(HomeView, {
    attachTo: attach ? document.body : undefined,
    global: { stubs: { RouterView: { template: '<p />' } } },
  })
}

describe('UX2-P5 — narrative order & composition', () => {
  it('narrative sections follow the frozen grammar order (Hero → 皇甫谧 → 甲乙经 → 文献 → 非遗 → 研究)', () => {
    const wrapper = mountHome()
    const headings = wrapper.findAll('h1, h2').map((h) => h.text().trim())
    expect(headings[0]).toBe('皇甫谧人文数字平台') // H1 hero
    const h2 = headings.slice(1)
    const order = ['皇甫谧', '《针灸甲乙经》', '文献与史料', '皇甫谧针灸非遗 · 活态传承', '从资料到研究']
    for (const expected of order) {
      const idx = h2.indexOf(expected)
      expect(idx, `missing narrative section ${expected}`).toBeGreaterThanOrEqual(0)
    }
    const idxs = order.map((o) => h2.indexOf(o))
    for (let i = 1; i < idxs.length; i += 1) {
      expect(idxs[i]).toBeGreaterThan(idxs[i - 1])
    }
  })

  it('narrative ordering is presentation only — no factual relationship claimed', () => {
    const wrapper = mountHome()
    const text = wrapper.text()
    // no sequence/causation/lineage wording implied by the narrative layout
    expect(text).not.toMatch(/因此|所以|由此传承|继而|一脉相承/)
    expect(text).not.toMatch(/师承自|衣钵/)
  })
})

describe('UX2-P5 — P0 state labels on surfaced data states', () => {
  it('jiayi lineage figcaption carries 版本关系整理中 (UNSTRUCTURED_OR_INCOMPLETE)', () => {
    const wrapper = mountHome()
    const figcaption = wrapper.find('.home-lineage figcaption')
    const badge = figcaption.find('.hfm-status')
    expect(badge.exists()).toBe(true)
    expect(badge.attributes('data-status')).toBe('UNSTRUCTURED_OR_INCOMPLETE')
    expect(badge.text()).toBe('版本关系整理中')
    expect(figcaption.text()).toContain('DATA-GAP')
  })

  it('heritage section carries 谱系整理中 (UNSTRUCTURED_OR_INCOMPLETE)', () => {
    const wrapper = mountHome()
    const heritage = wrapper.find('.home-section--heritage')
    const badge = heritage.find('.home-state-line .hfm-status')
    expect(badge.exists()).toBe(true)
    expect(badge.attributes('data-status')).toBe('UNSTRUCTURED_OR_INCOMPLETE')
    expect(badge.text()).toBe('谱系整理中')
    expect(heritage.text()).toContain('PARTIAL')
  })
})

describe('UX2-P5 — cross-links to implemented surfaces', () => {
  it('CTA and card links resolve to real implemented routes', () => {
    const wrapper = mountHome()
    const expected = [
      '/persons/person-huangfu-mi', // P1
      '/jiayi', // P2
      '/heritage', // P3
      '/search', // P4
      '/research', // research
      '/yan',
      '/archive',
    ]
    const hrefs = wrapper.findAll('a[href]').map((a) => a.attributes('href') ?? '')
    for (const target of expected) {
      expect(hrefs.some((h) => h === target || h.startsWith(target + '?'))).toBe(true)
    }
  })
})

describe('UX2-P5 — hero copy governed (no unsupported claims)', () => {
  it('hero copy comes from governed projection (no new facts, no superlatives)', () => {
    const wrapper = mountHome()
    const heroText = wrapper.find('.home-hero').text()
    expect(HOME_HERO.definition).toContain('针灸甲乙经')
    expect(heroText).toContain('皇甫谧人文数字平台')
    // no unsupported superlatives/authority claims
    expect(heroText).not.toMatch(/唯一|首个|权威唯一|国家级|全国第一/)
    expect(wrapper.text()).not.toMatch(/完整谱系|数字化完成|全部可阅|完整传承/)
  })

  it('false completion / false authority claims are absent from all copy', () => {
    const wrapper = mountHome()
    const text = wrapper.text()
    expect(text).not.toMatch(/数字化完成|全部可阅|权威唯一/)
  })
})

describe('UX2-P5 — cards / featured content truth', () => {
  it('no fake read/play/download CTAs on cards', () => {
    const wrapper = mountHome()
    const cardLinks = wrapper.findAll('.home-links a, .home-links__title')
    for (const link of cardLinks) {
      const t = link.text()
      expect(t).not.toMatch(/阅读全文|下载|播放|查看原件/)
    }
  })

  it('metrics derive from governed contentInventory (single source)', () => {
    expect(HOME_METRICS.find((m) => m.label === '版本记录')?.value).toBe(String(INVENTORY_EDITION_RECORDS))
    expect(HOME_METRICS.find((m) => m.label === '学术论文')?.value).toBe(String(INVENTORY_LUNWEN_FILES))
  })
})

describe('UX2-P5 — P1–P4 domain truth preserved on the homepage', () => {
  it('P1: no fake media resource-ready / playability claim', () => {
    const wrapper = mountHome()
    const text = wrapper.text()
    expect(text).not.toMatch(/播放|可观看|在线观影/)
  })

  it('P2: no false digitization — editions remain metadata/summary only', () => {
    const wrapper = mountHome()
    const jiayi = wrapper.find('.home-section--jiayi').text()
    expect(jiayi).not.toMatch(/阅读全文|下载|数字化完成/)
    expect(jiayi).toContain('版本脉络')
  })

  it('P3: 第六代名医 exact; recognition not honor-wall treated', () => {
    const wrapper = mountHome()
    const heritage = wrapper.find('.home-section--heritage').text()
    expect(heritage).toContain('第六代名医')
    expect(heritage).not.toMatch(/第[一二三四五]代[^\s（]*传承人/)
    expect(heritage).not.toMatch(/荣誉墙|一等奖/)
  })

  it('P4: no fake search count / full-text claim', () => {
    const wrapper = mountHome()
    const research = wrapper.find('.home-section--research').text()
    expect(research).not.toMatch(/全文可读|全部可阅|PDF/)
  })

  it('no internal register keys in public homepage copy', () => {
    const wrapper = mountHome()
    expect(wrapper.text()).not.toMatch(/hfmzl|zzcl/)
  })
})

describe('UX2-P5 — structure & accessibility', () => {
  it('single H1 + heading hierarchy (H1 → H2, no skips)', () => {
    const wrapper = mountHome()
    const levels = wrapper.findAll('h1, h2, h3').map((h) => Number(h.element.tagName.slice(1)))
    expect(levels.filter((l) => l === 1)).toHaveLength(1)
    for (let i = 1; i < levels.length; i += 1) {
      expect(levels[i] - levels[i - 1]).toBeLessThanOrEqual(1)
    }
  })

  it('passes axe assertions on the homepage', async () => {
    const wrapper = mountHome(true)
    const results = await axe.run(wrapper.element as HTMLElement)
    expect(results.violations).toHaveLength(0)
  })
})
