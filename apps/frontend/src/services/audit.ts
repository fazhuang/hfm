/**
 * Admin audit service (P2-09 unified admin audit view).
 *
 * Read-only client for the accepted admin audit endpoints: audit-log browse
 * (audit:read) and reconciliation results. No mutation methods exist on this
 * service — the audit view is strictly read-only (P2-09-AC-02).
 */

/** One immutable audit entry (P1-13 append-only journal). */
export interface AuditEntry {
  id: string
  actorId: string | null
  action: string
  targetType: string
  targetId: string
  createdAt: string
}

/** A reconciliation run result (P1-13). */
export interface ReconciliationResult {
  id: string
  status: 'PASS' | 'FAIL'
  recordedAt: string
  detail: string
}

async function adminGet<T>(path: string, token: string | null): Promise<T> {
  const headers: Record<string, string> = {}
  if (token) headers.Authorization = `Bearer ${token}`
  const response = await fetch(path, { method: 'GET', headers })
  if (!response.ok) {
    throw new Error(`audit request failed: ${response.status}`)
  }
  return (await response.json()) as T
}

/** Read-only audit browsing (role-gated at the backend; audit:read). */
export function fetchAuditLog(token: string | null, limit = 50): Promise<AuditEntry[]> {
  return adminGet<AuditEntry[]>(`/api/v1/admin/audit-log?limit=${limit}`, token)
}

/** Read-only reconciliation result view. */
export function fetchReconciliation(token: string | null): Promise<ReconciliationResult[]> {
  return adminGet<ReconciliationResult[]>('/api/v1/admin/reconciliation', token)
}
