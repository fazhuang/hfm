/**
 * Public portal navigation configuration.
 *
 * 主导航按 HFM-UI-CONTRACT-v2 §2 与参考图（`HFM-SY-CK.png` / `HFM-LM-CK.png`）
 * 定为 8 项 —— 取代此前的"客户强制 5 链接"。
 *
 * 检索在页头工具区；「进入研究工作台」按参考图是工具区的按钮，指向 /research
 * （未登录时由路由守卫转登录页）。
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

/** 皇甫谧核心人物路由（全站唯一规范路由）。 */
export const CORE_PERSON_ROUTE = '/persons/ENT-PERSON-HFM-HUANGFUMI'

export const PUBLIC_NAV_ITEMS: readonly NavItem[] = [
  { label: '首页', href: '/', description: '平台首页' },
  { label: '人物', href: CORE_PERSON_ROUTE, description: '皇甫谧生平、学术成就与思想体系' },
  { label: '典籍', href: '/jiayi', description: '《针灸甲乙经》版本谱系、结构导览与原刻影印' },
  { label: '知识图谱', href: '/knowledge', description: '经穴术语与知识实体的关联' },
  { label: '数字资源', href: '/library', description: '影印、影像与档案的开放访问' },
  { label: '研究', href: '/research', description: '研究工作台（需登录）' },
  { label: '互动', href: '/interactive', description: '互动与沉浸式内容' },
  { label: '关于', href: '/about', description: '平台介绍、合规与联系方式' },
] as const

/** 栏目页二级导航（参考图 `HFM-LM-CK.png`）。锚点落在人物页各段。 */
export const PERSON_SECTION_NAV: readonly { label: string; href: string }[] = [
  { label: '概览', href: '#person-overview' },
  { label: '生平年表', href: '#person-timeline' },
  { label: '学术成就', href: '#person-works' },
  { label: '思想体系', href: '#person-thought' },
  { label: '历史影响', href: '#person-influence' },
  { label: '相关人物', href: '#person-related' },
  { label: '研究论文', href: '#person-papers' },
] as const
