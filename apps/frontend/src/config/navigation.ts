/**
 * Public portal navigation configuration (UI-02 Global Shell / Navigation).
 *
 * Customer-mandated 5-link main navigation (2026-08-31). Search / login /
 * about are NOT part of the main nav: search + login live in the header
 * utility area, about lives in the footer.
 *
 * NOTE: the 皇甫谧 person route uses a frontend constant until content
 * admission assigns the canonical entity id ([DATA-GAP: CONTENT_METADATA /
 * ENTITY_RELATIONS]); PersonDetailView degrades to an empty state when the
 * record is absent — no fabricated content.
 */
export interface NavItem {
  label: string
  href: string
  /** Short aria/description used for the mobile drawer and a11y. */
  description: string
}

/** 皇甫谧 core person canonical route (UI-12 correction: aligned with the
 * canonical entity route /persons/person-huangfu-mi used across PersonDetail
 * and all public CTAs). */
export const CORE_PERSON_ROUTE = '/persons/person-huangfu-mi'

export const PUBLIC_NAV_ITEMS: readonly NavItem[] = [
  { label: '首页', href: '/', description: '平台首页' },
  { label: '人物（皇甫谧）', href: CORE_PERSON_ROUTE, description: '皇甫谧人物档案' },
  { label: '其言', href: '/yan', description: '其言：三都赋、玄守论、释劝论、笃终论' },
  { label: '《针灸甲乙经》', href: '/jiayi', description: '针灸甲乙经：版本脉络、论著、论文' },
  {
    label: '皇甫谧针灸非遗的传承',
    href: '/heritage',
    description: '皇甫谧针灸非遗传承：证书、非遗资料、传承人物',
  },
] as const
