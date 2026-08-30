/**
 * Public API client (P2-01 public frontend foundation).
 *
 * Anonymous, read-only boundary to the accepted public namespace. The client
 * refuses any path outside `/api/v1/public/*` (fail-closed: a public client
 * can never reach research/admin surfaces — P2-01-AC-02/03).
 */
import type { PublicHomeProjection } from '../types/public'

/** Accepted public namespace prefix. */
export const PUBLIC_NAMESPACE = '/api/v1/public'

/** Error carrying the HTTP status for loading-state rendering. */
export class ApiError extends Error {
  readonly status: number

  constructor(message: string, status: number) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

/** True only for paths inside the public namespace (fail-closed boundary). */
export function isPublicPath(path: string): boolean {
  return path === PUBLIC_NAMESPACE || path.startsWith(`${PUBLIC_NAMESPACE}/`)
}

/**
 * GET-only fetch within the public namespace. Rejects non-public paths and
 * non-2xx responses; returns the parsed projection.
 */
export async function publicGet<T>(path: string, signal?: AbortSignal): Promise<T> {
  if (!isPublicPath(path)) {
    throw new ApiError(`refusing non-public path: ${path}`, 403)
  }
  const response = await fetch(path, { method: 'GET', signal })
  if (!response.ok) {
    throw new ApiError(`public request failed: ${response.status}`, response.status)
  }
  return (await response.json()) as T
}

/** Load the public home projection (published items only). */
export function fetchPublicHome(signal?: AbortSignal): Promise<PublicHomeProjection> {
  return publicGet<PublicHomeProjection>(`${PUBLIC_NAMESPACE}/home`, signal)
}
