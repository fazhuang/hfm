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
