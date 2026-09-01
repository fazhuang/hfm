/**
 * UX2-P4 Scholarly Discovery — BibliographicRecord results + truth tests.
 *
 * Covers the UX2-P4 contract: results render via the shared BibliographicRecord
 * primitive; 515/5 shown separately; facet semantic = search-index type counts;
 * discovery ≠ resource availability (no fake full-text/PDF/reader/download);
 * NB-06 no synthesized citation; empty state truthful; ResearchSearchView uses
 * the shared P0 state mapping (no local duplication); heading + axe.
 */
import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import { createMemoryHistory, createRouter } from 'vue-router'
import axe from 'axe-core'
import SearchView from '../views/search/SearchView.vue'
import ResearchSearchView from '../views/research/ResearchSearchView.vue'
import {
  AUDITED_PAPER_TOTAL,
  SEARCHABLE_PAPER_TOTAL,
  facetCounts,
  searchIndex,
} from '../data/searchIndex'
import { presentationLabel, resolvePresentationState } from '../presentation/stateMapping'

async function mountSearch(query: string): Promise<ReturnType<typeof mount>> {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [{ path: '/search', component: SearchView }],
  })
  await router.push(query ? `/search?q=${encodeURIComponent(query)}` : '/search')
  await router.isReady()
  return mount(SearchView, { global: { plugins: [router] } })
}

describe('UX2-P4 — results render via BibliographicRecord', () => {
  it('renders search results through the shared record primitive', async () => {
    const wrapper = await mountSearch('针灸甲乙经')
    const records = wrapper.findAll('[data-primitive="bib-record"]')
    expect(records.length).toBeGreaterThan(0)
    for (const record of records) {
      expect(record.find('.bib-record__title').exists()).toBe(true)
    }
    // paper results go through the aligned BibliographyEntry — which itself
    // renders a BibliographicRecord (query that ranks a paper on page 1)
    const paperWrapper = await mountSearch('读法')
    const paperRecords = paperWrapper.findAll('.bib-entry [data-primitive="bib-record"]')
    expect(paperRecords.length).toBeGreaterThan(0)
  })

  it('renders result metadata from governed search-index data (author/year/kind/source)', async () => {
    const wrapper = await mountSearch('黄龙祥')
    const records = wrapper.findAll('[data-primitive="bib-record"]')
    expect(records.length).toBeGreaterThan(0)
    const text = records.map((r) => r.text()).join(' ')
    expect(text).toContain('黄龙祥')
    expect(text).toContain('版本')
  })
})

describe('UX2-P4 — count integrity (515/5 + facets)', () => {
  it('515/5 paper split shown separately (no 515 searchable claim)', async () => {
    const wrapper = await mountSearch('针灸甲乙经')
    expect(SEARCHABLE_PAPER_TOTAL).toBe(5)
    expect(AUDITED_PAPER_TOTAL).toBe(515)
    expect(wrapper.text()).toContain('已结构化 5')
    expect(wrapper.text()).toContain('审计 515')
  })

  it('facet counts come from the actual result set (search-index type counts)', async () => {
    const wrapper = await mountSearch('针灸甲乙经')
    const counts = facetCounts(searchIndex('针灸甲乙经', 'all'))
    for (const facet of counts) {
      const button = wrapper
        .findAll('.facet-btn')
        .find((b) => b.find('.facet-btn__label').text() === facet.label)
      if (button) {
        expect(button.find('.facet-btn__count').text()).toBe(String(facet.count))
      }
    }
  })
})

describe('UX2-P4 — discovery ≠ resource availability', () => {
  it('no fake full-text/PDF/reader/download affordances on results', async () => {
    const wrapper = await mountSearch('针灸甲乙经')
    const resultsText = wrapper.find('.result-list').text()
    expect(resultsText).not.toContain('阅读全文')
    expect(resultsText).not.toMatch(/查看\s*PDF|下载\s*PDF/i)
    expect(resultsText).not.toContain('在线阅读')
    expect(resultsText).not.toContain('下载')
  })

  it('NB-06: no synthesized page/volume citation', async () => {
    const wrapper = await mountSearch('针灸甲乙经')
    expect(wrapper.find('.result-list').text()).not.toMatch(/第\s*\d+\s*(页|卷)/)
  })

  it('metadata-only records show 仅题录 (METADATA_ONLY), never 可阅读', async () => {
    const wrapper = await mountSearch('针灸甲乙经')
    const paperRecord = wrapper.find('.bib-entry [data-primitive="bib-record"]')
    if (paperRecord.exists()) {
      const badge = paperRecord.find('.hfm-status')
      expect(badge.attributes('data-status')).toBe('METADATA_ONLY')
      expect(badge.text()).toBe('仅题录')
    }
  })
})

describe('UX2-P4 — empty state & navigation truth', () => {
  it('zero results render a truthful empty state (no fake success)', async () => {
    const wrapper = await mountSearch('完全不存在的词xyz')
    expect(wrapper.find('.empty-state').exists()).toBe(true)
    expect(wrapper.text()).toContain('未找到匹配')
    expect(wrapper.findAll('[data-primitive="bib-record"]')).toHaveLength(0)
    // the truthful count line reports 0 — never a fabricated positive count
    expect(wrapper.text()).toContain('找到 0 条结果')
    expect(wrapper.text()).not.toMatch(/找到 [1-9]\d* 条结果/)
  })

  it('result hrefs resolve to real routes from the index', async () => {
    const wrapper = await mountSearch('针灸甲乙经')
    const links = wrapper.findAll('.result-list a[href]')
    expect(links.length).toBeGreaterThan(0)
    for (const link of links) {
      const href = link.attributes('href') ?? ''
      expect(href.startsWith('/')).toBe(true)
    }
  })
})

describe('UX2-P4 — ResearchSearchView uses the shared P0 state mapping', () => {
  async function mountResearch(query: string): Promise<ReturnType<typeof mount>> {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [{ path: '/research/search', component: ResearchSearchView }],
    })
    await router.push(`/research/search?q=${encodeURIComponent(query)}`)
    await router.isReady()
    return mount(ResearchSearchView, { global: { plugins: [router] } })
  }

  it('status labels derive from the P0 G1-C mapping (no local duplication)', async () => {
    const wrapper = await mountResearch('甲乙经')
    const statusLabels = wrapper
      .findAll('.research-result__meta div')
      .filter((row) => row.find('dt').text() === '状态')
      .map((row) => row.find('dd').text())
    expect(statusLabels.length).toBeGreaterThan(0)
    const p0Labels = new Set(['数字资源可阅', '仅题录', '存目', '资料整理中', '尚有争议', '文献阙佚'])
    for (const label of statusLabels) {
      expect(p0Labels.has(label)).toBe(true)
    }
    // the old local labels are gone
    expect(statusLabels).not.toContain('已展示')
    expect(statusLabels).not.toContain('元数据已录')
    expect(statusLabels).not.toContain('整理中')
  })

  it('mapping is deterministic: AVAILABLE → 数字资源可阅, METADATA_ONLY → 仅题录', () => {
    expect(
      presentationLabel(resolvePresentationState({ contentStatus: 'AVAILABLE', hasMetadata: true })),
    ).toBe('数字资源可阅')
    expect(
      presentationLabel(resolvePresentationState({ contentStatus: 'METADATA_ONLY', hasMetadata: true })),
    ).toBe('仅题录')
  })
})

describe('UX2-P4 — structure & accessibility', () => {
  it('single h1 + heading hierarchy on the discovery surface', async () => {
    const wrapper = await mountSearch('针灸甲乙经')
    const headings = wrapper.findAll('h1, h2, h3').map((h) => Number(h.element.tagName.slice(1)))
    expect(headings.filter((l) => l === 1)).toHaveLength(1)
    for (let i = 1; i < headings.length; i += 1) {
      expect(headings[i] - headings[i - 1]).toBeLessThanOrEqual(1)
    }
  })

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
      expect(results.violations, `axe on q=${query}`).toHaveLength(0)
    }
  })
})
