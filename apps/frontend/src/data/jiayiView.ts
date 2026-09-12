/**
 * Jiayi Jing — typed static view model (UI-08).
 *
 * Every record is derived from the audited customer material register
 * (hfmzl/针灸甲乙经/论著/…, 论文/…, 版本及各版本之间脉络联系/…), which is
 * customer-provided and publication-authorized. No invented publisher, year,
 * collection, or genealogical edge. Chronology (year-sorted timeline) is
 * explicitly NOT lineage (no implied derivation edges).
 */
import type { EditionRecord, ModernScholarRecord, PaperRecord, RelatedWork } from '../types/jiayi'

/** Customer register source paths (audit reference — INTERNAL provenance, never rendered). */
export const JIAYI_SOURCE_REGISTER = {
  lineagePng: 'hfmzl/针灸甲乙经/版本及各版本之间脉络联系/39b5fde4…png',
  lunzhu: 'hfmzl/针灸甲乙经/论著/',
  lunwen: 'hfmzl/针灸甲乙经/论文/',
} as const

/** Public-facing source labels (UI-12: internal provenance → public projection). */
export const JIAYI_PUBLIC_SOURCES = {
  lineage: '客户提供《针灸甲乙经》版本脉络图资料',
  lunzhu: '客户提供《针灸甲乙经》论著资料',
  lunwen: '客户提供《针灸甲乙经》学术论文资料',
  all: '客户提供《针灸甲乙经》资料（目录审计）',
} as const

/** Web derivative of the customer lineage PNG (source asset untouched). */
export const JIAYI_LINEAGE_IMAGE_SRC = '/assets/jiayi/edition-lineage.png'
export const JIAYI_LINEAGE_IMAGE_ALT =
  '《针灸甲乙经》版本及各版本之间脉络联系图（客户提供资料）；图中关系为资料示意，结构化版本关系尚未建模（DATA-GAP）'

/** Audited counts from the customer register (not hardcoded business logic). */
export const JIAYI_LUNZHU_FILE_COUNT = 92
export const JIAYI_LUNWEN_FILE_COUNT = 515

/**
 * 古代版本 — all fields from directory/file names in the register.
 * year only when the material states it; otherwise period text only.
 */
export const JIAYI_ANCIENT_EDITIONS: EditionRecord[] = [
  {
    id: 'yitong-zhengmai-1601',
    title: '《针灸甲乙经》医统正脉全书本',
    period: '明万历 29 年（1601）',
    imprint: '吴勉学刊',
    editionType: 'ancient',
    description: '医统正脉全书所收本（5 册）。',
    source: `${JIAYI_SOURCE_REGISTER.lunzhu}《针灸甲乙经》医统正脉全书明万历29年吴勉学（1601）`,
    status: 'METADATA_ONLY',
    year: 1601,
  },
  {
    id: 'wuche-lou',
    title: '《甲乙经》五车楼藏板本',
    period: '明万历',
    imprint: '五车楼藏板（吴勉学）',
    editionType: 'ancient',
    description: '五车楼藏板明刻（4 册）。',
    source: `${JIAYI_SOURCE_REGISTER.lunzhu}《甲乙经》五车楼藏板（明万历吴勉学）`,
    status: 'METADATA_ONLY',
  },
  {
    id: 'siku-quanshu',
    title: '《针灸甲乙经》四库全书本',
    period: '清乾隆',
    imprint: '《四库全书》',
    editionType: 'ancient',
    description: '四库全书所收本（卷一至卷十二）。',
    source: `${JIAYI_SOURCE_REGISTER.lunzhu}《针灸甲乙经》四库全书本清乾隆`,
    status: 'METADATA_ONLY',
  },
  {
    id: 'xingsu-caotang',
    title: '《甲乙经》行素草堂藏板本',
    period: '清光绪',
    imprint: '行素草堂藏板',
    editionType: 'ancient',
    description: '行素草堂藏板清光绪本（卷一二至卷八—十二）。',
    source: `${JIAYI_SOURCE_REGISTER.lunzhu}《甲乙经》行素草堂藏板清光绪`,
    status: 'METADATA_ONLY',
  },
  {
    id: 'cunxun-xuan',
    title: '《针灸甲乙经》清四明存存轩本',
    period: '清',
    imprint: '四明存存轩',
    editionType: 'ancient',
    description: '清四明存存轩刻本。',
    source: `${JIAYI_SOURCE_REGISTER.lunzhu}《针灸甲乙经》清四明存存轩本`,
    status: 'METADATA_ONLY',
  },
  {
    id: 'jiangzuo-shulin-1977',
    title: '《黄帝甲乙经》江左书林印本',
    period: '1977',
    imprint: '江左书林印（曹智涵校正）',
    editionType: 'ancient',
    description: '江左书林 1977 年印本，曹智涵校正（4 册）。',
    source: `${JIAYI_SOURCE_REGISTER.lunzhu}皇帝甲乙经/《黄帝甲乙经》江左书林印1977曹智涵校正`,
    status: 'METADATA_ONLY',
    year: 1977,
  },
]

/** 近现代整理/校注版本 — collators and years from the material names. */
export const JIAYI_MODERN_EDITIONS: EditionRecord[] = [
  {
    id: 'shangwu-1955',
    title: '《针灸甲乙经》商务印书馆本',
    period: '1955',
    imprint: '商务印书馆（宋林亿等校）',
    editionType: 'modern',
    description: '商务印书馆 1955 年排印本。',
    source: `${JIAYI_SOURCE_REGISTER.lunzhu}针灸甲乙经校注/《针灸甲乙经》商务印书馆宋林亿等校1955`,
    status: 'METADATA_ONLY',
    year: 1955,
  },
  {
    id: 'renwei-1956',
    title: '《针灸甲乙经》人民卫生出版社本',
    period: '1956',
    imprint: '人民卫生出版社',
    editionType: 'modern',
    description: '人民卫生出版社 1956 年排印本。',
    source: `${JIAYI_SOURCE_REGISTER.lunzhu}针灸甲乙经校注/人民卫生出版社/《针灸甲乙经》人卫出版社1956`,
    status: 'METADATA_ONLY',
    year: 1956,
  },
  {
    id: 'shandong-1979',
    title: '《针灸甲乙经校释》',
    period: '1979',
    imprint: '山东中医学院',
    editionType: 'modern',
    description: '山东中医学院校释本（1979；2009 第 2 版）。',
    source: `${JIAYI_SOURCE_REGISTER.lunzhu}针灸甲乙经校注/山东中医学院/`,
    status: 'METADATA_ONLY',
    year: 1979,
  },
  {
    id: 'zhonghua-1991',
    title: '《针灸甲乙经》中华书局本',
    period: '1991',
    imprint: '中华书局',
    editionType: 'modern',
    description: '中华书局 1991 年点校本。',
    source: `${JIAYI_SOURCE_REGISTER.lunzhu}针灸甲乙经校注/中华书局/`,
    status: 'METADATA_ONLY',
    year: 1991,
  },
  {
    id: 'luzhaolin-1994',
    title: '《针灸甲乙经》鲁兆麟校本',
    period: '1994',
    imprint: '鲁兆麟校',
    editionType: 'modern',
    description: '鲁兆麟 1994 年校勘本。',
    source: `${JIAYI_SOURCE_REGISTER.lunzhu}针灸甲乙经校注/《针灸甲乙经》鲁兆麟校1994`,
    status: 'METADATA_ONLY',
    year: 1994,
  },
  {
    id: 'zhangcanjie-1996',
    title: '《针灸甲乙经校注》',
    period: '1996',
    imprint: '张灿玾、徐国千校注',
    editionType: 'modern',
    description: '张灿玾、徐国千 1996 年校注（2014 再版）。',
    source: `${JIAYI_SOURCE_REGISTER.lunzhu}针灸甲乙经校注/张灿岬/`,
    status: 'METADATA_ONLY',
    year: 1996,
  },
  {
    id: 'huanglongxiang-2006',
    title: '《针灸甲乙经》黄龙祥整理本',
    period: '2006 / 2017',
    imprint: '人民卫生出版社（黄龙祥整理）',
    editionType: 'modern',
    description: '黄龙祥整理本（人卫 2006、2017 两版）。',
    source: `${JIAYI_SOURCE_REGISTER.lunzhu}针灸甲乙经校注/人民卫生出版社/`,
    status: 'METADATA_ONLY',
    year: 2006,
  },
  {
    id: 'linzhenghong-2007',
    title: '《针灸甲乙经一学就通》',
    period: '2007',
    imprint: '林政宏（现代解读本）',
    editionType: 'modern',
    description: '现代解读本（现代版）。',
    source: `${JIAYI_SOURCE_REGISTER.lunzhu}针灸甲乙经现代版/《针灸甲乙经一学就通》林政宏2007`,
    status: 'METADATA_ONLY',
    year: 2007,
  },
  {
    id: 'huaxia-2008',
    title: '《针灸甲乙经》黄龙祥校注本',
    period: '2008',
    imprint: '华夏出版社（黄龙祥校注）',
    editionType: 'modern',
    description: '华夏出版社 2008 年黄龙祥校注本。',
    source: `${JIAYI_SOURCE_REGISTER.lunzhu}针灸甲乙经校注/《针灸甲乙经》华夏出版社2008黄龙祥校注`,
    status: 'METADATA_ONLY',
    year: 2008,
  },
  {
    id: 'wangzhuxing-2010',
    title: '《针灸甲乙经》白话精解',
    period: '2010',
    imprint: '王竹星（现代解读本）',
    editionType: 'modern',
    description: '白话精解（现代版）。',
    source: `${JIAYI_SOURCE_REGISTER.lunzhu}针灸甲乙经现代版/《针灸甲乙经》白话精解王竹星2010`,
    status: 'METADATA_ONLY',
    year: 2010,
  },
  {
    id: 'liding-2011',
    title: '《针灸甲乙经理论与实践》',
    period: '2011',
    imprint: '人民卫生出版社（李鼎）',
    editionType: 'modern',
    description: '理论与实践研究专著（2011；另有中国中医药出版社 2017 高树中本）。',
    source: `${JIAYI_SOURCE_REGISTER.lunzhu}《针灸甲乙经理论与实践》人民卫生出版社李鼎2011`,
    status: 'METADATA_ONLY',
    year: 2011,
  },
  {
    id: 'wangxinyuan-2012',
    title: '《黄帝三部针灸甲乙经新校》',
    period: '2012',
    imprint: '学苑出版社（王心远）',
    editionType: 'modern',
    description: '王心远 2012 年新校本。',
    source: `${JIAYI_SOURCE_REGISTER.lunzhu}皇帝甲乙经/《黄帝三部针灸甲乙经新校》学苑出版社王心远2012`,
    status: 'METADATA_ONLY',
    year: 2012,
  },
  {
    id: 'shanghai-2017',
    title: '《黄帝三部针灸甲乙经》',
    period: '2017',
    imprint: '上海科学技术出版社',
    editionType: 'modern',
    description: '上海科学技术出版社 2017 年版（三册）。',
    source: `${JIAYI_SOURCE_REGISTER.lunzhu}皇帝甲乙经/《黄帝三部针灸甲乙经》上海科学技术出版社2017`,
    status: 'METADATA_ONLY',
    year: 2017,
  },
]

/** 现代整理与研究 — collators/editors only as named in the material. */
export const JIAYI_MODERN_SCHOLARS: ModernScholarRecord[] = [
  {
    id: 'ms-hlx',
    title: '《黄帝针灸甲乙经新校本》（1990）、《针灸甲乙经》整理本（2006/2017）',
    collator: '黄龙祥',
    year: 1990,
    kind: 'collation',
    source: `${JIAYI_SOURCE_REGISTER.lunzhu}皇帝甲乙经/《黄帝针灸甲乙经新校本》黄龙祥1990`,
  },
  {
    id: 'ms-zcj',
    title: '《针灸甲乙经校注》',
    collator: '张灿玾、徐国千',
    year: 1996,
    kind: 'collation',
    source: `${JIAYI_SOURCE_REGISTER.lunzhu}针灸甲乙经校注/张灿岬/`,
  },
  {
    id: 'ms-sd',
    title: '《针灸甲乙经校释》',
    collator: '山东中医学院',
    year: 1979,
    kind: 'collation',
    source: `${JIAYI_SOURCE_REGISTER.lunzhu}针灸甲乙经校注/山东中医学院/`,
  },
  {
    id: 'ms-wxy',
    title: '《黄帝三部针灸甲乙经新校》',
    collator: '王心远',
    year: 2012,
    kind: 'collation',
    source: `${JIAYI_SOURCE_REGISTER.lunzhu}皇帝甲乙经/《黄帝三部针灸甲乙经新校》学苑出版社王心远2012`,
  },
  {
    id: 'ms-gsz',
    title: '《针灸甲乙经理论与实践》',
    collator: '高树中',
    year: 2017,
    kind: 'research',
    source: `${JIAYI_SOURCE_REGISTER.lunzhu}《针灸甲乙经理论与实践》中国中医药出版社2017高树中`,
  },
]

/** 相关论著 / 相关文献（WORK 级入口）。 */
export const JIAYI_RELATED_WORKS: RelatedWork[] = [
  {
    id: 'dwsj',
    title: '《帝王世纪》',
    kind: 'related-material',
    note: '皇甫谧撰 · 版本资料见数字档案',
    href: '/archive',
  },
  {
    id: 'gsc',
    title: '《高士传》',
    kind: 'related-material',
    note: '皇甫谧撰 · 中华书局 1985',
    href: '/archive',
  },
  { id: 'lunzhu', title: '论著 / 研究', kind: 'work', note: '作品目录 · 研究资料', href: '/works' },
  {
    id: 'qiyan',
    title: '其言（三都赋 · 玄守论 · 释劝论 · 笃终论）',
    kind: 'work',
    note: '皇甫谧著述',
    href: '/yan',
  },
  {
    id: 'hfm',
    title: '皇甫谧人物档案',
    kind: 'work',
    note: '生平 · 身份 · 史料依据',
    href: '/persons/person-huangfu-mi',
  },
  {
    id: 'heritage',
    title: '皇甫谧针灸非遗传承',
    kind: 'work',
    note: '传承人物 · 证书 · 师承教育',
    href: '/heritage',
  },
]

/** 论文 preview — real titles from the customer paper register (515 files audited). */
export const JIAYI_PAPER_PREVIEW: PaperRecord[] = [
  { id: 'p1', title: '《针灸甲乙经》的读法' },
  { id: 'p2', title: '皇甫谧与《针灸甲乙经》' },
  { id: 'p3', title: '世界最早的针灸专著《针灸甲乙经》' },
  { id: 'p4', title: '《黄帝三部针灸甲乙经》题名解' },
  { id: 'p5', title: '《针灸甲乙经》研究现状的分析' },
]
