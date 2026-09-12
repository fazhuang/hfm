/**
 * CF-02 presentation state semantics — minimal shared contract.
 *
 * Presentation-only. Never invents provenance, content, scholarly conclusions,
 * or field values. A state is derived deterministically from real data / props
 * / domain projection, never inferred by a visual component on its own.
 *
 * Contract:
 *   DETERMINISTIC · TOTAL_FOR_SUPPORTED_INPUTS · FAIL_CLOSED
 *
 * The states cover the real states present in the recovery foundation:
 *   COMPLETE    — the object / field is fully available.
 *   PARTIAL     — explicitly known partial record (e.g. lineage PARTIAL gap).
 *   UNAVAILABLE — documented unavailability (never inferred from absence).
 *   UNKNOWN     — value is genuinely unknown / undocumented.
 *   LOADING     — a real, asynchronous load is in progress (live region ok).
 *   ERROR       — a real load / projection error occurred (role="alert").
 *
 * DATA STATE != VISUAL DECORATION: a component receives a state from its
 * caller's projection; it must not fabricate a state for visual effect.
 */

export type PresentationState =
  | 'COMPLETE'
  | 'PARTIAL'
  | 'UNAVAILABLE'
  | 'UNKNOWN'
  | 'LOADING'
  | 'ERROR'

export const PRESENTATION_STATES: readonly PresentationState[] = [
  'COMPLETE',
  'PARTIAL',
  'UNAVAILABLE',
  'UNKNOWN',
  'LOADING',
  'ERROR',
] as const

export function isPresentationState(value: string | null | undefined): value is PresentationState {
  return (
    value !== null && value !== undefined && (PRESENTATION_STATES as readonly string[]).includes(value)
  )
}

/** Deterministic source-fact → presentation state. Fail-closed default is UNKNOWN. */
export type PresentationStateInputs = {
  /** A real, explicitly-known completeness signal from the projection. */
  completeness?: 'COMPLETE' | 'PARTIAL' | 'UNAVAILABLE' | 'UNKNOWN'
  /** A real load/projection error (only from an actual thrown/known failure). */
  loadError?: boolean
  /** A real, in-progress async load. */
  loading?: boolean
}

export function resolvePresentationState(inputs: PresentationStateInputs): PresentationState {
  if (inputs.loading === true) return 'LOADING'
  if (inputs.loadError === true) return 'ERROR'
  if (inputs.completeness === 'COMPLETE') return 'COMPLETE'
  if (inputs.completeness === 'PARTIAL') return 'PARTIAL'
  if (inputs.completeness === 'UNAVAILABLE') return 'UNAVAILABLE'
  if (inputs.completeness === 'UNKNOWN') return 'UNKNOWN'
  return 'UNKNOWN' // fail-closed
}

/** Canonical public label for a presentation state (readable without color alone). */
export function presentationLabel(state: PresentationState): string {
  switch (state) {
    case 'COMPLETE':
      return '完成'
    case 'PARTIAL':
      return '部分整理'
    case 'UNAVAILABLE':
      return '暂不可用'
    case 'UNKNOWN':
      return '未知'
    case 'LOADING':
      return '正在加载'
    case 'ERROR':
      return '加载失败'
  }
}

/** Badge label: explicit label wins, else canonical label, else fail-closed '未知'. */
export function presentationStatusLabel(
  status: string | null | undefined,
  explicitLabel?: string | null,
): string {
  if (explicitLabel !== null && explicitLabel !== undefined && explicitLabel !== '') {
    return explicitLabel
  }
  if (status !== null && status !== undefined && status !== '' && isPresentationState(status)) {
    return presentationLabel(status)
  }
  return '未知'
}

export type TitleTag = number | 'none' | null | undefined

/**
 * N-F-1 heading contract — deterministic, no truthiness branch:
 *   1..6 → h1..h6   ;   null / undefined / 'none' → non-heading <p>
 *   anything else (including 0) → fail-closed <p> + a dev warning.
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
      `[CF-02] invalid titleTag=${String(tag)} — failing closed to non-heading <p>. ` +
        'Valid: 1..6, null, undefined, "none". 0 is not a valid production titleTag value.',
    )
  }
  return 'p'
}
