/**
 * Homepage projection types (UI-03).
 *
 * Presentation/selection layer only — never duplicates Person/Work/Edition/
 * Heritage/Paper domain data. All numbers come from contentInventory.
 */
import type { ContentStatus } from './content'

export interface HomeMetric {
  label: string
  value: string
  /** Accurate semantic note (e.g. 审计 vs 结构化). */
  note: string
}

export interface HomeQuotation {
  text: string
  attribution: string
  source: string
}

export interface HomeFeatureLink {
  label: string
  href: string
}

export interface HomeEditionPreview {
  title: string
  period: string
  imprint?: string
}

export interface HomeFeature {
  heading: string
  lede: string
  items?: Array<{ title: string; meta?: string; href?: string }>
  status?: ContentStatus
}
