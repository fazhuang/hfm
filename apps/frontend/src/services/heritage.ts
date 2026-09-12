/**
 * Heritage lineage service (P2-04 heritage visualization).
 *
 * Consumes the public heritage endpoint (P1-06 API projection) and exposes
 * evidence-backed, published-only lineage data. Unverified or private nodes
 * are filtered out before rendering (P2-04-AC-02); no lineage is fabricated
 * (P2-04-AC-01 negative).
 */
import { publicGet } from './api'
import type { LineageNode, LineageProjection, LineageRelation } from '../types/heritage'

/** Published, evidence-backed nodes only (fail-closed display filter). */
export function visibleNodes(projection: LineageProjection): LineageNode[] {
  return projection.nodes.filter((n) => n.publicationState === 'published' && n.evidenceBound)
}

/** Published, evidence-backed relations only. */
export function visibleRelations(projection: LineageProjection): LineageRelation[] {
  return projection.relations.filter((r) => r.publicationState === 'published' && r.evidenceBound)
}

/** Load the public heritage lineage projection (P1-06 API). */
export function fetchHeritageLineage(entityId: string): Promise<LineageProjection> {
  return publicGet<LineageProjection>(`/api/v1/public/heritage/${entityId}`)
}
