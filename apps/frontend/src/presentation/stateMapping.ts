/**
 * UX2 shared presentation logic (G1-C state mapping + G4 N-F-1 titleTag contract).
 *
 * Presentation-only. No domain fields are created: predicates that are not
 * literal backend fields (scholarlyUncertain, historicalAbsence,
 * collationDescriptionPresent, digitizedResourceAbsent) are
 * DERIVED_PRESENTATION_ONLY and MUST be supplied by callers from verified
 * source text — never inferred from data absence.
 *
 * State mapping contract (G1-C §0):
 *   DETERMINISTIC · TOTAL_FOR_SUPPORTED_INPUTS · PRIORITY_DEFINED · FAIL_CLOSED
 * Precedence (G1-C §3, higher wins):
 *   7 SCHOLARLY_UNCERTAIN — documented controversy outranks availability.
 *   6 HISTORICAL_ABSENCE  — documented loss outranks unavailability (never
 *                           inferred from data absence).
 *   5 RESOURCE_READY      — available resource (no controversy/loss).
 *   4 METADATA_ONLY       — bibliographic record only.
 *   3 UNSTRUCTURED_OR_INCOMPLETE — platform incompleteness (fail-closed default).
 *
 * titleTag contract (frozen N-F-1 resolution, G4 contract §5):
 *   titleTag 1..6                → semantic heading h1..h6
 *   titleTag null|undefined|"none" → non-heading <p>
 *   anything else, including 0   → invalid → fail-closed <p> + dev warning
 *   0 is NOT a valid production titleTag value. No truthiness-based branch.
 */

export type ContentStatus = 'AVAILABLE' | 'METADATA_ONLY' | 'DATA_GAP'
export type ReadingAvailability = 'FULL_TEXT' | 'EXCERPT' | 'METADATA_ONLY'

export type PresentationState =
  | 'RESOURCE_READY'
  | 'METADATA_ONLY'
  | 'SCHOLARLY_UNCERTAIN'
  | 'HISTORICAL_ABSENCE'
  | 'UNSTRUCTURED_OR_INCOMPLETE'

export const PRESENTATION_STATES: readonly PresentationState[] = [
  'RESOURCE_READY',
  'METADATA_ONLY',
  'SCHOLARLY_UNCERTAIN',
  'HISTORICAL_ABSENCE',
  'UNSTRUCTURED_OR_INCOMPLETE',
] as const

export function isPresentationState(value: string | null | undefined): value is PresentationState {
  return value !== null && value !== undefined && (PRESENTATION_STATES as readonly string[]).includes(value)
}

export const PRESENTATION_STATE_PRECEDENCE: Record<PresentationState, number> = {
  SCHOLARLY_UNCERTAIN: 7,
  HISTORICAL_ABSENCE: 6,
  RESOURCE_READY: 5,
  METADATA_ONLY: 4,
  UNSTRUCTURED_OR_INCOMPLETE: 3,
}

export interface PresentationStateInputs {
  /** existing ContentStatus (source fact). */
  contentStatus?: ContentStatus | null
  /** existing ReadingAvailability (source fact). */
  readingAvailability?: ReadingAvailability | null
  /** metadata fields present (source fact, G1-C row 3). */
  hasMetadata?: boolean
  /** 整理说明/collation description present while the classical full text is
   *  not in corpus (G1-C row 5 — 仅题录（原典全文未收录）, never 文献阙佚). */
  collationDescriptionPresent?: boolean
  /** DERIVED_PRESENTATION_ONLY: verified text explicitly records 佚/散佚
   *  (G1-C row 6 — loss is never inferred from data absence). */
  historicalAbsence?: boolean
  /** DERIVED_PRESENTATION_ONLY: verified text explicitly asserts scholarly
   *  controversy, e.g. 生卒年 建安/正始 之议 (G1-C row 7). */
  scholarlyUncertain?: boolean
  /** digitized resource absent for an existing edition (G1-C row 10 — 存目). */
  digitizedResourceAbsent?: boolean
}

/**
 * Deterministic SOURCE FACT → PRESENTATION STATE mapping (G1-C §2 rows 1–7, 10).
 * Rows 8/9/11 (lineage PARTIAL, edition-relations DATA-GAP, papers
 * unstructured) are surface-specific incomplete states; callers pass the
 * fail-closed default for them (UNSTRUCTURED_OR_INCOMPLETE).
 */
export function resolvePresentationState(inputs: PresentationStateInputs): PresentationState {
  const {
    contentStatus,
    readingAvailability,
    hasMetadata,
    collationDescriptionPresent,
    historicalAbsence,
    scholarlyUncertain,
    digitizedResourceAbsent,
  } = inputs

  // Precedence 7 — documented controversy outranks availability (row 7).
  if (scholarlyUncertain === true) return 'SCHOLARLY_UNCERTAIN'

  // Precedence 6 — documented loss outranks unavailability (row 6).
  if (historicalAbsence === true) return 'HISTORICAL_ABSENCE'

  // Precedence 5 — RESOURCE_READY (rows 1, 2, 12, 13).
  if (contentStatus === 'AVAILABLE') {
    if (readingAvailability === 'FULL_TEXT' || readingAvailability === 'EXCERPT') return 'RESOURCE_READY'
    if (digitizedResourceAbsent === true) return 'METADATA_ONLY' // row 10 — edition 存目
    return 'RESOURCE_READY'
  }

  // Precedence 4 — METADATA_ONLY (rows 3, 5).
  if (contentStatus === 'METADATA_ONLY' && hasMetadata !== false) return 'METADATA_ONLY'
  if (collationDescriptionPresent === true) return 'METADATA_ONLY'

  // Precedence 3 — fail-closed default (rows 4, 8, 9, 11-rest; unknown inputs).
  return 'UNSTRUCTURED_OR_INCOMPLETE'
}

export interface PresentationLabelOptions {
  /** reader/full-text context → 全文已整理. */
  reader?: boolean
  /** excerpt-only resource → 存目. */
  excerpt?: boolean
  /** searchable subset → 仅题录（可检索）. */
  searchable?: boolean
}

/** Canonical PUBLIC LABEL per presentation state (G1-C §6). */
export function presentationLabel(state: PresentationState, options: PresentationLabelOptions = {}): string {
  switch (state) {
    case 'RESOURCE_READY':
      return options.reader ? '全文已整理' : '数字资源可阅'
    case 'METADATA_ONLY':
      if (options.excerpt) return '存目'
      if (options.searchable) return '仅题录（可检索）'
      return '仅题录'
    case 'SCHOLARLY_UNCERTAIN':
      return '尚有争议'
    case 'HISTORICAL_ABSENCE':
      return '文献阙佚'
    case 'UNSTRUCTURED_OR_INCOMPLETE':
      return '资料整理中'
  }
}

/** Badge label: explicit label wins; else canonical label for a known state; else raw status; else fail-closed text. */
export function presentationStatusLabel(status: string | null | undefined, explicitLabel?: string | null): string {
  if (explicitLabel !== null && explicitLabel !== undefined && explicitLabel !== '') return explicitLabel
  if (status !== null && status !== undefined && status !== '' && isPresentationState(status)) {
    return presentationLabel(status)
  }
  return status !== null && status !== undefined && status !== '' ? status : '资料整理中'
}

export type TitleTag = number | 'none' | null | undefined

/**
 * N-F-1 production contract (G4 §5) — deterministic, NO truthiness branch:
 *   1..6 → h1..h6 ; null | undefined | "none" → 'p' ;
 *   anything else (including 0) → 'p' + development warning.
 */
export function resolveTitleTag(tag: TitleTag): string {
  if (typeof tag === 'number' && Number.isInteger(tag) && tag >= 1 && tag <= 6) {
    return `h${tag}`
  }
  if (tag === null || tag === undefined || tag === 'none') {
    return 'p'
  }
  if (import.meta.env.DEV) {
    console.warn(
      `[UX2 DHObjectLayout] invalid titleTag=${String(tag)} — failing closed to non-heading <p>. ` +
        'Valid values: 1..6, null, undefined, "none". 0 is NOT a valid production titleTag value.',
    )
  }
  return 'p'
}
