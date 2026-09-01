/**
 * UX2-P5 Homepage Exhibition Narrative — composition-truth tests (corrected).
 *
 * P1-01 correction: surfaced lineage/relation states are verified THROUGH the
 * shared P0 mapping wiring — the badges must derive data-status from
 * resolvePresentationState and the label from the shared presentationStatusLabel
 * helper (spied via vi.mock), not from template literals. A change in the
 * shared mapping must propagate to the homepage DOM.
 *
 * Also covers: narrative order (frozen grammar), cross-links to implemented
 * surfaces, hero copy governed (no superlatives), no fake CTAs, P1–P4 domain
 * truth preserved, heading hierarchy + axe.
 */
import { afterEach, describe, expect, it, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import axe from 'axe-core'
import HomeView from '../views/HomeView.vue'
import { HOME_HERO, HOME_METRICS } from '../data/homeProjection'
import { INVENTORY_EDITION_RECORDS, INVENTORY_LUNWEN_FILES } from '../data/contentInventory'

/* Spy-wire the shared P0 mapping: HomeView must route through these exact
 * exports. The mocks delegate to the real implementations and record calls. */
vi.mock('../presentation/stateMapping', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../presentation/stateMapping')>()
  return {
    ...actual,
    resolvePresentationState: vi.fn(actual.resolvePresentationState),
    presentationStatusLabel: vi.fn(actual.presentationStatusLabel),
  }
})
import { presentationStatusLabel, resolvePresentationState } from '../presentation/stateMapping'

afterEach(() => {
  vi.clearAllMocks()
})

function mountHome(attach = false): ReturnType<typeof mount> {
  return mount(HomeView, {
    attachTo: attach ? document.body : undefined,
    global: { stubs: { RouterView: { template: '<p />' } } },
  })
}

describe('UX2-P5 — surfaced states route through the shared P0 mapping (P1-01)', () => {
  it('jiayi lineage badge: data-status = resolver output, label = shared helper', () => {
    const wrapper = mountHome()
    const badge = wrapper.find('.home-lineage figcaption .hfm-status')
    // data-status comes from resolvePresentationState (not a template literal)
    expect(badge.attributes('data-status')).toBe('UNSTRUCTURED_OR_INCOMPLETE')
    expect(badge.attributes('data-status')).toBe(
      resolvePresentationState({ contentStatus: 'DATA_GAP' }),
    )
    // label comes from the shared presentationStatusLabel helper
    expect(badge.text()).toBe(
      presentationStatusLabel(resolvePresentationState({ contentStatus: 'DATA_GAP' }), '版本关系整理中'),
    )
    // the shared functions were actually invoked by HomeView (no local bypass)
    expect(resolvePresentationState).toHaveBeenCalled()
    expect(presentationStatusLabel).toHaveBeenCalled()
    // DATA-GAP caption remains present
    expect(wrapper.find('.home-lineage figcaption').text()).toContain('DATA-GAP')
  })

  it('heritage lineage badge: data-status = resolver output, label = shared helper', () => {
    const wrapper = mountHome()
    const badge = wrapper.find('.home-section--heritage .home-state-line .hfm-status')
    expect(badge.attributes('data-status')).toBe('UNSTRUCTURED_OR_INCOMPLETE')
    expect(badge.text()).toBe(
      presentationStatusLabel(resolvePresentationState({ contentStatus: 'DATA_GAP' }), '谱系整理中'),
    )
    expect(resolvePresentationState).toHaveBeenCalled()
    expect(presentationStatusLabel).toHaveBeenCalled()
    // PARTIAL lede remains present
    expect(wrapper.find('.home-section--heritage').text()).toContain('PARTIAL')
  })

  it('a change in the shared label mapping propagates to the homepage DOM (no literal masking)', () => {
    vi.mocked(presentationStatusLabel).mockReturnValue('映射传播验证')
    const wrapper = mountHome()
    expect(wrapper.find('.home-lineage figcaption .hfm-status').text()).toBe('映射传播验证')
  })

  it('a change in the shared resolver propagates to the data-status (no literal masking)', () => {
    vi.mocked(resolvePresentationState).mockReturnValue('HISTORICAL_ABSENCE')
    const wrapper = mountHome()
    expect(wrapper.find('.home-section--heritage .home-state-line .hfm-status').attributes('data-status')).toBe(
      'HISTORICAL_ABSENCE',
    )
  })
})

describe('UX2-P5 — narrative order & composition', () => {
  it('narrative sections follow the frozen grammar order', () => {
    const wrapper = mountHome()
    const headings = wrapper.findAll('h1, h2').map((h) => h.text().trim())
    expect(headings[0]).toBe('皇甫谧人文数字平台')
    const h2 = headings.slice(1)
    const order = ['皇甫谧', '《针灸甲乙经》', '文献与史料', '皇甫谧针灸非遗 · 活态传承', '从资料到研究']
    const idxs = order.map((o) => h2.indexOf(o))
    for (const [i, expected] of order.entries()) {
      expect(idxs[i], `missing narrative section ${expected}`).toBeGreaterThanOrEqual(0)
    }
    for (let i = 1; i < idxs.length; i += 1) {
      expect(idxs[i]).toBeGreaterThan(idxs[i - 1])
    }
  })

  it('narrative ordering is presentation only — no factual relationship claimed', () => {
    const wrapper = mountHome()
    const text = wrapper.text()
    expect(text).not.toMatch(/因此|所以|由此传承|继而|一脉相承/)
    expect(text).not.toMatch(/师承自|衣钵/)
  })
})

describe('UX2-P5 — cross-links to implemented surfaces', () => {
  it('CTA and card links resolve to real implemented routes', () => {
    const wrapper = mountHome()
    const expected = [
      '/persons/person-huangfu-mi',
      '/jiayi',
      '/heritage',
      '/search',
      '/research',
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
  it('hero copy comes from governed projection (no superlatives)', () => {
    const wrapper = mountHome()
    const heroText = wrapper.find('.home-hero').text()
    expect(HOME_HERO.definition).toContain('针灸甲乙经')
    expect(heroText).toContain('皇甫谧人文数字平台')
    expect(heroText).not.toMatch(/唯一|首个|权威唯一|国家级|全国第一/)
    expect(wrapper.text()).not.toMatch(/完整谱系|数字化完成|全部可阅|完整传承/)
  })
})

describe('UX2-P5 — cards / featured content truth', () => {
  it('no fake read/play/download CTAs on cards', () => {
    const wrapper = mountHome()
    const cardLinks = wrapper.findAll('.home-links a, .home-links__title')
    for (const link of cardLinks) {
      expect(link.text()).not.toMatch(/阅读全文|下载|播放|查看原件/)
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
    expect(wrapper.text()).not.toMatch(/播放|可观看|在线观影/)
  })

  it('P2: no false digitization — editions remain summary only', () => {
    const jiayi = mountHome().find('.home-section--jiayi').text()
    expect(jiayi).not.toMatch(/阅读全文|下载|数字化完成/)
    expect(jiayi).toContain('版本脉络')
  })

  it('P3: 第六代名医 exact; recognition not honor-wall treated', () => {
    const heritage = mountHome().find('.home-section--heritage').text()
    expect(heritage).toContain('第六代名医')
    expect(heritage).not.toMatch(/第[一二三四五]代[^\s（]*传承人/)
    expect(heritage).not.toMatch(/荣誉墙|一等奖/)
  })

  it('P4: no fake search count / full-text claim', () => {
    const research = mountHome().find('.home-section--research').text()
    expect(research).not.toMatch(/全文可读|全部可阅|PDF/)
  })

  it('no internal register keys in public homepage copy', () => {
    expect(mountHome().text()).not.toMatch(/hfmzl|zzcl/)
  })
})

describe('UX2-P5 — structure & accessibility', () => {
  it('single H1 + heading hierarchy (no skips)', () => {
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
