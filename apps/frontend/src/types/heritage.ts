/**
 * Heritage types (UI-09 — 非遗活态传承数字档案).
 *
 * Keeps the P2-04 API projection types (LineageNode / LineageRelation /
 * LineageProjection + services contract) and adds the flagship content
 * models built from the audited zzcl/ register.
 *
 * Content discipline: only customer-material-supported fields are filled;
 * nothing is derived from common knowledge. Lineage only contains confirmed
 * nodes/edges — intermediate generations stay PARTIAL with an explicit note.
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

/* ============ UI-09 flagship content models ============ */

/** 非遗项目本体 — distinct from the heritage person. */
export interface HeritageProject {
  name: string
  classification: string
  recognitionLevel?: string
  description: string
  inheritors: string[]
  activities: string[]
  sourceName: string
}

/** 传承人物档案 — 第六代名医·刘君奇 (HERITAGE_GENERATION CLOSED). */
export interface HeritagePersonProfile {
  name: string
  generationTitle: string
  heritageRole: string
  professionalTitle: string
  institutionRole: string
  biography: string
  academicRoles: string[]
  sourceName: string
}

/** 认定与荣誉记录（结构化；证书图像如需展示走脱敏 public derivative）。 */
export interface RecognitionRecord {
  id: string
  title: string
  category: '非遗认定' | '职业荣誉' | '学术荣誉' | '技术奖励' | '社会荣誉'
  issuer: string
  date: string
  description: string
  sourceName: string
}

/** 学术成果记录。 */
export interface AcademicAchievementRecord {
  id: string
  title: string
  year: string
  type: '研究项目' | '学术成果' | '论文' | '学术任职' | '学术活动'
  description: string
  sourceName: string
}

/** 技术成果记录 — 档案记录"是什么"，不扩展医疗含义。 */
export interface TechnicalAchievementRecord {
  id: string
  title: string
  year: string
  award: string
  issuer: string
  description: string
  sourceName: string
}

/** 师承教育活动。 */
export interface ApprenticeshipEvent {
  id: string
  title: string
  date: string
  location?: string
  description: string
  sourceName: string
}

/** 名中医工作室。 */
export interface StudioRecord {
  id: string
  name: string
  institution: string
  description: string
  sourceName: string
}

/** 媒体报道。 */
export interface MediaCoverage {
  id: string
  title: string
  mediaOutlet: string
  date: string
  description: string
  sourceName: string
}

/** 谱系节点（已确认节点 + 明确 PARTIAL 说明；不虚构中间代）。 */
export interface ConfirmedLineageNode {
  id: string
  person: string
  generation?: string
  role?: string
  evidence: string
  href?: string
}
