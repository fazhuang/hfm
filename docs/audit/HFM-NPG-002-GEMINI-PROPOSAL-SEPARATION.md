# HFM NPG-2 — Gemini Proposal Requirement / Design Separation

Date: 2026-08-29
Authority precedence: client-confirmed requirements in this NPG task override AI proposals and repository plans.

## 1. Evidence boundary

The original Gemini proposal artifact was **NOT FOUND** in the HFM baseline or HFB snapshot. HFB contains `GEMINI_PRODUCT_REVIEW_PROMPT.md` and `docs/09-prompts/Gemini_UI_Academic_Review.md`, but both are review prompts, not the proposal described by this task. Searches for its distinctive items (`8周`, `720全景`, `WebXR`, `虚拟针灸`, `按病寻穴`, `推荐主配穴`) returned no proposal document. Therefore this is a complete audit of the A–R items enumerated by the client in the NPG instruction, but not a claim that every sentence of the absent original proposal has been audited.

Classification vocabulary:

- **CONFIRMED_REQUIREMENT** — directly stated by the client.
- **DERIVED_REQUIREMENT** — necessary product implication, implementation-neutral.
- **DESIGN_OPTION** — one possible implementation or presentation.
- **DEFERRED** — explicitly outside current mandatory acceptance.
- **REJECTED** — conflicts with the confirmed current boundary.
- **NEEDS_DECISION** — plausible but not authorized or sufficiently defined.

## 2. Separation matrix

| Item | Proposal element | Classification | Customer/derived need retained | Design content separated | Risk / condition |
| --- | --- | --- | --- | --- | --- |
| A | 四大业务模块 | DERIVED_REQUIREMENT | 人物档案、文献思想、《针灸甲乙经》知识库、非遗传承可由 confirmed goals/assets组织为四域 | 页面树、菜单、数据库边界仍待设计 | 四域是分析框架，不自动成为四个系统或微服务 |
| B | 3D 人物 | DEFERRED | 参观者需要人物文化展示 | 3D 模型、动作、引擎均为远期选项 | 客户明确非当前必验收；需资产、性能、无障碍替代方案 |
| C | VR / 720 全景 | DEFERRED | 可能服务远期展陈 | 720 摄影、VR 导览、头显支持均未确认 | 场馆、设备、内容与拍摄权利未知 |
| D | WebXR | DEFERRED | 无当前必要客户需求 | WebXR 是 C 的技术选项 | 不得因 VR 设想锁定浏览器 XR 技术 |
| E | 展厅大屏 | NEEDS_DECISION | 示范中心可能有线下展示场景，但客户未明确设备 | 大屏布局、分辨率、播放控制是设计问题 | 需设备、网络、运维、值守、无障碍和离线需求 |
| F | 触控模式 | NEEDS_DECISION | 若存在触控终端则可能需要 | 专用触控 UI 与普通响应式页面并非同一验收物 | 需设备尺寸、操作距离、输入方式和现场测试 |
| G | Elasticsearch | DESIGN_OPTION | 全文/聚合检索能力可能必要 | 搜索引擎产品不属于客户需求 | 先证明 PostgreSQL 搜索不足并给出语料规模、中文分词、相关性与 SLA |
| H | Neo4j | DESIGN_OPTION | 传承关系与研究关系需要可表达 | 图数据库不是“关系展示”的必然方案 | HFM frozen Core 将 Graph DB/Neo4j列为 future option；先验证关系查询需求 |
| I | MinIO | DESIGN_OPTION | 图片、证书、扫描件需要受控对象存储能力 | MinIO 只是 S3-compatible 实现之一 | 需容量、备份、权限、公开派生图与原件隔离需求 |
| J | WebSocket | DESIGN_OPTION | 未确认实时协作或实时推送需求 | WebSocket 是协议选项 | 普通检索、阅读、后台审核可先用请求/响应；流式 AI 也未授权 |
| K | ECharts / D3 | DESIGN_OPTION | 时间线、谱系、统计可能需要可视化 | 两库均非客户要求，也不应默认同时引入 | 先定义图表、交互、移动端和可访问替代文本 |
| L | 原文阅读器 | DERIVED_REQUIREMENT | 客户有《针灸甲乙经》版本，且目标含教学与研究；需要可定位阅读版本内容 | 具体双栏、影像、OCR、IIIF、校勘 UI 待决定 | 取决于实际数字化文件、版权、章节/页码和校勘状态 |
| M | 全文检索 | DERIVED_REQUIREMENT | “数字知识库 + 汇聚研究成果 + 服务研究”必然要求可发现内容 | 引擎、索引结构、向量检索均待裁决 | 必须区分元数据搜索、全文搜索、版本内检索和研究后台搜索 |
| N | 传承谱系 | CONFIRMED_REQUIREMENT | 客户明确要求展示针灸传承脉络 | 树、时间线、网络图或叙事卡片均为设计选项 | 节点、关系、异说、完整性与发布授权尚无证据 |
| O | “按病寻穴” | NEEDS_DECISION | 可被重新定义为历史文献中的病证—穴位检索 | 若按当代疾病给出可操作穴位，已跨入医疗产品语义 | 当前仅允许数字人文检索框架；需明确输入、输出、免责声明和审核 |
| P | “推荐主配穴” | REJECTED | 无 confirmed customer need | 治疗推荐、主配穴组合和个体化建议不属于当前平台 | 高医疗边界风险；当前不得成为临床决策支持。未来另案需医学、法律、责任和验证治理 |
| Q | 8 周工期 | NEEDS_DECISION | 客户需要可执行排期，但未确认 8 周 | 8 周是估算，不是需求 | 资产数量/权利/数字化、双层架构、验收资源均未知，无法事实支持 |
| R | 技术栈绑定 | DESIGN_OPTION | 系统需可维护、可验收 | FastAPI/Vue/PostgreSQL等既有技术事实可作为候选，不构成客户强制绑定 | 最终栈必须在 Scope、复用和规模裁决后冻结；Phase 1 未授权 |

## 3. Medical product boundary

Current HFM positioning is a **digital-humanities, teaching, and research platform**, not a clinical decision-support system.

Allowed direction at this stage:

- retrieve and cite what a historical text says about a disease term, meridian, acupoint, or method;
- present variant readings, provenance, historical context, and scholarly interpretation;
- label material as historical/research/education content and preserve the source chain.

Rejected current behavior:

- recommending treatment for a person or symptom;
- ranking “main and auxiliary acupoints” as a treatment plan;
- implying efficacy, diagnosis, dosage, contraindication clearance, or individualized clinical suitability.

“按病寻穴” is only potentially admissible after the client chooses a strictly historical retrieval meaning. Any treatment-advice semantics changes the product category and requires a separate authorization and compliance program.

## 4. Technology facts vs proposal

At HFM `0167b170`, PostgreSQL/SQLAlchemy core models are implemented; Elasticsearch, Redis, MinIO, Neo4j, WebSocket, Three.js, WebXR, ECharts, and D3 are not HFM product dependencies. The frozen HFM documents explicitly treat Graph DB/Neo4j/Elasticsearch as future or conditional options.

At HFB `03755b57`, Elasticsearch, Redis, and MinIO clients are dependencies; Neo4j and AI packages are optional extras; the Vue frontend uses `vis-network`, not ECharts/D3/Three.js/WebXR. These are HFB implementation facts, not HFM requirements.

## 5. Audit finding

The proposal is useful as an option inventory, but only the transmission lineage goal is directly customer-confirmed among the feature forms above. Reader and full-text discovery are implementation-neutral derived needs. Immersive features are deferred; the stack remains a decision; clinical recommendation is outside the current boundary.

**Blocking evidence gap:** the original Gemini proposal must be supplied before claiming a true line-by-line proposal audit.
