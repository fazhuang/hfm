/**
 * Research presentation types (UI-11).
 *
 * View-model layer only — never duplicates Work/Edition/Person/Archive/
 * Evidence domain models. Research projections wrap existing domain data
 * with denser metadata presentation. Evidence "state" strictly maps the
 * existing ContentStatus; no invented governance states.
 */
import type { ContentStatus } from './content'
import type { SearchType } from './search'

export type ResearchEntityType = SearchType | 'heritage' | 'reader'

export interface ResearchEvidenceSummary {
  sourceName: string
  contentStatus: ContentStatus
  /** Citation availability — real citation data exists (e.g. 后论 引文). */
  citationCount?: number
  note?: string
}

export interface ResearchRelatedLink {
  label: string
  href: string
}

export interface ResearchEntityViewModel {
  type: ResearchEntityType
  id: string
  title: string
  subtitle: string
  /** Research-oriented metadata (definition-list style). */
  metadata: Array<{ label: string; value: string }>
  /** Real evidence summary (mapped from ContentStatus + sources). */
  evidence: ResearchEvidenceSummary[]
  related: ResearchRelatedLink[]
  /** Public counterpart link (Research → Public). */
  publicLink?: ResearchRelatedLink
  /** Optional body/description. */
  description?: string
  /** Optional items (editions/records). */
  items?: Array<{ title: string; meta?: string }>
}
