/**
 * Published-projection filter (P2-01 public frontend foundation).
 *
 * The public surface renders the published projection only: withdrawn and
 * unpublished (draft) records are excluded fail-closed (P2-01-AC-02).
 */
import type { PublishedItem, PublicationState } from '../types/public'

const VISIBLE_STATES: ReadonlySet<PublicationState> = new Set(['published'])

export function isPublished(item: PublishedItem): boolean {
  return VISIBLE_STATES.has(item.publicationState)
}

export function publishedOnly(items: readonly PublishedItem[]): PublishedItem[] {
  return items.filter(isPublished)
}
