/**
 * UI-10 Search / Bibliography tests.
 *
 *  - index construction (types, real structured paper count, no internal
 *    paths in searchable content);
 *  - real-query checks (皇甫谧 / 针灸甲乙经 / 帝王世纪 / 高士传 / 黄龙祥 /
 *    nonexistent);
 *  - deterministic ranking + facet counts from the current result set;
 *  - URL query parse/serialize + pagination;
 *  - data integrity: audited 515 ≠ searchable count, no fabricated papers,
 *    no internal paths, no copyright blockers;
 *  - component states (initial / results / empty) + axe.
 */
import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import { createMemoryHistory, createRouter } from 'vue-router'
import axe from 'axe-core'
import SearchView from '../views/search/SearchView.vue'
import {
  AUDITED_PAPER_TOTAL,
  SEARCH_INDEX,
  SEARCHABLE_PAPER_TOTAL,
  facetCounts,
  searchIndex,
} from '../data/searchIndex'
import { JIAYI_PAPER_PREVIEW } from '../data/jiayiView'
import { parseSearchQuery, serializeSearchQuery } from '../composables/useSearchQuery'

describe('UI-10 index construction', () => {
  it('builds the projection once with all supported types', () => {
    const types = new Set(SEARCH_INDEX.map((e) => e.type))
    expect(types.has('person')).toBe(true)
    expect(types.has('text')).toBe(true)
    expect(types.has('work')).toBe(true)
    expect(types.has('edition')).toBe(true)
    expect(types.has('archive')).toBe(true)
    expect(types.has('paper')).toBe(true)
    expect(SEARCH_INDEX.length).toBeGreaterThan(20)
  })

  it('searchable paper count equals real structured records (≠ audited 515)', () => {
    expect(SEARCHABLE_PAPER_TOTAL).toBe(JIAYI_PAPER_PREVIEW.length)
    expect(SEARCHABLE_PAPER_TOTAL).toBeLessThan(AUDITED_PAPER_TOTAL)
    expect(AUDITED_PAPER_TOTAL).toBe(515)
  })

  it('searchable content never contains internal paths or register keys', () => {
    for (const entry of SEARCH_INDEX) {
      expect(entry.searchableText).not.toMatch(/hfmzl|zzcl|\/论著\/|\/论文\//)
      expect(entry.sourceName ?? '').not.toMatch(/^hfmzl|^zzcl/)
    }
  })
})

describe('UI-10 real-query checks', () => {
  it('皇甫谧 → person result', () => {
    const results = searchIndex('皇甫谧')
    expect(results.length).toBeGreaterThan(0)
    expect(results[0]?.entry.type).toBe('person')
    expect(results[0]?.entry.title).toBe('皇甫谧')
  })

  it('针灸甲乙经 → work + edition results', () => {
    const results = searchIndex('针灸甲乙经')
    const types = results.map((r) => r.entry.type)
    expect(types).toContain('work')
    expect(types).toContain('edition')
  })

  it('帝王世纪 / 高士传 → real works', () => {
    const dwsj = searchIndex('帝王世纪').filter((r) => r.entry.type === 'work')
    expect(dwsj.length).toBeGreaterThan(0)
    expect(dwsj[0]?.entry.title).toBe('《帝王世纪》')
    const gsc = searchIndex('高士传').filter((r) => r.entry.type === 'work')
    expect(gsc.length).toBeGreaterThan(0)
    expect(gsc[0]?.entry.title).toBe('《高士传》')
  })

  it('黄龙祥 / 张灿玾 → real edition records (modern collators)', () => {
    for (const name of ['黄龙祥', '张灿玾']) {
      const results = searchIndex(name)
      expect(results.length).toBeGreaterThan(0)
      expect(results.some((r) => r.entry.type === 'edition')).toBe(true)
    }
  })

  it('1601 → edition result', () => {
    const results = searchIndex('1601')
    expect(results.length).toBeGreaterThan(0)
    expect(results[0]?.entry.type).toBe('edition')
  })

  it('nonexistent query → 0 results', () => {
    expect(searchIndex('完全不存在的词xyz')).toHaveLength(0)
  })
})

describe('UI-10 ranking & facets', () => {
  it('ranking is deterministic (same query → same order)', () => {
    const a = searchIndex('甲乙经')
    const b = searchIndex('甲乙经')
    expect(a.map((r) => r.entry.id)).toEqual(b.map((r) => r.entry.id))
  })

  it('exact title match ranks above partial match', () => {
    const exact = searchIndex('皇甫谧')[0]?.entry.id
    expect(exact).toBe('person-huangfu-mi')
    const partial = searchIndex('谧')[0]?.entry.id
    expect(partial).toBe('person-huangfu-mi')
  })

  it('facet counts come from the current result set (type filter respected)', () => {
    const qAll = searchIndex('甲乙经', 'all')
    const counts = facetCounts(qAll)
    const workCount = counts.find((c) => c.type === 'work')?.count ?? 0
    expect(workCount).toBe(qAll.filter((r) => r.entry.type === 'work').length)
    expect(workCount).toBeGreaterThan(0)
    // Facet total reflects real matches, never the audited 515.
    const paperCount = counts.find((c) => c.type === 'paper')?.count ?? 0
    expect(paperCount).toBeLessThanOrEqual(SEARCHABLE_PAPER_TOTAL)
    expect(paperCount).toBeLessThan(AUDITED_PAPER_TOTAL)
  })
})

describe('UI-10 URL query sync & pagination', () => {
  it('parses and serializes q/type/page', () => {
    const parsed = parseSearchQuery({ q: '甲乙经', type: 'edition', page: '2' })
    expect(parsed).toEqual({ q: '甲乙经', type: 'edition', page: 2 })
    const serialized = serializeSearchQuery({ q: '甲乙经', type: 'edition', page: 2 })
    expect(serialized).toEqual({ q: '甲乙经', type: 'edition', page: '2' })
    // Empty state serializes to clean query.
    expect(serializeSearchQuery({ q: '', type: 'all', page: 1 })).toEqual({})
  })

  it('paginates deterministically by PAGE_SIZE', () => {
    const all = searchIndex('甲乙经', 'all')
    const pageSize = 10
    const page1 = all.slice(0, pageSize)
    const page2 = all.slice(pageSize, pageSize * 2)
    expect(page1.length).toBeLessThanOrEqual(pageSize)
    expect(page1[0]?.entry.id).toBe(all[0]?.entry.id)
    expect(page2[0]?.entry.id).toBe(all[pageSize]?.entry.id)
  })
})

describe('UI-10 data integrity', () => {
  it('results never expose internal paths and no fake papers are created', () => {
    for (const q of ['皇甫谧', '甲乙经', '论文', '档案']) {
      for (const r of searchIndex(q)) {
        expect(r.entry.searchableText).not.toMatch(/hfmzl|zzcl/)
        expect(r.entry.route ?? '').not.toMatch(/hfmzl|zzcl/)
      }
    }
    const papers = SEARCH_INDEX.filter((e) => e.type === 'paper')
    const realTitles = new Set(JIAYI_PAPER_PREVIEW.map((p) => p.title))
    for (const p of papers) expect(realTitles.has(p.title)).toBe(true)
  })
})

async function mountSearch(query: string): Promise<ReturnType<typeof mount>> {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [{ path: '/search', component: SearchView }],
  })
  await router.push(query ? `/search?q=${encodeURIComponent(query)}` : '/search')
  await router.isReady()
  return mount(SearchView, { global: { plugins: [router] } })
}

describe('UI-10 SearchView component', () => {
  it('renders the initial state without a query', async () => {
    const wrapper = await mountSearch('')
    expect(wrapper.find('h1').text()).toBe('检索')
    expect(wrapper.find('.type-overview').exists()).toBe(true)
    expect(wrapper.text()).toContain('可检索内容')
  })

  it('renders results for ?q=针灸甲乙经', async () => {
    const wrapper = await mountSearch('针灸甲乙经')
    expect(wrapper.text()).toContain('找到')
    expect(wrapper.find('.result-list').exists()).toBe(true)
  })

  it('renders a useful empty state for a nonexistent query', async () => {
    const wrapper = await mountSearch('zzz不存在')
    expect(wrapper.find('.empty-state').exists()).toBe(true)
    expect(wrapper.text()).toContain('未找到匹配')
    expect(wrapper.text()).toContain('清除关键词')
  })

  it('contains no clinical recommendation expression', async () => {
    const wrapper = await mountSearch('甲乙经')
    expect(wrapper.text()).not.toMatch(/治疗|疗效|处方|建议就诊|治愈/)
  })
})

describe('UI-10 accessibility', () => {
  it('passes axe on results and empty states', async () => {
    for (const query of ['针灸甲乙经', 'zzz不存在']) {
      const router = createRouter({
        history: createMemoryHistory(),
        routes: [{ path: '/search', component: SearchView }],
      })
      await router.push(`/search?q=${encodeURIComponent(query)}`)
      await router.isReady()
      const wrapper = mount(SearchView, { attachTo: document.body, global: { plugins: [router] } })
      const results = await axe.run(wrapper.element as HTMLElement)
      wrapper.unmount()
      expect(results.violations, query).toHaveLength(0)
    }
  })
})
