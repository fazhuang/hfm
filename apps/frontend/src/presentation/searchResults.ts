/**
 * searchResults — CF-06 presentation projection for public search.
 *
 * REAL SEARCH DATA → PRESENTATION PROJECTION. Input is the backend
 * /api/v1/public/search response (kind-tagged SearchHit); this module maps
 * server kinds to public labels and to REAL canonical routes only.
 *
 * Navigation policy (CF-06 §9): a result is navigable only when the product
 * has a stable public route for that kind:
 *   - person → /persons/:id            (canonical person page)
 *   - work   → /works/:id              (canonical work detail page)
 * Other kinds (edition / heritage_project / c_term / passage / media) have
 * no stable per-record public page yet — they render WITHOUT an invented
 * link rather than fabricating a route.
 *
 * Labels are presentation copy; kind membership comes strictly from the
 * backend response. No local searchIndex participates in result data.
 */
import type { SearchHit } from '../types/public'

export interface SearchResultRow {
  kind: string
  kindLabel: string
  title: string
  snippet: string
  /** Real canonical route when the product has one; undefined otherwise. */
  href?: string
}

/** Presentation labels for the backend's published-search kinds. */
const KIND_LABELS: Record<string, string> = {
  person: '人物',
  work: '作品',
  edition: '版本',
  heritage_project: '非遗档案',
  c_term: '术语',
  passage: '文本片段',
  media: '资料',
}

const DEFAULT_LABEL = '条目'

/** Fallback label for an unknown server kind (still not a client decision). */
export function kindLabelOf(kind: string): string {
  return KIND_LABELS[kind] ?? DEFAULT_LABEL
}

/** Real canonical route for a kind; no route is invented for other kinds. */
export function canonicalHrefFor(hit: SearchHit): string | undefined {
  if (hit.kind === 'person') return `/persons/${hit.id}`
  if (hit.kind === 'work') return `/works/${hit.id}`
  return undefined
}

/** Map backend hits to presentation rows (API DATA → PROJECTION). */
export function toSearchResultRows(hits: readonly SearchHit[]): SearchResultRow[] {
  return hits.map((hit) => ({
    kind: hit.kind,
    kindLabel: kindLabelOf(hit.kind),
    title: hit.title,
    snippet: hit.snippet ?? '',
    href: canonicalHrefFor(hit),
  }))
}
