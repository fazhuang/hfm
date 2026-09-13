/**
 * Reader/search services (P2-03 reader/search frontend).
 *
 * resolveLocator is a pure, deterministic function: the same locator always
 * resolves to the same passage/version (P2-03-AC-01 reproducibility). The
 * public reader/search clients consume only the public namespace; research
 * search requires an authenticated token (P2-03-AC-03 role scoping).
 */
import { publicGet } from './api'
import type { PassageLocator, ReaderPassage, SearchResultItem } from '../types/reader'

/** Deterministic locator-to-passage resolution (reproducibility, AC-01). */
export function resolveLocator(
  locator: PassageLocator,
  passages: readonly ReaderPassage[],
): ReaderPassage | undefined {
  return passages.find(
    (p) =>
      p.locator.workId === locator.workId &&
      p.locator.editionId === locator.editionId &&
      p.locator.versionId === locator.versionId &&
      p.locator.passageId === locator.passageId,
  )
}

/** Canonical locator serialization (deterministic, used for E2E identity). */
export function locatorKey(locator: PassageLocator): string {
  return [locator.workId, locator.editionId, locator.versionId, locator.passageId]
    .filter(Boolean)
    .join('/')
}

/** Public reader resolution (published projection only). */
export async function resolvePublicPassage(locator: PassageLocator): Promise<ReaderPassage> {
  const params = new URLSearchParams({ locator: locatorKey(locator) })
  return publicGet<ReaderPassage>(`/api/v1/public/reader/resolve?${params.toString()}`)
}

/** Public search: published results only (anonymous scope, AC-03). */
export async function searchPublished(query: string): Promise<SearchResultItem[]> {
  const params = new URLSearchParams({ q: query })
  const result = await publicGet<{ items: SearchResultItem[] }>(
    `/api/v1/public/search?${params.toString()}`,
  )
  return result.items.filter((item) => item.publicationState === 'published')
}

/** Reader resolve projection (P1-07) — the fields the P4 reader uses. */
export interface ResolvedPassage {
  passage_id: string
  quotation: string
  translation: string | null
  notes: string | null
  chapter: { chapter_id: string; title: string; order: number }
  work: { work_id: string | null; title: string | null }
  publication_status: string
}

/** Resolve a passage to its full text + context by id (public projection). */
export async function resolvePassageById(passageId: string): Promise<ResolvedPassage> {
  const params = new URLSearchParams({ passage_id: passageId })
  const body = await publicGet<{ success?: boolean; data?: ResolvedPassage }>(
    `/api/v1/public/reader/resolve?${params.toString()}`,
  )
  if (body && typeof body === 'object' && 'data' in body && body.data) return body.data
  return body as unknown as ResolvedPassage
}
