/**
 * WP-05 Sections 05–08 (Evidence / Heritage / Domains / Closing) —
 * production-fidelity verification tests.
 *
 * Proves the WP-05 fidelity deltas preserve the accepted semantic contracts:
 *  - 05 Evidence: authoritative quotation + attribution + claim↔dispute +
 *    six-source provenance register visible (no fabrication, no clinical advice);
 *  - 06 Heritage: 刘君奇 / 第六代名医 / PARTIAL honesty kept; PARTIAL lineage chip
 *    still routes through the shared P0 resolver/label; the documentary photo is
 *    decorative-hidden on the img only, while the visible provenance figcaption
 *    stays in the accessibility tree (P1-01 rule);
 *  - 07 Domains: exactly four thresholds = four real routes; the removed
 *    "NARRATIVE → USABLE ARCHIVE" copy is NOT reintroduced;
 *  - 08 Closing: platform identity + subtitle only — no h2 carrying the platform
 *    name, no © / legal nav / links (AppFooter owns the global footer).
 */
import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import axe from 'axe-core'
import HomeView from '../views/HomeView.vue'
import { HOME_QUOTATION } from '../data/homeProjection'

function mountHome(attach = false): ReturnType<typeof mount> {
  return mount(HomeView, {
    attachTo: attach ? document.body : undefined,
    global: { stubs: { RouterView: { template: '<p />' } } },
  })
}

const hasAriaHiddenAncestor = (el: Element): boolean => {
  let cur: Element | null = el.parentElement
  while (cur) {
    if (cur.getAttribute('aria-hidden') === 'true') return true
    cur = cur.parentElement
  }
  return false
}

describe('WP-05 Section 05 — Evidence (S5-C fidelity)', () => {
  it('renders the scholarly argument: claim → source witness → dispute', () => {
    const wrapper = mountHome()
    const ev = wrapper.find('#home-evidence')
    expect(ev.text()).toContain('每一个结论，都回到它的出处。')
    expect(ev.text()).toContain('生卒年 215—282')
    expect(ev.text()).toContain('建安 / 正始 两说')
    // primary witness = the FULL verified quotation (房玄龄《晋书》) — no v-html
    expect(ev.find('.home-evidence__wit-text').text()).toContain(HOME_QUOTATION.text)
    expect(ev.text()).toContain(HOME_QUOTATION.attribution)
    expect(ev.text()).toContain('《晋书》')
    expect(ev.find('blockquote.home-evidence__wit').exists()).toBe(true)
    expect(ev.element.querySelectorAll('[v-html]')).toHaveLength(0)
  })

  it('six-source provenance register is present and CTA is real', () => {
    const wrapper = mountHome()
    const ev = wrapper.find('#home-evidence')
    expect(ev.findAll('.home-evidence__row')).toHaveLength(6)
    const titles = ev.findAll('.home-evidence__row b').map((b) => b.text())
    expect(titles).toEqual(['本源史料', '地方志', '类书', '现代考据', '谱系', '图像遗存'])
    expect(ev.find('.home-evidence__act').attributes('href')).toBe('/reader/houlun')
  })

  it('the argument is text-only content — no arrows/boxes clinical advice or links inside', () => {
    const wrapper = mountHome()
    const ev = wrapper.find('#home-evidence')
    expect(ev.findAll('a').length).toBeLessThanOrEqual(1)
    expect(ev.text()).not.toMatch(/疗效|治疗推荐|适用于.*疾病|预约|问诊/)
  })
})

describe('WP-05 Section 06 — Heritage (S6-B fidelity)', () => {
  it('keeps 刘君奇 · 第六代名医 · PARTIAL honesty and the shared chip contract', () => {
    const wrapper = mountHome()
    const hg = wrapper.find('#home-heritage')
    expect(hg.text()).toContain('刘君奇')
    expect(hg.text()).toContain('第六代名医')
    expect(hg.text()).toContain('PARTIAL')
    expect(hg.text()).toContain('整理中')
    const chip = hg.find('.home-state-line .hfm-status')
    expect(chip.attributes('data-status')).toBe('UNSTRUCTURED_OR_INCOMPLETE')
    expect(chip.text()).toBe('谱系整理中')
    expect(hg.text()).not.toMatch(/荣誉墙|一等奖|完整谱系/)
  })

  it('documentary photo is decorative on the img only; the visible figcaption is accessible', () => {
    const wrapper = mountHome()
    const fig = wrapper.find('.home-heritage__act-pic')
    expect(fig.attributes('aria-hidden')).toBeUndefined()
    const img = fig.find('img')
    expect(img.attributes('alt')).toBe('')
    expect(img.attributes('aria-hidden')).toBe('true')
    const cap = fig.find('figcaption')
    expect(cap.attributes('aria-hidden')).toBeUndefined()
    expect(hasAriaHiddenAncestor(cap.element)).toBe(false)
    expect(cap.text()).toContain('师承教育拜师大会')
    expect(cap.text()).toContain('客户实拍')
  })

  it('shows the three documentary transmission records + ONE CTA', () => {
    const wrapper = mountHome()
    const hg = wrapper.find('#home-heritage')
    const traces = hg.findAll('.home-heritage__trace-row')
    expect(traces.length).toBeGreaterThanOrEqual(3)
    expect(hg.find('.home-heritage__act').attributes('href')).toBe('/heritage')
  })
})

describe('WP-05 Section 07 — Domains (S7-A fidelity)', () => {
  it('four thresholds map to the four real routes (no fake doors)', () => {
    const wrapper = mountHome()
    const dom = wrapper.find('#home-domains')
    const doors = dom.findAll('.home-domains__door')
    expect(doors).toHaveLength(4)
    const hrefs = dom.findAll('.home-domains__go').map((a) => a.attributes('href'))
    expect(hrefs).toEqual(['/persons/person-huangfu-mi', '/archive', '/jiayi', '/heritage'])
    const titles = dom.findAll('.home-domains__t').map((t) => t.text())
    expect(titles).toEqual(['皇甫谧', '文献史料', '《针灸甲乙经》', '活态传承'])
  })

  it('does NOT reintroduce the removed NARRATIVE → USABLE ARCHIVE copy', () => {
    const wrapper = mountHome()
    const text = wrapper.find('#home-domains').text()
    expect(text).not.toMatch(/NARRATIVE|USABLE ARCHIVE|叙事之后/)
  })

  it('medical numbers render as a quiet register (19/92/515 from data)', () => {
    const wrapper = mountHome()
    const bib = wrapper.find('#home-domains').text()
    expect(bib).toMatch(/19/)
    expect(bib).toMatch(/92/)
    expect(bib).toMatch(/515/)
    expect(bib).not.toMatch(/阅读全文|下载|播放/)
  })
})

describe('WP-05 Section 08 — Closing (S8-A fidelity)', () => {
  it('closing = identity + subtitle only (no legal nav / © / links)', () => {
    const wrapper = mountHome()
    const cl = wrapper.find('#home-closing')
    expect(cl.find('.home-closing__name').text()).toBe('皇甫谧人文数字平台')
    expect(cl.find('.home-closing__subtitle').text()).toContain('权威数字人文资料')
    expect(cl.findAll('a')).toHaveLength(0)
    expect(cl.text()).not.toMatch(/©|版权|隐私|关于平台/)
  })

  it('closing identity is a non-heading <p> (no duplicate H1 name as heading)', () => {
    const wrapper = mountHome()
    const headings = wrapper.findAll('h1, h2').map((h) => h.text().trim())
    expect(headings.filter((t) => t.includes('皇甫谧人文数字平台')).length).toBe(1)
    expect(wrapper.find('.home-closing__name').element.tagName).toBe('P')
  })
})

describe('WP-05 — homepage integrity & accessibility', () => {
  it('single H1 + heading no-skip + 8 section roots in order', () => {
    const wrapper = mountHome()
    const ids = wrapper.findAll('section').map((s) => s.attributes('id'))
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
    const levels = wrapper.findAll('h1, h2, h3').map((h) => Number(h.element.tagName.slice(1)))
    expect(levels.filter((l) => l === 1)).toHaveLength(1)
    for (let i = 1; i < levels.length; i += 1) {
      expect(levels[i] - levels[i - 1]).toBeLessThanOrEqual(1)
    }
  })

  it('passes axe on the homepage after the Sections 05–08 fidelity pass', async () => {
    const wrapper = mountHome(true)
    const results = await axe.run(wrapper.element as HTMLElement)
    wrapper.unmount()
    expect(results.violations).toHaveLength(0)
  })
})
