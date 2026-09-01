/**
 * UI-06 Literature / Qiyan / Archive tests.
 *
 *  - /yan renders the customer 其言.docx content faithfully (no fabricated
 *    quotes, no invented full text);
 *  - WORK / EDITION / ARCHIVE RECORD semantics are kept distinct;
 *  - 帝王世纪 / 高士传 live in the WORK layer;
 *  - archive public view never exposes internal absolute paths;
 *  - search CTA targets the real /search route;
 *  - axe passes on all three surfaces.
 */
import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import { createMemoryHistory, createRouter } from 'vue-router'
import axe from 'axe-core'
import YanView from '../views/yan/YanView.vue'
import WorksView from '../views/works/WorksView.vue'
import ArchiveView from '../views/archive/ArchiveView.vue'
import { YAN_COLLECTION } from '../data/yanCollection'
import { WORK_COLLECTION } from '../data/workCollection'
import { ARCHIVE_RECORDS, ARCHIVE_GROUPS } from '../data/archiveInventory'
import { JIAYI_ANCIENT_EDITIONS, JIAYI_MODERN_EDITIONS } from '../data/jiayiView'

function mountRoute(path: string, component: typeof YanView): ReturnType<typeof mount> {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [{ path, component }],
  })
  router.push(path)
  return mount(component, { global: { plugins: [router] } })
}

describe('UI-06 其言 (Yan)', () => {
  it('renders the customer docx content faithfully', () => {
    const wrapper = mountRoute('/yan', YanView)
    const text = wrapper.text()
    // Customer docx opening + four section titles.
    expect(text).toContain('皇甫谧本人存世文章、序跋、著作序言，是研究其思想的一手文本。')
    expect(text).toContain('《三都赋》序')
    expect(text).toContain('《玄守论》')
    expect(text).toContain('《释劝论》')
    expect(text).toContain('《笃终论》')
    // Supplement paragraph present.
    expect(text).toContain('《帝王世纪》《高士传》《逸士传》《列女传》片段辑佚')
  })

  it('does not fabricate full classical texts or invented quotes', () => {
    // Collection model: four sections, fullTextStatus DATA_GAP (no invented 全文).
    expect(YAN_COLLECTION.sections).toHaveLength(4)
    for (const section of YAN_COLLECTION.sections) {
      expect(section.fullTextStatus).toBe('DATA_GAP')
      for (const record of section.records) {
        // Every record text is the customer's own description, not a made-up aphorism.
        expect(record.text.length).toBeGreaterThan(10)
        expect(record.status).toBe('AVAILABLE')
        // Editorial themes are explicitly marked as presentation classification.
        expect(record.themeClassification).toBe('PRESENTATION_CLASSIFICATION')
      }
    }
  })

  it('marks the source and reading context', () => {
    const wrapper = mountRoute('/yan', YanView)
    expect(wrapper.find('#source-heading').exists()).toBe(true)
    expect(wrapper.text()).toContain('客户提供：其言文稿（docx）')
    expect(wrapper.find('.hfm-reading').exists()).toBe(true)
  })
})

describe('UI-06 Work / Edition / Archive separation', () => {
  it('帝王世纪 / 高士传 exist in the WORK layer', () => {
    const titles = WORK_COLLECTION.map((w) => w.title)
    expect(titles).toContain('《帝王世纪》')
    expect(titles).toContain('《高士传》')
    const dwsj = WORK_COLLECTION.find((w) => w.title === '《帝王世纪》')
    expect(dwsj?.attribution).toBe('皇甫谧')
    expect(dwsj?.kind).toBe('compilation')
  })

  it('WORK records never carry edition fields (Work ≠ Edition)', () => {
    for (const work of WORK_COLLECTION) {
      expect(work).not.toHaveProperty('editionType')
      expect(work).not.toHaveProperty('imprint')
    }
    // Editions live in the UI-08 edition collections.
    for (const edition of [...JIAYI_ANCIENT_EDITIONS, ...JIAYI_MODERN_EDITIONS]) {
      expect(edition.editionType).toBeDefined()
      expect(edition.title).not.toBe('《针灸甲乙经》') // editions are versions, not the work
    }
  })

  it('archive records are distinct from works and carry public source names', () => {
    const archiveIds = new Set(ARCHIVE_RECORDS.map((r) => r.id))
    const workIds = new Set(WORK_COLLECTION.map((w) => w.id))
    expect([...archiveIds].some((id) => workIds.has(id))).toBe(false)
    // Public source names are understandable — never internal absolute paths.
    for (const record of ARCHIVE_RECORDS) {
      expect(record.sourceName).not.toMatch(/^hfmzl\/|^zzcl\//)
      expect(record.sourceName.length).toBeGreaterThan(0)
    }
    // Six public categories.
    expect(ARCHIVE_GROUPS).toHaveLength(6)
  })
})

describe('UI-06 archive public view', () => {
  it('renders understandable source names and never internal paths', () => {
    const wrapper = mountRoute('/archive', ArchiveView)
    const text = wrapper.text()
    expect(text).not.toContain('hfmzl/')
    expect(text).not.toContain('zzcl/')
    expect(text).toContain('皇甫谧人物资料')
    expect(text).toContain('《针灸甲乙经》版本资料')
    expect(text).toContain('皇甫谧针灸非遗传承')
  })
})

describe('UI-06 navigation & search boundary', () => {
  it('related and search CTA links target real routes', () => {
    const yan = mountRoute('/yan', YanView)
    const hrefs = yan.findAll('a').map((a) => a.attributes('href'))
    expect(hrefs).toContain('/persons/person-huangfu-mi')
    expect(hrefs).toContain('/works')
    expect(hrefs).toContain('/archive')
    expect(hrefs).toContain('/jiayi')

    const works = mountRoute('/works', WorksView)
    const worksHrefs = works.findAll('a').map((a) => a.attributes('href'))
    expect(worksHrefs).toContain('/search?q=针灸甲乙经')
    expect(worksHrefs).toContain('/archive')
    expect(worksHrefs).toContain('/jiayi')
    expect(worksHrefs).toContain('/yan')
  })

  it('UI-06 contains no clinical recommendation expression', () => {
    for (const component of [YanView, WorksView, ArchiveView]) {
      const wrapper = mountRoute('/x', component)
      expect(wrapper.text()).not.toMatch(/治疗|疗效|处方|建议就诊|治愈/)
    }
  })
})

describe('UI-06 accessibility', () => {
  it('passes axe on yan / works / archive', async () => {
    for (const [path, component] of [
      ['/yan', YanView],
      ['/works', WorksView],
      ['/archive', ArchiveView],
    ] as const) {
      const router = createRouter({
        history: createMemoryHistory(),
        routes: [{ path, component }],
      })
      router.push(path)
      const wrapper = mount(component, { attachTo: document.body, global: { plugins: [router] } })
      const results = await axe.run(wrapper.element as HTMLElement)
      wrapper.unmount()
      expect(results.violations, path).toHaveLength(0)
    }
  })
})
