/**
 * Search projection types (UI-10).
 *
 * DOMAIN DATA → SEARCH PROJECTION. These are retrieval projections over the
 * established content semantics (QuotationRecord / Work / Edition /
 * ArchiveRecord / PaperRecord / core person) — never new domain models.
 * Internal provenance (registerKey / hfmzl/ / zzcl/ paths) is used only to
 * BUILD the projection and never surfaces in result content.
 */

export type SearchType = 'person' | 'text' | 'work' | 'edition' | 'archive' | 'paper'

export interface SearchIndexEntry {
  id: string
  type: SearchType
  title: string
  subtitle?: string
  /** Aggregated searchable text (public fields only — no internal paths). */
  searchableText: string
  year?: number
  authors?: string[]
  themes?: string[]
  relatedEntities?: string[]
  status: string
  sourceName?: string
  route?: string
}

export interface SearchResult {
  entry: SearchIndexEntry
  /** Ranked 0-based position within the filtered result set. */
  rank: number
}

export interface FacetCount {
  type: SearchType
  label: string
  count: number
}
