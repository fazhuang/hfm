/**
 * Export client (P2-06 export/print).
 *
 * Produces deterministic markdown/print output with the historical-research
 * disclaimer always retained; withdrawn/draft records are never exportable
 * (fail-closed at the service boundary).
 */

/** Historical-research disclaimer (G9) retained in every export output. */
export const EXPORT_DISCLAIMER =
  '本文为历史文献研究内容，仅供学术研究；不构成任何诊断、治疗、用药或穴位操作建议。'

export interface ExportRecord {
  title: string
  body: string
  publicationState: 'published' | 'draft' | 'withdrawn'
}

const BLOCKED_STATES: ReadonlySet<string> = new Set(['withdrawn', 'draft'])

export class ExportError extends Error {
  constructor(message: string) {
    super(message)
    this.name = 'ExportError'
  }
}

/** Deterministic markdown export with the disclaimer retained. */
export function exportMarkdown(record: ExportRecord): string {
  assertExportable(record)
  return `# ${record.title}\n\n${record.body}\n\n> ${EXPORT_DISCLAIMER}\n`
}

/** Deterministic print artifact with the disclaimer retained. */
export function exportPrint(record: ExportRecord): string {
  assertExportable(record)
  return `${record.title}\n${'='.repeat(record.title.length)}\n${record.body}\n\n${EXPORT_DISCLAIMER}\n`
}

function assertExportable(record: ExportRecord): void {
  if (BLOCKED_STATES.has(record.publicationState)) {
    throw new ExportError(`cannot export ${record.publicationState} content`)
  }
}
