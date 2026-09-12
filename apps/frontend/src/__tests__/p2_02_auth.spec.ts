/**
 * P2-02 Research/Admin Frontend Foundation tests.
 *
 * Proves the frozen P2-02 acceptance criteria:
 *  - P2-02-AC-01 unauthenticated redirect to login on research/admin routes;
 *  - P2-02-AC-02 role/permission matrix enforced in the UI (deny-by-default);
 *  - P2-02-AC-03 admin publish/withdraw actions use the audit-logged endpoints;
 *  - P2-02-AC-04 token revocation yields 401 handling and logout.
 */
import { describe, expect, it, vi, beforeEach } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory, createRouter, type RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { authApi } from '../services/auth'
import { adminActions } from '../services/admin'
import { requireAnyRole } from '../router/guards'
import { ADMIN_ROLES, RESEARCH_ROLES } from '../types/auth'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: { template: '<p>public</p>' },
    meta: { publicOnly: true },
    children: [{ path: '', name: 'home', component: { template: '<p>home</p>' } }],
  },
  {
    path: '/login',
    component: { template: '<p>login</p>' },
    name: 'login',
    meta: { publicOnly: true },
  },
  {
    path: '/denied',
    component: { template: '<p>denied</p>' },
    name: 'denied',
    meta: { publicOnly: true },
  },
  {
    path: '/research',
    component: { template: '<p>research</p>' },
    name: 'research-home',
    meta: { requiresAuth: true, roles: RESEARCH_ROLES },
    beforeEnter: [requireAnyRole(RESEARCH_ROLES)],
  },
  {
    path: '/admin',
    component: { template: '<p>admin</p>' },
    name: 'admin-home',
    meta: { requiresAuth: true, roles: ADMIN_ROLES },
    beforeEnter: [requireAnyRole(ADMIN_ROLES)],
  },
]

function makeRouter(): ReturnType<typeof createRouter> {
  const router = createRouter({ history: createMemoryHistory(), routes })
  router.beforeEach((to) => {
    const store = useAuthStore()
    if (to.meta.publicOnly === true) return true
    if (to.meta.requiresAuth === true && store.isAuthenticated) return true
    return { name: 'login', query: { redirect: to.fullPath } }
  })
  return router
}

function user(roles: Array<(typeof RESEARCH_ROLES)[number] | (typeof ADMIN_ROLES)[number]>) {
  return { id: 'u1', roles, permissions: [] }
}

beforeEach(() => {
  setActivePinia(createPinia())
})

describe('P2-02-AC-01 unauthenticated redirect', () => {
  it('redirects unauthenticated visitors from /research to login', async () => {
    const router = makeRouter()
    router.push('/research')
    await router.isReady()
    expect(router.currentRoute.value.name).toBe('login')
    expect(router.currentRoute.value.query.redirect).toBe('/research')
  })

  it('redirects unauthenticated visitors from /admin to login', async () => {
    const router = makeRouter()
    router.push('/admin')
    await router.isReady()
    expect(router.currentRoute.value.name).toBe('login')
  })
})

describe('P2-02-AC-02 role matrix deny-by-default', () => {
  it('allows a researcher role on /research', async () => {
    const store = useAuthStore()
    store.$patch({ token: 't', user: user(['STUDENT_RESEARCHER']) })
    const router = makeRouter()
    router.push('/research')
    await router.isReady()
    expect(router.currentRoute.value.name).toBe('research-home')
  })

  it('denies a researcher role on /admin (default-deny)', async () => {
    const store = useAuthStore()
    store.$patch({ token: 't', user: user(['STUDENT_RESEARCHER']) })
    const router = makeRouter()
    router.push('/admin')
    await router.isReady()
    expect(router.currentRoute.value.name).toBe('denied')
  })

  it('denies an anonymous visitor everywhere outside public', async () => {
    const store = useAuthStore()
    store.$patch({ token: 't', user: user(['ANONYMOUS_VISITOR']) })
    const router = makeRouter()
    router.push('/research')
    await router.isReady()
    expect(router.currentRoute.value.name).toBe('denied')
  })

  it('allows a system admin on /admin', async () => {
    const store = useAuthStore()
    store.$patch({ token: 't', user: user(['SYSTEM_ADMIN']) })
    const router = makeRouter()
    router.push('/admin')
    await router.isReady()
    expect(router.currentRoute.value.name).toBe('admin-home')
  })
})

describe('P2-02-AC-03 audit-logged admin actions', () => {
  it('publish posts to the audit-logged admin endpoint with auth', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ artifact_id: 'a1', publication_status: 'published' }),
    })
    vi.stubGlobal('fetch', fetchMock)
    const result = await adminActions.publish('a1', 'token-1')
    expect(result.publication_status).toBe('published')
    const [url, init] = fetchMock.mock.calls[0] as [string, RequestInit]
    expect(url).toBe('/api/v1/admin/publication/publish')
    expect((init.headers as Record<string, string>).Authorization).toBe('Bearer token-1')
    vi.unstubAllGlobals()
  })

  it('withdraw posts to the audit-logged admin endpoint', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ artifact_id: 'a1', publication_status: 'withdrawn' }),
    })
    vi.stubGlobal('fetch', fetchMock)
    await adminActions.withdraw('a1', 'token-1')
    const [url] = fetchMock.mock.calls[0] as [string]
    expect(url).toBe('/api/v1/admin/publication/withdraw')
    vi.unstubAllGlobals()
  })

  it('propagates permission failures as errors', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: false, status: 403 }))
    await expect(adminActions.publish('a1', 'token-1')).rejects.toThrow(/403/)
    vi.unstubAllGlobals()
  })
})

describe('P2-02-AC-04 token revocation', () => {
  it('revokes the session on 401 and redirects to login on next nav', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({ ok: false, status: 401, json: async () => ({}) }),
    )
    const store = useAuthStore()
    store.$patch({ token: 't', user: user(['STUDENT_RESEARCHER']) })
    await expect(store.withRevocation(() => authApi.login('u', 'p'))).rejects.toThrow()
    expect(store.isAuthenticated).toBe(false)
    vi.unstubAllGlobals()
  })
})

// ND-1 B05 — the authoritative backend login contract is the shared
// `api_response` envelope `{success,data:{ok,token,user_id,role}}`; the client
// adapts it to LoginResponse and strict shape validation guards state writes.
function loginEnvelope(overrides: Record<string, unknown> = {}) {
  return {
    success: true,
    timestamp: '2026-09-07T00:00:00Z',
    message: 'ok',
    data: { ok: true, token: 't1', user_id: 'u1', role: 'STUDENT_RESEARCHER', ...overrides },
  }
}

function stubLoginResponse(body: unknown): void {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: async () => body }))
}

describe('B05 login envelope contract (existing-auth repair)', () => {
  it('login stores token + identity from the real envelope, then guards follow', async () => {
    stubLoginResponse(loginEnvelope())
    const store = useAuthStore()
    await store.login('researcher', 'pw')
    expect(store.isAuthenticated).toBe(true)
    expect(store.token).toBe('t1')
    expect(store.user?.id).toBe('u1')
    expect(store.hasRole('STUDENT_RESEARCHER')).toBe(true)
    expect(store.user?.permissions).toEqual([])

    const router = makeRouter()
    router.push('/research')
    await router.isReady()
    expect(router.currentRoute.value.name).toBe('research-home')
    await router.push('/admin')
    expect(router.currentRoute.value.name).toBe('denied')
    vi.unstubAllGlobals()
  })

  it('rejects a bare (non-envelope) login body and writes no auth state', async () => {
    // The contradictory pre-B05 bare success shape must never be accepted.
    stubLoginResponse({ token: 't1', user: user(['STUDENT_RESEARCHER']) })
    const store = useAuthStore()
    await expect(store.login('u', 'p')).rejects.toThrow(/login response/i)
    expect(store.isAuthenticated).toBe(false)
    expect(store.token).toBeNull()
    expect(store.user).toBeNull()
    vi.unstubAllGlobals()
  })

  it('rejects a failure envelope (success false / ok false) and writes no state', async () => {
    stubLoginResponse({ ...loginEnvelope(), success: false })
    const store = useAuthStore()
    await expect(store.login('u', 'p')).rejects.toThrow(/login response/i)
    expect(store.isAuthenticated).toBe(false)
    stubLoginResponse(loginEnvelope({ ok: false }))
    await expect(store.login('u', 'p')).rejects.toThrow(/not ok/i)
    expect(store.isAuthenticated).toBe(false)
    vi.unstubAllGlobals()
  })

  it('rejects an envelope with an unknown role and writes no state', async () => {
    stubLoginResponse(loginEnvelope({ role: 'SUPERUSER' }))
    const store = useAuthStore()
    await expect(store.login('u', 'p')).rejects.toThrow(/role/i)
    expect(store.isAuthenticated).toBe(false)
    vi.unstubAllGlobals()
  })

  it('rejects an envelope with missing token or user_id and writes no state', async () => {
    stubLoginResponse(loginEnvelope({ token: '' }))
    const store = useAuthStore()
    await expect(store.login('u', 'p')).rejects.toThrow(/token/i)
    stubLoginResponse(loginEnvelope({ user_id: '' }))
    await expect(store.login('u', 'p')).rejects.toThrow(/user_id/i)
    expect(store.isAuthenticated).toBe(false)
    vi.unstubAllGlobals()
  })

  it('invalid credentials (HTTP 401) reject and revoke, writing no state', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({ ok: false, status: 401, json: async () => ({}) }),
    )
    const store = useAuthStore()
    await expect(store.login('u', 'wrong')).rejects.toThrow()
    expect(store.isAuthenticated).toBe(false)
    vi.unstubAllGlobals()
  })
})
