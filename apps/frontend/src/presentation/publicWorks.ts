/**
 * publicWorks — presentation projection for the public works list (GAP-02).
 *
 * REAL WORKS DATA → PRESENTATION PROJECTION. Input is the backend
 * /api/v1/public/works response (WorkSummary); this module maps server rows
 * to public display rows with a real canonical route (/works/:id) and an
 * honest meta line (dynasty · category). A field the server omits is
 * presented as ABSENT — never "未知/N/A".
 */
import type { WorkSummary } from '../types/public'

export interface PublicWorkRow {
  workId: string
  title: string
  /** "朝代 · 类别" — only the fields the server actually returned. */
  meta: string
  editionCount: number
  /** Real canonical route (mirrors presentation/searchResults navigation policy). */
  href: string
}

/** Map backend work rows to presentation rows (API DATA → PROJECTION). */
export function toPublicWorkRows(works: readonly WorkSummary[]): PublicWorkRow[] {
  return works.map((w) => {
    const parts = [w.dynasty, w.category].filter(
      (p): p is string => typeof p === 'string' && p !== '',
    )
    return {
      workId: w.work_id,
      title: w.title,
      meta: parts.join(' · '),
      editionCount:
        typeof w.edition_count === 'number' && w.edition_count > 0 ? w.edition_count : 0,
      href: `/works/${w.work_id}`,
    }
  })
}
