/**
 * Heritage lineage types (P2-04 heritage visualization).
 *
 * Public lineage projection from the P1-06 relations API: nodes and
 * relations carry evidence and publication state; unverified or private
 * nodes are never displayed publicly (P2-04-AC-02).
 */
import type { PublicationState } from './public'

/** A lineage node (person/institution in the transmission chain). */
export interface LineageNode {
  id: string
  name: string
  officialName?: string
  evidenceBound: boolean
  publicationState: PublicationState
}

/** A directed transmission relation between two nodes. */
export interface LineageRelation {
  id: string
  from: string
  to: string
  relationType: string
  evidenceBound: boolean
  publicationState: PublicationState
}

/** The lineage projection returned by the public heritage API. */
export interface LineageProjection {
  nodes: LineageNode[]
  relations: LineageRelation[]
}
