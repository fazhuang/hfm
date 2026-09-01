import type { ContentStatus } from './content'

/**
 * Archive record (UI-06) — 平台保存的实际数字材料。
 *
 * 公共 UI 只展示可理解的来源名称（SourceRef.name），绝不渲染内部绝对
 * 文件系统路径（registerKey 仅作开发 provenance）。
 */

export type ArchiveCategory =
  | 'hfm-person' // 皇甫谧人物资料
  | 'hfm-works' // 皇甫谧著作
  | 'jiayi-editions' // 《针灸甲乙经》版本资料
  | 'modern-research' // 现代研究资料
  | 'media' // 影像资料
  | 'heritage' // 非遗资料（入口；详细展示属 UI-09）

export interface ArchiveRecord {
  id: string
  title: string
  category: ArchiveCategory
  /** Public-facing source name (never an absolute internal path). */
  sourceName: string
  /** Internal register key for provenance; never rendered publicly. */
  registerKey?: string
  description: string
  /** Count when derivable from the audited register. */
  count?: number
  status: ContentStatus
  /** Optional primary destination. */
  href?: string
}

export interface ArchiveCategoryGroup {
  category: ArchiveCategory
  label: string
  description: string
  records: ArchiveRecord[]
}
