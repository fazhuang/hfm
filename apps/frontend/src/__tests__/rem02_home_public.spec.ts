/**
 * REM-02 — homepage /api/v1/public/home integration tests.
 *
 * Proves: backend payload → projection adapter mapping; safe fallback for
 * failure and partial/missing data; HomeView performs exactly one real home
 * request on mount and exposes the source marker; the frozen 8-section
 * structure and hero search are preserved.
 */
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'
import { flushPromises, mount } from '@vue/test-utils'
import HomeView from '../views/HomeView.vue'
import { defineComponent } from 'vue'
import { mapPublicHomeToEnrichment } from '../data/homePublicEnrichment'
import { useHomePublicData } from '../composables/useHomePublicData'

const STUB = { template: '<div />' }
const SECTION_IDS = [
  'home-hero',
  'home-person',
  'home-yan',
  'home-book',
  'home-heritage',
  'home-closing',
]

function makeRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', component: STUB },
      { path: '/search', component: STUB },
    ],
  })
}

function mountHome() {
  return mount(HomeView, { attachTo: document.body, global: { plugins: [makeRouter()] } })
}

function envelope(data: unknown) {
  return { success: true, timestamp: 't', message: 'ok', data }
}

function okResponse(data: unknown) {
  return { ok: true, status: 200, json: async () => envelope(data) }
}

const HOME_PAYLOAD = {
  works: [
    {
      work_id: 'w-jiayi',
      title: '针灸甲乙经',
      dynasty: '西晋',
      category: '医书',
      edition_count: 19,
      publication_status: 'published',
    },
  ],
  counts: { works: 1, persons: 1, heritage_projects: 1, c_terms: 2 },
}

beforeEach(() => {
  vi.restoreAllMocks()
})

describe('home public adapter — backend payload mapping', () => {
  it('maps a real backend payload into typed enrichment', () => {
    const e = mapPublicHomeToEnrichment(HOME_PAYLOAD)
    expect(e.hasData).toBe(true)
    expect(e.works).toHaveLength(1)
    expect(e.works[0]?.work_id).toBe('w-jiayi')
    expect(e.counts).toEqual({ works: 1, persons: 1, heritage_projects: 1, c_terms: 2 })
  })

  it('defensive against partial/missing optional data (never throws)', () => {
    expect(mapPublicHomeToEnrichment(undefined).hasData).toBe(false)
    expect(mapPublicHomeToEnrichment(null).hasData).toBe(false)
    expect(mapPublicHomeToEnrichment({ works: 'nope' }).counts).toEqual({
      works: 0,
      persons: 0,
      heritage_projects: 0,
      c_terms: 0,
    })
    const partial = mapPublicHomeToEnrichment({ counts: { works: 3 } })
    expect(partial.counts.works).toBe(3)
    expect(partial.counts.persons).toBe(0)
    expect(partial.works).toEqual([])
    expect(partial.hasData).toBe(true)
  })

  it('drops malformed work rows but keeps valid ones', () => {
    const e = mapPublicHomeToEnrichment({
      works: [HOME_PAYLOAD.works[0], { title: 'no-id' }, null, 'x'],
      counts: HOME_PAYLOAD.counts,
    })
    expect(e.works).toHaveLength(1)
  })
})

function harness(fetcher: (signal?: AbortSignal) => Promise<unknown>) {
  const Harness = defineComponent({
    setup() {
      return { ...useHomePublicData(fetcher as never) }
    },
  })
  return mount(Harness, { global: { plugins: [makeRouter()] } })
}

describe('home public composable — graceful degradation states', () => {
  it('success path sets source=backend with mapped enrichment', async () => {
    let called = 0
    const fakeFetch = async () => {
      called += 1
      return HOME_PAYLOAD
    }
    const host = harness(fakeFetch)
    await flushPromises()
    expect(called).toBe(1)
    expect((host.vm as { source: string }).source).toBe('backend')
    expect((host.vm as { enrichment: { hasData: boolean } }).enrichment.hasData).toBe(true)
    host.unmount()
  })

  it('failure path degrades to fallback without throwing', async () => {
    const fakeFetch = async () => {
      throw new Error('boom')
    }
    const host = harness(fakeFetch)
    await flushPromises()
    expect((host.vm as { source: string }).source).toBe('fallback')
    expect((host.vm as { failed: boolean }).failed).toBe(true)
    host.unmount()
  })
})

describe('HomeView integration', () => {
  it('mounts, issues exactly one /api/v1/public/home request, marks source=backend', async () => {
    const fetchMock = vi.fn().mockResolvedValue(okResponse(HOME_PAYLOAD))
    vi.stubGlobal('fetch', fetchMock)
    const wrapper = mountHome()
    await flushPromises()
    await wrapper.vm.$nextTick()
    const homeCalls = fetchMock.mock.calls.filter((c) => (c[0] as string) === '/api/v1/public/home')
    expect(homeCalls).toHaveLength(1)
    expect(wrapper.find('.home').attributes('data-home-source')).toBe('backend')
    wrapper.unmount()
    vi.unstubAllGlobals()
  })

  it('backend failure degrades to fallback and the contract blocks still render', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('network down')))
    const wrapper = mountHome()
    await flushPromises()
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.home').attributes('data-home-source')).toBe('fallback')
    const ids = wrapper.findAll('section[id^="home-"]').map((s) => s.attributes('id'))
    expect(ids).toEqual(SECTION_IDS)
    // Hero content intact on the failure path.
    expect(wrapper.find('h1').text()).toBe('皇甫谧人文数字平台')
    expect(wrapper.find('#home-search-input').exists()).toBe(true)
    wrapper.unmount()
    vi.unstubAllGlobals()
  })

  it('empty backend payload marks fallback (no visible backend data)', async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValue(
        okResponse({
          works: [],
          counts: { works: 0, persons: 0, heritage_projects: 0, c_terms: 0 },
        }),
      )
    vi.stubGlobal('fetch', fetchMock)
    const wrapper = mountHome()
    await flushPromises()
    // Nothing from the backend participates visually -> truthful fallback marker.
    expect(wrapper.find('.home').attributes('data-home-source')).toBe('fallback')
    expect(wrapper.findAll('section[id^="home-"]')).toHaveLength(6)
    expect(wrapper.text()).not.toContain('已上线公开人物')
    wrapper.unmount()
    vi.unstubAllGlobals()
  })

  it('PARTICIPATION: the published person projection renders its assertions in the 人物 block', async () => {
    const fetchMock = vi.fn((url: string) => {
      if (url.includes('/public/persons/')) {
        return Promise.resolve(
          okResponse({
            entity_id: 'ENT-PERSON-HFM-HUANGFUMI',
            name_zh: '皇甫谧',
            name_pinyin: null,
            courtesy_name: null,
            pseudonym: null,
            dynasty: null,
            publication_status: 'PUBLISHED',
            assertions: [
              {
                id: 'a1',
                predicate: '医学地位',
                value: '针灸鼻祖；《针灸甲乙经》为规范千年之医学经典',
                object_entity_id: null,
                editorial_status: 'draft',
                confidence: 'medium',
              },
            ],
            events: [],
          }),
        )
      }
      if (url.includes('/public/home')) {
        return Promise.resolve(
          okResponse({ works: [], counts: { works: 14, persons: 17, heritage_projects: 0, c_terms: 30 } }),
        )
      }
      if (url.includes('/public/works/')) {
        return Promise.resolve(
          okResponse({ work_id: 'WORK-JIAYI', title: '针灸甲乙经', dynasty: null, category: 'classic', publication_status: 'PUBLISHED', rights_status: 'public_domain', editions: [] }),
        )
      }
      if (url.includes('/public/heritage')) return Promise.resolve(okResponse({ projects: [], total: 0 }))
      return Promise.resolve(okResponse({}))
    })
    vi.stubGlobal('fetch', fetchMock)
    const wrapper = mountHome()
    await flushPromises()

    // T0 participates visibly in the 人物 block
    expect(wrapper.find('#home-person').attributes('data-source')).toBe('backend')
    expect(wrapper.find('#home-person').text()).toContain('针灸鼻祖')
    // T0 participates visibly in the hero register
    expect(wrapper.find('#home-hero').text()).toContain('已发布著作')
    expect(wrapper.find('.home').attributes('data-home-source')).toBe('backend')
    // contract structure intact alongside participation
    expect(wrapper.findAll('section[id^="home-"]')).toHaveLength(6)
    expect(wrapper.find('h1').text()).toBe('皇甫谧人文数字平台')
    expect(wrapper.find('#home-search-input').exists()).toBe(true)
    wrapper.unmount()
    vi.unstubAllGlobals()
  })
})
