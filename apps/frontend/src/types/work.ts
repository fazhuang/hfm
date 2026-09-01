import type { ContentStatus } from './content'

/**
 * WORK layer (UI-06) — 作品语义，区别于 EDITION 与 ARCHIVE RECORD。
 *
 * Work = 作品（如《针灸甲乙经》《帝王世纪》《高士传》）；
 * Edition = 具体版本（见 UI-08 jiayi editions / jiayiView）；
 * ArchiveRecord = 平台保存的实际数字材料（见 archiveInventory）。
 * 禁止"一个 PDF = 一本书"。
 */

export type WorkKind = 'canonical' | 'essay' | 'compilation' | 'related-material'

export interface WorkRecord {
  id: string
  title: string
  workType: string
  attribution: string
  historicalPeriod: string
  description: string
  /** Edition count only when derivable from the audited register. */
  editionCount?: number
  /** Primary destination for the WORK. */
  href?: string
  /** Short related-note. */
  note?: string
  status: ContentStatus
  kind: WorkKind
}
