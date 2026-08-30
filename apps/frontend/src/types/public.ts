/**
 * Public API types (P2-01 public frontend foundation).
 *
 * Typed projection of the accepted public namespace (`/api/v1/public/*`).
 * The public surface consumes the published projection only; research/admin
 * namespaces are out of scope for this client (P2-01-AC-02/03).
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
