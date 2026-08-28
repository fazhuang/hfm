# HFM Gemini 原始实现提案归档 v1（Gemini Original Implementation Proposal）

Status: GOVERNANCE INPUT · Date: 2026-08-29 · Branch: `governance/next-phase-authorization`

## 治理头（Governance Header）

```text
Document Type:
AI-GENERATED DESIGN PROPOSAL

Authority:
L3（设计/交付/技术提案，非客户事实）

Binding:
NO

Customer Approval:
NOT ESTABLISHED

Implementation Authorization:
NONE

Purpose:
作为需求/设计分离与未来 ADR 评审的参考输入。
```

## 归档说明（Evidence Boundary）

依据 `docs/audit/HFM-NPG-002-GEMINI-PROPOSAL-SEPARATION.md` 审计结论：

- **原始 Gemini 提案工件在 HFM 基线或 HFB 快照中未找到**（HFB 仅含 `GEMINI_PRODUCT_REVIEW_PROMPT.md` 与 `docs/09-prompts/Gemini_UI_Academic_Review.md`，均为评审提示而非本提案）。
- 本归档为对客户/审计指令中列举的 A–R 项及其审计分类的**忠实枚举记录**，不代表原提案逐句可审计。
- 原始提案若日后提供，应在本文件之后另行归档并逐句对账。

## 提案枚举项（A–R，按 NPG-002 审计记录忠实保留）

| 项 | 提案元素 | 审计分类 | 保留的客户/派生需要 | 分离出的设计内容 | 风险/条件 |
| --- | --- | --- | --- | --- | --- |
| A | 四大业务模块 | DERIVED_REQUIREMENT | 人物档案、文献思想、《针灸甲乙经》知识库、非遗传承可组织为四域 | 页面树、菜单、数据库边界待设计 | 四域是分析框架，不自动成为四个系统/微服务 |
| B | 3D 人物 | DEFERRED | 参观者需要人物文化展示 | 3D 模型、动作、引擎均为远期选项 | 客户明确非当前必验收 |
| C | VR / 720 全景 | DEFERRED | 可能服务远期展陈 | 720 摄影、VR 导览、头显支持未确认 | 场馆/设备/内容/拍摄权利未知 |
| D | WebXR | DEFERRED | 无当前必要客户需求 | WebXR 是 C 的技术选项 | 不得因 VR 设想锁定浏览器 XR 技术 |
| E | 展厅大屏 | NEEDS_DECISION | 示范中心可能有线下展示场景 | 大屏布局、分辨率、播放控制是设计问题 | 需设备/网络/运维/无障碍/离线需求 |
| F | 触控模式 | NEEDS_DECISION | 若存在触控终端则可能需要 | 专用触控 UI 与响应式页面非同一验收物 | 需设备尺寸、输入方式与现场测试 |
| G | Elasticsearch | DESIGN_OPTION | 全文/聚合检索能力可能必要 | 搜索引擎产品不属于客户需求 | 先证明 PostgreSQL 搜索不足 |
| H | Neo4j | DESIGN_OPTION | 传承关系与研究关系需可表达 | 图数据库不是“关系展示”的必然方案 | HFM frozen Core 将 Graph DB/Neo4j 列为 future option |
| I | MinIO | DESIGN_OPTION | 图片/证书/扫描件需受控对象存储能力 | MinIO 只是 S3-compatible 实现之一 | 需容量、备份、权限、隔离需求 |
| J | WebSocket | DESIGN_OPTION | 未确认实时协作/推送需求 | WebSocket 是协议选项 | 普通检索/阅读/后台审核可用请求/响应 |
| K | ECharts / D3 | DESIGN_OPTION | 时间线、谱系、统计可能需要可视化 | 两库均非客户要求 | 先定义图表、交互、移动端与无障碍替代 |
| L | 原文阅读器 | DERIVED_REQUIREMENT | 客户有《针灸甲乙经》版本，教学/研究需可定位阅读 | 双栏/影像/OCR/IIIF/校勘 UI 待决定 | 取决于文件、版权、章节/页码与校勘状态 |
| M | 全文检索 | DERIVED_REQUIREMENT | “数字知识库+汇聚+服务研究”要求可发现内容 | 引擎、索引结构、向量检索待裁决 | 区分元数据/全文/版本内/后台搜索 |
| N | 传承谱系 | CONFIRMED_REQUIREMENT | 客户明确要求展示针灸传承脉络 | 树/时间线/网络图/叙事卡片均为设计选项 | 节点、关系、异说、完整性与授权无证据 |
| O | “按病寻穴” | NEEDS_DECISION | 可重定义为历史文献中的病证—穴位检索 | 若按当代疾病给可操作穴位则跨入医疗产品语义 | 当前仅允许数字人文检索框架 |
| P | “推荐主配穴” | REJECTED | 无 confirmed customer need | 治疗推荐/主配穴组合/个体化建议不属于当前平台 | 高医疗边界风险；当前不得成为临床决策支持 |
| Q | 8 周工期 | NEEDS_DECISION | 客户需要可执行排期，但未确认 8 周 | 8 周是估算，不是需求 | 资产/数字化/双层架构/验收资源未知 |
| R | 技术栈绑定 | DESIGN_OPTION | 系统需可维护、可验收 | FastAPI/Vue/PostgreSQL 等是候选，不构成客户强制绑定 | 最终栈须在 Scope、复用和规模裁决后冻结 |

## 不得提升为客户需求的技术项（明确禁止提升）

下列技术/交付元素为提案或选项，**不得**因本归档而成为客户需求：

```text
Three.js
WebGL
WebXR
Neo4j
Elasticsearch
MinIO
WebSocket
ECharts
D3.js
720 VR
8-week schedule
```

## 医学产品边界（保留自 NPG-002 §3）

当前 HFM 定位为数字人文 / 教学 / 研究平台，非临床决策支持系统。允许检索与引用历史文本中的病证/经络/穴位/刺灸法原文并保留证据链；**拒绝**治疗推荐、主配穴排序、疗效暗示、诊断/剂量/禁忌/个体化临床适用性语义。“按病寻穴”仅在客户选择严格历史检索语义后才可能准入。

## 交叉引用

- 分离审计：`docs/audit/HFM-NPG-002-GEMINI-PROPOSAL-SEPARATION.md`
- 技术事实（0167b17 / 03755b5 依赖状态）：见 NPG-002 §4
