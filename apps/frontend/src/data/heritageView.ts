/**
 * Heritage view data (UI-09) — 非遗活态传承数字档案.
 *
 * Every record is built from the audited customer register (zzcl/), with
 * public-facing source names only. Sensitive fields (phone numbers, ID
 * numbers, signatures, non-essential personal data) are excluded from
 * public derivatives. Lineage contains ONLY confirmed nodes: 皇甫谧 (源头)
 * and 刘君奇 (第六代名医); intermediate generations stay PARTIAL with an
 * explicit note — nothing is fabricated.
 */
import type {
  AcademicAchievementRecord,
  ApprenticeshipEvent,
  ConfirmedLineageNode,
  HeritagePersonProfile,
  HeritageProject,
  MediaCoverage,
  RecognitionRecord,
  StudioRecord,
  TechnicalAchievementRecord,
} from '../types/heritage'

/** 公共来源名（不暴露内部路径）。 */
const S = {
  recognition: '客户提供：非遗传承人资质与荣誉证书资料',
  research: '客户提供：刘君奇科研列表',
  news: '客户提供：师承教育拜师大会材料',
  media: '客户提供：媒体报道证明材料',
  studio: '客户提供：名中医工作室相关证明材料',
}

export const HERITAGE_PROJECT: HeritageProject = {
  name: '皇甫谧针灸',
  classification: '传统医药 · 针灸（市级非物质文化遗产代表性项目）',
  recognitionLevel:
    '皇甫谧针灸市级非物质文化遗产代表性传承人认定（皇甫谧针灸市级非遗代表性传承人）',
  description:
    '皇甫谧针灸以皇甫谧与《针灸甲乙经》为学术源头，是甘肃地域特色针灸文化传承项目。平台收录其传承人认定、荣誉、学术与技术成果、师承教育、工作室与媒体报道等活态传承档案。',
  inheritors: ['刘君奇（第六代名医）'],
  activities: ['师承教育拜师大会（2023-09-26）', '名中医工作室传承带教'],
  sourceName: S.recognition,
}

export const HERITAGE_PERSON: HeritagePersonProfile = {
  name: '刘君奇',
  generationTitle: '第六代名医',
  heritageRole: '皇甫谧针灸市级非物质文化遗产代表性传承人',
  professionalTitle: '甘肃省名中医 · 平凉市名中医 · 崆峒工匠',
  institutionRole: '皇甫谧针灸学院院长',
  biography:
    '刘君奇，皇甫谧针灸市级非物质文化遗产代表性传承人，第六代名医。长期从事皇甫谧针灸学术研究与传承，主持皇甫谧《针灸甲乙经》腧穴研究等项目，并推动皇甫谧针灸学院师承教育。',
  academicRoles: [
    '甘肃省高等学校医学类专业教学指导、认证与教材建设委员会委员',
    '甘肃省针灸学会副会长',
    '平凉市针灸学会会长',
    '中国针灸学会非物质文化遗产工作委员会委员（2023）',
    '全国综合及医科大学针灸推拿学联盟副理事长（2025）',
    '全国针灸推拿学行业产教融合共同体副理事长',
  ],
  sourceName: S.recognition,
}

export const HERITAGE_RECOGNITIONS: RecognitionRecord[] = [
  {
    id: 'r-fy',
    title: '皇甫谧针灸市级非物质文化遗产代表性传承人认定',
    category: '非遗认定',
    issuer: '（市级非遗认定）',
    date: '—',
    description: '皇甫谧针灸市级非物质文化遗产代表性传承人认定文件。',
    sourceName: S.recognition,
  },
  {
    id: 'r-gs-mzy',
    title: '甘肃省名中医',
    category: '职业荣誉',
    issuer: '甘肃省',
    date: '—',
    description: '甘肃省名中医称号。',
    sourceName: S.recognition,
  },
  {
    id: 'r-pl-mzy',
    title: '平凉市名中医',
    category: '职业荣誉',
    issuer: '平凉市',
    date: '—',
    description: '平凉市名中医称号。',
    sourceName: S.recognition,
  },
  {
    id: 'r-pl-my',
    title: '首届平凉名医',
    category: '职业荣誉',
    issuer: '平凉市',
    date: '—',
    description: '首届平凉名医称号。',
    sourceName: S.recognition,
  },
  {
    id: 'r-gs-xjj',
    title: '甘肃省先进工作者',
    category: '社会荣誉',
    issuer: '甘肃省',
    date: '—',
    description: '甘肃省先进工作者称号。',
    sourceName: S.recognition,
  },
  {
    id: 'r-kt-gj',
    title: '崆峒工匠',
    category: '社会荣誉',
    issuer: '崆峒区',
    date: '—',
    description: '崆峒工匠认定。',
    sourceName: S.recognition,
  },
  {
    id: 'r-gs-rc',
    title: '甘肃高层次专业技术人才津贴',
    category: '社会荣誉',
    issuer: '甘肃省',
    date: '—',
    description: '甘肃高层次专业技术人才津贴人员。',
    sourceName: S.recognition,
  },
  {
    id: 'r-yz-2016',
    title: '全区优秀院长（2016–2019）',
    category: '职业荣誉',
    issuer: '—',
    date: '2016—2019',
    description: '2016、2017、2018、2019 年度全区优秀院长荣誉。',
    sourceName: S.recognition,
  },
]

export const HERITAGE_ACADEMIC: AcademicAchievementRecord[] = [
  {
    id: 'a-project-2023',
    title: '甘肃特色地域文化传承创新研究——以皇甫谧文化传承创新路径研究为例',
    year: '2023',
    type: '研究项目',
    description: '市、厅级中医药课题（2023 年结项）。',
    sourceName: S.recognition,
  },
  {
    id: 'a-paper-zhitong',
    title: '皇甫谧滞通针法临床应用',
    year: '—',
    type: '论文',
    description: '刘君奇发表论文（客户资料收录）。',
    sourceName: S.research,
  },
  {
    id: 'a-paper-osteo',
    title: '中药外敷联合针刺治疗膝关节骨性关节炎的临床疗效及对关节疼痛的影响',
    year: '—',
    type: '论文',
    description: '刘君奇发表论文（客户资料收录）。',
    sourceName: S.research,
  },
]

export const HERITAGE_TECHNICAL: TechnicalAchievementRecord[] = [
  {
    id: 't-2007',
    title: '皇甫谧《针灸甲乙经》腧穴刺灸学成就及临床应用研究',
    year: '2007',
    award: '市级科技进步二等奖',
    issuer: '市级',
    description: '主持完成（客户科研列表）。档案记录该成果的获奖事实，不延伸医疗评价。',
    sourceName: S.research,
  },
  {
    id: 't-2001',
    title: '小针刀疗法临床应用',
    year: '2001',
    award: '市级科技进步二等奖',
    issuer: '市级',
    description: '主持完成（客户科研列表）。',
    sourceName: S.research,
  },
  {
    id: 't-2004',
    title: '肾衰1号保留灌肠与黄芪丹参联合治疗慢性肾功能衰竭临床研究',
    year: '2004',
    award: '市级科技进步二等奖',
    issuer: '市级',
    description: '主持完成（客户科研列表）。',
    sourceName: S.research,
  },
  {
    id: 't-2012',
    title: '综合康复疗法治疗痉挛性小儿脑瘫的临床研究',
    year: '2012',
    award: '市级科技进步二等奖',
    issuer: '市级',
    description: '主持完成（客户科研列表）。',
    sourceName: S.research,
  },
]

export const HERITAGE_APPRENTICESHIPS: ApprenticeshipEvent[] = [
  {
    id: 'ap-2023',
    title: '首届针灸推拿学本科生师承教育拜师大会',
    date: '2023-09-26',
    location: '甘肃医学院附属医院国医馆',
    description:
      '皇甫谧针灸学院、中医药系举办首届针灸推拿学本科生师承教育拜师大会，承担师承教育的 8 名老师与首届针灸推拿学本科专业 51 名学生参加。会上解读 2023 版针灸推拿学本科人才培养方案，师生签署师带徒协议书并举行宣誓。刘君奇院长就师承教育教学全过程提出要求。',
    sourceName: S.news,
  },
]

export const HERITAGE_STUDIOS: StudioRecord[] = [
  {
    id: 'st-kongtong',
    name: '刘君奇名中医工作室',
    institution: '崆峒区中医医院',
    description: '名中医工作室成立及运行相关证明材料（客户资料）。',
    sourceName: S.studio,
  },
  {
    id: 'st-lingtai',
    name: '刘君奇中医工作室',
    institution: '灵台县皇甫谧中医院',
    description: '中医工作室相关证明材料（客户资料）。',
    sourceName: S.studio,
  },
]

export const HERITAGE_MEDIA: MediaCoverage[] = [
  {
    id: 'm-cctv-2025',
    title: '中央电视台《中国中医药大会》（第二季）《陇脉医承》栏目播出',
    mediaOutlet: '中央电视台',
    date: '2025-04-25',
    description:
      '2025 年 4 月 25 日《中国中医药大会》（第二季）《陇脉医承》栏目播出，客户资料含播出截图与拍摄函证明。档案记录媒体报道事实，不作国家级权威背书的价值判断。',
    sourceName: S.media,
  },
  {
    id: 'm-xhfl',
    title: '协助中央广播电视总台华语环球节目中心纪录片部拍摄《杏林繁华》',
    mediaOutlet: '中央广播电视总台',
    date: '—',
    description: '拍摄工作方案（客户资料）。',
    sourceName: S.media,
  },
  {
    id: 'm-mlc',
    title: '央视《魅力中国城》栏目参与',
    mediaOutlet: '中央电视台',
    date: '—',
    description: '参与证明材料（客户资料）。',
    sourceName: S.media,
  },
  {
    id: 'm-gansu',
    title: '甘肃卫视等栏目宣传报道',
    mediaOutlet: '甘肃卫视等',
    date: '—',
    description: '栏目宣传报道截图或链接（客户资料）。',
    sourceName: S.media,
  },
]

/**
 * 谱系 — 仅已确认节点：
 * 皇甫谧（源头）→（第二代至第五代 · 整理中）→ 刘君奇（第六代名医）。
 * LINEAGE_STRUCTURING: PARTIAL —— 不虚构中间代人物或师承边。
 */
export const HERITAGE_LINEAGE: ConfirmedLineageNode[] = [
  {
    id: 'n-hfm',
    person: '皇甫谧',
    generation: '源头',
    role: '针灸鼻祖 · 《针灸甲乙经》作者',
    evidence: '平台人物档案（其传/史料依据）',
    href: '/persons/person-huangfu-mi',
  },
  {
    id: 'n-gap',
    person: '（第二代至第五代）',
    role: '谱系整理中',
    evidence: 'LINEAGE_STRUCTURING: PARTIAL —— 中间代谱系尚未结构化，不虚构',
  },
  {
    id: 'n-liujunqi',
    person: '刘君奇',
    generation: '第六代',
    role: '皇甫谧针灸市级非物质文化遗产代表性传承人',
    evidence: '市级非遗代表性传承人认定文件 · 客户正式确认',
    href: '/heritage#profile',
  },
]

/** 重要时间节点（chronology，非 lineage）——按时间先后排列。 */
export const HERITAGE_TIMELINE = [
  { id: 't-2001', date: '2001', title: '主持《小针刀疗法临床应用》获市级科技进步二等奖' },
  { id: 't-2004', date: '2004', title: '主持慢性肾功能衰竭相关研究获市级科技进步二等奖' },
  {
    id: 't-2007',
    date: '2007',
    title: '主持皇甫谧《针灸甲乙经》腧穴刺灸学成就及临床应用研究获市级科技进步二等奖',
  },
  { id: 't-2012', date: '2012', title: '主持综合康复疗法相关研究获市级科技进步二等奖' },
  { id: 't-2016', date: '2016', title: '全区优秀院长（2016–2019）' },
  { id: 't-2023b', date: '2023', title: '皇甫谧文化传承创新研究课题结项' },
  { id: 't-2023', date: '2023-09-26', title: '首届针灸推拿学本科生师承教育拜师大会' },
  { id: 't-2025', date: '2025-04-25', title: '央视《中国中医药大会》（第二季）《陇脉医承》播出' },
] as const
