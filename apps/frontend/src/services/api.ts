/**
 * Public API client (P2-01 public frontend foundation).
 *
 * Anonymous, read-only boundary to the accepted public namespace. The client
 * refuses any path outside `/api/v1/public/*` (fail-closed: a public client
 * can never reach research/admin surfaces — P2-01-AC-02/03).
 *
 * Pre-acceptance demo additions: persons/works/media/search fetchers; the
 * home fetch unwraps the api_response envelope while remaining compatible
 * with bare fixture projections used by the browser E2E mocks.
 */
import type {
  EditionSummary,
  HomeProjection,
  PersonSummary,
  PublicPerson,
  SearchHit,
  WorkDetail,
  WorkSummary,
} from '../types/public'
import type { MediaAssetItem, MediaCategory } from '../types/media'

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

/** Unwrap the api_response envelope ({success,data,...}) when present. */
function unwrap<T>(body: unknown): T {
  const candidate = body as { success?: boolean; data?: unknown }
  if (
    candidate !== null &&
    typeof candidate === 'object' &&
    'success' in candidate &&
    'data' in candidate &&
    candidate.data !== undefined
  ) {
    return candidate.data as T
  }
  return body as T
}

/** Load the public home projection (published items only). */
export async function fetchPublicHome(signal?: AbortSignal): Promise<HomeProjection> {
  const body = await publicGet<unknown>(`${PUBLIC_NAMESPACE}/home`, signal)
  return unwrap<HomeProjection>(body)
}

/** Published works list. */
export async function fetchPublicWorks(page = 1): Promise<{ works: WorkSummary[]; total: number }> {
  const body = await publicGet<unknown>(`${PUBLIC_NAMESPACE}/works?page=${page}&page_size=20`)
  return unwrap<{ works: WorkSummary[]; total: number }>(body)
}

/** Published persons list. */
export async function fetchPublicPersons(): Promise<{ persons: PersonSummary[]; total: number }> {
  const body = await publicGet<unknown>(`${PUBLIC_NAMESPACE}/persons`)
  return unwrap<{ persons: PersonSummary[]; total: number }>(body)
}

/** Published work detail. */
export async function fetchPublicWork(workId: string): Promise<WorkDetail> {
  const body = await publicGet<unknown>(`${PUBLIC_NAMESPACE}/works/${workId}`)
  return unwrap<WorkDetail>(body)
}

/** Editions of a published work. */
export async function fetchPublicWorkEditions(
  workId: string,
): Promise<{ work_id: string; editions: EditionSummary[] }> {
  const body = await publicGet<unknown>(`${PUBLIC_NAMESPACE}/works/${workId}/editions`)
  return unwrap<{ work_id: string; editions: EditionSummary[] }>(body)
}

/** Published person detail. */
export async function fetchPublicPerson(entityId: string): Promise<PublicPerson> {
  const body = await publicGet<unknown>(`${PUBLIC_NAMESPACE}/persons/${entityId}`)
  return unwrap<PublicPerson>(body)
}

/** Published media assets (optional category filter). */
export async function fetchPublicMedia(kind?: MediaCategory): Promise<MediaAssetItem[]> {
  const suffix = kind ? `?kind=${kind}` : ''
  const body = await publicGet<unknown>(`${PUBLIC_NAMESPACE}/media${suffix}`)
  const data = unwrap<{ items: MediaAssetItem[]; total: number }>(body)
  return data.items
}

/** Public search hits (kind-tagged; published projection only). */
export async function searchPublicHits(query: string): Promise<SearchHit[]> {
  const params = new URLSearchParams({ q: query })
  const body = await publicGet<unknown>(`${PUBLIC_NAMESPACE}/search?${params.toString()}`)
  const data = unwrap<{ hits: SearchHit[]; total: number }>(body)
  return data.hits
}
