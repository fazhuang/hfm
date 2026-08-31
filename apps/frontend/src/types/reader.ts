/**
 * Reader/search types (P2-03 reader/search frontend).
 *
 * Public-projection types only: passages and search results expose published
 * content with source/citation/rights context; no clinical semantics
 * (AB-14 / P2-03-AC-04).
 */
import type { PublicationState } from './public'

/** A resolvable passage locator (work/edition/version/passage chain). */
export interface PassageLocator {
  workId: string
  editionId?: string
  versionId: string
  passageId: string
}

/** A reader passage with source/citation/rights context. */
export interface ReaderPassage {
  locator: PassageLocator
  quotation: string
  sourceTitle: string
  citation: string
  rightsNote: string
  publicationState: PublicationState
}

/** A search result item (published projection). */
export interface SearchResultItem {
  id: string
  title: string
  sourceContext: string
  publicationState: PublicationState
}
