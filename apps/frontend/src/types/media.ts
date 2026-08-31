/**
 * Media asset types (pre-acceptance demo: published papers/classics/movies).
 */

export type MediaCategory = 'paper' | 'classic' | 'movie' | 'other'

/** Published media asset (public projection). */
export interface MediaAssetItem {
  id: string
  name: string
  object_key: string
  mime_type: string
  byte_size: number
  rights_holder: string
  license_basis: string
  restriction: string | null
  category: MediaCategory
  publication_state: string
}
