/**
 * Home public-data enrichment (REM-02).
 *
 * The homepage keeps its accepted editorial presentation (homeProjection +
 * contentInventory + config — the frozen 8-section narrative). This module is
 * the typed ADAPTER between the real backend `/api/v1/public/home` payload
 * (PortalService.home → api_response.data {works, counts:{works,persons,
 * heritage_projects,c_terms}}) and a safe enrichment object the orchestrator
 * can expose/consume. It is defensive: any unexpected/partial payload maps to
 * typed defaults and never throws, so backend data can never break the
 * homepage (integration, not CMS-ification).
 */
import type { HomeCounts, WorkSummary } from '../types/public'

/** Backend → enrichment mapping result for a successful /public/home call. */
export interface HomePublicEnrichment {
  works: WorkSummary[]
  counts: HomeCounts
  /** True only when the backend payload carried at least one non-empty part. */
  hasData: boolean
}

const EMPTY_COUNTS: HomeCounts = {
  works: 0,
  persons: 0,
  heritage_projects: 0,
  c_terms: 0,
}

function toCount(value: unknown): number {
  return typeof value === 'number' && Number.isFinite(value) && value >= 0 ? Math.floor(value) : 0
}

function toWork(row: unknown): WorkSummary | null {
  if (row === null || typeof row !== 'object') return null
  const r = row as Record<string, unknown>
  if (typeof r.work_id !== 'string' || !r.work_id) return null
  return {
    work_id: r.work_id,
    title: typeof r.title === 'string' ? r.title : '',
    dynasty: typeof r.dynasty === 'string' ? r.dynasty : null,
    category: typeof r.category === 'string' ? r.category : null,
    edition_count: toCount(r.edition_count),
    publication_status:
      typeof r.publication_status === 'string' ? r.publication_status : 'published',
  }
}

/**
 * Map an unknown /api/v1/public/home payload to a safe enrichment.
 * Never throws; never trusts field presence.
 */
export function mapPublicHomeToEnrichment(payload: unknown): HomePublicEnrichment {
  const root =
    payload !== null && typeof payload === 'object' ? (payload as Record<string, unknown>) : {}
  const rawWorks = Array.isArray(root.works) ? root.works : []
  const works = rawWorks
    .map((w) => toWork(w))
    .filter((w): w is WorkSummary => w !== null)
  const rawCounts =
    root.counts !== null && typeof root.counts === 'object'
      ? (root.counts as Record<string, unknown>)
      : {}
  const counts: HomeCounts = {
    works: toCount(rawCounts.works),
    persons: toCount(rawCounts.persons),
    heritage_projects: toCount(rawCounts.heritage_projects),
    c_terms: toCount(rawCounts.c_terms),
  }
  const hasData = works.length > 0 || counts.works + counts.persons + counts.heritage_projects + counts.c_terms > 0
  return { works, counts, hasData }
}

/** The empty enrichment used when the backend is unavailable. */
export function emptyHomeEnrichment(): HomePublicEnrichment {
  return { works: [], counts: { ...EMPTY_COUNTS }, hasData: false }
}
