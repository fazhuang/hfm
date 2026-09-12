/**
 * useSearchQuery — URL state sync for /search (UI-10).
 *
 * Single source of truth is the router query (?q= &type= &page=):
 * refresh and back/forward always recover the exact state. The composable
 * parses and serializes the query without mutating the router.
 */
import { computed, type Ref } from 'vue'
import type { SearchType } from '../types/search'

export interface SearchQueryState {
  q: string
  type: SearchType | 'all'
  page: number
}

export function parseSearchQuery(query: Record<string, unknown>): SearchQueryState {
  const q = typeof query.q === 'string' ? query.q : ''
  const type = (typeof query.type === 'string' ? query.type : 'all') as SearchType | 'all'
  const rawPage = typeof query.page === 'string' ? Number.parseInt(query.page, 10) : NaN
  const page = Number.isFinite(rawPage) && rawPage > 0 ? rawPage : 1
  return { q: q.trim(), type, page }
}

export function serializeSearchQuery(state: SearchQueryState): Record<string, string> {
  const query: Record<string, string> = {}
  if (state.q) query.q = state.q
  if (state.type && state.type !== 'all') query.type = state.type
  if (state.page > 1) query.page = String(state.page)
  return query
}

export function useSearchQuery(query: Ref<Record<string, unknown>>) {
  return computed(() => parseSearchQuery(query.value))
}
