/**
 * UI-08 《针灸甲乙经》核心学术界面 tests.
 *
 *  - core heading / work profile render;
 *  - edition collection renders the audited record set (ancient + modern);
 *  - lineage PNG is displayed with a meaningful alt (asset, not decoration);
 *  - chronology timeline is year-sorted and explicitly NOT lineage
 *    (no fabricated genealogical edges);
 *  - paper discovery entry + evidence/source expression present;
 *  - axe passes.
 */
import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import axe from 'axe-core'
import JiayiView from '../views/jiayi/JiayiView.vue'
import { JIAYI_ANCIENT_EDITIONS, JIAYI_MODERN_EDITIONS } from '../data/jiayiView'

function mountView(): ReturnType<typeof mount> {
  return mount(JiayiView, {
    global: { stubs: { RouterView: { template: '<p />' } } },
  })
}

describe('UI-08 page structure', () => {
  it('renders the core heading and work profile', () => {
    const wrapper = mountView()
    expect(wrapper.find('h1').text()).toBe('《针灸甲乙经》')
    expect(wrapper.find('#overview').exists()).toBe(true)
    expect(wrapper.text()).toContain('皇甫谧')
    expect(wrapper.text()).toContain('西晋')
  })

  it('renders the edition collection from the audited record set', () => {
    const wrapper = mountView()
    const cards = wrapper.findAll('.edition-card')
    expect(cards.length).toBe(JIAYI_ANCIENT_EDITIONS.length + JIAYI_MODERN_EDITIONS.length)
    // Ancient group first, modern group second.
    expect(wrapper.findAll('.edition-group-title')[0]?.text()).toBe('古代版本')
    expect(wrapper.findAll('.edition-group-title')[1]?.text()).toBe('近现代整理版本')
  })
})

describe('UI-08 lineage visual & data integrity', () => {
  it('displays the customer lineage PNG with a meaningful alt', () => {
    const wrapper = mountView()
    const img = wrapper.find('img.lineage__img')
    expect(img.exists()).toBe(true)
    expect(img.attributes('src')).toContain('edition-lineage.png')
    expect(img.attributes('alt') ?? '').toContain('版本')
    // Caption + source note present (not a bare image).
    expect(wrapper.find('.lineage__caption').exists()).toBe(true)
    expect(wrapper.find('.lineage__enlarge').text()).toBe('查看大图')
  })

  it('does not fabricate genealogical lineage edges', () => {
    const wrapper = mountView()
    const text = wrapper.text()
    // No derivation/heredity claims.
    expect(text).not.toMatch(/继承自|源自.*本|传自/)
    // Explicit data-gap statement is present.
    expect(text).toContain('DATA-GAP')
  })

  it('keeps chronology strictly separate from lineage (year-sorted, no edges)', () => {
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

describe('UI-08 paper discovery & evidence', () => {
  it('exposes a paper discovery entry with preview and CTA', () => {
    const wrapper = mountView()
    expect(wrapper.findAll('.paper-item').length).toBeGreaterThan(0)
    const cta = wrapper.find('.paper-cta__link')
    expect(cta.exists()).toBe(true)
    expect(cta.attributes('href')).toContain('/search?q=')
  })

  it('expresses evidence/source provenance via public labels (no internal paths)', () => {
    const wrapper = mountView()
    expect(wrapper.find('#evidence').text()).toContain('来源与证据')
    expect(wrapper.text()).toContain('客户提供《针灸甲乙经》资料')
    expect(wrapper.text()).not.toMatch(/hfmzl|zzcl/)
  })

  it('contains no clinical recommendation expression', () => {
    const wrapper = mountView()
    const text = wrapper.text()
    expect(text).not.toMatch(/治疗|疗效|处方|建议就诊|治愈/)
  })
})

describe('UI-08 accessibility', () => {
  it('passes axe assertions', async () => {
    const wrapper = mount(JiayiView, { attachTo: document.body })
    const results = await axe.run(wrapper.element as HTMLElement)
    wrapper.unmount()
    expect(results.violations).toHaveLength(0)
  })
})
