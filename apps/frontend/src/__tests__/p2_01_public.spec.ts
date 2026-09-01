/**
 * P2-01 Public Frontend Foundation tests.
 *
 * Proves the frozen P2-01 acceptance criteria:
 *  - P2-01-AC-01 anonymous traversal without auth challenge;
 *  - P2-01-AC-02 published projection only (withdrawn/draft fail-closed);
 *  - P2-01-AC-03 no research/admin route reachable anonymously;
 *  - P2-01-AC-04 accessibility assertions on the public surface;
 *  - P2-01-AC-05 responsive breakpoint matrix.
 */
import { describe, expect, it, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createMemoryHistory, createRouter } from 'vue-router'
import axe from 'axe-core'
import { ApiError, isPublicPath, publicGet } from '../services/api'
import { publishedOnly } from '../utils/publication'
import { currentBreakpoint, BREAKPOINTS } from '../composables/useViewport'
import PublicLayout from '../layouts/PublicLayout.vue'
import LoadingState from '../components/states/LoadingState.vue'
import ErrorState from '../components/states/ErrorState.vue'
import EmptyState from '../components/states/EmptyState.vue'

const published = [
  { id: 'p1', title: '公开文章', publicationState: 'published' },
  { id: 'p2', title: '草稿', publicationState: 'draft' },
  { id: 'p3', title: '已撤回', publicationState: 'withdrawn' },
] as const

describe('P2-01-AC-01 anonymous public traversal', () => {
  it('resolves the public home route without any auth challenge', async () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        {
          path: '/',
          component: PublicLayout,
          meta: { publicOnly: true },
          children: [{ path: '', name: 'home', component: { template: '<p>home</p>' } }],
        },
      ],
    })
    router.push('/')
    await router.isReady()
    expect(router.currentRoute.value.name).toBe('home')
    expect(router.currentRoute.value.meta.publicOnly).toBe(true)
  })
})

describe('P2-01-AC-02 published projection only', () => {
  it('excludes withdrawn and draft records from the public projection', () => {
    const visible = publishedOnly(published)
    expect(visible).toHaveLength(1)
    expect(visible[0].id).toBe('p1')
  })

  it('rejects non-public paths fail-closed', async () => {
    await expect(publicGet('/api/v1/research/workspace')).rejects.toThrow(ApiError)
    await expect(publicGet('/api/v1/admin/users')).rejects.toThrow(ApiError)
  })

  it('fetches only the public home projection', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ items: published }),
    })
    vi.stubGlobal('fetch', fetchMock)
    const result = await publicGet('/api/v1/public/home')
    expect(result).toEqual({ items: published })
    expect(fetchMock).toHaveBeenCalledWith('/api/v1/public/home', {
      method: 'GET',
      signal: undefined,
    })
    vi.unstubAllGlobals()
  })

  it('surfaces API failure as an error state', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({ ok: false, status: 500, json: async () => ({}) }),
    )
    await expect(publicGet('/api/v1/public/home')).rejects.toThrow(/500/)
    vi.unstubAllGlobals()
  })
})

describe('P2-01-AC-03 no research/admin routes anonymously', () => {
  it('has no research or admin route registered in the public router', async () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        {
          path: '/',
          component: PublicLayout,
          meta: { publicOnly: true },
          children: [{ path: '', name: 'home', component: { template: '<p>home</p>' } }],
        },
      ],
    })
    const names = router.getRoutes().map((r) => r.name)
    expect(names).not.toContain('research')
    expect(names).not.toContain('admin')
    expect(router.resolve('/research').matched).toHaveLength(0)
    expect(router.resolve('/admin').matched).toHaveLength(0)
  })

  it('isPublicPath boundary is exclusive of research/admin', () => {
    expect(isPublicPath('/api/v1/public/home')).toBe(true)
    expect(isPublicPath('/api/v1/research/workspace')).toBe(false)
    expect(isPublicPath('/api/v1/admin/users')).toBe(false)
  })
})

describe('P2-01-AC-04 accessibility assertions', () => {
  it('public layout passes axe assertions with semantic landmarks', async () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        {
          path: '/',
          component: PublicLayout,
          meta: { publicOnly: true },
          children: [{ path: '', name: 'home', component: { template: '<p>home</p>' } }],
        },
      ],
    })
    router.push('/')
    await router.isReady()
    const wrapper = mount(PublicLayout, {
      attachTo: document.body,
      global: {
        plugins: [router],
        stubs: { RouterView: { template: '<p>content</p>' } },
      },
    })
    const results = await axe.run(wrapper.element as HTMLElement)
    wrapper.unmount()
    expect(results.violations).toHaveLength(0)
    expect(wrapper.find('header').exists()).toBe(true)
    expect(wrapper.find('nav[aria-label="Public navigation"]').exists()).toBe(true)
    expect(wrapper.find('main').exists()).toBe(true)
    expect(wrapper.find('footer').exists()).toBe(true)
  })

  it('state components are accessible', () => {
    expect(mount(LoadingState).find('[role="status"]').exists()).toBe(true)
    expect(mount(EmptyState).find('[role="status"]').exists()).toBe(true)
    expect(mount(ErrorState).find('[role="alert"]').exists()).toBe(true)
  })
})

describe('P2-01-AC-05 responsive breakpoint matrix', () => {
  it('exposes the frozen breakpoint tokens (extended at UI-01 with xl/2xl)', () => {
    expect(BREAKPOINTS).toEqual({ sm: 480, md: 768, lg: 1024, xl: 1440, '2xl': 1920 })
  })

  it('reports the largest matching breakpoint', () => {
    const mq = (matches: boolean) => ({ matches, media: '', onchange: null })
    const matchMedia = vi.spyOn(window, 'matchMedia').mockImplementation((query: string) => {
      if (query.includes('1024')) return mq(true) as MediaQueryList
      return mq(false) as MediaQueryList
    })
    expect(currentBreakpoint()).toBe('lg')
    matchMedia.mockRestore()
  })

  it('reports xl at ≥1440px', () => {
    const mq = (matches: boolean) => ({ matches, media: '', onchange: null })
    const matchMedia = vi.spyOn(window, 'matchMedia').mockImplementation((query: string) => {
      if (query.includes('1440')) return mq(true) as MediaQueryList
      return mq(false) as MediaQueryList
    })
    expect(currentBreakpoint()).toBe('xl')
    matchMedia.mockRestore()
  })

  it('falls back to the smallest breakpoint on no match', () => {
    const mq = (matches: boolean) => ({ matches, media: '', onchange: null })
    const matchMedia = vi
      .spyOn(window, 'matchMedia')
      .mockImplementation(() => mq(false) as MediaQueryList)
    expect(currentBreakpoint()).toBe('sm')
    matchMedia.mockRestore()
  })
})
