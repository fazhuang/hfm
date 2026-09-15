import type { ContentStatus } from './content'

/**
 * 其言（UI-06）— Digital Quotation / Text Collection types.
 *
 * YanCollection mirrors the customer 其言.docx structure (collection intro +
 * four sections + supplement). QuotationRecord carries only fields the
 * material actually supports; editorial theme classification is explicitly
 * marked as PRESENTATION_CLASSIFICATION, never original-material taxonomy.
 */

export type ThemeClassification = 'PRESENTATION_CLASSIFICATION' | 'MATERIAL_STRUCTURE'

export interface QuotationRecord {
  id: string
  /** Text from the customer material (verbatim, unedited). */
  text: string
  /** Section in the customer collection. */
  section: string
  /** Editorial theme label — must be marked as presentation classification. */
  theme?: string
  themeClassification: ThemeClassification
  /** Source name shown to the public. */
  source: string
  /** Source context / notes from the material. */
  sourceContext?: string
  /** Related work (e.g. 《三都赋》序). */
  relatedWork?: string
  relatedPerson?: string
  notes?: string
  status: ContentStatus
}

export interface YanSection {
  id: string
  /** Section title (from the customer docx structure). */
  title: string
  records: QuotationRecord[]
  /** Full classical text not present in the docx — honest DATA_GAP. */
  fullTextStatus: ContentStatus
}

export interface YanCollection {
  title: string
  subtitle: string
  /** Collection intro (customer docx opening paragraph). */
  intro: string
  sections: YanSection[]
  /** Supplement paragraph from the customer docx. */
  supplement?: string
  source: string
}

// ---------------------------------------------------------------------------
// P-8a 全文录入（2026-09-15）
//
// 客户《其言》.docx 只有四篇的内容要点介绍，没有文言原文 —— 原 `fullTextStatus`
// 因此标为 DATA_GAP。四篇均为公版文献（皇甫谧卒于 282 年），本组类型承载
// 依公版录入的正文与校勘记。
//
// 录入规范（见 docs/product/HFM-PUBLIC-PORTAL-EXECUTION-PLAN-v1.md §3.2）：
// 底本用公版刻本，标点自行施加；两源以上互校，异文记录在案，不擅自择善。
// ---------------------------------------------------------------------------

/** 一部用于校勘的文献。 */
export interface YanTextSource {
  /** 版本标识，如「維基文庫《晉書》卷五十一所收本」。 */
  edition: string
  /** 该源在本篇上的定位。 */
  locus: string
  /** 对外呈现的引用形式。 */
  citation: string
}

/** 一处异文：底本用字与众本不同者。 */
export interface YanVariant {
  /** 底本用字（含上下文以便定位）。 */
  base: string
  /** 底本此处是否疑为脱文/讹字。 */
  baseSuspect?: boolean
  /** 他本异读。 */
  readings: ReadonlyArray<{ text: string; source: string }>
  /** 校记。 */
  note: string
}

/** 一篇的全文与校勘记。 */
export interface YanFullText {
  /** 底本正文，按自然段。 */
  paragraphs: readonly string[]
  /** 底本。 */
  base: YanTextSource
  /** 参校本。 */
  collated: readonly YanTextSource[]
  /** 校勘记。 */
  variants: readonly YanVariant[]
  /** 本篇录入的局限说明。 */
  caveat?: string
}
