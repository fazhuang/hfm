# HFM 架构边界（v0.1）

Status: Draft · Version: 0.1 · Last updated: Phase 0

## 目的与范围

本文档定义 HFM 的**架构边界（Boundaries）**——即系统内部与外部的逻辑划分、依赖方向与数据流契约。

本版本**不包含**：

- 数据库表设计
- 具体技术选型（框架、中间件、云服务）
- 模块内部实现细节
- API 定义

以上内容在后续版本或独立文档中定义。

## 边界总览

HFM 顶层边界：

```
HFM
├── Public Portal              # 公众门户：展示、浏览、检索、媒体呈现
├── Content & Research Workbench  # 内容与研究工作站：编辑、研究、治理
├── Publication                # 发布层：快照、投影、版本化发布
├── Domain                     # 领域层：领域模型与业务规则
├── Evidence & Provenance      # 证据与溯源：来源、证据链、引用
├── Media & Rights             # 媒体与版权：媒体资产、权利治理
├── Teaching                   # 教学：教学辅助、课程化内容
├── Identity & Access          # 身份与访问：认证、授权、RBAC
└── Shared Infrastructure      # 共享基础设施：搜索、存储、日志、消息等
```

## 核心数据流契约

### Research Data → Publication → Public Portal

数据**不允许**从 Research Data 直接流向 Public Portal。

```
Research Data
      ↓ editorial decision
Publication
      ↓ snapshot/projection
Public Portal
```

- **Research Data**（研究数据）属于 Content & Research Workbench / Evidence & Provenance 边界；
- 任何内容进入 **Publication** 必须经过**编辑决策（editorial decision）**；
- **Public Portal** 只消费 Publication 产生的**快照 / 投影（snapshot / projection）**，不直接读写研究数据；
- 编辑中的草稿、未发布研究数据对 Public Portal 不可见。

### 内部依赖方向

- 上层边界可依赖下层边界，下层不得反向依赖上层；
- Domain、Evidence & Provenance 为底层核心，不依赖任何展示或入口边界；
- Identity & Access、Shared Infrastructure 为横切边界，仅提供能力，不承载业务规则。

## 与 HFB 的集成边界

HFM 与 HFB 之间只允许通过 **Migration / Adapter / Reuse** 边界集成：

```
HFB
 ↓
Migration / Adapter / Reuse
 ↓
HFM
```

**禁止**：

```
HFM runtime
 ↓
直接依赖 HFB runtime
```

- HFM 不继承、不调用 HFB 的运行时；
- HFB 资产（数据、能力、研究成果）以**迁移产物、适配器、复用模块**的形式进入 HFM；
- 任何进入 HFM 的 HFB 资产必须经过 REUSE / EXTEND / ADAPT / DEPRECATE / NEW 裁决（见 ADR-0001 与 HFB Asset Reuse Matrix）。

## 边界责任（简表）

| 边界 | 职责 | 不允许 |
| --- | --- | --- |
| Public Portal | 公众展示、检索、媒体呈现 | 直接读写研究数据 |
| Content & Research Workbench | 编辑、研究、治理、证据链维护 | 绕过 Publication 直接发布 |
| Publication | 编辑决策、快照、投影、版本化发布 | 依赖 Public Portal |
| Domain | 领域模型与业务规则 | 依赖任何边界 |
| Evidence & Provenance | 来源、证据、引用、溯源 | 与媒体权利混同 |
| Media & Rights | 媒体资产、权利治理 | 绕过 Rights 输出受保护内容 |
| Teaching | 教学辅助、课程化内容 | 直接访问未授权研究数据 |
| Identity & Access | 认证、授权、RBAC | 承载业务规则 |
| Shared Infrastructure | 搜索、存储、日志、消息等 | 依赖业务边界 |

## 非目标（Non-Goals）

- 本版本不定义数据库表、物理部署拓扑或具体技术栈；
- 本版本不裁决具体 HFB 资产的去留（该工作在 HFB Asset Reuse Matrix 中进行）；
- 本版本不定义 API 契约。
