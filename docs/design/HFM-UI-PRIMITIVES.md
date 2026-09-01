# HFM UI Primitive Inventory — 组件原语清单

Status: DESIGN INPUT（UI-00 Design Baseline Closure v2 · 真实内容驱动 · 不实施运行时代码）
Date: 2026-09-01 · 配套: HFM-UI-CONTENT-MODEL / HFM-ASSET-PRESENTATION-POLICY / HFM-DESIGN-PRINCIPLES / HFM-DESIGN-TOKENS-PROPOSAL

每个 primitive 定义六要素：**semantic purpose / minimum fields / optional fields / empty state / evidence presentation / responsive behavior**。

已取消纯版权目的组件：`RightsState`、`RestrictedContentState`（保留定义但标记 NOT_REQUIRED_FOR_CUSTOMER_PROVIDED_ASSETS，仅当出现非客户来源内容时启用）。

---

## 1. 人物面 Primitives

### PersonHero

- purpose: 人物页顶部身份认知（姓名/生卒年/字/号/朝代），建立权威人物志首屏
- min: name, dates
- opt: pinyin, courtesy_name, pseudonym, dynasty, portrait
- empty: 显示占位名 + 空态提示
- evidence: 生卒年可挂 Source/Citation
- responsive: 移动端竖排（姓名/年份分两行）；桌面并排
- 复用: FLAGSHIP-01

### IdentityTag

- purpose: 多维身份徽标（医学家/文学家/史学家/学者）
- min: label
- opt: evidence_ref, href
- empty: 区不渲染
- evidence: 身份断言可挂 Citation
- responsive: 横向 wrap
- 复用: FLAGSHIP-01/03

### BiographyTimeline

- purpose: 生平时间轴（时间/事件/地点/人物/史料来源）
- min: events[]（year/label）
- opt: place, related_person, source_ref, phase_group
- empty: 空态文案"生平内容整理中"
- evidence: 每事件可挂 Source/Citation
- responsive: ≥768 横向/纵向时间轴；<768 纵向列表
- 复用: UI-05, FLAGSHIP-01

### HistoricalEvent

- purpose: 单个生平事件（求学悟道/拒仕治学/久病研医/著书传世）
- min: title, date
- opt: place, description, persons, sources
- empty: 无事件不渲染
- evidence: SourceBadge 可展开
- responsive: 卡片式自适应
- 复用: BiographyTimeline 内

### QuotationBlock

- purpose: 其言/典籍摘句展示（其言精选、引证）
- min: text
- opt: title, source_ref, citation
- empty: 不渲染
- evidence: CitationBlock 必见（P8）
- responsive: 衬线正文，列宽受控
- 复用: FLAGSHIP-01/02, UI-06

---

## 2. 著作/版本面 Primitives

### WorkCard

- purpose: 作品入口卡（其言四篇、甲乙经、帝王世纪、高士传…）
- min: title
- opt: dynasty, category, edition_count, cover, href
- empty: 空态卡"暂无著作"
- evidence: 版本数/出处可见
- responsive: 网格自适应（auto-fill）
- 复用: FLAGSHIP-01/02, UI-06

### EditionCard

- purpose: 具体版本卡（医统正脉本·明万历1601 等）
- min: edition_name
- opt: era, publisher_block, family, digital_resource, evidence
- empty: 空态"暂无版本"
- evidence: 版本出处/来源可见
- responsive: 列表/网格两态
- 复用: FLAGSHIP-02, UI-06

### EditionTimeline

- purpose: 历代版本时间轴（按年代排布版本）
- min: editions[]（year/name）
- opt: family, notes
- empty: 空态"版本整理中"
- evidence: 每版本 Source
- responsive: 横向滚动/纵向
- 复用: FLAGSHIP-02

### EditionRelation

- purpose: 版本-版本脉络关系（传本/校注链）——**仅当 JIAYI_EDITION_RELATIONS 结构化完成**后启用
- min: relations[]（from/to/kind）
- opt: description, evidence
- empty: 显示"版本脉络结构化整理中"（DATA-GAP 期间）；**版本脉络 PNG 展示不受影响**
- evidence: 关系挂 Citation
- responsive: 线稿图自适应
- 复用: FLAGSHIP-02（UI-08）

### BibliographyEntry

- purpose: 论著/版本书目条目（高密度列表）
- min: title, year
- opt: author, publisher, family, source, resource_link
- empty: 空态
- evidence: source 可见
- responsive: 列表始终（无卡片）
- 复用: UI-06

### PaperResult

- purpose: 论文题录条目（高密度学术结果）
- min: title
- opt: authors, year, source, keywords, related_entity, fulltext_link
- empty: 空态
- evidence: source/期刊可见
- responsive: 列表始终
- 复用: UI-10

---

## 3. 证据面 Primitives

### SourceBadge

- purpose: 来源徽标（P8 证据可见）
- min: label
- opt: href, detail
- empty: 无来源不渲染
- evidence: 自身即证据展示
- responsive: 内联徽章
- 复用: 全部内容面

### EvidenceBadge

- purpose: 证据徽标（Evidence 绑定状态）
- min: label
- opt: evidence_id, status
- empty: 不渲染
- evidence: 展开证据详情
- responsive: 内联徽章
- 复用: 全部内容面

### CitationBlock

- purpose: 引用块（原文引用 + 出处 + 复制引用）
- min: text, citation
- opt: copy_button, version
- empty: 不渲染
- evidence: Citation 显式呈现
- responsive: 列宽受控；复制按钮移动端可用
- 复用: FLAGSHIP-01/02, UI-07

---

## 4. 媒体/档案面 Primitives

### ArchiveItem

- purpose: 数字史料馆条目（资料/古籍/影像归档）
- min: title
- opt: category, thumbnail, size, license_note, href
- empty: 空态"暂无归档条目"
- evidence: 来源可见
- responsive: 网格/列表
- 复用: UI-06, /library

### MediaRecord

- purpose: 影像/媒体记录（元数据 + 播放入口）
- min: title
- opt: poster, year, media_type, description, relation_to_hfm, source
- empty: 不渲染
- evidence: source 可见
- responsive: 卡片 + 播放器
- 复用: FLAGSHIP-01/03, /library

### MediaPlayer

- purpose: 视频播放器（**仅当存在实际视频文件时启用**；无文件不伪造播放能力）
- min: playback_asset
- opt: poster, subtitles, description
- empty: 不可用状态（显示"影像资料整理中"）
- evidence: 来源标注
- responsive: 自适应宽高比
- 复用: FLAGSHIP-01/03

---

## 5. 非遗传承面 Primitives

### HeritageHero

- purpose: 传承区首屏（皇甫谧针灸非遗概览）
- min: title
- opt: subtitle, description, stats
- empty: 空态
- evidence: 项目证据
- responsive: Hero band
- 复用: FLAGSHIP-03

### HeritagePersonProfile

- purpose: 传承人物档案（刘君奇）
- min: name
- opt: generation_title, heritage_role, professional_title, institution_role, biography, honors, academic_roles, academic_achievements, technical_achievements, apprenticeship_activities, studio, media_coverage, heritage_relationships, evidence
- empty: 空态"传承人物档案整理中"
- evidence: 各字段可挂 Evidence
- responsive: 分栏（档案主区 + 侧栏关系）
- 复用: FLAGSHIP-03（UI-09）

### GenerationMarker

- purpose: 传承代数标记（**第六代名医**，HERITAGE_GENERATION CLOSED）
- min: generation_label
- opt: person_ref, evidence
- empty: 不渲染（数据缺失时）
- evidence: 认定文件 Evidence
- responsive: 徽标/横幅两种尺寸
- 复用: FLAGSHIP-03, 首页

### RecognitionRecord

- purpose: 单条证书/荣誉/认定记录
- min: title, category
- opt: preview, issuing_authority, date, description, related_person, evidence
- empty: 不渲染
- evidence: Evidence 绑定
- responsive: 展品式卡片（禁简单图片墙）
- 复用: FLAGSHIP-03

### CertificateGallery

- purpose: 证书展墙（组织 RecognitionRecord[]；禁简单图片墙 → 按类别/年份分组 + 说明）
- min: records[]
- opt: filters, grouping
- empty: 空态"证书整理中"
- evidence: 每证书 Evidence
- responsive: 分组网格
- 复用: FLAGSHIP-03（UI-09）

### AchievementRecord

- purpose: 学术/技术成果条目（课题/获奖/论文）
- min: title
- opt: category, year, authority, description, evidence
- empty: 不渲染
- evidence: 成果证据
- responsive: 列表
- 复用: FLAGSHIP-03

### ApprenticeshipEvent

- purpose: 师承教育活动（拜师大会 2023-09-26 等）
- min: title, date
- opt: place, description, participants, sources
- empty: 不渲染
- evidence: 活动新闻稿/大纲 Source
- responsive: 卡片/时间线
- 复用: FLAGSHIP-03

### StudioRecord

- purpose: 名中医工作室记录
- min: name, institution
- opt: description, established, evidence
- empty: 不渲染
- evidence: 工作室证明
- responsive: 卡片
- 复用: FLAGSHIP-03

### MediaCoverage

- purpose: 媒体报道记录（央视《陇脉医承》、甘肃卫视等）
- min: title, outlet
- opt: date, link, screenshot, description
- empty: 不渲染
- evidence: 报道来源
- responsive: 列表 + 截图缩略
- 复用: FLAGSHIP-03

### LineageGraph

- purpose: 传承谱系图/树（证据绑定，P2-04 不回归）
- min: nodes[], edges[]
- opt: generation_markers, evidence
- empty: 空态"谱系整理中"
- evidence: 仅渲染证据完备关系
- responsive: 桌面线稿图；移动端折叠为列表（reduced-motion 静态）
- 复用: FLAGSHIP-03（UI-09）

---

## 6. 隐私/状态面 Primitives

### PrivacyState

- purpose: 隐私分级呈现（P0–P3 对应的展示策略；见 HFM-ASSET-PRESENTATION-POLICY）
- min: privacy_class
- opt: derivative_ref
- empty: —（P0 正常渲染）
- evidence: 脱敏说明可展开
- responsive: 徽标
- 复用: 证书/名单类内容

### RedactedAssetState

- purpose: 已脱敏资产的呈现状态（P2 级 public derivative 标识）
- min: label
- opt: original_ref（非公开）, note
- empty: 不渲染
- evidence: 脱敏来源说明
- responsive: 徽标 + 说明
- 复用: 证书展墙/名单类

### RightsState / RestrictedContentState（保留，非本批客户材料用）

- purpose: **仅当出现非客户来源内容**（第三方新增/用户上传）时启用；本批客户材料不使用
- 标记: `NOT_REQUIRED_FOR_CUSTOMER_PROVIDED_ASSETS`
- 行为: 不用于阻塞本批客户材料展示
- 复用: 预留

---

## 7. 使用规则

1. 每个 primitive 的 empty state 是**一等公民**：内容未准入时优雅空态，不伪造内容（HFM-UI-CONTENT-MODEL §8）。
2. 证据呈现（evidence presentation）是默认能力，不是可选装饰（P8）。
3. 高密度列表（PaperResult/BibliographyEntry）优先于视觉卡片（515 篇论文禁止卡片墙）。
4. primitives 是设计合同；实施时组件命名/API 可调整，但 semantic purpose 与 empty/evidence 行为不变。
