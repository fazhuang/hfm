/**
 * Admin publication actions (P2-02 research/admin frontend foundation).
 *
 * Wraps the audit-logged admin publication endpoints (P1-09): review,
 * publish, withdraw. Every action requires the matching content permission
 * at the backend; the frontend foundation never bypasses the boundary.
 */
export interface PublicationActionResponse {
  artifact_id: string
  publication_status: string
}

async function adminPost<T>(path: string, body: unknown, token: string | null): Promise<T> {
  const headers: Record<string, string> = { 'Content-Type': 'application/json' }
  if (token) headers.Authorization = `Bearer ${token}`
  const response = await fetch(path, { method: 'POST', headers, body: JSON.stringify(body) })
  if (!response.ok) {
    throw new Error(`admin action failed: ${response.status}`)
  }
  return (await response.json()) as T
}

export const adminActions = {
  /** content:review — review an artifact for publication (audit-logged). */
  review(artifactId: string, approve: boolean, token: string | null) {
    return adminPost<PublicationActionResponse>(
      '/api/v1/admin/publication/review',
      { artifact_id: artifactId, approve },
      token,
    )
  },
  /** content:publish — publish an artifact (audit-logged). */
  publish(artifactId: string, token: string | null) {
    return adminPost<PublicationActionResponse>(
      '/api/v1/admin/publication/publish',
      { artifact_id: artifactId },
      token,
    )
  },
  /** content:withdraw — withdraw an artifact (audit-logged). */
  withdraw(artifactId: string, token: string | null) {
    return adminPost<PublicationActionResponse>(
      '/api/v1/admin/publication/withdraw',
      { artifact_id: artifactId },
      token,
    )
  },
}
