import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import BibliographicRecord from '../components/primitives/BibliographicRecord.vue'

describe('BibliographicRecord — rendering', () => {
  it('renders the record container with data-primitive and title', () => {
    const wrapper = mount(BibliographicRecord, { props: { title: '《针灸甲乙经》' } })
    expect(wrapper.find('div.bib-record[data-primitive="bib-record"]').exists()).toBe(true)
    expect(wrapper.find('.bib-record__title').text()).toContain('《针灸甲乙经》')
  })

  it('renders status badge only when status/statusLabel is provided', () => {
    const without = mount(BibliographicRecord, { props: { title: '《针灸甲乙经》' } })
    expect(without.find('.hfm-status').exists()).toBe(false)

    const withStatus = mount(BibliographicRecord, {
      props: { title: '《针灸甲乙经》', status: 'METADATA_ONLY' },
    })
    const badge = withStatus.find('.hfm-status')
    expect(badge.exists()).toBe(true)
    expect(badge.attributes('data-status')).toBe('METADATA_ONLY')
    expect(badge.text()).toBe('仅题录')
  })

  it('full record renders all meta rows, description and locator', () => {
    const wrapper = mount(BibliographicRecord, {
      props: {
        title: '《针灸甲乙经》医统正脉全书本',
        author: '皇甫谧',
        year: '明万历 29 年（1601）',
        edition: '吴勉学刊',
        kind: '古代版本',
        source: '客户提供：甲乙经论著资料',
        status: 'METADATA_ONLY',
        statusLabel: '存目',
        description: '医统正脉全书所收版本。',
        locator: '引用定位：文献级（文档级）',
        href: '/jiayi#editions',
      },
    })
    const meta = wrapper.findAll('.bib-record__meta dd').map((n) => n.text())
    expect(meta).toEqual([
      '皇甫谧',
      '明万历 29 年（1601）',
      '吴勉学刊',
      '古代版本',
      '客户提供：甲乙经论著资料',
      '引用定位：文献级（文档级）',
    ])
    expect(wrapper.find('.bib-record__desc').text()).toBe('医统正脉全书所收版本。')
    expect(wrapper.find('a.bib-record__link').attributes('href')).toBe('/jiayi#editions')
    expect(wrapper.find('.hfm-status').text()).toBe('存目')
  })
})

describe('BibliographicRecord — degradation (NB-06)', () => {
  it('missing optional fields are omitted (no synthesized rows)', () => {
    const wrapper = mount(BibliographicRecord, {
      props: { title: '《针灸甲乙经》', status: 'METADATA_ONLY' },
    })
    expect(wrapper.find('.bib-record__meta').exists()).toBe(false)
    expect(wrapper.find('.bib-record__desc').exists()).toBe(false)
    const text = wrapper.text()
    expect(text).not.toContain('作者')
    expect(text).not.toContain('年份')
    expect(text).not.toContain('版本')
    expect(text).not.toContain('馆藏')
  })

  it('never synthesizes bibliographic facts (卷/页/版本号/馆藏)', () => {
    const wrapper = mount(BibliographicRecord, {
      props: { title: '《针灸甲乙经》', author: '皇甫谧' },
    })
    const text = wrapper.text()
    expect(text).not.toMatch(/卷\d+/)
    expect(text).not.toMatch(/页\d+/)
    expect(text).not.toContain('馆藏')
    expect(text).not.toContain('版本号')
  })

  it('locator renders exactly the caller-supplied value — no page/volume invention', () => {
    const supplied = '引用定位：文档级'
    const wrapper = mount(BibliographicRecord, {
      props: { title: '后论 · 历史评价汇编', locator: supplied },
    })
    const dd = wrapper.find('.bib-record__meta dd')
    expect(dd.exists()).toBe(true)
    expect(dd.text()).toBe(supplied)
    expect(wrapper.text()).not.toMatch(/页\d+/)
    expect(wrapper.text()).not.toMatch(/卷\d+/)
  })

  it('has no CitationExport behavior (no export control, no export prop)', () => {
    const wrapper = mount(BibliographicRecord, { props: { title: '《针灸甲乙经》' } })
    const html = wrapper.html()
    expect(html).not.toContain('导出')
    expect(html).not.toMatch(/export/i)
  })
})

describe('BibliographicRecord — surface role', () => {
  it('applies ux2-surface-paper role', () => {
    const wrapper = mount(BibliographicRecord, { props: { title: '《针灸甲乙经》' } })
    expect(wrapper.find('div.bib-record.ux2-surface-paper').exists()).toBe(true)
  })
})
