/**
 * Public API types (P2-01 public frontend foundation).
 *
 * Typed projection of the accepted public namespace (`/api/v1/public/*`).
 * The public surface consumes the published projection only; research/admin
 * namespaces are out of scope for this client (P2-01-AC-02/03).
 *
 * Pre-acceptance demo additions: home projection carries published Works +
 * per-domain counts; persons/works/media/search projections for the public
 * browsing surface.
 */

/** Publication states exposed by the accepted publication contract. */
export type PublicationState = 'draft' | 'published' | 'withdrawn'

/** A public-projection content record. */
export interface PublishedItem {
  id: string
  title: string
  publicationState: PublicationState
}

/** Public portal home projection (fixture-friendly). */
export interface PublicHomeProjection {
  items: PublishedItem[]
}

/** Published work summary (portal home / works list). */
export interface WorkSummary {
  work_id: string
  title: string
  dynasty: string | null
  category: string | null
  edition_count: number
  publication_status: string
}

/** Published person summary (persons list). */
export interface PersonSummary {
  entity_id: string
  name_zh: string | null
  name_pinyin: string | null
  dynasty: string | null
  publication_status: string
}

/** Per-domain published counts. */
export interface HomeCounts {
  works: number
  persons: number
  heritage_projects: number
  c_terms: number
}

/** Public portal home projection (real API shape; `items` kept for mocks). */
export interface HomeProjection {
  works: WorkSummary[]
  counts: HomeCounts
  items?: PublishedItem[]
}

/** Public edition summary. */
export interface EditionSummary {
  edition_id: string
  edition_name: string
  era: string | null
  publisher_block: string | null
}

/** Public work detail. */
export interface WorkDetail {
  work_id?: string
  title: string
  dynasty: string | null
  category: string | null
  publication_status?: string
  edition_count?: number
}

/** Public person detail. */
export interface PublicPerson {
  entity_id: string
  name_zh: string | null
  name_pinyin: string | null
  courtesy_name: string | null
  pseudonym: string | null
  dynasty: string | null
  publication_status: string
  assertions: unknown[]
  events: unknown[]
}

/** Public search hit (kind-tagged; published only). */
export interface SearchHit {
  kind: string
  id: string
  title: string
  snippet: string
  version_id: string | null
  publication_status: string
}
