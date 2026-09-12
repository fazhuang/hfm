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
