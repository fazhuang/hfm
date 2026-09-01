/**
 * Reader projection types (UI-07 — Ancient Text / Scholarly Reader).
 *
 * Reader is a DISPLAY projection over verified content — it never redefines
 * Work / Edition domain facts. Documents are built from real customer docx
 * text (read-only extraction). Classical full texts not present in customer
 * materials stay DATA_GAP — never fabricated.
 */
import type { ContentStatus } from './content'
import type { PublicationState } from './public'

/** Reader-specific reading availability (NOT copyright states). */
export type ReadingAvailability = 'FULL_TEXT' | 'EXCERPT' | 'METADATA_ONLY'

/* ===== Legacy P2-03 reader/search service types (keep contract intact) ===== */

/** Deterministic passage locator (P2-03-AC-01 reproducibility). */
export interface PassageLocator {
  workId: string
  editionId: string
  versionId: string
  passageId: string
}

/** A published-projection passage (reader resolve / search). */
export interface ReaderPassage {
  locator: PassageLocator
  quotation: string
  sourceTitle?: string
  citation?: string
  rightsNote?: string
  publicationState: PublicationState
}

/** A published search result item (anonymous scope). */
export interface SearchResultItem {
  kind: string
  id: string
  title: string
  snippet: string
  publicationState: PublicationState
}

export interface ReaderCitation {
  /** Attribution (评价者/整理者). */
  attribution: string
  /** Source name (出处/文献). */
  source: string
}

export interface ReaderSection {
  id: string
  heading: string
  /** Stable paragraph anchor ids when real structure supports them. */
  paragraphs?: Array<{ id: string; text: string; citation?: ReaderCitation; note?: string }>
  /** Table-like real entries (e.g. 影视/著作/命名名录). */
  entries?: Array<{ title: string; meta?: string; note?: string }>
}

export interface ReaderDocument {
  id: string
  title: string
  subtitle: string
  textType: string
  attribution?: string
  period?: string
  description: string
  sections: ReaderSection[]
  source: string
  readingStatus: ReadingAvailability
  contentStatus: ContentStatus
  relatedEntities: Array<{ label: string; href: string }>
  /** Edition context — only when the text is bound to a specific edition. */
  editionContext?: { work: string; edition?: string; period?: string; note?: string }
}
