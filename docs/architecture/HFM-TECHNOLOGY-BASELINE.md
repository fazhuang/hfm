# HFM 技术基线（v1.0）

Status: **Frozen** · Version: 1.0 · Date: 2026-08-27 · Phase 0 — Repository Bootstrap & HFB Asset Reuse Planning

## 目的与范围

本文档定义 HFM 各架构边界的技术基线（Technology Baseline），与 HFB Asset Reuse Matrix v1.0 共同构成 **Frozen Architecture Baseline**。原始 Provisional 基线（提交 `ba4f615`）经 Codex Re-Acceptance（VALIDATED_WITH_CORRECTIONS）修正、候选绑定门禁证明（G14/G15）后获得 **Frozen Eligibility: ELIGIBLE**，由本轮治理提交正式升级为 Frozen（见 `docs/governance/BASELINE-MANAGEMENT.md`）。

**依据**：

- ADR-0001（独立仓库 + Architecture Greenfield + Capability Brownfield）
- HFM-BOUNDARIES-v0.1（九大边界与数据流契约）
- HFD-PHASE0-BASELINE-AUDIT v1.1（HFB 实测证据，HEAD `2d98b610`）
- HFD-PHASE0-DOMAIN-MAP v1.1（领域映射与验证分层）
- HFD-PHASE0-CODEX-REACCEPTANCE（VALIDATED_WITH_CORRECTIONS；技术确定性分类见 §4）

**本版本不定义**：数据库表、API 契约、物理部署拓扑、云厂商选择。

## 冻结语义（Frozen Semantics）

**Frozen 表示**：当前 Phase 0 架构与技术决策已经冻结，可作为后续 Skeleton 和迁移工作的开发输入。

**Frozen 不表示**：

- 所有 Phase 1 功能已实现；
- G1/G2/G3/G4/G7 已完成；
- HFB 代码可以无条件迁移；
- HFM 可以开始业务开发。

## 决策原则

1. **同源复用**：HFM 与 HFB 保持同语言/框架族（Python + FastAPI / Vue 3 + TypeScript），最小化 Port 成本；不因引入新技术而迁移已验证能力。
2. **无 HFB runtime 依赖**：HFM 不得导入、调用 HFB 运行时。HFB 能力仅以 **Port / Extract / Adapt / Migration** 产物进入 HFM（带 Model→Service→API→Test 证据链溯源）。**禁止 HFM runtime → permanent HFB runtime dependency**。
3. **数据继承边界**：HFB 数据仅为 **migration/import source**；HFM 后续建立自己的 canonical model。**禁止**复制 HFB live DB 直接运行；**禁止** HFM 永久共享 HFB production DB。Phase 1 必须为 Entity、Assertion、Evidence、Source、Citation、Version、Publication、Rights、Teaching 定义迁移/导入契约。
4. **条件性基础设施原则**：> Introduce infrastructure only when target requirements or measured scale justify it. Redis、MinIO、Elasticsearch 不得作为一期无条件强制基础设施。
5. **前端不引入 React**：遵循 AGENTS.md 约束；UI 组件资源选择须兼容 Vue 3 面（shadcn/ui 仅作概念基础，React-only 组件不得直接落入 Vue 面）。
6. **边界契约优先**：技术选型服从 HFM-BOUNDARIES-v0.1 的依赖方向（上层可依赖下层，Domain/Evidence & Provenance 不依赖任何边界）。
7. **先冷冻结、后演进**：Frozen 之后任何变更须经 ADR 裁决并升版本号，禁止静默替换。

## Codex 技术确定性分类（CODEX-REACCEPTANCE §9）

| 领域 | 分类 | 条件 / 依据 |
| --- | --- | --- |
| Backend / Frontend / Database / Testing / CI | **JUSTIFIED** | 已验证 HFB 栈与显式 CI 来源 |
| Cache / Queue（Redis） | **JUSTIFIED_WITH_CONDITIONS** | HFB 角色未被独立验证；按实测需要引入 |
| Object Storage（MinIO） | **JUSTIFIED_WITH_CONDITIONS** | G4 媒体需求证明需要；审计环境 MinIO 未运行 |
| Search（Elasticsearch） | **JUSTIFIED_WITH_CONDITIONS** | PG ILIKE MVP 已存在；ES 需目标规模/索引需求 |
| Observability | **UNKNOWN / TO BE DECIDED** | 审计/日志存在；观测栈与运行时 SLO 证据未建立 |
| Auth / RBAC | **JUSTIFIED_WITH_CONDITIONS** | 先 Port 已验证 Auth/RBAC，再实现匿名 Visitor 与 SoD（Phase 1） |
| Export | **JUSTIFIED_WITH_CONDITIONS** | markdown 已验证；PDF/打印/免责声明为新需求 |
| Media Processing | **JUSTIFIED_WITH_CONDITIONS** | 仅为 G4 需要；不选择多余处理平台 |

## 技术基线（按层）

| 层 | 选择 | 分类 | 备注 |
| --- | --- | --- | --- |
| 仓库形态 | pnpm workspaces monorepo（`apps/` + `packages/` + `infra/` + `scripts/` + `tests/`） | JUSTIFIED | 与 HFB 同构（BASELINE §2.1）；对齐九边界布局 |
| 后端 | Python 3.12+ · FastAPI · Pydantic v2 · SQLAlchemy 2.0 async · Alembic | JUSTIFIED | REUSE HFB 栈（§2.1/§3）；UUIDv7 + 软删除模式随迁 |
| 前端 | Vue 3 + TypeScript · Vite · Pinia · vue-router | JUSTIFIED | REUSE HFB 栈（§3）；AGENTS.md 禁止 React 迁移 |
| 数据 | PostgreSQL 16（唯一事实源） | JUSTIFIED | REUSE（§2.2，HFB 64 表 PG 实测运行） |
| 检索 | PostgreSQL ILIKE 为 MVP 基础；Elasticsearch 为**条件性**扩展 | JUSTIFIED_WITH_CONDITIONS | ES 不写成一期强制依赖；按公开检索规模/索引需求引入（§9） |
| 缓存 / 限流 / 队列 | Redis（**条件性**） | JUSTIFIED_WITH_CONDITIONS | HFB 角色未独立验证；按实测需要引入（§9） |
| 对象存储 | MinIO / S3 兼容（**条件性**） | JUSTIFIED_WITH_CONDITIONS | G4 媒体/PDF/非遗资产需求证明后引入（§9） |
| AI | OpenAI / Anthropic 网关 + Evidence-Gate | JUSTIFIED（基础）+ 条件扩展 | Evidence-Gated 复用；医学护栏（G8）为条件性扩展 |
| 测试 | pytest · vitest · vue-tsc · ESLint/Prettier · ruff · mypy · Playwright · pre-commit | JUSTIFIED | REUSE HFB 门禁体系（§2.3/§12）；**G14/G15 已关闭**（候选绑定门禁证明，见 `docs/audit/HFD-PHASE0-GATE-PROOF.md`） |
| CI/CD | GitHub Actions（对齐 HFB CI 门禁清单） | JUSTIFIED | REUSE（§2.3） |
| 本地运行 | Docker Compose（PG + ES + Redis + MinIO） | 开发工具 | 仅本地开发便利；不等同于一期强制基础设施 |
| Observability | **UNKNOWN / TO BE DECIDED** | UNKNOWN | **不引入** Prometheus / Grafana / OpenTelemetry / ELK / Sentry；Phase 1 依运行与验收需求单独 ADR 决策 |

## 边界 → 基线映射

| 边界 | 主要技术 | 来源 |
| --- | --- | --- |
| Public Portal | Vue 3 公开面 + 匿名读 API（FastAPI）+ PG 检索 MVP（ES 条件性）+ PG 快照投影消费 | REUSE / EXTEND（G2 匿名访问 = Phase 1 占位） |
| Content & Research Workbench | Vue 3 工作台 + FastAPI 研究/工作流服务 + 报告导出（markdown 已验证；PDF/打印条件性） | REUSE / EXTEND |
| Publication | FastAPI 发布服务 + PG 快照/投影模型（表结构后续文档定义） | NEW（G3，Phase 1 占位） |
| Domain | SQLAlchemy 模型 + 领域服务 + 治理模式（准入/晋升/撤回） | REUSE |
| Evidence & Provenance | 服务层 + PG 约束/触发器 + 清单哈希 + Fail-Closed 查询 | REUSE |
| Media & Rights | 媒体元数据模型 + 权利状态机 + 审计（新建）；MinIO 与媒体处理管线**条件性**（G4 证明后） | NEW（G4，Phase 1 占位） |
| Teaching | V4 education 扩展（分级 + evidence 强制 + 医学合规） | EXTEND（G1/G8，Phase 1 占位） |
| Identity & Access | JWT 双通道 + token_version + RBAC 8 角色（Port 基础）；匿名 Visitor + SoD（**条件性**扩展） | REUSE / EXTEND（G2/G7，Phase 1 占位） |
| Shared Infrastructure | PG（JUSTIFIED）/ ES、Redis、MinIO（条件性）/ 日志与审计（现有）/ Observability（UNKNOWN，Phase 1 ADR） | REUSE + 条件 |

## 明确不选（Rejected / Deferred）

| 项 | 决定 | 理由 |
| --- | --- | --- |
| React / Next.js | **Rejected** | AGENTS.md 约束；Vue 栈已复用且能力已验证 |
| HFB runtime 依赖 | **Rejected（禁止）** | ADR-0001；HFB 仅作能力/数据/参考来源 |
| 复制 HFB live DB / 永久共享 HFB production DB | **Rejected（禁止）** | 数据继承边界（原则 3）；HFB 数据仅作 migration/import source |
| 一期无条件强制 Redis / MinIO / ES | **Rejected（Frozen）** | 条件性基础设施原则（§4 JUSTIFIED_WITH_CONDITIONS） |
| Observability 平台（Prometheus / Grafana / OpenTelemetry / ELK / Sentry） | Deferred | Phase 1 依运行与验收需求单独 ADR 决策 |
| 统一消息总线（Kafka 等） | Deferred | 单体起步；队列需求出现时再评估 |
| 云厂商锁定 | Deferred | 归属 `infra/` 阶段决策 |
| 统一 Assertion 模型 | Deferred | DOMAIN-MAP §1.7 为 PARTIAL；切片验收证明需要再建 |
| 数据库表 / API 契约 | Deferred | Phase 1 设计阶段定义 |
| 前端 UI 库完整引入 | Deferred | 按 AGENTS.md 选择顺序按需引入，不预装 |

## 版本与升级信息

- **版本**：v1.0（**Frozen**）
- **冻结日期**：2026-08-27（Phase 0）
- **升级路径**：`ba4f615`（Provisional）→ `344821a`（Codex 修正对齐）→ `a6a83c0`（门禁证明）→ 本轮治理提交（Frozen）
- **依据**：BASELINE-AUDIT v1.1（HEAD `2d98b610`）+ DOMAIN-MAP v1.1 + CODEX-REACCEPTANCE（VALIDATED_WITH_CORRECTIONS）+ GATE-PROOF（G14/G15 关闭）+ ADR-0001 + HFM-BOUNDARIES-v0.1
- **Gate 状态**：G14（验证环境）、G15（mypy 门禁）**已关闭**；G1 医学合规 / G2 匿名访问 / G3 发布快照 / G4 非遗媒体 / G7 SoD 为 **Phase 1 Deliverables**，不属 Phase 0 未完成项。
- **变更规则**：Frozen 之后任何技术基线变更须新增 ADR 并升版本号（v1.1、v2.0 …），不得静默替换。
