/**
 * UI-07 Ancient Text Reader tests.
 *
 *  - reader projection: real documents from customer docx, correct status
 *    accounting (FULL_TEXT=2, EXCERPT=0, METADATA_ONLY classical entries);
 *  - text integrity: no fabricated ancient text, no invented 卷/页/版本号;
 *  - citation generation is deterministic and never invents volume/page;
 *  - section ids stable; invalid reader id resolves to not-found;
 *  - search integration: reader documents route to /reader/:id;
 *  - component states (full text / metadata-only / invalid) + axe.
 */
import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import { createMemoryHistory, createRouter } from 'vue-router'
import axe from 'axe-core'
import ReaderDocView from '../views/reader/ReaderDocView.vue'
import CitationBlock from '../components/reader/CitationBlock.vue'
import { READER_DOCUMENTS, READER_METADATA_ONLY, getReaderDocument } from '../data/readerDocuments'
import { SEARCH_INDEX, searchIndex } from '../data/searchIndex'

describe('UI-07 reader projection & availability accounting', () => {
  it('two FULL_TEXT documents from real customer docx', () => {
    expect(READER_DOCUMENTS).toHaveLength(2)
    expect(READER_DOCUMENTS.every((d) => d.readingStatus === 'FULL_TEXT')).toBe(true)
    expect(READER_DOCUMENTS.some((d) => d.id === 'houlun')).toBe(true)
    expect(READER_DOCUMENTS.some((d) => d.id === 'qichuan')).toBe(true)
  })

  it('classical full texts stay METADATA_ONLY (no fabrication)', () => {
    expect(READER_METADATA_ONLY).toHaveLength(4)
    for (const entry of READER_METADATA_ONLY) {
      expect(entry.note).toContain('未见于客户材料')
      expect(getReaderDocument(entry.id)).toBeUndefined()
    }
  })

  it('reader documents carry real source names (no internal paths)', () => {
    for (const doc of READER_DOCUMENTS) {
      expect(doc.source).not.toMatch(/hfmzl|zzcl/)
      expect(doc.description.length).toBeGreaterThan(0)
      expect(doc.sections.length).toBeGreaterThan(0)
      for (const section of doc.sections) {
        expect(section.id).toMatch(/^[a-z0-9-]+$/)
      }
    }
  })
})

describe('UI-07 text & citation integrity', () => {
  it('houlun 论其人 carries 12 real attributed quotes with sources', () => {
    const houlun = getReaderDocument('houlun')!
    const section = houlun.sections.find((s) => s.id === 'lunqiren')!
    expect(section.paragraphs?.length).toBe(12)
    for (const p of section.paragraphs ?? []) {
      expect(p.citation?.attribution).toBeTruthy()
      expect(p.citation?.source).toBeTruthy()
      expect(p.text.length).toBeGreaterThan(5)
    }
    // Real quoted source: 《晋书》 attributions present.
    expect(section.paragraphs?.some((p) => p.citation?.source.includes('晋书'))).toBe(true)
  })

  it('citation never invents volume/page/edition numbers', () => {
    const text = JSON.stringify(READER_DOCUMENTS)
    expect(text).not.toMatch(/卷\d|页\d|第\d+卷/)
    // Citation granularity stays at document/source level.
    for (const doc of READER_DOCUMENTS) {
      if (doc.editionContext?.edition) {
        expect(doc.editionContext.work.length).toBeGreaterThan(0)
      }
    }
  })

  it('CitationBlock produces deterministic text without invented detail', () => {
    const wrapper = mount(CitationBlock, {
      props: {
        title: '《后论》',
        attribution: '唐代·房玄龄等',
        work: '《后论》',
        section: '论其人',
        source: '客户提供：后论文稿（docx）',
      },
      slots: { default: '「引文」' },
    })
    expect(wrapper.find('blockquote').text()).toContain('引文')
    expect(wrapper.find('.citation__meta').text()).toContain('作品：《后论》')
    expect(wrapper.find('.citation__meta').text()).toContain('章节：论其人')
    expect(wrapper.find('.citation__copy').attributes('aria-label')).toContain('复制引用')
  })
})

describe('UI-07 reader navigation & states', () => {
  it('invalid reader id renders not-found with recovery links', async () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [{ path: '/reader/:id', component: ReaderDocView }],
    })
    await router.push('/reader/does-not-exist')
    await router.isReady()
    const wrapper = mount(ReaderDocView, { global: { plugins: [router] } })
    expect(wrapper.find('.reader__not-found').exists()).toBe(true)
    expect(wrapper.text()).toContain('未找到该文献')
    const hrefs = wrapper.findAll('a').map((a) => a.attributes('href'))
    expect(hrefs).toContain('/search')
    expect(hrefs).toContain('/archive')
  })

  it('renders a real full-text document with sections', async () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [{ path: '/reader/:id', component: ReaderDocView }],
    })
    await router.push('/reader/houlun')
    await router.isReady()
    const wrapper = mount(ReaderDocView, { global: { plugins: [router] } })
    expect(wrapper.find('.reader__title').text()).toContain('后论')
    expect(wrapper.findAll('.reader__section').length).toBe(4)
    expect(wrapper.findAll('.citation').length).toBe(12)
    expect(wrapper.find('.reader__paragraph').exists()).toBe(true)
  })
})

describe('UI-07 search integration', () => {
  it('reader documents are searchable and route to /reader/:id', () => {
    const queries: Record<string, string> = { houlun: '后论', qichuan: '其传' }
    for (const doc of READER_DOCUMENTS) {
      const results = searchIndex(queries[doc.id] ?? doc.title)
      expect(
        results.some((r) => r.entry.route === `/reader/${doc.id}`),
        doc.id,
      ).toBe(true)
    }
    const readerEntries = SEARCH_INDEX.filter((e) => e.route?.startsWith('/reader/'))
    // 2 TEXT + 2 ARCHIVE (archive 其传/后论 records now point to the reader)
    expect(readerEntries.length).toBeGreaterThanOrEqual(2)
    for (const entry of readerEntries.filter((e) => e.type === 'text')) {
      expect(entry.searchableText).not.toMatch(/hfmzl|zzcl/)
    }
  })
})

describe('UI-07 accessibility & clinical boundary', () => {
  it('passes axe on a full-text document', async () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [{ path: '/reader/:id', component: ReaderDocView }],
    })
    await router.push('/reader/houlun')
    await router.isReady()
    const wrapper = mount(ReaderDocView, { attachTo: document.body, global: { plugins: [router] } })
    const results = await axe.run(wrapper.element as HTMLElement)
    wrapper.unmount()
    expect(results.violations).toHaveLength(0)
  })

  it('contains no clinical recommendation expression', () => {
    const text = JSON.stringify([READER_DOCUMENTS, READER_METADATA_ONLY])
    expect(text).not.toMatch(/治疗推荐|疗效显著|适用于.*疾病|预约|问诊/)
  })
})
