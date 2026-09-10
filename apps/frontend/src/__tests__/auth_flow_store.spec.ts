/**
 * Auth-flow store-level unit tests — P2-02 in-memory session semantics.
 *
 * Complements the browser auth-flow E2E with deterministic store coverage for
 * the pieces that are pure JS/session state (no DOM dependency):
 *  - login success / failure;
 *  - role matrix (hasRole / hasAnyRole / hasPermission);
 *  - logout drops the session and calls the API;
 *  - token revocation (401 -> AuthRevokedError -> revoke()).
 * These mirror the P2-02-AC-01/02/04 contracts at the store level.
 */
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useAuthStore } from '../stores/auth'
import { authApi, AuthRevokedError } from '../services/auth'
import type { AuthUser } from '../types/auth'

function sessionUser(roles: AuthUser['roles']): AuthUser {
  return { id: 'u1', roles, permissions: ['research:read'] }
}

beforeEach(() => {
  setActivePinia(createPinia())
  vi.restoreAllMocks()
})

describe('auth store — login', () => {
  it('login success stores token + user and marks authenticated', async () => {
    const store = useAuthStore()
    vi.spyOn(authApi, 'login').mockResolvedValue({ token: 't', user: sessionUser(['STUDENT_RESEARCHER']) })
    await store.login('u', 'p')
    expect(store.isAuthenticated).toBe(true)
    expect(store.hasRole('STUDENT_RESEARCHER')).toBe(true)
    expect(store.token).toBe('t')
  })

  it('login failure leaves the store unauthenticated (fail-open not granted)', async () => {
    const store = useAuthStore()
    vi.spyOn(authApi, 'login').mockRejectedValue(new Error('bad credentials'))
    await expect(store.login('u', 'bad')).rejects.toThrow()
    expect(store.isAuthenticated).toBe(false)
    expect(store.user).toBeNull()
  })
})

describe('auth store — role matrix', () => {
  it('hasAnyRole admits a researcher for RESEARCH_ROLES but not ADMIN_ROLES', () => {
    const store = useAuthStore()
    store.$patch({ token: 't', user: sessionUser(['SCHOLAR_RESEARCHER']) })
    expect(store.hasAnyRole(['STUDENT_RESEARCHER', 'SCHOLAR_RESEARCHER'])).toBe(true)
    expect(store.hasAnyRole(['CONTENT_REVIEWER', 'SYSTEM_ADMIN'])).toBe(false)
  })

  it('hasPermission reflects the permission set (deny-by-default otherwise)', () => {
    const store = useAuthStore()
    store.$patch({ token: 't', user: sessionUser(['SYSTEM_ADMIN']) })
    expect(store.hasPermission('research:read')).toBe(true)
    expect(store.hasPermission('admin:publish')).toBe(false)
  })

  it('anonymous role (ANONYMOUS_VISITOR) is never admitted to guarded surfaces', () => {
    const store = useAuthStore()
    store.$patch({ token: 't', user: sessionUser(['ANONYMOUS_VISITOR']) })
    expect(store.hasAnyRole(['STUDENT_RESEARCHER', 'SCHOLAR_RESEARCHER', 'CONTENT_REVIEWER', 'SYSTEM_ADMIN'])).toBe(false)
  })
})

describe('auth store — logout & revocation', () => {
  it('logout drops the session in finally even if the API call throws', async () => {
    const store = useAuthStore()
    store.$patch({ token: 't', user: sessionUser(['CONTENT_REVIEWER']) })
    vi.spyOn(authApi, 'logout').mockRejectedValue(new Error('network'))
    await expect(store.logout()).rejects.toThrow()
    expect(store.isAuthenticated).toBe(false)
    expect(store.token).toBeNull()
    expect(store.user).toBeNull()
  })

  it('withRevocation converts a 401 AuthRevokedError into revoke()', async () => {
    const store = useAuthStore()
    store.$patch({ token: 't', user: sessionUser(['STUDENT_RESEARCHER']) })
    vi.spyOn(authApi, 'login').mockRejectedValue(new AuthRevokedError())
    await expect(store.withRevocation(() => store.login('u', 'p'))).rejects.toThrow()
    expect(store.isAuthenticated).toBe(false)
  })

  it('revoke() clears session without an API call (401 path)', () => {
    const store = useAuthStore()
    store.$patch({ token: 't', user: sessionUser(['SYSTEM_ADMIN']) })
    store.revoke()
    expect(store.isAuthenticated).toBe(false)
  })
})
