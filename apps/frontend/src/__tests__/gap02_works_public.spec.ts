/**
 * GAP-02 — WorksView /api/v1/public/works integration tests.
 *
 * Proves: backend works payload → presentation projection mapping; safe
 * fallback for failure/empty data; WorksView performs exactly one real
 * /api/v1/public/works request on mount and exposes the source marker;
 * the static WORK_COLLECTION fallback still renders the accepted links.
 */
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import { defineComponent } from 'vue'
import WorksView from '../views/works/WorksView.vue'
import { usePublicWorks } from '../composables/usePublicWorks'
import { toPublicWorkRows } from '../presentation/publicWorks'
import type { WorkSummary } from '../types/public'

const WORK: WorkSummary = {
  work_id: 'w-jiayi',
  title: '针灸甲乙经',
  dynasty: '西晋',
  category: '医书',
  edition_count: 19,
  publication_status: 'published',
}

function envelope(data: unknown) {
  return { success: true, timestamp: 't', message: 'ok', data }
}

function okResponse(data: unknown) {
  return { ok: true, status: 200, json: async () => envelope(data) }
}

beforeEach(() => {
  vi.restoreAllMocks()
})

describe('works public projection — backend payload mapping', () => {
  it('maps backend work rows to presentation rows with a canonical route', () => {
    const rows = toPublicWorkRows([WORK])
    expect(rows).toHaveLength(1)
    expect(rows[0]).toEqual({
      workId: 'w-jiayi',
      title: '针灸甲乙经',
      meta: '西晋 · 医书',
      editionCount: 19,
      href: '/works/w-jiayi',
    })
  })

  it('omits absent dynasty/category and zero edition counts (never 未知/N/A)', () => {
    const rows = toPublicWorkRows([{ ...WORK, dynasty: null, category: null, edition_count: 0 }])
    expect(rows[0]?.meta).toBe('')
    expect(rows[0]?.editionCount).toBe(0)
  })
})

function harness(fetcher: (page?: number, signal?: AbortSignal) => Promise<unknown>) {
  const Harness = defineComponent({
    template: '<div />',
    setup() {
      return { ...usePublicWorks(fetcher as never) }
    },
  })
  return mount(Harness)
}

describe('works public composable — graceful degradation states', () => {
  it('success path sets source=backend with real works', async () => {
    let called = 0
    const fake = async () => {
      called += 1
      return { works: [WORK], total: 1 }
    }
    const host = harness(fake)
    await flushPromises()
    expect(called).toBe(1)
    expect((host.vm as { source: string }).source).toBe('backend')
    expect((host.vm as { works: WorkSummary[] }).works).toHaveLength(1)
    host.unmount()
  })

  it('failure path degrades to fallback without throwing', async () => {
    const fake = async () => {
      throw new Error('boom')
    }
    const host = harness(fake)
    await flushPromises()
    expect((host.vm as { source: string }).source).toBe('fallback')
    expect((host.vm as { failed: boolean }).failed).toBe(true)
    host.unmount()
  })
})

describe('WorksView integration', () => {
  it('mounts, issues exactly one /api/v1/public/works request, marks source=backend', async () => {
    const fetchMock = vi.fn().mockResolvedValue(okResponse({ works: [WORK], total: 1 }))
    vi.stubGlobal('fetch', fetchMock)
    const wrapper = mount(WorksView)
    await flushPromises()
    await wrapper.vm.$nextTick()
    const worksCalls = fetchMock.mock.calls.filter(
      (c) => (c[0] as string) === '/api/v1/public/works?page=1&page_size=20',
    )
    expect(worksCalls).toHaveLength(1)
    expect(wrapper.find('.works').attributes('data-works-source')).toBe('backend')
    expect(wrapper.text()).toContain('已发布作品 1 部')
    expect(wrapper.text()).toContain('针灸甲乙经')
    expect(wrapper.find('a[href="/works/w-jiayi"]').exists()).toBe(true)
    wrapper.unmount()
    vi.unstubAllGlobals()
  })

  it('backend failure degrades to fallback and the static WORK layer still renders', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('network down')))
    const wrapper = mount(WorksView)
    await flushPromises()
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.works').attributes('data-works-source')).toBe('fallback')
    const hrefs = wrapper.findAll('a').map((a) => a.attributes('href'))
    // Static WORK_COLLECTION links preserved on the fallback path.
    expect(hrefs).toContain('/jiayi')
    expect(hrefs).toContain('/yan')
    expect(hrefs).toContain('/search?q=针灸甲乙经')
    expect(hrefs).toContain('/archive')
    wrapper.unmount()
    vi.unstubAllGlobals()
  })

  it('empty backend payload renders static content and marks fallback (no visible backend data)', async () => {
    const fetchMock = vi.fn().mockResolvedValue(okResponse({ works: [], total: 0 }))
    vi.stubGlobal('fetch', fetchMock)
    const wrapper = mount(WorksView)
    await flushPromises()
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.works').attributes('data-works-source')).toBe('fallback')
    expect(wrapper.text()).not.toContain('已发布作品 0 部')
    expect(wrapper.text()).toContain('作品目录')
    wrapper.unmount()
    vi.unstubAllGlobals()
  })
})
