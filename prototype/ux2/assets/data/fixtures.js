/* ==========================================================================
   UX2-G2 PROTOTYPE FIXTURES — derived from frozen baseline data
   ==========================================================================
   PROVENANCE: every fixture traces to a committed frozen-baseline source
   (apps/frontend/src/data/* or src/config/* @ ae55abc). No new historical
   facts are created. Fields whose frozen source is absent are marked
   SOURCE_FIELD_UNRESOLVED and collapse (G1-C §5, U-01..U-05).
   ========================================================================== */

window.UX2 = {};

/* ---- P-G2-01 Huangfu Mi Person Archive -------------------------------- */
/* source: src/config/corePerson.ts, src/data/readerDocuments.ts, workCollection.ts */
UX2.PERSON = {
  object: {
    title: '皇甫谧',
    dates: '215—282',
    type: '人物档案',
    identity: ['医学家', '文学家', '史学家', '学者'],
    definition:
      '西晋著名医学家、文学家、史学家，针灸学专著《针灸甲乙经》的编纂者，世称针灸鼻祖。',
  },
  context: [
    { label: '作品', value: '《针灸甲乙经》 · 其言四篇 · 《帝王世纪》 · 《高士传》' },
    { label: '史料整理', value: '其传（史料来源整理） · 后论（历史评价汇编）' },
  ],
  evidence: [
    { type: 'Source', label: '《晋书》房玄龄等（后论引文 12 条）', afford: 'citation available' },
    { type: 'Archive', label: '其传文稿（docx）', afford: 'metadata only' },
    { type: 'Document', label: '后论文稿（docx）', afford: 'citation available' },
  ],
  relations: [
    { label: '作品《针灸甲乙经》', href: 'p02-jiayi.html', sem: 'EXPLICIT_RELATION' },
    { label: '非遗传承（刘君奇）', href: 'p03-heritage.html', sem: 'ASSOCIATED_CONTEXT' },
    { label: '其言四篇', href: 'index.html', sem: 'EXPLICIT_RELATION' },
  ],
  /* optional slots that collapse (demonstrated on the page) */
  optional: {
    holdingInstitution: { state: 'ABSENT_OPTIONAL', note: 'SOURCE_FIELD_UNRESOLVED U-03 — no holding-institution field; slot collapses' },
    portrait: { state: 'ABSENT_OPTIONAL', note: 'no customer-approved portrait derivative; slot collapses (no AI portrait)' },
  },
  /* evidence-bearing incomplete states */
  incomplete: [
    { state: 'INCOMPLETE_WITH_EVIDENCE_STATE', label: '原典全文未收录', note: '四论古典全文未见于客户材料；整理说明已可读', status: 'METADATA_ONLY' },
    { state: 'INCOMPLETE_WITH_EVIDENCE_STATE', label: '生卒年尚有学术争议', note: '其传考据记载建安/正始两说；平台以客户确认值 215—282 为准并明示争议存在', status: 'SCHOLARLY_UNCERTAIN' },
  ],
};

/* ---- P-G2-02 Jiayi Work / Edition ------------------------------------- */
/* source: src/data/jiayiView.ts (19 editions), readerDocuments.ts (2 FULL_TEXT) */
UX2.JIAYI = {
  object: {
    title: '《针灸甲乙经》',
    type: '作品 · 针灸学专著',
    period: '西晋',
    author: '皇甫谧',
  },
  editions: [
    { id: 'yitong', title: '《针灸甲乙经》医统正脉全书本', period: '明万历 29 年（1601）', imprint: '吴勉学刊', kind: 'ancient' },
    { id: 'wuche', title: '《甲乙经》五车楼藏板本', period: '明万历', imprint: '五车楼藏板', kind: 'ancient' },
    { id: 'siku', title: '《针灸甲乙经》四库全书本', period: '清乾隆', imprint: '四库全书', kind: 'ancient' },
    { id: 'xingsu', title: '《甲乙经》行素草堂藏板本', period: '清光绪', imprint: '行素草堂藏板', kind: 'ancient' },
    { id: 'cunxun', title: '《针灸甲乙经》清四明存存轩本', period: '清', imprint: '四明存存轩', kind: 'ancient' },
    { id: 'jiangzuo', title: '《黄帝甲乙经》江左书林印本', period: '1977', imprint: '江左书林印（曹智涵校正）', kind: 'ancient' },
    { id: 'shangwu', title: '《针灸甲乙经》商务印书馆本', period: '1955', imprint: '商务印书馆（宋林亿等校）', kind: 'modern' },
    { id: 'renwei56', title: '《针灸甲乙经》人民卫生出版社本', period: '1956', imprint: '人民卫生出版社', kind: 'modern' },
    { id: 'shandong', title: '《针灸甲乙经校释》', period: '1979', imprint: '山东中医学院', kind: 'modern' },
    { id: 'zhonghua', title: '《针灸甲乙经》中华书局本', period: '1991', imprint: '中华书局', kind: 'modern' },
    { id: 'luzhaolin', title: '《针灸甲乙经》鲁兆麟校本', period: '1994', imprint: '鲁兆麟校', kind: 'modern' },
    { id: 'zhangcanjie', title: '《针灸甲乙经校注》', period: '1996', imprint: '张灿玾、徐国千校注', kind: 'modern' },
    { id: 'hlx2006', title: '《针灸甲乙经》黄龙祥整理本', period: '2006 / 2017', imprint: '人民卫生出版社（黄龙祥整理）', kind: 'modern' },
    { id: 'linzh', title: '《针灸甲乙经一学就通》', period: '2007', imprint: '林政宏（现代解读本）', kind: 'modern' },
    { id: 'huaxia', title: '《针灸甲乙经》黄龙祥校注本', period: '2008', imprint: '华夏出版社', kind: 'modern' },
    { id: 'wangzx', title: '《针灸甲乙经》白话精解', period: '2010', imprint: '王竹星（现代解读本）', kind: 'modern' },
    { id: 'liding', title: '《针灸甲乙经理论与实践》', period: '2011', imprint: '人民卫生出版社（李鼎）', kind: 'modern' },
    { id: 'wxy2012', title: '《黄帝三部针灸甲乙经新校》', period: '2012', imprint: '学苑出版社（王心远）', kind: 'modern' },
    { id: 'sh2017', title: '《黄帝三部针灸甲乙经》', period: '2017', imprint: '上海科学技术出版社', kind: 'modern' },
  ],
  invariants: {
    EDITION_COUNT: 19,
    FULL_TEXT_COUNT: 2,
    JIAYI_DATA_STATE: 'DATA_GAP',
  },
  fullText: ['后论 · 历史评价汇编（12 条可引用引文）', '其传 · 史料来源整理'],
  dataGap: {
    label: '版本关系整理中',
    note: '客户脉络图为展示资产；结构化版本关系未建模（JIAYI_EDITION_RELATIONS = DATA-GAP），不据此推断版本谱系。',
    status: 'DATA_GAP',
  },
  /* U-05: per-edition digitization flag unresolved — every edition renders METADATA_ONLY 存目 */
  editionState: { status: 'METADATA_ONLY', label: '存目' },
};

/* ---- P-G2-03 Heritage Living Archive ---------------------------------- */
/* source: src/data/heritageView.ts */
UX2.HERITAGE = {
  project: {
    title: '皇甫谧针灸非遗',
    classification: '传统医药 · 针灸（市级非物质文化遗产代表性项目）',
    inheritor: '刘君奇',
  },
  person: {
    name: '刘君奇',
    generation: '第六代名医',
    role: '皇甫谧针灸市级非物质文化遗产代表性传承人',
    institution: '皇甫谧针灸学院院长',
  },
  historical: [
    { label: '源头', value: '皇甫谧 · 针灸鼻祖 · 《针灸甲乙经》作者（其传/史料依据）', status: 'AVAILABLE' },
    { label: '中间代', value: '第二代至第五代谱系整理中（不虚构）', status: 'PARTIAL' },
  ],
  contemporary: [
    { label: '师承教育', value: '首届针灸推拿学本科生师承教育拜师大会 · 2023-09-26 · 甘肃医学院附属医院国医馆', status: 'AVAILABLE' },
    { label: '技术成果', value: '皇甫谧《针灸甲乙经》腧穴刺灸学成就及临床应用研究 · 2007 · 市级科技进步二等奖', status: 'AVAILABLE' },
    { label: '媒体报道', value: '央视《中国中医药大会》（第二季）《陇脉医承》· 2025-04-25', status: 'AVAILABLE' },
    { label: '工作室', value: '刘君奇名中医工作室（崆峒区中医医院）· 刘君奇中医工作室（灵台县皇甫谧中医院）', status: 'AVAILABLE' },
  ],
  /* 认定与荣誉 — 8/8 verified HERITAGE_RECOGNITIONS records, condensed into
     4 grouped display strings (secondary metadata, no honor wall):
     r-fy / r-gs-mzy+r-pl-mzy+r-pl-my+r-kt-gj / r-gs-xjj+r-gs-rc / r-yz-2016.
     Every recognition below maps to a verified record in heritageView.ts
     HERITAGE_RECOGNITIONS (8 records, full coverage — G2 F-4). */
  recognition: [
    '皇甫谧针灸市级非物质文化遗产代表性传承人认定',
    '甘肃省名中医 · 平凉市名中医 · 首届平凉名医 · 崆峒工匠',
    '甘肃省先进工作者 · 甘肃高层次专业技术人才津贴',
    '全区优秀院长（2016–2019）',
  ],
};

/* ---- P-G2-04 Scholarly Discovery -------------------------------------- */
/* source: src/data/searchIndex.ts — SEARCH_INDEX type counts (deterministic,
   computed once at module load). FACET SEMANTIC (G2 F-3): every facet count
   is the SEARCH_INDEX type count, i.e. the number of index entries of that
   type — 人物 2 / 作品 8 / 版本 19 / 论文题录 5 / 文本 6 match SEARCH_INDEX
   person/work/edition/paper/text counts. 档案 = archive-type index entries =
   16 (heritage-project 1 + HERITAGE_APPRENTICESHIPS 1 + HERITAGE_STUDIOS 2
   + HERITAGE_MEDIA 4 + ARCHIVE_RECORDS 8). NOT the ARCHIVE_RECORDS.length
   (8) inventory-object count — the two are different semantics and the
   facet reports the search-index semantic. AUDITED 515 / SEARCHABLE 5 from
   searchIndex.ts invariants. */
UX2.DISCOVERY = {
  invariants: { AUDITED: 515, SEARCHABLE: 5 },
  facets: [
    { label: '人物', count: 2 },
    { label: '作品', count: 8 },
    { label: '版本', count: 19 },
    { label: '档案', count: 16 },
    { label: '论文题录', count: 5 },
    { label: '文本', count: 6 },
  ],
  results: [
    {
      kind: 'work',
      title: '《针灸甲乙经》',
      author: '皇甫谧',
      year: '西晋',
      source: '客户提供《针灸甲乙经》资料',
      state: 'AVAILABLE',
      stateLabel: '数字资源可阅',
    },
    {
      kind: 'edition',
      title: '《针灸甲乙经》医统正脉全书本',
      author: '吴勉学刊',
      year: '明万历 29 年（1601）',
      source: '客户提供《针灸甲乙经》论著资料',
      state: 'METADATA_ONLY',
      stateLabel: '存目',
    },
    {
      kind: 'paper',
      title: '《针灸甲乙经》的读法',
      author: '（题录）',
      year: '—',
      source: '客户提供《针灸甲乙经》学术论文资料',
      state: 'METADATA_ONLY',
      stateLabel: '仅题录',
    },
  ],
  note: '审计 515 篇；已结构化题录 5 条。论文不自行重分类。',
};

/* ---- P-G2-05 Homepage Exhibition Narrative ----------------------------- */
/* source: src/data/homeProjection.ts */
UX2.HOME = {
  hero: {
    title: '皇甫谧人文数字平台',
    subtitle: '权威数字人文资料 · 古籍与研究 · 非遗活态传承',
    dates: '皇甫谧 215—282',
    definition: '西晋著名医学家、文学家、史学家，针灸学专著《针灸甲乙经》的编纂者。',
    primary: [
      { label: '探索皇甫谧', href: 'p01-person.html' },
      { label: '进入《针灸甲乙经》', href: 'p02-jiayi.html' },
    ],
    secondary: { label: '检索文献', href: 'p04-discovery.html' },
  },
  narrative: [
    { n: '01', title: '皇甫谧', desc: '人物档案 · 其传 · 其言 · 后论', href: 'p01-person.html' },
    { n: '02', title: '《针灸甲乙经》', desc: '版本脉络 · 19 版本记录 · 版本关系整理中', href: 'p02-jiayi.html' },
    { n: '03', title: '文献与史料', desc: '其言 · 帝王世纪 · 高士传 · 数字档案', href: 'index.html' },
    { n: '04', title: '皇甫谧针灸非遗 · 活态传承', desc: '第六代名医·刘君奇 · 师承教育 · 媒体报道', href: 'p03-heritage.html' },
    { n: '05', title: '数字研究', desc: '检索 → 阅读 → 来源 → 引用', href: 'p04-discovery.html' },
  ],
};

/* ---- Shared: status → public label mapping (G1-C) ---------------------- */
UX2.STATE_LABELS = {
  RESOURCE_READY: '数字资源可阅',
  METADATA_ONLY: '仅题录',
  SCHOLARLY_UNCERTAIN: '尚有争议',
  HISTORICAL_ABSENCE: '文献阙佚',
  UNSTRUCTURED_OR_INCOMPLETE: '资料整理中',
};
