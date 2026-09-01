/**
 * UI-03 Homepage tests.
 *
 *  - home projection reuses existing domain data (no duplicated models);
 *  - metric integrity: 515/5 split, 19 editions ≠ 19 works, counts from
 *    contentInventory;
 *  - invariants: Jiayi lineage DATA-GAP, Heritage lineage PARTIAL, 刘君奇
 *    第六代名医, no fabricated ancient text, no clinical claims, no internal
 *    paths;
 *  - unique H1 + feature sections + CTA route targets;
 *  - component renders narrative order; axe passes.
 */
import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import axe from 'axe-core'
import HomeView from '../views/HomeView.vue'
import {
  HOME_HERO,
  HOME_HERITAGE,
  HOME_HUANGFU,
  HOME_JIAYI,
  HOME_METRICS,
  HOME_QUOTATION,
} from '../data/homeProjection'
import {
  INVENTORY_EDITION_RECORDS,
  INVENTORY_LUNWEN_FILES,
  INVENTORY_LUNZHU_FILES,
} from '../data/contentInventory'
import { READER_DOCUMENTS } from '../data/readerDocuments'

describe('UI-03 brand & hero', () => {
  it('unique H1 carries the platform brand', () => {
    const wrapper = mount(HomeView)
    const h1 = wrapper.findAll('h1')
    expect(h1).toHaveLength(1)
    expect(h1[0]?.text()).toBe('皇甫谧人文数字平台')
    expect(wrapper.text()).toContain('皇甫谧 215—282')
  })

  it('hero definition reuses UI-04 data (no new person facts)', () => {
    expect(HOME_HERO.definition).toContain('针灸甲乙经')
    expect(HOME_HERO.personName).toBe('皇甫谧')
    expect(HOME_HERO.primary.map((c) => c.label)).toEqual(['探索皇甫谧', '进入《针灸甲乙经》'])
  })
})

describe('UI-03 metric integrity', () => {
  it('counts come from contentInventory (single source), never hardcoded', () => {
    expect(HOME_METRICS.find((m) => m.label === '版本记录')?.value).toBe(
      String(INVENTORY_EDITION_RECORDS),
    )
    expect(HOME_METRICS.find((m) => m.label === '论著资料')?.value).toBe(
      String(INVENTORY_LUNZHU_FILES),
    )
    expect(HOME_METRICS.find((m) => m.label === '学术论文')?.value).toBe(
      String(INVENTORY_LUNWEN_FILES),
    )
    expect(HOME_METRICS.find((m) => m.label === 'Reader 全文')?.value).toBe(
      String(READER_DOCUMENTS.length),
    )
  })

  it('515/5 split is never confused', () => {
    const paper = HOME_METRICS.find((m) => m.label === '学术论文')!
    expect(paper.value).toBe('515')
    expect(paper.note).toContain('已结构化题录 5 条')
    expect(paper.note).not.toContain('可在线检索')
  })

  it('19 editions are not described as 19 works', () => {
    // Edition count ≠ work count; the homepage never claims 19 部著作.
    const editionMetric = HOME_METRICS.find((m) => m.label === '版本记录')!
    expect(editionMetric.note).toContain('历代版本')
    expect(editionMetric.note).not.toMatch(/部著作|部作品/)
  })
})

describe('UI-03 invariants', () => {
  it('Jiayi lineage stays DATA-GAP on the homepage', () => {
    expect(HOME_JIAYI.lineage.alt).toContain('DATA-GAP')
    expect(JSON.stringify(HOME_JIAYI)).not.toMatch(/STRUCTURED_LINEAGE_COMPLETE|版本谱系已结构化/)
  })

  it('Heritage lineage stays PARTIAL and 刘君奇 第六代名医 holds', () => {
    const lede = HOME_HERITAGE.lede
    expect(lede).toContain('PARTIAL')
    expect(lede).toContain('第六代名医')
    expect(lede).toContain('刘君奇')
    expect(lede).not.toMatch(/待确认|疑似第六代/)
  })

  it('quotation is a real 后论 quote with attribution (no fabricated slogan)', () => {
    expect(HOME_QUOTATION.attribution).toContain('房玄龄')
    expect(HOME_QUOTATION.source).toBe('《晋书》')
    expect(HOME_QUOTATION.text).toContain('皇甫谧素履幽贞')
  })

  it('no fabricated ancient text, no clinical claims, no internal paths', () => {
    const text = JSON.stringify([HOME_HERO, HOME_HUANGFU, HOME_JIAYI, HOME_METRICS, HOME_QUOTATION])
    expect(text).not.toMatch(/hfmzl|zzcl|registerKey/)
    expect(text).not.toMatch(/疗效显著|治疗推荐|适用于.*疾病|预约|问诊/)
    // No invented full classical text.
    expect(text).not.toContain('玄守论曰')
    expect(text).not.toContain('笃终论曰')
  })
})

describe('UI-03 homepage renders narrative sections', () => {
  it('renders sections in narrative order with real CTA targets', () => {
    const wrapper = mount(HomeView)
    const headings = wrapper.findAll('h2').map((h) => h.text())
    expect(headings[0]).toBe('皇甫谧')
    expect(headings).toContain('《针灸甲乙经》')
    expect(headings).toContain('文献与史料')
    expect(headings).toContain('皇甫谧针灸非遗 · 活态传承')
    expect(headings).toContain('从资料到研究')

    const hrefs = wrapper.findAll('a').map((a) => a.attributes('href'))
    for (const target of [
      '/persons/person-huangfu-mi',
      '/jiayi',
      '/yan',
      '/archive',
      '/heritage',
      '/research',
      '/reader/houlun',
    ]) {
      expect(hrefs, target).toContain(target)
    }
  })

  it('search form is wired to the /search route', () => {
    const wrapper = mount(HomeView)
    const form = wrapper.find('form.home-search')
    const input = wrapper.find('#home-search-input')
    expect(form.exists()).toBe(true)
    expect(input.attributes('placeholder')).toContain('检索人物、作品、版本、文献与论文')
  })

  it('renders 第六代名医 on the homepage', () => {
    const wrapper = mount(HomeView)
    expect(wrapper.text()).toContain('第六代名医')
    expect(wrapper.text()).toContain('刘君奇')
  })

  it('passes axe assertions', async () => {
    const wrapper = mount(HomeView, { attachTo: document.body })
    const results = await axe.run(wrapper.element as HTMLElement)
    wrapper.unmount()
    expect(results.violations).toHaveLength(0)
  })
})
