/**
 * Jiayi Jing — UI-08 《针灸甲乙经》核心学术界面 types.
 *
 * All display records are built from the audited customer material register
 * (hfmzl/针灸甲乙经/…) — no invented publishers, years, or relationships.
 * Structured edition-lineage remains [DATA-GAP: JIAYI_EDITION_RELATIONS];
 * the customer-provided lineage PNG is displayed as an asset, never
 * reconstructed as a formal genealogical edge set.
 */

import type { ContentStatus } from './content'

/** Content status shared across content surfaces (defined in types/content.ts). */
export type { ContentStatus } from './content'

/** One edition record (metadata only — no file content promised). */
export interface EditionRecord {
  id: string
  /** Edition title (from the material). */
  title: string
  /** Era / date — only when the material supports it. */
  period: string
  /** Publisher / collection / imprint — only when the material names it. */
  imprint?: string
  /** Edition type: 古代版本 / 近现代整理版本. */
  editionType: 'ancient' | 'modern'
  description: string
  /** Source path in the customer material register. */
  source: string
  status: ContentStatus
  /** Gregorian year when derivable from the material (chronology only). */
  year?: number
}

/** Related work entry (WORK level — distinct from editions). */
export interface RelatedWork {
  id: string
  title: string
  kind: 'work' | 'related-material'
  note: string
  href?: string
}

/** Modern collation/research record — names only where the material supports them. */
export interface ModernScholarRecord {
  id: string
  title: string
  collator: string
  year: number
  source: string
  kind: 'collation' | 'modern-edition' | 'research'
}

/** Paper bibliography record (preview + count from audited register). */
export interface PaperRecord {
  id: string
  title: string
  /** Real paper filenames from the customer register; author/year when in the name. */
  note?: string
}
