/**
 * Core person (皇甫谧) flagship anchors — UI-04 Huangfu Mi Profile.
 *
 * These are customer-confirmed flagship content anchors (UI-00 v2 content
 * model: PersonHero dates 215—282, 多维身份, 人生阶段) pending content
 * admission. Once 其传/后论/assertions/events are admitted and projected,
 * the UI should switch these sections to data-driven sources; these
 * constants remain the confirmed baseline until then ([DATA-GAP:
 * CONTENT_METADATA / ENTITY_RELATIONS]).
 */

export const CORE_PERSON_NAME = '皇甫谧'

/** 生卒年（客户确认内容模型 PersonHero.dates = 215—282） */
export const CORE_PERSON_DATES = '215—282'

/** 一句话权威定义（客户材料确认的权威表述，待其传内容准入后由数据驱动） */
export const CORE_PERSON_DEFINITION =
  '西晋著名医学家、文学家、史学家，针灸学专著《针灸甲乙经》的编纂者，世称针灸鼻祖。'

/** 多维身份（UI-00 v2 内容模型） */
export const CORE_PERSON_IDENTITIES = ['医学家', '文学家', '史学家', '学者'] as const

/** 人生阶段（客户导航要求：求学悟道 · 拒仕治学 · 久病研医 · 著书传世） */
export const CORE_PERSON_LIFE_PHASES: ReadonlyArray<{ title: string; note: string }> = [
  { title: '求学悟道', note: '少家贫，躬自稼穑，带经而农；就乡人席坦受书。' },
  { title: '拒仕治学', note: '屡征不仕，自号玄晏先生，专事著述。' },
  { title: '久病研医', note: '中年风痹，犹手不释卷，旁通医理。' },
  { title: '著书传世', note: '编撰《针灸甲乙经》等，垂范后世。' },
]

/** 核心著作入口（其言四篇 + 甲乙经；对应 /yan 与 /jiayi） */
export const CORE_PERSON_WORKS: ReadonlyArray<{ title: string; href: string; note: string }> = [
  { title: '三都赋', href: '/yan', note: '赋序' },
  { title: '玄守论', href: '/yan', note: '论' },
  { title: '释劝论', href: '/yan', note: '论' },
  { title: '笃终论', href: '/yan', note: '论' },
  { title: '《针灸甲乙经》', href: '/jiayi', note: '针灸学专著' },
]
