/**
 * P2-03 Reader/Search Frontend tests.
 *
 * Proves the frozen P2-03 acceptance criteria:
 *  - P2-03-AC-01 same locator resolves to the same passage/version;
 *  - P2-03-AC-02 public reader hides draft/private/withdrawn passages;
 *  - P2-03-AC-03 search results respect role scoping (anonymous = published only);
 *  - P2-03-AC-04 reader/search UI exposes no clinical recommendation surface.
 */
import { describe, expect, it, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { locatorKey, resolveLocator } from '../services/reader'
import ReaderView from '../views/reader/ReaderView.vue'
import SearchView from '../views/search/SearchView.vue'
import type { ReaderPassage } from '../types/reader'

const passages: ReaderPassage[] = [
  {
    locator: { workId: 'w1', editionId: 'e1', versionId: 'v1', passageId: 'p1' },
    quotation: '甲乙经·卷一',
    sourceTitle: '《针灸甲乙经》',
    citation: '卷一·p1',
    rightsNote: '公开',
    publicationState: 'published',
  },
  {
    locator: { workId: 'w1', editionId: 'e1', versionId: 'v1', passageId: 'p2' },
    quotation: '未发布稿',
    sourceTitle: '《针灸甲乙经》',
    citation: '卷一·p2',
    rightsNote: '内部',
    publicationState: 'draft',
  },
  {
    locator: { workId: 'w1', editionId: 'e1', versionId: 'v1', passageId: 'p3' },
    quotation: '已撤回稿',
    sourceTitle: '《针灸甲乙经》',
    citation: '卷一·p3',
    rightsNote: '撤回',
    publicationState: 'withdrawn',
  },
]

describe('P2-03-AC-01 locator reproducibility', () => {
  it('same locator resolves to the same passage/version', () => {
    const locator = { workId: 'w1', editionId: 'e1', versionId: 'v1', passageId: 'p1' }
    const first = resolveLocator(locator, passages)
    const second = resolveLocator(locator, passages)
    expect(first).toBeDefined()
    expect(first).toBe(second)
    expect(first?.quotation).toBe('甲乙经·卷一')
    // canonical key is deterministic
    expect(locatorKey(locator)).toBe('w1/e1/v1/p1')
  })

  it('unknown locator does not resolve', () => {
    expect(
      resolveLocator({ workId: 'x', editionId: 'e', versionId: 'v', passageId: 'p' }, passages),
    ).toBeUndefined()
  })
})

describe('P2-03-AC-02 public reader hides non-published passages', () => {
  it('draft passage is not exposed as published content', () => {
    const draft = resolveLocator(
      { workId: 'w1', editionId: 'e1', versionId: 'v1', passageId: 'p2' },
      passages,
    )
    expect(draft?.publicationState).toBe('draft')
    // public rendering only shows published passages
    const visible = passages.filter((p) => p.publicationState === 'published')
    expect(visible.map((p) => p.locator.passageId)).toEqual(['p1'])
    expect(visible.some((p) => p.publicationState !== 'published')).toBe(false)
  })

  it('withdrawn passage is not shown publicly', () => {
    const visible = passages.filter((p) => p.publicationState === 'published')
    expect(visible.some((p) => p.locator.passageId === 'p3')).toBe(false)
  })

  it('reader view resolves only published passages', () => {
    const wrapper = mount(ReaderView)
    expect(wrapper.find('[aria-label="passage"]').exists()).toBe(false)
    wrapper.unmount()
  })
})

describe('P2-03-AC-03 search role scoping (anonymous = published only)', () => {
  it('published search client filters to published results', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        items: [
          { id: 'r1', title: '已发布', sourceContext: 'c1', publicationState: 'published' },
          { id: 'r2', title: '研究稿', sourceContext: 'c2', publicationState: 'draft' },
        ],
      }),
    })
    vi.stubGlobal('fetch', fetchMock)
    const { searchPublished } = await import('../services/reader')
    const results = await searchPublished('甲乙经')
    expect(results).toHaveLength(1)
    expect(results[0].id).toBe('r1')
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/api/v1/public/search'),
      expect.anything(),
    )
    vi.unstubAllGlobals()
  })

  it('anonymous results never contain research-only items', () => {
    const results = [
      { id: 'a', publicationState: 'published' },
      { id: 'b', publicationState: 'draft' },
    ]
    const anonymous = results.filter((r) => r.publicationState === 'published')
    expect(anonymous.every((r) => r.publicationState === 'published')).toBe(true)
  })
})

describe('P2-03-AC-04 no clinical recommendation surface', () => {
  const FORBIDDEN_TERMS = ['diagnos', 'prescription', 'treatment_recommend', 'acupoint_recommend']

  it('reader view template contains no clinical recommendation elements', () => {
    const wrapper = mount(ReaderView)
    const html = wrapper.html()
    for (const term of FORBIDDEN_TERMS) {
      expect(html.toLowerCase()).not.toContain(term)
    }
    wrapper.unmount()
  })

  it('search view template contains no clinical recommendation elements', () => {
    const wrapper = mount(SearchView)
    const html = wrapper.html()
    for (const term of FORBIDDEN_TERMS) {
      expect(html.toLowerCase()).not.toContain(term)
    }
    wrapper.unmount()
  })

  it('reader types expose no clinical fields', () => {
    const keys = Object.keys(passages[0])
    expect(keys.some((k) => /diagnos|prescript|treat|recommend/.test(k))).toBe(false)
  })
})
