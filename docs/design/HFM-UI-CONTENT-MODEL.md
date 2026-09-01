# HFM UI 内容模型 — UI Content Model（CONTENT → ENTITY → RELATION → EVIDENCE → PRESENTATION）

Status: DESIGN INPUT（UI-00 Design Baseline Closure v2 · 客户真实内容驱动 · 不实施运行时代码）
Date: 2026-09-01 · 配套: HFM-CONTENT-ASSET-MAP / HFM-ASSET-PRESENTATION-POLICY / HFM-UI-PRIMITIVES
正式前提（本模型的事实基础）:

- 刘君奇 = 第六代名医（客户正式确认，`HERITAGE_GENERATION` CLOSED）
- 客户提供材料统一授权公开（`CUSTOMER_PROVIDED = TRUE` → `PUBLICATION_AUTHORIZATION = GRANTED`）
- 版权不作为开发约束；隐私/安全/敏感个人信息仍为独立治理问题

---

## 0. 设计主链

```text
CONTENT（客户真实材料）
   ↓ 内容准入 / 结构化（后续实施 WP，不在本轮）
ENTITY（内容实体：人物/作品/版本/传承人/档案/媒体）
   ↓
RELATION（实体关系：师承/著作/版本脉络/证据绑定）
   ↓
EVIDENCE（证据：来源/版本/Citation 可见，P8）
   ↓
PRESENTATION（UI：三个旗舰页 + 内容面 + primitives）
```

**原则**：UI 围绕真实内容建立展示系统；不再以"有没有内容"作假设；不存在的内容不伪造 UI 能力（如无全文则显示题录、无视频则不伪造播放器）。

---

## 1. 客户内容资产 → 实体 → 展示映射（主链 A–R）

| 客户资产（§2 指令清单） | 内容实体 | 关系 | 证据 | 展示面 |
| --- | --- | --- | --- | --- |
| A 皇甫谧人物资料 / B 其传 / C 其言 / D 后论 | Person（皇甫谧）+ Work（其言四篇） | 人物-著作、人物-生平事件 | Source/Evidence/Citation | FLAGSHIP-01 人物页 |
| E 电影/影像 | MediaRecord（MediaAsset） | 人物-影像 | Source | 人物页影像区 + 媒体面 |
| F 甲乙经版本资料 / G 版本脉络图 | Work（针灸甲乙经）+ EditionFamily/Edition | 版本脉络（JIAYI_EDITION_RELATIONS [DATA-GAP]） | Source/Evidence | FLAGSHIP-02 甲乙经页 |
| H 论著 ≈100 件 | Work / Edition / BibliographicRecord | 作品-版本、作品-研究 | Source | 论著区（UI-06） |
| I 论文 ≈515 篇 | PaperResult（题录） | 关联作品/人物 | Source（题录） | 论文检索（UI-10） |
| J 非遗传承人物资料 / K 刘君奇档案 | HeritagePersonProfile（Person+Heritage 关联） | 传承关系（师承/传承） | Evidence 绑定 | FLAGSHIP-03 传承页 |
| L 非遗认定材料 / M 荣誉证书 | RecognitionRecord | 人物-认定/荣誉 | Evidence | 证书区（CertificateGallery） |
| N 学术成果 / O 技术成果 | AchievementRecord | 人物-成果 | Evidence | 传承页成果区 |
| P 师承教育资料 | ApprenticeshipEvent | 人物-活动 | Evidence | 传承页师承区 |
| Q 名中医工作室资料 | StudioRecord | 人物-机构 | Evidence | 传承页工作室区 |
| R 媒体报道 | MediaCoverage | 人物-媒体 | Source | 传承页媒体区 |

---

## 2. FLAGSHIP-01 — 皇甫谧人物档案内容模型（Digital Scholarly Biography）

展示模型（UI 层，字段候选；后端字段映射见 §7）：

```text
PersonHero        name=皇甫谧 · dates=215—282 · pinyin · courtesy_name · pseudonym
权威人物定义      一句话权威定义（内容化，[DATA-GAP: CONTENT_METADATA 范围内]）
多维身份          IdentityTag[]：医学家 / 文学家 / 史学家 / 学者
生平              BiographyTimeline + HistoricalEvent[]（时间/事件/地点/人物/史料来源）
其传              其传.docx 全文（内容准入后）
其言精选          QuotationBlock[]（三都赋/玄守论/释劝论/笃终论 摘句）
主要著作          WorkCard[]（其言四篇 + 相关著作）
《针灸甲乙经》     专题入口（→ FLAGSHIP-02）
后论 / 历史评价    后论.docx 内容 + Citation
电影 / 影像        MediaRecord[]（皇甫谧电影 2 部）
相关史料          SourceBadge[] / EvidenceBadge[] / CitationBlock[]
```

---

## 3. FLAGSHIP-02 — 《针灸甲乙经》内容模型

```text
作品概览          Work（针灸甲乙经：成书/结构/影响 摘要）
版本脉络主视觉    版本脉络 PNG（客户授权公开展示资产）
版本时间轴        EditionTimeline（按年代排布历代版本）
历代版本          EditionCard[]：医统正脉本·明万历1601 / 五车楼本·明万历 /
                 四库全书本·清乾隆 / 行素草堂本·清光绪 / 存存轩本·清 /
                 江左书林1977 / 黄龙祥校注本 / 张灿玾校注本 /
                 山东中医学院校释本 / 现代整理本 / 帝王世纪 / 高士传 …
版本资料          BibliographicRecord（版本-年代-来源-数字资源）
相关论著          WorkCard[]（理论与实践等）
现代整理研究      现代整理本/校注本研究区
515 篇论文检索     BibliographicSearch（UI-10）
Evidence / Citation 出处可见（P8）
```

**边界（关键）**：版本脉络 PNG 允许公开展示 ≠ 版本关系已完成结构化建模。
`JIAYI_EDITION_RELATIONS` 在结构化提取完成前**继续保留为 [DATA-GAP]**——只影响结构化关系功能，不影响图片展示。

---

## 4. FLAGSHIP-03 — 皇甫谧针灸非遗传承内容模型

```text
HeritageHero         皇甫谧针灸非遗（概览）
第六代名医·刘君奇     GenerationMarker（HERITAGE_GENERATION CLOSED）
HeritagePersonProfile 传承人物档案（见 §5）
非遗认定              RecognitionRecord（市级非遗代表性传承人认定文件）
荣誉                  RecognitionRecord[]（省/市名中医、先进工作者、崆峒工匠、优秀院长…）
学术成果              AchievementRecord[]（学术兼职/课题/论文）
技术成果              AchievementRecord[]（2007 甲乙经腧穴研究市级科技进步二等奖等）
师承教育              ApprenticeshipEvent[]（2023-09-26 拜师大会、师承实施办法）
名中医工作室          StudioRecord[]（崆峒区中医医院 / 灵台县皇甫谧中医院）
媒体报道              MediaCoverage[]（央视《陇脉医承》2025-04-25、甘肃卫视等）
传承谱系              LineageGraph（证据绑定）
Evidence             证据可见
```

---

## 5. HeritagePersonProfile（刘君奇）

```text
name                    = 刘君奇
generation_title        = 第六代名医          ← 正式内容字段（HERITAGE_GENERATION CLOSED）
heritage_role           = 皇甫谧针灸市级非物质文化遗产代表性传承人
professional_title      = 甘肃省名中医 / 平凉市名中医 / 崆峒工匠 …
institution_role        = 皇甫谧针灸学院院长
biography               简介（内容化）
honors                  RecognitionRecord[]
academic_roles          学术兼职[]（省针灸学会副会长 / 市针灸学会会长 / 中国针灸学会非遗工作委员会委员 …）
academic_achievements   学术成果[]（课题：皇甫谧文化传承创新路径研究等）
technical_achievements  技术成果[]（甲乙经腧穴研究市级科技进步二等奖、皇甫谧滞通针法临床应用等）
apprenticeship_activities ApprenticeshipEvent[]（带徒传技/师承教育）
studio                  StudioRecord[]（名中医工作室）
media_coverage          MediaCoverage[]（媒体报道）
heritage_relationships  LineageGraph 关联（师承/传承关系，证据绑定）
evidence                Evidence/Citation 可见
```

---

## 6. 内容记录模型（通用）

### 6.1 RecognitionRecord（证书/荣誉/认定）

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| preview | 媒体 | 证书预览（经脱敏的 public derivative） |
| title | string | 证书名称 |
| category | enum | 非遗认定 / 荣誉称号 / 科研成果奖 / 资质 |
| issuing_authority | string | 颁发机构 |
| date | string | 颁发时间 |
| description | string | 说明 |
| related_person | string | 关联人物（刘君奇） |
| evidence | ref | Evidence 绑定 |

### 6.2 MediaRecord（电影/影像）

| 字段 | 说明 |
| --- | --- |
| title / poster / year / media_type | 基本元数据 |
| description | 简介 |
| relation_to_hfm | 与皇甫谧的关联 |
| playback_asset | 播放资产（存在视频文件才可播放；不存在则不伪造播放能力） |
| source / evidence | 来源/证据 |

### 6.3 Work / Edition / EditionFamily / BibliographicRecord（论著）

```text
Work（作品：如《针灸甲乙经》《帝王世纪》《高士传》）
  └── EditionFamily（版本家族：如"医统正脉本"）
        └── Edition（具体版本：明万历29年吴勉学 1601）
              ├── BibliographicRecord（版本-年代-来源-数字资源-研究）
              └── Evidence
```

**约束**：Work 与 Edition 不得混成普通文件列表（UI-06 acceptance）。

### 6.4 PaperResult / BibliographicSearch（515 篇论文）

```text
PaperResult: title / authors / year / source / keywords / related_entity / evidence
BibliographicSearch: search + filters（年份/作者/主题/文献类型/关联作品）
                    + 高密度学术 Result List（禁止 515 张视觉卡片）
```

- 有全文 → 设计全文阅读入口；仅题录 → 显示题录。由实际资产决定，不制造不存在全文。

### 6.5 EditionRelation（版本脉络关系）

```text
JIAYI_EDITION_RELATIONS = [DATA-GAP]（结构化提取未完成前保持开放）
```

---

## 7. 后端模型映射（供实施参考，不改后端）

| 内容模型 | 后端模型/API | 现状 |
| --- | --- | --- |
| Person / 人物档案 | persons API（entity_id） | 公共投影有 persons/{id} |
| Work / Edition | works / works/{id}/editions | 存在 |
| 版本脉络 | works/{id}/structure + editions + JIAYI_EDITION_RELATIONS [DATA-GAP] | 部分 |
| 传承人物 | HeritageProject / HeritageRelation + Person | 存在（无代数/档案字段） |
| 证书/荣誉 | media（类别扩展 certificate [DATA-GAP: CONTENT_METADATA]） | 待扩展 |
| 论著/论文 | media（classic/paper 类别）+ BibliographicRecord | 部分（题录需元数据） |
| 电影/影像 | media（movie）+ MediaRecord | 存在 |
| Evidence/Citation | evidence-chain（研究端）；公共投影需出版层 | 研究端存在 |

---

## 8. 内容准入与 UI 空态原则

1. 内容准入（docx→结构化、PDF→题录、媒体→登记）属后续实施 WP，本轮不执行。
2. 每个 UI 面有显式 empty state（primitive 定义，见 HFM-UI-PRIMITIVES）：内容未准入时优雅空态，不阻断页面。
3. **不伪造内容**：无全文显示题录；无视频不伪造播放器；无结构化关系不伪造图谱。
4. 隐私脱敏（P2 级）在准入时生成 public derivative（见 HFM-ASSET-PRESENTATION-POLICY）。
