/**
 * CF-04 《针灸甲乙经》work / edition presentation tests (rebuild).
 *
 *  - single coherent H1 = work identity, built from the shared WORK record;
 *  - WORK (作品本体) and EDITION (版本记录) are strictly distinct surfaces;
 *  - edition records render through the CF-02 BibliographicRecord primitive
 *    with honest PARTIAL catalog states (「仅版本信息」);
 *  - DATA-GAP / TODO / internal register paths are never public copy;
 *  - chronology is year-sorted and never implies lineage;
 *  - axe passes on the page.
 *
 * Data source is the audited customer register view model (static/domain
 * content — CF-04 §5 VERSIONED_CONTENT, no mocked API integration).
 */
import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import axe from 'axe-core'
import JiayiView from '../views/jiayi/JiayiView.vue'
import { JIAYI_ANCIENT_EDITIONS, JIAYI_MODERN_EDITIONS } from '../data/jiayiView'
import { WORK_COLLECTION } from '../data/workCollection'

const EDITION_TOTAL = JIAYI_ANCIENT_EDITIONS.length + JIAYI_MODERN_EDITIONS.length
const JIAYI_WORK = WORK_COLLECTION.find((work) => work.id === 'w-jiayi')

function mountView(attach = false): ReturnType<typeof mount> {
  return mount(JiayiView, {
    attachTo: attach ? document.body : undefined,
    global: { stubs: { RouterView: { template: '<p />' } } },
  })
}

describe('CF-04 work identity & WORK/EDITION distinction', () => {
  it('renders a single coherent H1 with the shared WORK identity', () => {
    const wrapper = mountView()
    const headings = wrapper.findAll('h1')
    expect(headings).toHaveLength(1)
    expect(headings[0].text()).toBe('《针灸甲乙经》')
    expect(wrapper.find('.jiayi-hero__meta').text()).toContain('皇甫谧')
    expect(wrapper.find('.jiayi-hero__meta').text()).toContain('西晋')
  })

  it('keeps the WORK profile distinct from edition records', () => {
    const wrapper = mountView()
    // Overview is ONE work-level surface — not a bibliographic-record list.
    expect(wrapper.find('#overview[data-record-kind="work"]').exists()).toBe(true)
    expect(wrapper.find('#overview [data-primitive="bibliographic-record"]').exists()).toBe(false)
    // Edition collection holds exactly the audited edition set.
    const editionItems = wrapper.findAll('[data-record-kind="edition"]')
    expect(editionItems.length).toBe(EDITION_TOTAL)
    const first = wrapper.find('[data-record-kind="edition"]')
    expect(first.attributes('data-edition-id')).toBe(JIAYI_ANCIENT_EDITIONS[0].id)
    expect(first.find('[data-primitive="bibliographic-record"]').exists()).toBe(true)
  })

  it('composes the work profile from the shared WORK record fields', () => {
    const wrapper = mountView()
    expect(JIAYI_WORK).toBeDefined()
    const overviewText = wrapper.find('#overview').text()
    expect(overviewText).toContain(JIAYI_WORK?.description.slice(0, 12))
    expect(overviewText).toContain('撰者')
    expect(overviewText).toContain('著作类型')
    expect(overviewText).toContain(`${EDITION_TOTAL} 种版本记录`)
    expect(wrapper.find('.record-state__pill').attributes('data-status')).toBe('COMPLETE')
    expect(wrapper.find('.record-state__source').text()).toContain('来源：')
  })
})

describe('CF-04 bibliographic / edition rendering', () => {
  it('renders every edition through CF-02 BibliographicRecord with honest catalog state', () => {
    const wrapper = mountView()
    const records = wrapper.findAll('[data-primitive="bibliographic-record"]')
    expect(records.length).toBe(EDITION_TOTAL)
    // Groups keep the audited ordering (ancient first, modern second).
    const groupTitles = wrapper.findAll('.edition-group-title').map((n) => n.text())
    expect(groupTitles).toEqual(['古代版本', '近现代整理版本'])
    // Each record exposes a PARTIAL band with the public label 仅版本信息.
    const pills = wrapper.findAll('.bib-record__status[data-status="PARTIAL"]')
    expect(pills.length).toBe(EDITION_TOTAL)
    expect(pills[0]?.text()).toBe('仅版本信息')
  })

  it('shows only fields present in the record (metadata honesty)', () => {
    const wrapper = mountView()
    const text = wrapper.find('#editions').text()
    expect(text).toContain('医统正脉全书本')
    expect(text).toContain('明万历')
    // Provenance uses public labels — never the internal register key.
    expect(wrapper.find('#editions').text()).toContain('客户提供《针灸甲乙经》论著资料')
  })
})

describe('CF-04 data-gap is presentation, never developer copy', () => {
  it('expresses partial data as states without DATA-GAP/TODO/internal terms', () => {
    const wrapper = mountView()
    const text = wrapper.text()
    expect(text).not.toMatch(/DATA-GAP|TODO|FIXME|hfmzl|zzcl/)
    expect(text).toContain('仅版本信息')
    expect(text).toContain('随整理逐步呈现')
  })

  it('does not fabricate lineage edges or invented bibliographic fields', () => {
    const wrapper = mountView()
    const text = wrapper.text()
    expect(text).not.toMatch(/继承自|源自.*本|传自/)
    expect(text).not.toMatch(/馆藏：|收藏单位：|索书号/)
    // The lineage asset caveat is public and plain.
    expect(wrapper.find('.lineage__caveat').text()).toContain('传承谱系推断')
  })
})

describe('CF-04 lineage visual, chronology & semantics', () => {
  it('displays the lineage PNG with a public alt (no developer term)', () => {
    const wrapper = mountView()
    const img = wrapper.find('img.lineage__img')
    expect(img.exists()).toBe(true)
    expect(img.attributes('src')).toContain('edition-lineage.png')
    const alt = img.attributes('alt') ?? ''
    expect(alt).toContain('版本及各版本之间脉络联系')
    expect(alt).not.toContain('DATA-GAP')
    expect(wrapper.find('.lineage__caption').exists()).toBe(true)
    expect(wrapper.find('.lineage__enlarge').text()).toBe('查看大图')
  })

  it('keeps chronology strictly year-sorted and never lineage', () => {
    const wrapper = mountView()
    const dates = wrapper
      .findAll('.timeline__date')
      .map((d) => Number(d.text()))
      .filter((n) => !Number.isNaN(n))
    const sorted = [...dates].sort((a, b) => a - b)
    expect(dates.length).toBeGreaterThan(0)
    expect(dates).toEqual(sorted)
    const note = wrapper.find('#edition-timeline').text()
    expect(note).toContain('按可考年代排序')
    expect(note).toContain('不代表版本间的传承关系')
  })
})

describe('CF-04 papers, evidence & accessibility', () => {
  it('exposes a paper discovery entry with preview and CTA', () => {
    const wrapper = mountView()
    expect(wrapper.findAll('.paper-item').length).toBeGreaterThan(0)
    const cta = wrapper.find('.paper-cta__link')
    expect(cta.exists()).toBe(true)
    expect(cta.attributes('href')).toContain('/search?q=')
  })

  it('expresses evidence/source via public labels', () => {
    const wrapper = mountView()
    expect(wrapper.find('#evidence').text()).toContain('来源与证据')
    expect(wrapper.text()).toContain('客户提供《针灸甲乙经》资料')
  })

  it('contains no clinical recommendation expression', () => {
    const wrapper = mountView()
    const text = wrapper.text()
    expect(text).not.toMatch(/治疗|疗效|处方|建议就诊|治愈/)
  })

  it('passes axe assertions', async () => {
    const wrapper = mountView(true)
    const results = await axe.run(wrapper.element as HTMLElement)
    wrapper.unmount()
    expect(results.violations).toHaveLength(0)
  })
})
