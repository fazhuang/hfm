/**
 * /knowledge — the term list must come from the public projection, and must
 * not silently render as empty when the API answer is the real envelope.
 *
 * This is the check that was missing: the page called the raw GET and read
 * `terms` off the envelope instead of off `data`, so it reported "0 条 /
 * 尚未发布" while 30 terms were published.
 */
import { describe, expect, it, vi, beforeEach, afterEach } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import KnowledgeGraphView from '../views/knowledge/KnowledgeGraphView.vue'

const TERMS = [
  { entity_id: 'K-ACUPOINT-三阴交', term_type: 'acupoint', term_name: '三阴交', publication_status: 'PUBLISHED' },
  { entity_id: 'K-MERIDIAN-任脉', term_type: 'meridian', term_name: '任脉', publication_status: 'PUBLISHED' },
  { entity_id: 'K-DISEASE-中风', term_type: 'disease_symptom', term_name: '中风', publication_status: 'PUBLISHED' },
  { entity_id: 'K-TREATMENT-刺络', term_type: 'technique', term_name: '刺络', publication_status: 'PUBLISHED' },
]

const envelope = (data: unknown) => ({
  ok: true,
  status: 200,
  json: async () => ({ success: true, timestamp: 't', message: 'ok', data }),
})

beforeEach(() => {
  vi.stubGlobal(
    'fetch',
    vi.fn().mockResolvedValue(envelope({ terms: TERMS, total: TERMS.length })),
  )
})
afterEach(() => vi.unstubAllGlobals())

describe('knowledge graph page', () => {
  it('renders the published terms grouped by type', async () => {
    const wrapper = mount(KnowledgeGraphView)
    await flushPromises()
    const text = wrapper.text()
    expect(text).toContain('三阴交')
    expect(text).toContain('任脉')
    expect(text).toContain('中风')
    expect(text).toContain('刺络')
    // 分组标题是中文名，不是 type 原文
    expect(text).toContain('经穴')
    expect(text).toContain('经脉')
    expect(text).toContain('病症')
    expect(text).toContain('治法')
    expect(wrapper.text()).not.toContain('知识实体尚未发布')
  })

  it('states the real total, not zero', async () => {
    const wrapper = mount(KnowledgeGraphView)
    await flushPromises()
    expect(wrapper.find('#kg-terms-title').exists()).toBe(true)
    expect(wrapper.text()).toContain(`${TERMS.length}`)
  })

  it('degrades honestly when the projection is unavailable', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('offline')))
    const wrapper = mount(KnowledgeGraphView)
    await flushPromises()
    expect(wrapper.text()).toContain('暂时无法读取知识实体')
  })
})
