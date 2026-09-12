/**
 * Shared content types (UI-06).
 *
 * Customer materials are publication-authorized; copyright states are out of
 * scope. Content states: AVAILABLE / METADATA_ONLY / DATA_GAP.
 */

/** Content state — customer materials are authorized; copyright states are out. */
export type ContentStatus = 'AVAILABLE' | 'METADATA_ONLY' | 'DATA_GAP'

/** Public-facing source name (never an internal absolute path). */
export interface SourceRef {
  /** Human-readable source name shown to the public. */
  name: string
  /** Material register key (e.g. 'qiyan-docx'); internal provenance only. */
  registerKey?: string
  status: ContentStatus
}
