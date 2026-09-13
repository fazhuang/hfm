/**
 * CF-06 SearchView tests (real public search API orchestration).
 *
 * The public surface is wired to searchPublicHits → GET /api/v1/public/search.
 * These component tests stub ONLY the API-client transport (unit boundary,
 * CF-06 §15); real-browser acceptance of the full chain
 * (Browser → Vite proxy → FastAPI → PostgreSQL → JSON → render) is the
 * golden real-runtime journey + the CF-06 real browser gate — never mocked.
 *
 * Coverage: idle / loading / ready / empty / error (4xx ≠ 5xx), result
 * projection (kind labels, canonical navigation), URL q/page state, axe.
 */
import { afterEach, describe, expect, it, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createMemoryHistory, createRouter } from 'vue-router'
import axe from 'axe-core'
import { ApiError, searchPublicHits } from '../services/api'
import SearchView from '../views/search/SearchView.vue'
import type { PublicSearchPage } from '../services/api'

vi.mock('../services/api', () => {
  class ApiErrorMock extends Error {
    status: number
    constructor(message: string, status: number) {
      super(message)
      this.name = 'ApiError'
      this.status = status
    }
  }
  return {
    ApiError: ApiErrorMock,
    searchPublicHits: vi.fn(),
  }
})

const searchPublicHitsMock = vi.mocked(searchPublicHits)

function page(hits: PublicSearchPage['hits'], total?: number): PublicSearchPage {
  return { hits, total: total ?? hits.length, page: 1, page_size: 20 }
}

const PERSON_HIT = {
  kind: 'person',
  id: 'ENT-PERSON-HFM-HUANGFUMI',
  title: '皇甫谧',
  snippet: '',
  version_id: null,
  publication_status: 'PUBLISHED',
}

const mountedWrappers: ReturnType<typeof mount>[] = []

afterEach(() => {
  while (mountedWrappers.length > 0) {
    mountedWrappers.pop()?.unmount()
  }
  vi.unstubAllGlobals()
  searchPublicHitsMock.mockReset()
})

async function mountSearch(
  query: Record<string, string> = {},
  attach = false,
): Promise<{ wrapper: ReturnType<typeof mount>; router: ReturnType<typeof createRouter> }> {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [{ path: '/search', name: 'search', component: SearchView }],
  })
  await router.push({ path: '/search', query })
  await router.isReady()
  const wrapper = mount(SearchView, {
    attachTo: attach ? document.body : undefined,
    global: { plugins: [router] },
  })
  mountedWrappers.push(wrapper)
  return { wrapper, router }
}

describe('CF-06 idle & loading', () => {
  it('idle (no q): scope copy + static entry points; API not called', async () => {
    const { wrapper } = await mountSearch({})
    expect(wrapper.find('h1').text()).toBe('检索')
    expect(wrapper.text()).toContain('检索范围')
    expect(wrapper.text()).toContain('皇甫谧')
    expect(searchPublicHitsMock).not.toHaveBeenCalled()
  })

  it('shows a programmatically understandable loading state', async () => {
    let resolve!: (v: PublicSearchPage) => void
    searchPublicHitsMock.mockReturnValueOnce(
      new Promise<PublicSearchPage>((r) => {
        resolve = r
      }),
    )
    const { wrapper } = await mountSearch({ q: '皇甫谧' })
    expect(wrapper.find('[role="status"]').text()).toContain('正在检索')
    resolve(page([PERSON_HIT]))
    await vi.waitFor(() => {
      expect(wrapper.find('.result-row').exists()).toBe(true)
    })
  })
})

describe('CF-06 ready results & navigation', () => {
  it('renders a person result with the real canonical route', async () => {
    searchPublicHitsMock.mockResolvedValueOnce(page([PERSON_HIT]))
    const { wrapper } = await mountSearch({ q: '皇甫谧' })
    await vi.waitFor(() => {
      expect(wrapper.find('.result-row__type').text()).toBe('人物')
    })
    const link = wrapper.find('.result-row__link')
    expect(link.attributes('href')).toBe('/persons/ENT-PERSON-HFM-HUANGFUMI')
    expect(wrapper.find('.search-summary').text()).toContain('找到 1 条结果')
    expect(searchPublicHitsMock).toHaveBeenCalledWith('皇甫谧', 1, 20)
  })

  it('work results navigate to /works/:id; route-less kinds render without invented links', async () => {
    searchPublicHitsMock.mockResolvedValueOnce(
      page([
        PERSON_HIT,
        {
          kind: 'work',
          id: 'work-1',
          title: '《针灸甲乙经》',
          snippet: '',
          version_id: null,
          publication_status: 'PUBLISHED',
        },
        {
          kind: 'passage',
          id: 'p-1',
          title: '（片段）',
          snippet: '……皇甫谧曰……',
          version_id: null,
          publication_status: 'PUBLISHED',
        },
        {
          kind: 'edition',
          id: 'e-1',
          title: '明万历本',
          snippet: '',
          version_id: null,
          publication_status: 'PUBLISHED',
        },
      ]),
    )
    const { wrapper } = await mountSearch({ q: '皇甫' })
    await vi.waitFor(() => {
      expect(wrapper.findAll('.result-row').length).toBe(4)
    })
    const hrefs = wrapper.findAll('.result-row__link').map((n) => n.attributes('href'))
    expect(hrefs).toContain('/persons/ENT-PERSON-HFM-HUANGFUMI')
    expect(hrefs).toContain('/works/work-1')
    // Route-less kinds never fabricate a link.
    expect(hrefs).not.toContain('/reader/p-1')
    expect(hrefs).not.toContain('/e-1')
    const passageRow = wrapper.findAll('.result-row')[2]
    expect(passageRow.find('.result-row__link').exists()).toBe(false)
    expect(passageRow.find('.result-row__meta').text()).toContain('皇甫谧')
  })
})

describe('CF-06 empty vs error semantics', () => {
  it('empty (total 0) is a distinct valid state, never an error', async () => {
    searchPublicHitsMock.mockResolvedValueOnce(page([], 0))
    const { wrapper } = await mountSearch({ q: '完全没有的词xyz' })
    await vi.waitFor(() => {
      expect(wrapper.find('[data-search-state="empty"]').exists()).toBe(true)
    })
    expect(wrapper.find('[data-search-state="empty"]').text()).toContain('未找到匹配')
    expect(wrapper.find('[role="alert"]').exists()).toBe(false)
  })

  it('server failure (5xx) shows an error — never masked as 暂无结果', async () => {
    searchPublicHitsMock.mockRejectedValueOnce(new ApiError('public request failed: 500', 500))
    const { wrapper } = await mountSearch({ q: '皇甫谧' })
    await vi.waitFor(() => {
      expect(wrapper.find('[data-search-state="error"]').exists()).toBe(true)
    })
    const error = wrapper.find('[data-search-state="error"]')
    expect(error.text()).toContain('检索服务暂时不可用')
    expect(error.attributes('role')).toBe('alert')
    expect(wrapper.find('[data-search-state="empty"]').exists()).toBe(false)
  })

  it('client 4xx is distinguished from a server 5xx', async () => {
    searchPublicHitsMock.mockRejectedValueOnce(new ApiError('public request failed: 400', 400))
    const { wrapper } = await mountSearch({ q: '皇甫谧' })
    await vi.waitFor(() => {
      expect(wrapper.find('[data-search-state="error"]').text()).toContain('检索条件无效')
    })
  })

  it('network failure renders the error state with a retry affordance', async () => {
    searchPublicHitsMock.mockRejectedValueOnce(new TypeError('Failed to fetch'))
    const { wrapper } = await mountSearch({ q: '皇甫谧' })
    await vi.waitFor(() => {
      expect(wrapper.find('[data-search-state="error"]').exists()).toBe(true)
    })
    expect(wrapper.find('.search-error__retry').exists()).toBe(true)
    // Retry issues a fresh real request.
    searchPublicHitsMock.mockResolvedValueOnce(page([PERSON_HIT]))
    await wrapper.find('.search-error__retry').trigger('click')
    await vi.waitFor(() => {
      expect(wrapper.find('.result-row').exists()).toBe(true)
    })
    expect(searchPublicHitsMock).toHaveBeenCalledTimes(2)
  })
})

describe('CF-06 URL state & submission', () => {
  it('submitting updates the URL query and triggers the real API with paging', async () => {
    searchPublicHitsMock.mockResolvedValueOnce(page([PERSON_HIT]))
    const { wrapper, router } = await mountSearch({})
    await wrapper.find('.search-form input').setValue('皇甫谧')
    await wrapper.find('.search-form').trigger('submit')
    await vi.waitFor(() => {
      expect(router.currentRoute.value.query.q).toBe('皇甫谧')
    })
    await vi.waitFor(() => {
      expect(wrapper.find('.result-row').exists()).toBe(true)
    })
    expect(searchPublicHitsMock).toHaveBeenCalledWith('皇甫谧', 1, 20)
  })

  it('honors the URL page parameter on initial load', async () => {
    searchPublicHitsMock.mockResolvedValueOnce(page([PERSON_HIT], 25))
    await mountSearch({ q: '皇甫谧', page: '2' })
    await vi.waitFor(() => {
      expect(searchPublicHitsMock).toHaveBeenCalledWith('皇甫谧', 2, 20)
    })
  })
})

describe('CF-06 accessibility', () => {
  it('exposes a labeled input and passes axe on results', async () => {
    searchPublicHitsMock.mockResolvedValueOnce(page([PERSON_HIT]))
    const { wrapper } = await mountSearch({ q: '皇甫谧' }, true)
    await vi.waitFor(() => {
      expect(wrapper.find('.result-row').exists()).toBe(true)
    })
    const input = wrapper.find('input[type="search"]')
    expect(input.attributes('id')).toBe('search-input')
    const label = wrapper.find('label[for="search-input"]')
    expect(label.exists()).toBe(true)
    expect(label.text()).toBe('检索平台内容')
    const results = await axe.run(wrapper.element as HTMLElement)
    const messages = results.violations.map((v) => v.id)
    expect(messages).toEqual([])
  })
})
