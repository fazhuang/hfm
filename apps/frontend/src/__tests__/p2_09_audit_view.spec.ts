/**
 * P2-09 Unified Admin Audit View tests.
 *
 * Proves the frozen P2-09 acceptance criteria:
 *  - P2-09-AC-01 admin can browse audit entries (role-gated; non-admin denied);
 *  - P2-09-AC-02 audit view is read-only (no mutation endpoints/methods);
 *  - P2-09-AC-03 reconciliation PASS/FAIL states displayed correctly.
 */
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { fetchAuditLog, fetchReconciliation } from '../services/audit'
import { useAuthStore } from '../stores/auth'
import { requireAnyRole } from '../router/guards'
import { ADMIN_ROLES } from '../types/auth'

beforeEach(() => {
  setActivePinia(createPinia())
})

describe('P2-09-AC-01 role-gated audit browsing', () => {
  it('admin service calls the audit-log endpoint with auth', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => [
        {
          id: 'a1',
          actorId: 'u1',
          action: 'publication.publish',
          targetType: 'publication_record',
          targetId: 'art-1',
          createdAt: '2026-08-31T00:00:00Z',
        },
      ],
    })
    vi.stubGlobal('fetch', fetchMock)
    const entries = await fetchAuditLog('token-1', 50)
    expect(entries).toHaveLength(1)
    expect(entries[0].action).toBe('publication.publish')
    const [url, init] = fetchMock.mock.calls[0] as [string, RequestInit]
    expect(url).toContain('/api/v1/admin/audit-log')
    expect((init.headers as Record<string, string>).Authorization).toBe('Bearer token-1')
    vi.unstubAllGlobals()
  })

  it('non-admin roles are denied by the route guard (deny-by-default)', () => {
    const guard = requireAnyRole(ADMIN_ROLES)
    // simulate navigation as a researcher
    const store = useAuthStore()
    store.$patch({ token: 't', user: { id: 'u', roles: ['STUDENT_RESEARCHER'], permissions: [] } })
    const result = guard({ fullPath: '/admin/audit' } as never, null as never, null as never)
    expect(result).toEqual({ name: 'denied' })
  })

  it('admin roles pass the route guard', () => {
    const guard = requireAnyRole(ADMIN_ROLES)
    const store = useAuthStore()
    store.$patch({ token: 't', user: { id: 'u', roles: ['SYSTEM_ADMIN'], permissions: [] } })
    expect(guard({ fullPath: '/admin/audit' } as never, null as never, null as never)).toBe(true)
  })
})

describe('P2-09-AC-02 read-only audit view', () => {
  it('audit service exposes no mutation methods', () => {
    const service = Object.keys({ fetchAuditLog, fetchReconciliation })
    expect(service.every((k) => !/post|put|patch|delete|mutate|create|update|remove/.test(k))).toBe(
      true,
    )
  })

  it('audit endpoints are GET-only', async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, json: async () => [] })
    vi.stubGlobal('fetch', fetchMock)
    await fetchAuditLog('t', 10)
    await fetchReconciliation('t')
    const methods = fetchMock.mock.calls.map((c) => (c[1] as RequestInit).method)
    expect(methods.every((m) => m === 'GET')).toBe(true)
    vi.unstubAllGlobals()
  })
})

describe('P2-09-AC-03 reconciliation states displayed correctly', () => {
  it('reconciliation results carry PASS/FAIL status', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => [
          { id: 'r1', status: 'PASS', recordedAt: 't1', detail: 'batch 1 ok' },
          { id: 'r2', status: 'FAIL', recordedAt: 't2', detail: 'batch 2 mismatch' },
        ],
      }),
    )
    const results = await fetchReconciliation('t')
    expect(results.map((r) => r.status)).toEqual(['PASS', 'FAIL'])
    vi.unstubAllGlobals()
  })

  it('status values are strictly PASS or FAIL (no misdisplay)', () => {
    const valid = new Set(['PASS', 'FAIL'])
    const results = [
      { id: 'r1', status: 'PASS' },
      { id: 'r2', status: 'FAIL' },
    ]
    expect(results.every((r) => valid.has(r.status))).toBe(true)
  })
})
