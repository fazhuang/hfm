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
import { SEARCH_INDEX, SEARCHABLE_PAPER_TOTAL } from './searchIndex'
import { READER_DOCUMENTS } from './readerDocuments'
import { HERITAGE_PERSON } from './heritageView'
import {
  JIAYI_ANCIENT_EDITIONS,
  JIAYI_MODERN_EDITIONS,
  JIAYI_LINEAGE_IMAGE_ALT,
  JIAYI_LINEAGE_IMAGE_SRC,
} from './jiayiView'

export const HOME_HERO = {
  title: '皇甫谧人文数字平台',
  subtitle: '权威数字人文资料 · 古籍与研究 · 非遗活态传承',
  personName: CORE_PERSON_NAME,
  personDates: CORE_PERSON_DATES,
  definition: CORE_PERSON_DEFINITION,
  primary: [
    { label: '探索皇甫谧', href: '/persons/person-huangfu-mi' },
    { label: '进入《针灸甲乙经》', href: '/jiayi' },
  ],
  secondary: [{ label: '检索文献', href: '/search' }],
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
 * STEP 3 WP-02 — ADDITIVE presentation projections for the accepted
 * 8-section homepage structure. These SELECT/derive existing
 * authoritative data only; no new domain facts, no fabricated counts.
 * -------------------------------------------------------------------- */

/** Accepted homepage chapter labels (presentation microcopy only). */
export const HOME_CHAPTERS = {
  hero: { no: '01', label: '人物 · 史料在场' },
  life: { no: '02', label: 'A LIFE' },
  book: { no: '03', label: 'THE BOOK' },
  knowledge: { no: '04', label: 'KNOWLEDGE' },
  evidence: { no: '05', label: 'EVIDENCE' },
  heritage: { no: '06', label: 'LIVING HERITAGE' },
  domains: { no: '07', label: 'FOUR WORLDS' },
  closing: { no: '08', label: 'CLOSING' },
} as const

/** Section 02 — 一生。Life stages derive from the verified life-phase model. */
export const HOME_LIFE = {
  headline: '生于乱世，终于著述。',
  dates: CORE_PERSON_DATES,
  stages: CORE_PERSON_LIFE_PHASES,
  intro:
    '皇甫谧的一生，录于后世整理的其传史料与《晋书》等本源记载。四个阶段彼此衔接——少时带经而农，壮岁屡征不仕，中年抱病研医，晚年著书传世——从一位农家子弟，走向针灸鼻祖。',
  cta: { label: '进入人物档案', href: '/persons/person-huangfu-mi' },
} as const

/** Section 03 — 一部书。Book object + edition/lineage preview (existing data). */
export const HOME_BOOK = {
  headline: '一部书，成为历史中的物。',
  book: HOME_JIAYI,
  cta: { label: '进入古籍库', href: '/jiayi' },
} as const

/** Section 04 — 一套知识。Knowledge layer numbers derive from inventory/search. */
export const HOME_KNOWLEDGE = {
  headline: '从古籍文字，到可探索的知识。',
  searchable: SEARCH_INDEX.length,
  categories: 6,
  editions: INVENTORY_EDITION_RECORDS,
  lunzhu: INVENTORY_LUNZHU_FILES,
  lunwen: INVENTORY_LUNWEN_FILES,
  structured: SEARCHABLE_PAPER_TOTAL,
  structure: [
    { title: '篇章', role: '章目层级', note: '全书结构 · 文本与版本承载' },
    { title: '腧穴', role: '针灸之体', note: '取穴知识 · 穴名与定位条目' },
    { title: '经脉', role: '经络之网', note: '经络体系 · 气血循行的联系' },
    { title: '病候', role: '病症之用', note: '病症与治则 · 临床的对应' },
    { title: '史料依据', role: '出处之锚', note: '回到出处 · 证据回溯（见下节）' },
  ],
  cta: { label: '进入研究工作台', href: '/research/search' },
} as const

/** Section 05 — 史料证据。Authoritative quotation + source register. */
export const HOME_EVIDENCE = {
  headline: '每一个结论，都回到它的出处。',
  quotation: HOME_QUOTATION,
  sources: [
    { title: '本源史料', note: '《晋书》等正史记载本传' },
    { title: '地方志', note: '历代州县志所录乡贤事迹' },
    { title: '类书', note: '类书所辑逸文与事迹' },
    { title: '现代考据', note: '当代学者对生卒与史实的考证' },
    { title: '谱系', note: '世系与传承关系的整理' },
    { title: '图像遗存', note: '画像、碑刻等视觉史料' },
  ],
  claim: { number: '215—282', note: '客户确认值 · 其传 · 史证来源整理' },
  dispute: '建安 / 正始 两说',
  cta: { label: '阅读《后论》全文', href: '/reader/houlun' },
} as const

/** Section 06 — 活态传承。Living transmission (existing heritage data). */
export const HOME_HERITAGE_LIVING = {
  headline: '一千七百年之后，传承仍在继续。',
  person: HERITAGE_PERSON,
  project: '皇甫谧针灸 · 市级非物质文化遗产代表性项目',
  cta: { label: '进入活态传承档案', href: '/heritage' },
  lineageNote: '谱系中间代结构化整理中（PARTIAL），不虚构。',
} as const

/** Section 07 — 四域探索。Four domains map to existing routes/data. */
export const HOME_DOMAINS = {
  headline: '四域探索',
  lede: '人物 · 文献 · 医学 · 传承 —— 四类知识，四个入口。',
  domains: [
    {
      no: '01',
      key: '人物档案',
      label: 'THE PERSON',
      title: '皇甫谧',
      href: '/persons/person-huangfu-mi',
      cta: '进入人物档案',
    },
    {
      no: '02',
      key: '文献史料',
      label: 'TEXTS & ARCHIVE',
      title: '文献史料',
      href: '/archive',
      cta: '进入文献库',
    },
    {
      no: '03',
      key: '医学知识',
      label: 'THE BOOK',
      title: '《针灸甲乙经》',
      href: '/jiayi',
      cta: '进入古籍库',
    },
    {
      no: '04',
      key: '活态传承',
      label: 'LIVING HERITAGE',
      title: '活态传承',
      href: '/heritage',
      cta: '进入传承档案',
    },
  ],
} as const

/** Section 08 — 结语。Platform closing identity (AppFooter owns global footer). */
export const HOME_CLOSING = {
  name: HOME_HERO.title,
  subtitle: HOME_HERO.subtitle,
} as const
