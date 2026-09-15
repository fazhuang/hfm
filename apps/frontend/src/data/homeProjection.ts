/**
 * homeProjection — UI-03 homepage content projection.
 *
 * SELECTS and orders existing verified data only. No new domain facts, no
 * duplicated models, no fabricated quotes or metrics. All counts come from
 * contentInventory (single source). 515/5 paper split, Jiayi lineage
 * DATA-GAP, Heritage lineage PARTIAL, 刘君奇 第六代名医 invariants hold.
 */
import type {
  HomeEditionPreview,
  HomeFeature,
  HomeFeatureLink,
  HomeMetric,
  HomeQuotation,
} from '../types/home'
import {
  CORE_PERSON_DATES,
  CORE_PERSON_DEFINITION,
  CORE_PERSON_IDENTITIES,
  CORE_PERSON_LIFE_PHASES,
  CORE_PERSON_NAME,
} from '../config/corePerson'
import {
  INVENTORY_EDITION_RECORDS,
  INVENTORY_LUNWEN_FILES,
  INVENTORY_LUNZHU_FILES,
} from './contentInventory'
import { SEARCHABLE_PAPER_TOTAL, SEARCH_INDEX } from './searchIndex'
import { getReaderDocument, READER_DOCUMENTS } from './readerDocuments'
import { HERITAGE_PERSON } from './heritageView'
import {
  JIAYI_ANCIENT_EDITIONS,
  JIAYI_MODERN_EDITIONS,
  JIAYI_LINEAGE_IMAGE_ALT,
  JIAYI_LINEAGE_IMAGE_SRC,
} from './jiayiView'

export const HOME_HERO = {
  /** 首屏 H1（参考图 HFM-SY-CK 的写法）。 */
  title: '走进皇甫谧的世界',
  subtitle: '在这里，历史、典籍与当代生活相遇。',
  kicker: ['HFM', 'TRADITION', 'IN DATA', 'HUMANITY', 'FOR TOMORROW'],
  personName: CORE_PERSON_NAME,
  personDates: CORE_PERSON_DATES,
  definition: CORE_PERSON_DEFINITION,
  primary: [
    { label: '开启探索', href: '/persons/ENT-PERSON-HFM-HUANGFUMI' },
    { label: '阅读《针灸甲乙经》', href: '/jiayi' },
  ],
  /** 首屏右侧引文卡 —— 皇甫谧本人的话，注明出处。 */
  quote: {
    text: '上以疗君亲之疾，下以救贫贱之厄，中以保身长全。',
    source: '皇甫谧《针灸甲乙经·序》',
  },
  place: { zh: '甘肃 · 灵台', en: 'LINGTAI · GANSU' },
  motto: ['传承一部文明', '服务一个未来'],
  /** 分页刻度：三段展线的位置标记（本轮为静态标记，未做轮播）。 */
  scale: ['01', '02', '03'],
  platform: '皇甫谧人文数字平台',
} as const

export const HOME_HUANGFU_DATE = CORE_PERSON_DATES

export const HOME_METRICS: HomeMetric[] = [
  {
    label: '版本记录',
    value: String(INVENTORY_EDITION_RECORDS),
    note: '《针灸甲乙经》历代版本（据客户资料审计）',
  },
  { label: '论著资料', value: String(INVENTORY_LUNZHU_FILES), note: '件（客户资料目录审计）' },
  {
    label: '学术论文',
    value: String(INVENTORY_LUNWEN_FILES),
    note: `篇（客户资料审计；已结构化题录 ${SEARCHABLE_PAPER_TOTAL} 条）`,
  },
  {
    label: 'Reader 全文',
    value: String(READER_DOCUMENTS.length),
    note: '篇（后论 · 其传史料整理）',
  },
]

export const HOME_HUANGFU_IDENTITIES = [...CORE_PERSON_IDENTITIES]

export const HOME_HUANGFU: HomeFeature = {
  heading: CORE_PERSON_NAME,
  lede: CORE_PERSON_DEFINITION,
  items: [
    { title: '其传 · 史料来源整理', meta: '本源史料 / 地方志 / 类书', href: '/reader/qichuan' },
    { title: '其言', meta: '三都赋序 · 玄守论 · 释劝论 · 笃终论', href: '/yan' },
    { title: '后论 · 历史评价', meta: '12 条带出处引文', href: '/reader/houlun' },
  ],
}

export const HOME_JIAYI: {
  heading: string
  lede: string
  editions: HomeEditionPreview[]
  lineage: { src: string; alt: string }
  cta: HomeFeatureLink
} = {
  heading: '《针灸甲乙经》',
  lede: '皇甫谧所撰针灸学专著，中国现存最早的针灸学典籍之一。平台收录历代版本、版本脉络、论著与研究资料。',
  editions: [
    { title: '医统正脉全书本', period: '明万历 29 年（1601）', imprint: '吴勉学刊' },
    { title: '四库全书本', period: '清乾隆' },
    { title: '行素草堂藏板本', period: '清光绪' },
    { title: '黄龙祥整理本', period: '2006 / 2017' },
    { title: '张灿玾、徐国千校注', period: '1996 / 2014' },
  ],
  lineage: { src: JIAYI_LINEAGE_IMAGE_SRC, alt: JIAYI_LINEAGE_IMAGE_ALT },
  cta: { label: '进入数字学术专题', href: '/jiayi' },
}

/** 后论真实引文（带出处；无编造 slogan）。 */
export const HOME_QUOTATION: HomeQuotation = {
  text: '「皇甫谧素履幽贞，闲居养疾，留情笔削，敦悦丘坟，轩冕未足为荣，贫贱不以为耻，确乎不拔，斯固有晋之高人者欤！」',
  attribution: '唐代·房玄龄等',
  source: '《晋书》',
}

export const HOME_LITERATURE: HomeFeature = {
  heading: '文献与史料',
  lede: '平台是文献基础设施：其言、著作、古籍版本、史料整理与研究资料，而非人物展示站。',
  items: [
    { title: '其言', meta: '皇甫谧言论与文字选编', href: '/yan' },
    { title: '《帝王世纪》', meta: '皇甫谧撰 · 版本资料', href: '/archive' },
    { title: '《高士传》', meta: '皇甫谧撰 · 中华书局 1985', href: '/archive' },
    { title: '数字档案', meta: '人物资料 · 版本资料 · 现代研究 · 影像', href: '/archive' },
  ],
}

export const HOME_HERITAGE: HomeFeature = {
  heading: '皇甫谧针灸非遗 · 活态传承',
  lede: `从历史文献到当代传承：${HERITAGE_PERSON.generationTitle}·${HERITAGE_PERSON.name}，皇甫谧针灸市级非遗代表性传承人。谱系中间代结构化整理中（PARTIAL），不虚构。`,
  items: [
    {
      title: HERITAGE_PERSON.generationTitle,
      meta: HERITAGE_PERSON.heritageRole,
      href: '/heritage',
    },
    {
      title: '师承教育拜师大会',
      meta: '2023-09-26 · 甘肃医学院附属医院国医馆',
      href: '/heritage#apprenticeship',
    },
    { title: '央视《陇脉医承》', meta: '2025-04-25', href: '/heritage#media' },
    {
      title: '名中医工作室',
      meta: '崆峒区中医医院 · 灵台县皇甫谧中医院',
      href: '/heritage#studios',
    },
  ],
}

export const HOME_RESEARCH_STEPS = [
  { label: '检索', note: '统一索引检索（人物/作品/版本/档案/论文）', href: '/research/search' },
  { label: '阅读', note: '古籍与长文本专业阅读', href: '/reader/houlun' },
  { label: '来源', note: 'Evidence · 版本上下文', href: '/research/entity/reader/houlun' },
  { label: '引用', note: '确定性引用与复制', href: '/reader/houlun' },
] as const

export const HOME_EDITIONS_TOTAL = JIAYI_ANCIENT_EDITIONS.length + JIAYI_MODERN_EDITIONS.length

/* --------------------------------------------------------------------
 * CF-07 — ADDITIVE presentation projections for the accepted homepage
 * 8-section structure. These SELECT/derive existing authoritative data
 * only: no new domain facts, no fabricated counts, no second domain
 * model. The macro sequence is: 01 Hero → 02 一生 → 03 一部书 → 04
 * 知识对象 → 05 史料证据 → 06 活态传承 → 07 研究导航 → 08 Close.
 * -------------------------------------------------------------------- */

/** Accepted homepage chapter labels (presentation microcopy only). */
export const HOME_CHAPTERS = {
  hero: { no: '01', label: 'Hero' },
  life: { no: '02', label: '一生' },
  book: { no: '03', label: '一部书' },
  knowledge: { no: '04', label: '知识对象' },
  evidence: { no: '05', label: '史料证据' },
  heritage: { no: '06', label: '活态传承' },
  domains: { no: '07', label: '研究导航' },
  closing: { no: '08', label: 'Institutional Close' },
} as const

/** Section 02 — 一生。Life stages derive from the verified life-phase model. */
export const HOME_LIFE = {
  headline: '从带经而农，到著书传世。',
  dates: CORE_PERSON_DATES,
  intro:
    '皇甫谧的一生，见诸《晋书》等本源史料与后世整理的其传。生平四阶段彼此衔接：少家贫、躬自稼穑、带经而农；屡征不仕、专事著述；中年风痹、犹手不释卷、旁通医理；晚年编撰《针灸甲乙经》，垂范后世。',
  stages: CORE_PERSON_LIFE_PHASES,
  /** 人物档案入口（其传 / 其言 / 后论 — 与 HOME_HUANGFU 同源）。 */
  items: HOME_HUANGFU.items,
  cta: { label: '进入人物档案', href: '/persons/ENT-PERSON-HFM-HUANGFUMI' },
} as const

/** Section 03 — 一部书。Book object + edition preview (existing HOME_JIAYI data). */
export const HOME_BOOK = {
  headline: '一部书，成为历史中的物。',
  book: HOME_JIAYI,
  editionsTotal: HOME_EDITIONS_TOTAL,
  lineageCaption: '版本脉络（客户资料）· 结构化版本关系整理中',
  cta: { label: '进入古籍库', href: '/jiayi' },
} as const

/**
 * Section 04 — 知识对象。The six rows mirror the platform's real search
 * facet vocabulary (person/text/work/edition/archive/paper); the register
 * values derive from contentInventory / searchIndex (single source).
 */
/**
 * Section 04 — 知识对象。The six rows mirror the platform's real search
 * facet vocabulary (person/text/work/edition/archive/paper); every count in
 * the S4-B register derives from contentInventory / searchIndex (single source).
 */
const KNOWLEDGE_CATEGORIES = [
  { title: '人物', note: '皇甫谧 · 传承人物 · 人物档案' },
  { title: '文本', note: '古籍全文与长文本 · 专业阅读' },
  { title: '作品', note: '《针灸甲乙经》及相关著作' },
  { title: '版本', note: '历代版本与近现代整理本' },
  { title: '档案', note: '数字档案 · 史料来源整理' },
  { title: '论文', note: '学术论文目录审计' },
] as const

export const HOME_KNOWLEDGE = {
  headline: '从古籍文字，到可探索的知识。',
  lede: '古籍文字经结构化记录成为可检索的知识，并始终可以回到阅读、来源与引用。',
  categories: KNOWLEDGE_CATEGORIES,
  /** CF-08 S4-B evidence register — all values derive from inventory / searchIndex. */
  searchable: SEARCH_INDEX.length,
  categoriesCount: KNOWLEDGE_CATEGORIES.length,
  editions: INVENTORY_EDITION_RECORDS,
  lunzhu: INVENTORY_LUNZHU_FILES,
  lunwen: INVENTORY_LUNWEN_FILES,
  structured: SEARCHABLE_PAPER_TOTAL,
  knowledgeTypes: KNOWLEDGE_CATEGORIES.map((c) => c.title).join(' / '),
  register: [
    {
      label: '可检索记录',
      value: String(SEARCH_INDEX.length),
      note: '统一索引：人物 / 文本 / 作品 / 版本 / 档案 / 论文',
    },
    { label: '论著资料', value: String(INVENTORY_LUNZHU_FILES), note: '件（客户目录审计）' },
    {
      label: '学术论文',
      value: String(INVENTORY_LUNWEN_FILES),
      note: `篇（客户目录审计；已结构化题录 ${SEARCHABLE_PAPER_TOTAL} 条）`,
    },
  ],
  cta: { label: '进入研究工作台', href: '/research/search' },
} as const

/**
 * Section 05 — 史料证据。The quotation is the real 房玄龄等《晋书》
 * witness (HOME_QUOTATION). The source register derives from the real
 * 其传 · 史料来源整理 document sections (reader/qichuan) — never invented.
 */
const QICHUAN = getReaderDocument('qichuan')

export const HOME_EVIDENCE = {
  headline: '每一个结论，都回到它的出处。',
  lede: '平台的判断不替代考证，只呈现考证：结论旁标注依据，争议如实明示。',
  claim: {
    label: '结论',
    text: `生卒年 ${CORE_PERSON_DATES}`,
    note: '客户确认值 · 其传 · 史证来源整理',
  },
  sourceLabel: '《晋书》等本源史料',
  quotation: HOME_QUOTATION,
  dispute: {
    label: '争议',
    text: '建安 / 正始 两说',
    note: '其传考据另载建安 / 正始两说（现代学术考据）；平台以客户确认的生卒年呈现，并明示争议存在。',
  },
  sources: (QICHUAN?.sections ?? []).map((section) => ({
    title: section.heading,
    href: '/reader/qichuan',
  })),
  cta: { label: '阅读《后论》全文', href: '/reader/houlun' },
} as const

/** Section 06 — 活态传承。Living transmission (existing heritage data). */
export const HOME_HERITAGE_LIVING = {
  headline: '一千七百年之后，传承仍在继续。',
  project: '皇甫谧针灸 · 市级非物质文化遗产代表性项目',
  person: HERITAGE_PERSON,
  /** Documentary traces of living transmission (existing HOME_HERITAGE items). */
  traces: HOME_HERITAGE.items,
  lineageNote: '谱系中间代（第二代至第五代）结构化整理中，不虚构。',
  cta: { label: '进入活态传承档案', href: '/heritage' },
} as const

/** Section 07 — 研究导航。Four doors map to existing real routes. */
export const HOME_DOMAINS = {
  headline: '四域探索',
  lede: '人物 · 典籍 · 知识 · 资源 —— 四类内容，四个入口。',
  domains: [
    {
      no: '01',
      key: '生平 · 年表 · 学术 · 思想',
      en: 'PERSONS',
      title: '人物',
      href: '/persons/ENT-PERSON-HFM-HUANGFUMI',
      cta: '走进皇甫谧',
    },
    {
      no: '02',
      key: '《针灸甲乙经》与版本流传',
      en: 'WORKS',
      title: '典籍',
      href: '/jiayi',
      cta: '进入典籍库',
    },
    {
      no: '03',
      key: '构建可探索的知识网络',
      en: 'KNOWLEDGE',
      title: '知识图谱',
      href: '/knowledge',
      cta: '查看知识实体',
    },
    {
      no: '04',
      key: '开放、可持续的数字资源',
      en: 'RESOURCES',
      title: '数字资源',
      href: '/library',
      cta: '进入资源库',
    },
  ],
} as const

/** 03 段 — 皇甫谧与《针灸甲乙经》（参考图 band 3）。 */
export const HOME_CLASSICS = {
  title: '皇甫谧与《针灸甲乙经》',
  en: 'HUANGFU MI AND THE CLASSICS',
  body: '皇甫谧（215—282），西晋著名学者、医学家，以《针灸甲乙经》闻名于世。他博通经史，兼通医学，注重实证与仁心，在医学、哲学、史学与文学等方面均有重要贡献，是中国医学史与思想史上不可忽视的重要人物。',
  cta: { label: '深入了解', href: '/persons/ENT-PERSON-HFM-HUANGFUMI' },
  plateCaption: '明万历吴勉学刻本 · 原刻影印',
  quote: {
    text: '医之道，非独疗疾，亦所以养生、立德、安民。',
    source: '皇甫谧《针灸甲乙经·序》',
  },
} as const

/** 04 段 — 数字人文视角（参考图 band 4）。 */
export const HOME_APPROACH = {
  title: '数字人文视角下的皇甫谧',
  en: 'A DIGITAL HUMANITIES APPROACH',
  body: '我们通过数字化、结构化与可视化的方式，重建皇甫谧的知识世界：连接古籍、人物、概念与历史的多重关系，让传统智慧在当代研究与社会传播中焕发新的生命力。',
  cta: { label: '探索知识图谱', href: '/knowledge' },
} as const

/** 05 段 — 活态传承（参考图 band 5）的编辑文案。 */
export const HOME_LIVING = {
  title: '活态传承 · 连接当下',
  en: 'LIVING HERITAGE',
  lede: '皇甫谧针灸是市级非物质文化遗产代表性项目。传承没有停在书上，它今天仍在医院、课堂与故里发生。',
  quote: '让传统智慧走进当代生活',
  cta: { label: '了解更多', href: '/heritage' },
} as const

/** Section 08 — 结语。Platform closing identity; AppFooter owns the global footer. */
export const HOME_CLOSING = {
  name: HOME_HERO.platform,
  subtitle: HOME_HERO.subtitle,
  quote: '传统不是过去的遗存，而是理解未来的一种方式。',
  quoteEn: 'THE PAST IS A RESOURCE FOR THE FUTURE',
  motto: ['连接古今', '面向未来'],
  cta: { label: '检索全站已发布内容', href: '/search' },
} as const
