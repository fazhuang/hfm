# HFM UI/UX 现状审计 — Design Audit

Status: DESIGN INPUT（只读审计，非治理文档，不修改任何正式 Scope/Baseline）
Date: 2026-08-31 · 范围: `apps/frontend` 只读审计 + 首页/人物页/Reader/研究工作台专项审计
审计基线（保持不变）:

- Phase-2 Governance Baseline: `7fa7c4f60244daa6999e377d08502bde522c56b2`
- Frontier-3 Acceptance Baseline: `cd8176dac880f4229a2979aca51b6d5e8d638036`
- Formal Phase-2 Completion Baseline: `50572a4eba453c3eafa396e48e632a6ac49db73e`

本审计未修改任何运行时代码、数据模型、API、migration 或正式治理文档。

---

## 0. 审计范围与方法

| 项 | 说明 |
| --- | --- |
| 审计对象 | `apps/frontend`（Vue 3 + Vite + Pinia + vue-router），只读 |
| 事实来源 | 客户需求归档（CR-001…CR-010）、Phase-2 Scope Register / DAG / Acceptance Contract、Core Domain Scope、架构边界、现行前端代码与测试 |
| 前端规模 | 15 views / 3 layouts / 6 components / 1 token 文件，共约 2,600 行 |
| 后端能力面 | `/api/v1/public/*`（11 个端点）、`/api/v1/research/*`（30 个端点）、`/api/v1/admin/*` |
| 判定分类 | KEEP（保留）/ REFINE（结构正确仅需视觉优化）/ REDESIGN（重新设计）/ REMOVE（不符合产品性质）/ MISSING（客户需求要求但当前不存在） |

---

## 1. 技术栈审计

| 层 | 现状 | 判定 |
| --- | --- | --- |
| 框架 | Vue 3.5 + Vite 6 + Pinia 2.3 + vue-router 4.5 | KEEP |
| UI 组件库 | 无（原生 + scoped CSS） | KEEP（不引入重型库；按需扩展） |
| 样式方案 | CSS custom properties + scoped style | KEEP（机制正确，值需重设计） |
| 图标 | 无图标系统 | MISSING |
| 字体 | 仅 `system-ui` 栈，无中文显示字体、无古籍衬线 | MISSING |
| 测试 | Vitest + Playwright + axe-core（P2-01/02 AC 通过） | KEEP |
| 暗色模式 | `useTheme` 切换 `.dark` class，但 **tokens.css 无任何暗色覆盖**（切换无视觉效果，功能实际失效） | REDESIGN |

---

## 2. 页面 / 路由清单

| Route | View | 布局 | 现状摘要 | 判定 |
| --- | --- | --- | --- | --- |
| `/` | HomeView | Public | Hero（合规声明式文案）+ 统计卡片 + 著作/人物/公开内容三个平铺列表 | REDESIGN |
| `/reader` | ReaderView | Public | 章节 TOC（左栏）+ 正文面板 + 上/下一段分页 + 原始定位符字符串 | REDESIGN（体验）/ REFINE（结构） |
| `/search` | SearchView | Public | 单关键词输入 + kind 标签结果列表 | REFINE |
| `/heritage` | HeritageView | Public | 传承谱系平面列表（非树/图） | REFINE |
| `/library` | MediaLibraryView | Public | 分类 tabs + 关键词过滤 + 卡片网格 + 分页 | REFINE |
| `/persons/:id` | PersonDetailView | Public | 姓名/拼音/字/号/朝代 + 影视资料列表；**无生平、无时间轴、无著作、无证据** | REDESIGN |
| `/works/:id` | WorkDetailView | Public | 标题/朝代/分类 + 版本列表 | REFINE |
| `/login` | LoginView | Public | 用户名/密码表单 | REFINE |
| `/denied` | DeniedView | Public | 单行提示 | REFINE |
| `/research` | ResearchHomeView | Research | 仅一个演示导出面板 | REDESIGN |
| `/admin` | AdminHomeView | Admin | 标题 + "发布演示条目"按钮 | REDESIGN |
| `/admin/audit` | AuditLogView | Admin | 对账结果 + 审计条目列表（含硬编码 hex 徽标色） | REFINE |
| — | App.vue | — | 仅 RouterView | KEEP |

路由守卫（publicOnly / requiresAuth / deny-by-default）与 fail-closed 公共 API 客户端为正式验收资产：**KEEP，不得弱化**。

---

## 3. 组件清单

| 组件 | 现状 | 判定 |
| --- | --- | --- |
| LoadingState / ErrorState / EmptyState | 纯文本居中提示，无骨架屏、无图标 | REFINE（保持语义，视觉升级） |
| LineageTree | 平面列表，且 **未被 HeritageView 使用**（重复实现） | REMOVE 或整合 |
| ExportPanel | 内嵌硬编码演示记录（《针灸甲乙经》校勘笔记） | REMOVE 演示脚手架，重建为真实导出流程 |
| 布局三件套（Public/Research/Admin） | 顶部条 + 内容 + 单行页脚 | REFINE |

---

## 4. 设计 Token 审计（tokens.css，共 40 行）

| 域 | 现有 | 问题 |
| --- | --- | --- |
| 颜色 | bg `#fafaf9` / surface `#ffffff` / border `#e7e5e4` / text `#1c1917` / muted `#78716c` / **accent `#7c3aed`（紫）** / danger `#b91c1c` | 紫色强调与东方人文、权威数字人文气质无关（SaaS 中性模板感）；无 heritage/evidence/citation/warning/success 语义色；无暗色变体 |
| 字体 | 仅 `--hfm-font-sans: system-ui` | 无 display、无长文阅读、无古籍、无数字/引用专用角色；系统无衬线不承担"古籍"阅读 |
| 字号 | xs/sm/base/lg/xl（0.75–1.5rem） | 无 display 级、无 long-form 舒适字号策略、无行高/字距 token |
| 间距 | 0.25/0.5/0.75/1/1.5/2rem（8 档） | 缺少大间距档（3/4/6/8/12/16rem），页面节奏单一 |
| 圆角 | sm 4 / md 8 / lg 12px | 可用；文化平台应更克制（见提案） |
| 阴影 | 无 token（未使用） | 缺失即"零浮起"——方向正确，需显式定义层级规则 |
| 断点 | 480 / 768 / 1024 | 缺 ≥1440 档；`useViewport` 只到 lg |
| 暗色 | 无 | 见 §1 |

**结论：token 机制 KEEP，token 值 REDESIGN。**

---

## 5. 二十项检查清单（KEEP / REFINE / REDESIGN / REMOVE / MISSING）

### 5.1 清单明细

1. **页面 inventory** — 12 个有效页面；缺首页叙事结构、人物旗舰页、史料馆展陈、知识探索、About。→ MISSING/REDESIGN
2. **route inventory** — 路由与守卫正确。→ KEEP
3. **layout** — 三套 shell 结构正确；品牌区无识别度、导航未覆盖完整 IA、页脚缺失署名与合规信息。→ REFINE
4. **components** — 状态组件模式正确；LineageTree 重复；无表格/表单/时间轴/图组件。→ REFINE（+MISSING 组件族）
5. **design tokens** — 机制正确、值不合格（紫 accent、无暗色、无语义色）。→ REDESIGN
6. **typography** — 无层级系统、无中文显示字体、无古籍字体。→ MISSING（整体建立）
7. **colors** — 单调中性 + 单一紫；无 heritage/evidence/citation 语义色。→ REDESIGN
8. **spacing** — 基础档位存在，无大档位与节奏规范。→ REDESIGN
9. **responsive breakpoints** — sm/md/lg 存在且有 e2e 矩阵（P2-01-AC-05 通过）；缺 xl/2xl 与平板专项。→ REFINE
10. **navigation** — 公共导航仅 5 链接，未覆盖"文献/甲乙经/史料馆/研究/关于"；无移动端抽屉/汉堡。→ REDESIGN（注：客户已于 2026-08-31 强制主导航=5 链接，见 §12 客户导航补充）
11. **cards** — 卡片大量使用 1px 边框 + 白底，无层级区分；"SaaS 悬浮卡片"未出现（好）。→ REFINE
12. **tables** — 无表格组件（Admin/研究数据用列表代替）。→ MISSING
13. **reader** — 结构存在；缺证据/引文/版本/注释/阅读模式/深链接。→ REDESIGN（见 §8）
14. **search** — 单输入 + 结果列表；无 facets/filters/高亮/分面计数。→ REFINE
15. **forms** — 仅登录表单；无研究/管理录入表单系统。→ MISSING（研究端）
16. **loading** — 纯文本，无骨架屏/进度语义。→ REFINE
17. **empty states** — 语义正确（有 label），无引导动作。→ REFINE
18. **error states** — 语义正确（role=alert），无重试/恢复引导。→ REFINE
19. **accessibility** — axe 通过（P2-01-AC-04）；有 aria-labelledby/visually-hidden/focus-trap；**缺 skip-link、可见 focus 样式、prefers-reduced-motion、对比度审计（muted #78716c 在浅底约 4.6:1，临界）**。→ REFINE（部分）
20. **visual inconsistencies** — 直接硬编码 hex（AuditLogView 徽标）、Hero 文案与产品气质不符、Reader 定位符裸字符串、首页三个列表无视觉叙事。→ REDESIGN（散点）

### 5.2 分类计数

| 分类 | 计数 | 代表项 |
| --- | --- | --- |
| **KEEP** | 9 | token 机制、路由守卫、公共 API fail-closed 客户端、useViewport、useFocusTrap、状态组件模式、visually-hidden、媒体库网格/分页交互、axe 基线 |
| **REFINE** | 11 | 三套 layout shell、SearchView、MediaLibraryView、HeritageView（列表→真树）、WorkDetailView、AuditLogView、登录/无权限页、页面标题规范、卡片层级、loading/empty/error 视觉 |
| **REDESIGN** | 9 | HomeView、PersonDetailView、颜色系统、字体系统、暗色模式、公共导航、页脚、研究工作台首页、Hero 文案 |
| **REMOVE** | 7 | 紫 accent 作身份色、Hero 合规声明式文案、Reader OCR 演示免责声明入 UI、ExportPanel 硬编码演示记录、"发布演示条目"按钮、AuditLog 硬编码 hex、未使用且重复的 LineageTree |
| **MISSING** | 24 | 生平/传记 UI、时间轴组件、身份/精神/历史评价区、相关人物/地点/证据/研究区、首页 IDENTITY/LIFE/WORKS/JIAYI JING/ARCHIVE/KNOWLEDGE/HERITAGE/RESEARCH/CO-CONSTRUCTION 九区、阅读器证据层、深链接/复制引用、搜索 facets、研究端检索与证据链、表格、表单系统、骨架屏/404/全局错误边界、skip-link/focus/reduced-motion、暗色 token、中文字体策略、图标系统、肖像/图像策略、关于页、政校共建页脚、史料馆展陈、关系图谱可视化、展览就绪 token |

---

## 6. 首页专项审计（10 区判定）

| 区 | 必要性 | 内容目标 | 用户目标 | 信息密度 | 推荐组件 | 推荐层级 | 当前状态 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 01 HERO | 必须 | 皇甫谧核心认知 + 一句话权威定义 + 入口气质 | 3 秒建立"权威人文平台"认知 | 低 | Hero band（大标题/副题/CTA，非大图堆砌） | 最高 | 存在但为合规声明式文案 → REDESIGN |
| 02 IDENTITY | 必须 | 医学家/文学家/史学家/学者多维身份 | 快速建立人物轮廓 | 低 | 身份徽章行 + 一句定义 | 高 | MISSING |
| 03 LIFE | 必须 | 生平时间轴入口（求学悟道→拒仕治学→久病研医→著书传世） | 激发浏览欲 | 中 | 横向/纵向时间轴摘要 + 链接人物页 | 中高 | MISSING |
| 04 WORKS | 必须 | 核心著作与文献 | 发现著作并进入阅读 | 中 | 著作卡（题名/朝代/版本数） | 中 | 存在为平铺列表 → REDESIGN |
| 05 JIAYI JING | 必须（核心 IP） | 《针灸甲乙经》知识入口 | 一键进入结构化阅读 | 中 | 专题入口卡 + 篇章结构预览 | 高（视觉锚点） | MISSING |
| 06 ARCHIVE | 必须 | 数字史料馆藏 | 浏览馆藏 | 中 | 分类网格（古籍/史料/影像） | 中 | 仅 /library 存在 → 需入口整合 |
| 07 KNOWLEDGE EXPLORATION | 建议（分阶段） | 人物—事件—地点—著作—知识关系 | 自由探索 | 中高 | 关系图/关联卡簇（渐进披露） | 中 | MISSING（依赖图数据 UI，非本期阻塞） |
| 08 HERITAGE | 必须 | 非遗活态传承展示 | 感受"活态" | 中 | 传承谱系缩略 + 活动影像 | 中 | 有 /heritage 路由但未入首页 → MISSING |
| 09 RESEARCH | 必须 | 学术研究入口 | 研究者发现研究工作台 | 低 | 低调入口（勿做成登录墙） | 低-中 | MISSING |
| 10 CO-CONSTRUCTION | 必须 | 甘肃医学院 × 灵台县相关公共部门共建成果 | 建立政校共建信任 | 低 | 署名带/页脚区（CR-001/006 署名规范） | 低 | MISSING |

---

## 7. 人物档案页专项审计

目标结构（提议） vs 现状：

| 目标模块 | 现状 | 数据可用性（后端） | 判定 |
| --- | --- | --- | --- |
| 人物视觉识别（姓名/215—282/字/号） | 有姓名+拼音+字/号/朝代（无生卒年展示） | person API 有 dynasty；生卒年在 Assertion/Event 层 | REFINE |
| 核心身份 + 一句话权威定义 | 无 | 需内容化（Assertion 层可承载） | MISSING |
| 人物摘要 | 无 | person API `assertions/events` 字段存在（UI 未消费） | MISSING |
| 生平时间轴（时间/事件/地点/人物/史料来源） | 无 | `events` + `event_relation` + Evidence 链 API 存在 | MISSING（UI-05） |
| 人生阶段（求学悟道/拒仕治学/久病研医/著书传世） | 无 | 内容/断言组织 | MISSING |
| 思想/精神 | 无 | 内容/断言 | MISSING |
| 著作 | 无（人物页只列影视） | works API（可经关联查询） | MISSING |
| 历史评价 | 无 | 内容/断言 | MISSING |
| 相关人物（师承/亲属/关联） | 无 | heritage relations + event_relation | MISSING |
| 相关地点 | 无 | Event.location / Entity | MISSING |
| 史料证据（Evidence 可见） | 无 | evidence-chain（研究端）→ 公共投影需出版层 | MISSING |
| 研究成果 | 无 | research 层 | MISSING |
| 影视/媒体 | 有（前 8 条） | media API | KEEP（并入档案媒体区） |

**人物页应成为 HFM 标志性页面（UI-04）；任何一条人物信息都应可继续进入 事件/地点/文献/原文/版本/Citation。**

---

## 8. 古籍 Reader 专项审计

| 能力 | 现状 | 判定 |
| --- | --- | --- |
| 原文阅读宽度 | 面板随栏宽全宽，无 `max-width` 阅读度量 | REDESIGN |
| 字号/行距 | 1rem / 1.9 行高（方向正确） | REFINE（需阅读模式档位） |
| 篇章导航 | 左栏章节按钮（扁平，无卷/篇层级） | REFINE |
| 页码/页序 | "第 N 页"（passage order，演示语义） | REFINE（需结构化 locator 展示） |
| 卷/篇结构 | 仅 chapter 一层 | REFINE |
| 原文/现代标点切换 | 无 | MISSING |
| 注释 | 无 | MISSING |
| Source / Citation / Version / Evidence | 仅显示裸 locator 字符串 | MISSING（核心缺口，P8 EVIDENCE VISIBLE） |
| 搜索命中/锚点/深链接 | 无（无 `#locator` 路由） | MISSING |
| 复制引用 | 无 | MISSING |
| 左右栏布局 | 260px TOC + 面板 | KEEP（骨架） |
| 阅读模式/全屏 | 无 | MISSING |
| 临床边界 | 无推荐/诊疗面（P2-03-AC-04 通过） | KEEP（保持） |

**Reader 不应变成 CMS article 页：阅读体验 + 证据层 + 结构化定位是核心专业能力。**

---

## 9. 研究工作台专项审计

| 能力 | 现状 | 判定 |
| --- | --- | --- |
| 工作台首页 | 仅 ExportPanel 演示 | REDESIGN |
| Search（研究检索，role-scoped） | 无 UI（后端 `/api/v1/research/search` 存在） | MISSING |
| Filters / Facets | 无 | MISSING |
| Result / Source / Evidence / Citation / Version 展示 | 无 | MISSING |
| Entity Relation 导航 | 无 | MISSING |
| Evidence Chain（`/evidence-chain/{citation_id}`） | 无 UI | MISSING |
| 内容管理入口（persons/works/c-terms/heritage/notes CRUD） | 无 UI（后端全存在） | MISSING |
| 导出/打印 | 有（演示面板） | REFINE（接入真实选择流程） |
| 密度要求 | — | 研究端必须高密度、可追溯；**不得为"古风"牺牲效率** |

**公共门户与研究工作台必须明确区分：公众端低认知负担/高视觉叙事；研究端高信息密度/高检索效率/高可追溯性。**

---

## 10. 响应式与展厅能力审计

| 视口 | 现状 | 判定 |
| --- | --- | --- |
| Desktop ≥1440 | 无专项；内容全宽拉伸 | MISSING（xl 档） |
| Laptop 1024–1439 | 存在（lg） | KEEP |
| Tablet 768–1023 | 仅 767px 断点切换列布局；导航无抽屉 | REFINE |
| Mobile <768 | 可用（e2e 验证无横向溢出） | KEEP |
| 触摸目标 | 按钮多为 24–32px 高，未达 44px 建议 | REFINE |

**展厅/大屏（Exhibition）**：本轮不开发独立大屏应用。但设计系统须在未来可扩展到：展厅触摸屏（≥44px 触摸目标、遥控/无鼠标可达）、4K 大屏（间距/字号 token 可放大档位、无固定像素布局假设）、数字展陈（深色画布 token、影像优先布局）、720 全景与 WebGL/WebXR（设计 token 与视图层解耦、资产命名/版权字段已具备 —— 见 Phase-2 ADR-01 Media & Rights）。判定：**当前 token 机制可扩展，但需在 UI-01 建立可放大档位与"画布无关"约定，并在 UI-14 显式验证。**

---

## 11. 总体 Verdict

现行 UI 是**功能性完整、视觉未成形**的工程面：

- 工程正确性高：路由守卫、fail-closed 客户端、状态组件、可访问性基线、响应式矩阵全部通过正式 AC。
- 产品呈现弱：无视觉识别、无叙事层级、无阅读体验、无证据可见性、无研究工作面；紫 accent + 系统字体 + 平铺列表构成"未定稿通用模板"观感。
- 与产品定义的差距：当前 UI 更接近"HFB 换皮 + 功能菜单集合"，未承担"权威文化展示 / 数字人文研究 / 教学辅助 / 非遗传播 / 政校共建"的产品职责。

**总体 verdict：KEEP 工程骨架，REDESIGN 视觉语言与信息架构，系统性补齐 MISSING 能力。**

---

## 12. 客户导航补充要求（2026-08-31，L1 客户事实）

客户明确要求门户主导航**只保留五个链接**，内容组织如下（与客户内容资产目录 `hfmzl/` 一一对应）：

| # | 导航 | 内容范围 | 客户资产目录 |
| --- | --- | --- | --- |
| 1 | 首页 | — | — |
| 2 | 人物（皇甫谧） | 人物档案 | `hfmzl/皇甫谧/其传`、`后论`、`皇甫谧电影` |
| 3 | 其言 | 三都赋、玄守论、释劝论、笃终论 | `hfmzl/皇甫谧/其言`（其言.docx） |
| 4 | 《针灸甲乙经》 | 版本与各版本之间的脉络联系、论著、论文 | `hfmzl/针灸甲乙经/版本及各版本之间脉络联系`、`论著`、`论文` |
| 5 | 皇甫谧针灸非遗的传承 | 证书、非遗资料、传承人物——重点第六代名医 | 非遗证书/传承人资料（CR-005） |

**对审计结论的修订**（仅限 IA/导航相关，不影响 §0–§11 的工程审计事实）：

1. §5.10 导航审计目标从"7 分支 IA"修订为**客户 5 链接**；检索/登录移入 header 工具区，关于平台入页脚（能力不删除）。
2. §6 首页 10 区中的"ARCHIVE/RESEARCH/KNOWLEDGE EXPLORATION"不再作为顶级导航；其能力并入甲乙经区（论著/论文/版本）与传承区（证书/非遗资料）；首页叙事区调整为与 5 链接对应的区块。
3. §7 人物页增加"其传/后论/电影"内容源映射（`hfmzl/皇甫谧/`）。
4. §8 Reader 保持；甲乙经区新增"版本脉络联系"（客户脉络图）与"论著/论文"展陈要求。
5. 新增 MISSING 项：其言区（`/yan`）、甲乙经区（`/jiayi`）、证书展示、传承人物档案页（第六代名医·刘君奇）。
6. 新数据缺口（均须治理裁决后实施）：其言四篇文本准入、版本脉络结构化（JIAYI_EDITION_RELATIONS）、CONTENT_METADATA、ENTITY_RELATIONS、PRIVACY_REVIEW、证书媒体类别。

完整 IA 映射见 `HFM-INFORMATION-ARCHITECTURE.md §0.1/§3`；WP 调整见 `HFM-UI-OPTIMIZATION-DAG.md`。

### 12.1 客户材料审阅与授权结论（2026-09-01，`zzcl/` + `hfmzl/`）

客户材料目录结构与 5 导航同构，审阅与授权结论（详见 `HFM-CONTENT-ASSET-MAP.md` / `HFM-ASSET-PRESENTATION-POLICY.md`）：

1. **`hfmzl/`（620 件）** = 平台内容资产：其传/其言/后论（3 个 docx）、皇甫谧电影（2 部）、甲乙经版本脉络图（PNG）、论著 ≈100 件（古籍版本/校注本/现代版/相关文献）、论文 515 篇。直接支撑导航 2/3/4。
2. **`zzcl/`（68 件）** = 非遗传承申报档案（**第六代名医·刘君奇**——客户正式确认，`HERITAGE_GENERATION` CLOSED）：荣誉/资质/学术兼职/技术成果（含 2007 甲乙经腧穴研究市级科技进步二等奖）/媒体报道（央视《陇脉医承》2025-04-25）/师承教育与工作室（拜师大会 2023-09-26）。直接支撑 FLAGSHIP-03。
3. **UI 方案调整**：三个旗舰页（人物/甲乙经/非遗传承）由真实内容驱动；传承区含传承人物档案页/荣誉认定/学术技术成果/师承教育/工作室/媒体报道/谱系；甲乙经区含版本脉络主视觉 + 历代版本 + 论著四类 + 515 篇论文 BibliographicSearch；其言/人物页内容源明确。
4. **客户授权（取代版权约束）**：客户提供材料统一授权公开，版权退出开发阻塞（RIGHTS/R0–R3/版权 fail-closed 取消，标记 NOT_REQUIRED_FOR_CUSTOMER_PROVIDED_ASSETS）。
5. **隐私独立治理**：P0–P3 模型（HFM-ASSET-PRESENTATION-POLICY §4）；证书编号/签字/名单/联系方式等 P2 生成 public derivative 脱敏；法人证照/考评员名单/不动产证明（P3）不进入公共投影；**不因单字段废弃整份材料**。
6. **新增 MISSING**：传承人物档案页（刘君奇，第六代名医）、证书展墙（media certificate 类别）、其言区、甲乙经区。
7. **新增数据缺口**：`CONTENT_METADATA` / `ENTITY_RELATIONS` / `JIAYI_EDITION_RELATIONS` / `PRIVACY_REVIEW` / 证书类别 / 电影转码（见 DAG §2）；**HERITAGE_GENERATION CLOSED；RIGHTS REMOVED_FROM_DEVELOPMENT_BLOCKERS**。

**未执行**：未入库、未迁移、未发布任何客户材料；材料处理属内容准入实施 WP，不在本设计阶段。
