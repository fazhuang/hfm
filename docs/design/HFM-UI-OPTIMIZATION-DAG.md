# HFM UI 优化 DAG — UI Work Package Plan

Status: DESIGN INPUT（实施规划；不改变正式 Phase-2 DAG / Scope；仅规划 UI 优化阶段）
Date: 2026-08-31（UI-00 v2 收敛 2026-09-01）· 依据: HFM-UI-DESIGN-AUDIT / HFM-DESIGN-PRINCIPLES / HFM-INFORMATION-ARCHITECTURE / HFM-VISUAL-DIRECTION / HFM-DESIGN-TOKENS-PROPOSAL / HFM-UI-CONTENT-MODEL / HFM-ASSET-PRESENTATION-POLICY / HFM-UI-PRIMITIVES

**约束**：UI WPs 不修改后端 API 契约；凡 UI 需要而当前 API 不提供的数据，标为 `[DATA-GAP]`，须经治理裁决后再实施，不得在本阶段发明数据。

**客户导航变更（2026-08-31，L1 客户事实）**：门户主导航 = 恰好 5 链接（首页 / 人物（皇甫谧）/ 其言 / 《针灸甲乙经》 / 皇甫谧针灸非遗的传承）。检索/登录/关于平台移入 header 工具区与页脚，能力不删除。

**UI-00 v2 收敛（2026-09-01，客户正式确认）**：

- 刘君奇 = 第六代名医 → `HERITAGE_GENERATION` **CLOSED**（不再是 DATA-GAP）
- 客户材料统一授权公开 → 版权退出开发阻塞（RIGHTS / R0–R3 / 版权 fail-closed 取消；见 HFM-ASSET-PRESENTATION-POLICY.md）
- 隐私独立治理：P0–P3（P2 脱敏 / P3 归档）
- DAG 顺序按 §14 链更新：01→02→04→08→06→10→09→07→11→03→12→13→14→15（首页延后，由四套成熟视觉语言组合）
- 三个旗舰页：FLAGSHIP-01 人物 / FLAGSHIP-02 甲乙经 / FLAGSHIP-03 非遗传承（内容模型见 HFM-UI-CONTENT-MODEL.md）

---

## 0. 总览

| WP | 名称 | 类型 | 前置 | 建议批次 |
| --- | --- | --- | --- | --- |
| UI-00 | Design Audit（含 v2 收敛） | 已完成（本文档集） | — | 0 |
| UI-01 | Design Foundations（token/字体/暗色） | 基础 | UI-00 | 1 |
| UI-02 | Global Shell / Navigation | 基础 | UI-01 | 1 |
| UI-04 | Huangfu Mi Profile（FLAGSHIP-01 人物旗舰页） | 页面 | UI-01, UI-02 | 2 |
| UI-08 | Jiayi Jing（FLAGSHIP-02 甲乙经区） | 页面 | UI-04（视觉语言就绪后） | 2 |
| UI-06 | Literature / Qiyan / Archive（其言与文献） | 页面 | UI-01, UI-02 | 2 |
| UI-10 | Search / Bibliography（检索与论文题录） | 页面 | UI-01, UI-02 | 3 |
| UI-09 | Heritage（FLAGSHIP-03 非遗传承） | 页面 | UI-01, UI-02 | 3 |
| UI-07 | Ancient Text Reader（阅读器） | 页面 | UI-01, UI-02 | 3 |
| UI-11 | Research Workbench（研究端） | 面 | UI-01 | 3 |
| UI-03 | Homepage（叙事首页，延后） | 页面 | 四套视觉语言成熟后 | 4 |
| UI-12 | Responsive（断点矩阵加固） | 横切 | UI-01 | 随各 WP |
| UI-13 | Accessibility（无障碍达标） | 横切 | UI-01 | 持续+收尾 |
| UI-14 | Exhibition Readiness（展厅就绪） | 横切 | UI-01 | 5 |
| UI-15 | Visual QA（视觉验收） | 收尾 | 全部 | 5 |

建议顺序（§14 链）：`UI-01 → UI-02 → UI-04 → UI-08 → UI-06 → UI-10 → UI-09 → UI-07 → UI-11 → UI-03 → UI-12 → UI-13 → UI-14 → UI-15`。
UI-05（Timeline 组件）作为 UI-04/UI-03 的依赖组件随 UI-04 一并落地。
**首页（UI-03）延后**：首页最终由 人物/甲乙经/论著/非遗 四套成熟视觉语言组合产生，不得提前制作脱离真实内容的宣传首页。

---

## UI-00 — Design Audit（已完成）

- scope: 现状审计、原则、IA、视觉方向、token 提案（本文档集）
- status: DONE（本批次交付物）
- 交付: `docs/design/HFM-{UI-DESIGN-AUDIT,DESIGN-PRINCIPLES,INFORMATION-ARCHITECTURE,VISUAL-DIRECTION,DESIGN-TOKENS-PROPOSAL,UI-OPTIMIZATION-DAG}.md`

---

## UI-01 — Design Foundations（token / 字体 / 暗色）— IMPLEMENTED 2026-09-01

> **实施记录**：tokens.css 三层（primitive→semantic→.dark）落盘；foundations.css 全局基础；main.ts 引入；useViewport 扩展 xl/2xl；AuditLog 徽标 token 化。验证：typecheck/lint(0 errors)/vitest 80/80/build/e2e 10/10 全过；计算样式断言确认浅/暗主题真实生效（见 HFM-DESIGN-TOKENS-PROPOSAL §10）。

- **scope**：按 Token 提案落盘 primitive→semantic 两层 token（semantic direction：暖白/墨色/低饱和朱砂/土褐/铜金/青灰；HEX 不冻结）；修复暗色模式（`.dark` 语义覆盖）；建立字号/行高/间距/圆角/边框/断点/焦点环体系；中文字体栈（系统字体，不引入字体文件）；图标集初步（线条型 SVG）。
- **dependencies**：UI-00。
- **Entry Gate（UI-01 准入，全部满足才开工）**：
  - [x] 客户材料 → UI surface 映射完成（HFM-CONTENT-ASSET-MAP.md）
  - [x] 刘君奇"第六代名医"进入正式内容模型（HFM-UI-CONTENT-MODEL.md §5）
  - [x] `HERITAGE_GENERATION` DATA-GAP 关闭
  - [x] 三个旗舰页面内容模型完成（FLAGSHIP-01/02/03）
  - [x] UI primitives inventory 完成（HFM-UI-PRIMITIVES.md）
  - [x] PUBLIC IA 完成（HFM-INFORMATION-ARCHITECTURE.md §3）
  - [x] RESEARCH IA 完成（§4）
  - [x] Privacy 模型完成（HFM-ASSET-PRESENTATION-POLICY.md §4，P0–P3）
  - [x] 剩余 DATA-GAP inventory 完成（本文件 §2）
  - [x] UI DAG 更新完成（§14 链）
  - [x] 无正式 Governance baseline 漂移
  - [x] worktree 可解释
  - （已删除：版权逐件核验 / RIGHTS_CLASS / RIGHTS DATA-GAP / 电影播放版权核验 / 论文全文版权核验——不再属于开发准入条件）
- **files**：`apps/frontend/src/styles/tokens.css`（重建）、新增 `styles/foundations.css`（可选）、`composables/useTheme.ts`（暗色接线）、`composables/useViewport.ts`（xl/2xl）、全局组件样式对齐。
- **acceptance**：全部 token 有 WCAG 对比度记录；暗色模式切换有实际视觉效果（现状失效）；现有 e2e/axe 不回归；token 只读引用无硬编码 hex 泄漏（AuditLog 徽标 token 化）。
- **visual acceptance**：浅/暗两套主题在 人物页 与 Reader 预览一致通过设计评审；焦点环、hover、active 状态完整。
- **regression risk**：中——全局样式替换影响所有页面；用灰度策略（先 2–3 页）。

## UI-02 — Global Shell / Navigation — IMPLEMENTED 2026-09-01

> **实施记录**：PublicLayout 重建（客户 5 链接主导航 + header 检索/登录工具区 + 移动抽屉（aria-expanded/焦点圈闭/Escape）+ skip-link + AppFooter 政校共建署名）；新增 /yan /jiayi /about 路由与占位页（内容建设中空态，不伪造内容）；Research/Admin 布局对齐（skip-link + main id）；SearchView 支持 header 检索 ?q= 深链；导航数据模块 `src/config/navigation.ts`（CORE_PERSON_ROUTE 待内容准入对齐实体 id）。验证：typecheck ✓ · lint 0 errors ✓ · vitest 85/85 ✓（含 ui02_shell 5 链接/抽屉/焦点用例）· build ✓ · e2e 11/11 ✓（含 5 链接 e2e 断言 + 移动抽屉交互 + 全断点无溢出）· 计算样式断言（5 链接/active 朱砂/品牌铜金宋体/页脚完整机构署名/skip-link）✓

- **scope**：公共导航按**客户强制 5 链接**实现（首页 / 人物（皇甫谧）/ 其言 / 《针灸甲乙经》 / 皇甫谧针灸非遗的传承）；检索与登录从主导航移入 header 工具区（搜索框/登录入口）；品牌区识别度（heritage 色 + 徽记候选）；页脚补全（署名带：甘肃医学院 × 灵台县皇甫谧中医针灸传承创新示范中心——完整官方名称，CR-001/006；关于平台/合规/版权/免责声明链接 → `/about`）；移动端导航抽屉；skip-link 与全站焦点样式；研究/管理端 shell 对齐 token。
- **dependencies**：UI-01。
- **files**：`layouts/PublicLayout.vue`、`layouts/ResearchLayout.vue`、`layouts/AdminLayout.vue`、`App.vue`、新增 `components/AppFooter.vue`、`components/AppSkipLink.vue`、`views/AboutView.vue`（页脚指向）、导航数据模块。
- **acceptance**：主导航恰为 5 个链接（e2e 断言）；检索/登录能力在 header 工具区可达；移动端 <768 抽屉可用且焦点圈闭；skip-link 直达 main；页脚含完整官方机构署名与关于链接；e2e 不回归。
- **visual acceptance**：三端 header/footer 气质统一、识别度高；无装饰元素。
- **regression risk**：中——导航改动影响全部公共路由（e2e nav 断言需同步）；登录入口从主导航移出但路径不变。

## UI-03 — Homepage（叙事首页）— IMPLEMENTED 2026-09-01

> **实施记录**：HomeView 重建为 CONTEMPORARY CHINESE DIGITAL HUMANITIES PORTAL（叙事首页，非功能拼盘）：
>
> - **Hero**：唯一 H1 皇甫谧人文数字平台 + 副题（权威数字人文资料 · 古籍与研究 · 非遗活态传承）+ 皇甫谧 215—282 + 复用 UI-04 定义 + 双主 CTA（探索皇甫谧/进入《针灸甲乙经》）+ 次级检索 + 首页 Search（→ /search?q=，零独立搜索逻辑）。
> - **叙事链**：Hero → 皇甫谧 Feature（身份标签/其传/其言/后论入口）→ 《针灸甲乙经》Feature（作品定位 + 版本脉络图带 caption/DATA-GAP 说明 + 5 代表版本 + CTA）→ 文献与史料（后论真实引文《晋书》房玄龄带出处 + 其言/帝王世纪/高士传/档案入口）→ 非遗 Feature（第六代名医·刘君奇 + 师承 2023-09-26 + 央视《陇脉医承》+ 工作室；PARTIAL 明示）→ Research Discovery（检索→阅读→来源→引用 流程 + 研究工作台次级 CTA）。
> - **指标**：4 个真实指标全部来自 contentInventory（版本 19/论著 92/论文 515（审计，已结构化题录 5 明示）/Reader 2）；19 版本 ≠ 19 部著作、515 ≠ 5 语义严格分离。
> - **数据策略**：homeProjection 仅选取/排序既有已验证数据，零新领域事实、零虚构引文/古文/肖像；机构名与公益定位复用 UI-02（Hero metadata + footer bridge）。
> 验证：typecheck ✓ · lint 0 errors ✓ · vitest 187/187 ✓（含 ui03_home：品牌/指标完整性/515-5 不变量/19≠19部/引文真实/无临床/无内部路径/CTA 路由/axe）· build ✓ · e2e 57/57 ✓（含 ui03：唯一 H1/叙事五区/CTA 路由/Search 提交/第六代名医+DATA-GAP/真实引文/375–1920/暗色/640px 200% 缩放）· 数据完整性 + 性能扫描全绿 ✓（首页为静态投影，零 docx/fs/AI 运行时依赖）

- **scope**：叙事首页按 5 链接 IA 组织：HERO（皇甫谧认知 + 一句话权威定义）/ 人物（皇甫谧）入口 / 其言四篇入口 / 《针灸甲乙经》入口（版本脉络/论著/论文）/ 传承入口（证书/非遗资料/传承人物）/ 政校共建署名区；HERO 文案从合规声明改为叙事；合规声明移至页脚/关于页。
- **dependencies**：UI-01, UI-02；消费 UI-05 时间轴摘要。
- **files**：`views/HomeView.vue`（重建）、新增首页区块组件。
- **acceptance**：首页各区块与 5 导航一一对应并可跳转；匿名可见（P2-01-AC-01/02 不回归）；axe 通过；无未发布内容泄漏。
- **visual acceptance**：Hero 3 秒建立"权威人文平台"认知；层级 = 留白+字重+细线；无伪古风元素。
- **regression risk**：中高——首页数据投影 `fetchPublicHome` 消费不变；若某区缺数据 `[DATA-GAP]` 须空态优雅降级（不得阻断整页）。

## UI-04 — Huangfu Mi Profile（FLAGSHIP-01 人物旗舰页，导航「人物（皇甫谧）」目的地）— IMPLEMENTED 2026-09-01

> **实施记录**：PersonDetailView 重建为 Digital Scholarly Biography：Hero（姓名/215—282/字·号·朝代）→ 权威定义 → 多维身份（4 徽标）→ 生平时间轴（UI-05 Timeline：核心人生四阶段，数据准入后由 events 驱动）→ 其传（空态）→ 其言精选（空态 + /yan 链接）→ 主要著作（5 入口卡 → /yan /jiayi）→ 后论（空态）→ 史料依据（断言 + 证据徽标，P8）→ 影像（真实 media 投影）→ Evidence 注；types/public.ts 断言/事件类型化；核心人物锚点配置 `src/config/corePerson.ts`（客户确认内容模型，待内容准入后转数据驱动）。验证：typecheck ✓ · lint 0 errors ✓ · vitest 92/92 ✓（含 ui04_person 旗舰结构/证据徽标/axe）· build ✓ · e2e 11/11 ✓ · 真实浏览器断言（Hero/四徽标/四阶段/五著作/证据徽标/影片/8 区；移动端无溢出）✓

- **scope**：按审计 §7 重建（也是导航 5 链接之「人物（皇甫谧）」的目的页）：视觉识别（姓名/生卒年 215—282/字/号/朝代）→ 核心身份 + 一句话权威定义 → 其传（人物摘要/生平：求学悟道·拒仕治学·久病研医·著书传世）→ 生平时间轴（UI-05）→ 身份 / 思想精神 → 历史评价（后论）→ 著作（其言四篇/甲乙经入口）→ 相关人物/地点 → 史料证据 → 皇甫谧电影（影视资料）。
- **dependencies**：UI-01, UI-02, UI-05。
- **files**：`views/persons/PersonDetailView.vue`（重建）、`types/public.ts` 扩展（[DATA-GAP] 处标注）、可能新增 `services/person.ts`。
- **acceptance**：每条人物信息可进入 事件/地点/文献/原文/版本/Citation（P7 可达性走查）；证据出处可见（P8）；axe 通过；无临床内容；其传/后论内容准入 `[DATA-GAP]` 未落地前以空态/占位呈现。
- **visual acceptance**：人物页为 HFM 标志性页面（扉页式题名 + 衬线正文）；克制朱砂/铜金点睛。
- **regression risk**：中——`/persons/:id` 路径不变；现有 API 字段 `assertions/events` 需确认公共投影字段名（[DATA-GAP] 治理）。

## UI-05 — Timeline（时间轴组件）— IMPLEMENTED 2026-09-01

> **实施记录**：`components/Timeline.vue`（线稿纵向时间轴：节点/日期铜金/地点·人物·史料来源元数据/描述）+ `types/timeline.ts`（TimelineEvent：id/title/date/place/person/source/description，可选字段适配 [DATA-GAP] 投影）。reduced-motion 静态安全；键盘原生可达；空态由父级渲染。已供 UI-04 消费（核心人生四阶段）。验证：随 UI-04 单测覆盖。

- **scope**：线稿时间轴组件（时间/事件/地点/人物/史料来源）；人生阶段分组；responsive（纵向/横向切换）。
- **dependencies**：UI-01。
- **files**：新增 `components/Timeline.vue`、`types/timeline.ts`。
- **acceptance**：键盘可操作（焦点进入每个事件节点）；`prefers-reduced-motion` 下降级为静态列表；空数据优雅降级。
- **visual acceptance**：细线+节点+年份衬线数字；无装饰动画。
- **regression risk**：低——新组件，仅被 UI-03/04 消费。

## UI-06 — Literature / Qiyan / Archive（其言与文献，导航「其言」+ 论著/档案）— IMPLEMENTED 2026-09-01

> **实施记录**：
>
> - **其言（/yan 重建）**：忠实呈现客户其言.docx 真实内容（引言 + 四篇说明《三都赋》序/玄守论/释劝论/笃终论 + 辑佚补充；docx 文本提取，无 OCR、无改写、无虚构全文——四篇古典全文 DATA_GAP 诚实标注）；主题标签显式标记 PRESENTATION_CLASSIFICATION；长文用 .hfm-reading；出处/来源逐条可见。
> - **论著（/works 新建）**：WORK 层作品目录（甲乙经/帝王世纪/高士传/其言四篇/后论），字段缺失不显示，不以"未知/N/A"堆积；Work ≠ Edition ≠ ArchiveRecord 语义明确。
> - **数字档案（/archive 新建）**：六类收录概览（人物资料/著作/甲乙经版本资料/现代研究/影像/非遗入口），公开来源名展示，registerKey 仅 provenance 不渲染，内部路径零暴露。
> - **contentInventory**：计数单一来源（92/515/19/2/3/1，源头 jiayiView），各页不再各自硬编码。
> - 路由新增 /works /archive；jiayiView 相关入口补链（帝王世纪/高士传 → /archive、论著/研究 → /works）。
> 验证：typecheck ✓ · lint 0 errors ✓ · vitest 112/112 ✓（含 ui06_literature：真实内容/无虚构全文/Work≠Edition/档案路径不暴露/CTA 路由/axe）· build ✓ · e2e 30/30 ✓（含 ui06：三面 heading+375 无溢出/其言真实内容/档案无内部路径/暗色阅读）· 全断点 375–1920 三面 0 溢出 · 暗色长文/档案徽标 token 正确 ✓

- **scope**：其言区（`/yan`）：三都赋、玄守论、释劝论、笃终论四篇全文阅读（衬线正文/出处可见；内容源 `hfmzl/皇甫谧/其言/其言.docx`，`[DATA-GAP: CONTENT_METADATA]` 内容准入）；著作/版本展示按 **Work / Edition / EditionFamily / BibliographicRecord** 模型（不得混成普通文件列表）；版本卡含 era/publisher/证据标识；来源/Citation 元数据可见（P8）；甲乙经论著（≈100 件，古籍版本/校注本/现代版/相关文献 四类）与论文（515 篇题录，BibliographicSearch）以资料子面呈现（客户授权公开；数字资源按实际文件提供）。
- **dependencies**：UI-01, UI-02。
- **files**：新增 `views/yan/YanView.vue`（+ 四篇详情）、`views/works/WorkDetailView.vue`、新增著作列表视图或首页区块复用。
- **acceptance**：四篇入口齐全（无文本时优雅空态）；Work/Edition 层级正确；版本信息完整呈现；出处可见；空态优雅；匿名可读（P2-01-AC-01/02 不回归）。
- **visual acceptance**：档案式列表/表格（无阴影卡片）；衬线标题；四篇以"其言"统一气质呈现。
- **regression risk**：低中——新增路由 `/yan`；`/works/:id` 路径不变。

## UI-07 — Ancient Text Reader（阅读器）— IMPLEMENTED 2026-09-01

> **实施记录**：新建专业古籍/学术阅读器（/reader/:id，原 /reader 保持 P2-03 面不动）：
>
> - **真实内容**（只读 docx 提取，零虚构）：`houlun`《后论·历史评价汇编》（论其人 12 条带出处引文 + 演其人/讲其人/冠其名 三表）+ `qichuan` 其传史料来源整理（本源史料/地方志/类书/现代考据/谱系/图像遗存）。四论古典全文未见于客户材料 → METADATA_ONLY 条目（DATA_GAP 诚实标注，链接其言）。
> - **阅读体验**：宋体 hfm-reading 排版（字阶 A−/标准/A＋）、章节导航（sticky、hash 恢复、scroll-margin-top）、CitationBlock（确定性引用 + 复制，文档级粒度不虚构卷/页/版本号）、aside（来源/状态/版本上下文/相关实体）、底部导航、无效 ID → not-found + 恢复链接。
> - **联动**：Search 接入 2 条 TEXT（→ /reader/:id）+ 档案其传/后论记录转 AVAILABLE 指向 reader；保留 P2-03 legacy 类型（ReaderPassage/SearchResultItem）。
> 验证：typecheck ✓ · lint 0 errors ✓ · vitest 160/160 ✓（含 ui07_reader：投影/可用性核算/引文确定性/无效 ID/检索路由/axe）· build ✓ · e2e 46/46 ✓（含 ui07：真实正文/章节 hash 恢复/复制引用/无效 ID/检索→阅读/375+1920+640(200%缩放)+暗色）· 全断点 0 溢出 · 零内部路径/零虚构卷页/零临床 ✓

- **scope**：按审计 §8：阅读列宽受控（720px）、原文/现代标点切换（[DATA-GAP] 若数据不支持则先做排版档位）、注释（[DATA-GAP]）、篇章层级导航（卷/篇/条目）、结构化 locator 展示、Source/Citation/Version/Evidence 出处行（P8）、复制引用、深链接（`/reader#locator`）、阅读模式（字号放大/衬线）、全屏阅读、滚动位置保持；保持"非临床"边界（P2-03-AC-04 不回归）。
- **dependencies**：UI-01, UI-02。
- **files**：`views/reader/ReaderView.vue`（重建）、`types/reader.ts` 扩展、`composables/useReader.ts`（新）。
- **acceptance**：深链接可复现同一定位（P2-03-AC-01 语义延续）；证据/出处行可见；键盘+读屏可读；不出现诊疗推荐。
- **visual acceptance**：阅读区裸排（无边框卡片干扰）、衬线正文、舒适行距（P6 10 分钟阅读走查）。
- **regression risk**：中高——阅读器为核心能力；保留 TOC+面板骨架；分阶段（先排版/证据层，后标点/注释 [DATA-GAP] 项）。

## UI-08 — Jiayi Jing（FLAGSHIP-02 甲乙经区，导航「《针灸甲乙经》」目的地）— IMPLEMENTED 2026-09-01

> **实施记录**：JiayiView 重建为数字学术作品档案：HERO → 作品档案（版本/研究计数取自审计注册表：92 件论著 / 515 篇论文，非硬编码业务逻辑）→ 版本脉络（客户 PNG 正式展示资产，web 派生 `/assets/jiayi/edition-lineage.png`，带 alt/caption/来源/DATA-GAP 说明 + 键盘可操作放大对话框（ESC 关闭/焦点返回/reduced-motion））→ 历代版本（EditionCollection：古代 6 种 / 近现代整理 13 种，全部字段来自客户目录名）→ 版本年代排序（chronology 时间轴，明确 ≠ lineage，无虚构继承边）→ 相关论著与入口 → 现代整理与研究（黄龙祥/张灿玾等，仅材料支持的姓名）→ 学术论文（515 审计数 + 5 条真实题录 preview + 检索 CTA → /search?q=）→ 来源与证据 → 相关导航；数据视图模型 `src/data/jiayiView.ts`（typed static view model，来源路径逐条标注）；`JIAYI_EDITION_RELATIONS` 保持 DATA-GAP（PNG 展示 ≠ 结构化完成）。验证：typecheck ✓ · lint 0 errors ✓ · vitest 102/102 ✓（含 ui08_jiayi 结构/数据完整性/chronology≠lineage/axe）· build ✓ · e2e 24/24 ✓（含 ui08：heading+PNG/键盘放大对话框/375 无溢出/暗色 PNG 不反色）· 全断点 375–1920 无溢出 ✓

- **scope**：甲乙经区（`/jiayi`）：作品概览 → **版本脉络主视觉**（客户脉络图 PNG，正式公共展示资产）→ **版本时间轴**（EditionTimeline）→ 历代版本（EditionCard：医统正脉本·明万历1601、五车楼藏板·明万历、四库全书本·清乾隆、行素草堂本·清光绪、清四明存存轩本、江左书林1977、黄龙祥校注本、张灿玾/徐国千校注本、山东中医学院校释本、现代整理本、帝王世纪、高士传…）→ 版本资料（BibliographicRecord）→ 相关论著 → 现代整理研究 → 515 篇论文检索（BibliographicSearch）→ Evidence/Citation；结构化知识入口：篇章结构导航、穴位/理论关系/历史医学知识图谱入口（渐进披露 T2→T3；[DATA-GAP] 图谱数据需治理）；明确"非临床诊疗"标识；阅读入口指向 reader（UI-07）。
  **边界**：版本脉络 PNG 允许公开 ≠ `JIAYI_EDITION_RELATIONS` 结构化完成；该关系保持 [DATA-GAP]，不影响图片展示。
- **dependencies**：UI-04（人物页视觉语言就绪后），UI-01/02。
- **files**：新增 `views/jiayi/JiayiView.vue`、`views/reader/ReaderView.vue` 扩展、`types/reader.ts`。
- **acceptance**：作品概览/版本脉络/历代版本/论著/论文入口齐全（无数据时优雅空态）；知识结构导航可用；无临床推荐面；证据可追溯；匿名可读。
- **visual acceptance**：图谱为线稿式（细线+节点+青灰/朱砂点缀）；版本脉络以客户脉络图作主视觉 + 时间线呈现。
- **regression risk**：中——依赖图谱/版本关系数据可用性；无数据时以结构导航+空态呈现。

## UI-09 — Heritage（FLAGSHIP-03 皇甫谧针灸非遗传承，导航「传承」目的地）— IMPLEMENTED 2026-09-01

> **实施记录**：HeritageView 重建为非遗活态传承数字档案（LIVING HERITAGE SCHOLARLY ARCHIVE）：
>
> - 结构：非遗项目（HeritageProject 与 HeritagePerson 分离）→ 第六代名医·刘君奇（GenerationMarker 正式展示，HERITAGE_GENERATION CLOSED）→ 认定与荣誉（RecognitionRecord 结构化 8 条；证书图像 N/A——客户 PDF 未转派生产物，结构化记录为主）→ 学术与技术成果（含 2007《甲乙经》腧穴研究市级科技进步二等奖等真实科研列表记录）→ 师承教育（2023-09-26 拜师大会，新闻稿脱敏——剔除手机号）→ 名中医工作室（崆峒/灵台两室）→ 媒体报道（CCTV《陇脉医承》2025-04-25 等，无国家级背书价值判断）→ 传承谱系（LineageGraph：仅皇甫谧 + 刘君奇已确认节点，中间代 LINEAGE_STRUCTURING: PARTIAL 显式占位，零虚构人物/边）→ 重要时间节点（chronology ≠ lineage）→ Evidence/来源。
> - **Privacy Review**：拜师新闻稿手机号已从公共派生剔除；名单/法人/考评员/场地类（P2/P3）不进入公共投影；页面/数据扫描 0 手机号、0 内部路径。
> - **Search 接入**：刘君奇 → person 类型（route /heritage）；非遗项目/师承/工作室/媒体报道 → archive 类型（复用六类 taxonomy，未扩张）。
> - **Archive 联动**：UI-06 档案非遗条目已指向 /heritage。
> 验证：typecheck ✓ · lint 0 errors ✓ · vitest 149/149 ✓（含 ui09_heritage：代际/真实性/谱系完整性/隐私扫描/检索投影/axe）· build ✓ · e2e 40/40 ✓（含 ui09：旗舰内容/谱系 PARTIAL/检索集成/375+暗色+无临床面）· 全断点 0 溢出 · 浅/暗 token 正确 ✓

- **scope**：传承区升级为核心页面，以 `zzcl/` 申报档案为内容源（见 HFM-CONTENT-ASSET-MAP.md §2 / HFM-UI-CONTENT-MODEL.md §4）：
  - **传承人物档案页**（HeritagePersonProfile）：**第六代名医·刘君奇**（`generation_title` 正式字段，`HERITAGE_GENERATION` CLOSED）——荣誉（名中医/先进工作者/崆峒工匠/优秀院长）、学术兼职（省针灸学会副会长/市针灸学会会长等）、技术成果（2007 皇甫谧《针灸甲乙经》腧穴刺灸学成就及临床应用研究 市级科技进步二等奖等）、课题（皇甫谧文化传承创新路径研究）、论文（皇甫谧滞通针法临床应用）；
  - **证书展墙**（CertificateGallery + RecognitionRecord）：非遗传承人认定文件 + 荣誉/科研成果奖证书；P2 脱敏后展示（禁止简单图片墙）；
  - **非遗资料/媒体报道**（MediaCoverage）：央视《中国中医药大会》第二季《陇脉医承》（2025-04-25）、甘肃卫视等（注明来源）；
  - **传承活动**（ApprenticeshipEvent）：师承教育拜师大会（2023-09-26 甘肃医学院附属医院国医馆）、名中医工作室（StudioRecord：崆峒区中医医院/灵台县皇甫谧中医院）；
  - **传承谱系**（LineageGraph）：从平面列表升级为关系图/树（线稿，证据绑定，P2-04-AC-01/02 不回归）。
- **dependencies**：UI-01, UI-02。
- **files**：`views/heritage/HeritageView.vue`（重建）、新增传承人物档案视图/组件、整合或重建 `components/LineageTree.vue`（消除重复）、`types/heritage.ts` 扩展（generation_title/证书/档案）。
- **acceptance**：传承人物/证书/非遗资料/传承活动/传承谱系五区齐全（无数据优雅空态）；仅渲染证据完备关系；空态优雅（P2-04-AC-03）；键盘可达；P2 证书脱敏后公开、P3 证照不进入公共投影（隐私治理，非版权）；第六代名医为页面视觉锚点。
- **visual acceptance**：谱系图为线稿树/图；证书以"展品"式呈现；GenerationMarker"第六代名医"作视觉核心；无伪古风。
- **regression risk**：中——现有 e2e（p2_04）需同步。

## UI-10 — Search / Bibliography（公共端统一学术检索）— IMPLEMENTED 2026-09-01

> **实施记录**：SearchView 重建为 entity-aware scholarly discovery（本地确定性索引）：
>
> - **Search projection**（src/data/searchIndex.ts）：DOMAIN → SEARCH 单向投影，6 类型（person/text/work/edition/archive/paper），模块加载时构建一次，searchableText 仅公共字段（registerKey/hfmzl/zzcl 零暴露）；**AUDITED_PAPER_TOTAL=515 与 SEARCHABLE_PAPER_TOTAL=5 严格分离**（页面明示）。
> - **确定性 ranking**（exact title > prefix > includes > author exact > metadata > body；type/year/title 稳定 tie-break），同 query 同序。
> - **Facets**：类型（全部+6），计数来自当前结果集；**URL 单一事实源**（?q=&type=&page=）：refresh/back/forward 恢复；分页 ?page=（page size 10，aria-current）。
> - **结果渲染**：BibliographyEntry（论文高密度学术列表）+ 各类型行；SearchHighlight 安全高亮（无 v-html，<mark> 文本节点，screen reader 原文）。
> - 初始态（内容类型概览 + 真实内容入口）；空态（关键词/清除/建议）；aria-live 结果数；facet 键盘可操作。
> 验证：typecheck ✓ · lint 0 errors ✓ · vitest 132/132 ✓（含 ui10_search：索引构建/真实查询/确定性排序/facet 计数/URL 同步/分页/数据完整性/axe）· build ✓ · e2e 36/36 ✓（含 ui10：查询/type URL/刷新与 back-forward/键盘提交/375+1920/暗色高亮）· 全断点 0 溢出 · 真实查询验证（皇甫谧 18 / 帝王世纪 2 / 黄龙祥 2 / 不存在词 0）✓

- **scope**：单输入 → 检索面：kind facets（著作/人物/段落/词条/版本/资料）、结果元数据（kind/版本/出处）、命中高亮（[DATA-GAP] 高亮片段依赖后端 snippet，先呈现现有 snippet）、搜索建议（可选，[DATA-GAP]）。
- **dependencies**：UI-01, UI-02。
- **files**：`views/search/SearchView.vue`、`services/api.ts`（不改变路径，扩展参数）。
- **acceptance**：facets 过滤与 role-scope（匿名=已发布，P2-03-AC-03 不回归）；空/错误态优雅；键盘可操作。
- **visual acceptance**：结果列表密度适中；kind 徽标用语义色。
- **regression risk**：低——公共搜索端点不变。

## UI-11 — Research Workbench（研究端）— IMPLEMENTED 2026-09-01

> **实施记录**：研究端由"仅 ExportPanel 演示面"升级为 SCHOLARLY RESEARCH INTERFACE（REFINE not REPLACE）：
>
> - **Research Shell**（ResearchLayout 重建）：研究侧栏（仅真实功能：总览/检索/人物/作品/版本/档案/论文/非遗/阅读）+ 面包屑（IA 语义）+ 研究端账户导航（含 公众门户 反向链接）+ 保留 RBAC guard 与退出登录。
> - **Landing**：搜索入口 + 真实 inventory（人物 2/作品 8/版本 19/档案 8/论文 5（审计 515）/Reader 2）+ Evidence·引用·阅读入口 + ExportPanel（P2-06 原样保留）；零假用户统计。
> - **研究检索**：复用 UI-10 SEARCH_INDEX + 确定性 searchIndex（ONE INDEX，无第二索引）；高密度结果（作者/年份/状态/来源/公众页+研究视图双链）。
> - **实体研究视图**（/research/entity/:type/:id）：person/work/edition/archive/paper/heritage/reader 七类，researchProjection 视图层（零领域模型复制）；EvidenceExplorer（映射现有 ContentStatus，无虚构状态）；Research→Public 链接（人物页/甲乙经/非遗/Reader）。
> - **不变量保持**：515/5 分离 · Jiayi lineage DATA-GAP · Heritage lineage PARTIAL · 刘君奇第六代名医 · 四论无虚构 · 零内部路径。
> 验证：typecheck ✓ · lint 0 errors ✓ · vitest 174/174 ✓（含 ui11_research：投影/领域复用/不变量/RBAC guard/组件/axe）· build ✓ · e2e 53/53 ✓（含 ui11：登录流/landing/检索/四实体研究视图/Evidence/公共↔研究回环/移动侧栏键盘/375+1920+暗色）· 数据完整性扫描全绿 ✓

- **scope**：研究 IA（见 IA §4）：工作台首页（概览）、研究检索（facets+role-scoped）、证据链视图（Citation→Evidence→Source，复用 `/evidence-chain/{citation_id}`）、内容管理列表/表单（persons/works/c-terms/heritage/notes——高密度表格 + 表单系统）、导出/打印重建（保留免责声明，P2-06 不回归）；研究端零装饰、效率优先。
- **dependencies**：UI-01。
- **files**：`views/research/ResearchHomeView.vue`、新增 `views/research/*`、`components/DataTable.vue`（新）、`components/form/`（新）、`components/EvidenceChain.vue`（新）。
- **acceptance**：role-scoped 路由不回归（P2-02-AC-01/02）；证据链从 citation_id 完整渲染；导出含免责声明（P2-06-AC-01）；无匿名访问。
- **visual acceptance**：高密度、无装饰、信息层级靠表格线与字重。
- **regression risk**：中——研究端为新增面，不触碰公共端；ExportPanel 重建需保 P2-06 测试语义。

## UI-12 — Cross-Surface Consistency & Content Integrity Audit — CORRECTION PASSED 2026-09-01

> **UI-12 Correction（P0=0 · P1=0 · P2=2 non-blocking）**：
>
> - **P1-01 CLOSED**：主导航「人物（皇甫谧）」canonical route 修正 `/persons/huangfu-mi` → `/persons/person-huangfu-mi`（config/navigation.ts CORE_PERSON_ROUTE）；全仓非测试源码扫描 0 残留；桌面/移动抽屉导航 e2e 验证可达人物页 + aria-current；direct URL 正常。
> - **P1-02 CLOSED**：Jiayi 公共 UI 内部路径移除（JiayiView 研究记录来源 + 来源与证据 + EditionLineageImage 脉络图来源），改为公共来源标签（JIAYI_PUBLIC_SOURCES：客户提供《针灸甲乙经》资料/论著资料/学术论文资料/版本脉络图资料）；内部 provenance 仅存数据层（registerKey/JIAYI_SOURCE_REGISTER），DOM 渲染面零暴露（渲染面扫描 0 命中 + ui06/09/12 断言）。
> - **P2-01 CLOSED**：`pnpm format` 格式化 36 个合法前端 source/test 文件，format:check PASS（test-results/ 生成物目录加入 .prettierignore，与 dist/coverage 模式一致）。
> - **P2-02 NON-BLOCKING**：ESLint 0 errors（历史 warning 保留，格式化后 930→844）；jsdom Canvas 为 axe tooling observation。
> 验证：typecheck ✓ · lint 0 errors ✓ · format:check PASS ✓ · vitest 195/195 ✓ · build ✓ · e2e 61/61 ✓（含 ui12-correction：PATH D 桌面+移动人物导航/canonical URL/PATH E jiayi 无内部路径+标签可读）· 等价 whitespace PASS ✓ · 不变量复核全过（515/5 · Jiayi DATA-GAP · Heritage PARTIAL · 第六代名医 · FULL_TEXT=2）

> 原审计：视觉一致性 / 内容事实一致性 / route/CTA / domain invariant / responsive / accessibility / dark-light / privacy / clinical boundary / interoperability / legacy Phase-2 regression（P2 项延续）

- **dependencies**：UI-01；随各 WP 同步。
- **files**：`composables/useViewport.ts`、各视图 media queries、`e2e/viewport.spec.ts` 扩展。
- **acceptance**：断点矩阵 e2e 不回归（P2-01-AC-05）+ xl 档新增用例；触摸目标审计通过。
- **visual acceptance**：≥1440 阅读与首页无拉伸感。
- **regression risk**：低中——新增断点不改变既有 <lg 行为。

## UI-13 — Visual Polish & Interaction Refinement — IMPLEMENTED 2026-09-01

> **实施记录**（只做 polish，零 IA/domain/route/fact/governance 变更，零新依赖）：
>
> - **字阶统一**（foundations.css）：全局标题字阶 h1 28 / h2 22 / h3 18 / h4 16（页级 hero 标题由视图显式字号覆盖不受影响）。
> - **共享展示原语**：`.hfm-eyebrow`（SectionEyebrow，heritage 色 · sm · 0.12em）应用到 8 个页面（Home kicker+5 section label / Jiayi / Yan / Works / Archive / Heritage / Search / Reader），移除 9 处本地重复规则；`.hfm-status`（StateLabel，仅映射现有 ContentStatus）统一 Archive + EvidenceExplorer 徽标。
> - **节奏对齐**：AboutView section 间距 space-8 → space-12，与全站 section rhythm 一致。
> - **审计确认**：CTA/link/status/source-evidence 层级跨页一致（Home 已统一 home-cta；研究端 citation 色 eyebrow 保留局部语义）；zero-lift shadow、克制 radius、reduced-motion、focus-visible 全站保持。
> 验证：typecheck ✓ · lint 0 errors ✓ · format:check PASS ✓ · vitest 195/195 ✓ · build ✓ · e2e 67/67 ✓（含 ui13-polish：8 面 375/1920 无溢出 · eyebrow 计算样式（heritage 色/13px/1.56px）· hfm-status token 底色 · 字阶（默认 h1 28px · hero 56px）· 暗色质量 · focus ring）· 不变量静态复核全过 · 等价 whitespace PASS · 0 新增硬编码色

- **scope**：skip-link（UI-02）、全站可见焦点、`prefers-reduced-motion`、对比度复验（muted 提至 ≥4.5:1）、键盘走查（Reader/图谱/抽屉）、axe 扩展至全部新页面（P2-01-AC-04 扩展）、400% 缩放阅读可用。
- **dependencies**：UI-01 起贯穿；收尾全量。
- **files**：全局样式 + 各新组件 + e2e a11y 用例。
- **acceptance**：axe 全站无阻断级违规；键盘走查清单通过；reduced-motion 下功能等价。
- **visual acceptance**：焦点环为 heritage/朱砂系（非浏览器默认闪烁）。
- **regression risk**：低。

## UI-14 — Exhibition Readiness（展厅就绪，仅设计系统）

- **scope**：验证 token 体系可放大档位（间距/字号 scale 整体放大）、深色画布 token 复用、影像优先布局约定、触摸/遥控可达性约定、隐私/授权策略就绪（P0–P3 映射到展陈面）；**不开发独立大屏应用**（延续 DEFERRED）。
- **dependencies**：UI-01。
- **files**：token 文档 + 就绪性核对清单（docs/design 内）。
- **acceptance**：核对清单全项 PASS 或记录阻塞项；无运行时代码要求。
- **visual acceptance**：4K 画布下 2 个代表页（人物页/甲乙经页）预览无像素级断裂（可用缩放模拟）。
- **regression risk**：无（只读核对）。

## UI-15 — Visual QA（视觉验收）

- **scope**：全页面视觉一致性走查（对照本 DAG 各 WP visual acceptance + Design Principles P1–P10）；移动/桌面截图矩阵；不一致修复。
- **dependencies**：UI-01…UI-14。
- **files**：全部受影响文件。
- **acceptance**：每 WP visual acceptance 逐条过；无硬编码 hex/任意样式泄漏；P3 反模式扫描（无卷轴/宣纸/祥云/宫廷元素）。
- **visual acceptance**：六文档定义的气质在全站成立。
- **regression risk**：低——仅样式微调。

---

## 1. 依赖图（简化，§14 链）

```text
UI-00 ─► UI-01 ─► UI-02 ─► UI-04 ─► UI-08 ─► UI-06 ─► UI-10 ─► UI-09 ─► UI-07 ─► UI-11 ─► UI-03
                │            └─► UI-05（组件，供 UI-04/03）         │
                ├─► UI-12（横切，随各 WP）                          └─► UI-12/13 贯穿
                ├─► UI-13（横切，持续）
                └─► UI-14（只读核对）─► UI-15（收尾，依赖全部）
```

批次建议：**B1** = UI-01, UI-02（视觉基线）；**B2** = UI-04（人物）→ UI-08（甲乙经）→ UI-06（其言/文献）串行（各旗舰页视觉语言先后成熟）；**B3** = UI-10（检索）→ UI-09（传承）→ UI-07（阅读器）→ UI-11（研究端）；**B4** = UI-03（首页，由四套成熟视觉语言组合）；**B5** = UI-12/13 收尾 + UI-14 + UI-15。

---

## 2. 数据缺口登记（[DATA-GAP]，均需治理裁决后实施；v2 收敛后口径）

| 缺口 | 相关 WP | 说明 |
| --- | --- | --- |
| `CONTENT_METADATA` | UI-06/08/10 | 部分文件缺年份/作者/版本/来源等元数据，需题录化（其言/论著/论文/证书均适用） |
| 人物公共投影的 assertions/events 字段语义 | UI-04 | person API 返回 `assertions/events: unknown[]`，公共投影字段未定型 |
| 原文/标点双版本、注释数据 | UI-07 | reader resolve 现仅返回 quotation/locator |
| 结构化 locator（卷/篇/页/行） | UI-07 | 现 locator 为字符串 |
| 搜索命中高亮片段 | UI-10 | 现 snippet 为纯文本 |
| `ENTITY_RELATIONS` | UI-04/08/09 | 人物/作品/事件/版本关系可靠提取与结构化 |
| `JIAYI_EDITION_RELATIONS` | UI-08 | 版本脉络 PNG 公开 ≠ 关系结构化完成；版本-版本关系（传本/校注链）建模保持开放 |
| 甲乙经知识图谱投影 | UI-08 | 图谱数据与公共投影需治理 |
| 首页各叙事区内容（身份/评价/共建文案） | UI-03 | 需内容化（可先由 Assertion/内容批次供给） |
| 其言四篇内容准入 | UI-06 | 内容源 `hfmzl/皇甫谧/其言/其言.docx`；未准入前 UI 以空态呈现 |
| 其传/后论.docx 内容准入 + 电影转码 | UI-04 | 传记/后世论述结构化；2 部 mpg 转码与播放资产 |
| 证书媒体类别 | UI-09 | media 类别扩展 `certificate`（证书展墙）或归属 other，须治理裁决 |
| 传承人物档案建模（含 generation_title） | UI-09 | `zzcl/` 档案（荣誉/资质/学术兼职/成果/媒体/师承/工作室）建模为 HeritagePersonProfile 并关联 HeritageProject |
| `PRIVACY_REVIEW` | UI-09/UI-02 | zzcl 含证书编号/签字/名单/联系方式/身份证明等 P2 敏感信息；生成 public derivative 脱敏；法人证照/考评员名单/不动产证明（P3）不进入公共投影 |

**已关闭/移除（v2）**：

- `HERITAGE_GENERATION` → **CLOSED**（刘君奇 = 第六代名医，客户正式确认，进入内容模型）
- RIGHTS / 版权核验 / R0–R3 / 版权 fail-closed → **REMOVED_FROM_DEVELOPMENT_BLOCKERS**（客户授权，见 HFM-ASSET-PRESENTATION-POLICY.md）

> 材料审阅与展示策略（授权 + 隐私 P0–P3）见 `HFM-CONTENT-ASSET-MAP.md` 与 `HFM-ASSET-PRESENTATION-POLICY.md`。

## 3. 验收纪律

- 每个 WP 完成后：typecheck + lint + test + build（`pnpm check` 对应前端子集）+ 相关 e2e。
- 视觉验收由设计评审对照 P1–P10 与 visual acceptance 进行；"好看"类主观项一律转为可检查条目。
- 任何 WP 不得触碰 Phase-2 正式基线提交或 Governance 文档。
