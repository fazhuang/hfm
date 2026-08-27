# HFM 技术基线（v1.0）

Status: **Frozen** · Version: 1.0 · Date: 2026-08-27 · Phase 0 — Repository Bootstrap & HFB Asset Reuse Planning

## 目的与范围

本文档冻结 HFM 各架构边界的技术基线（Technology Baseline），是 Phase 0 的第二个冻结交付物（第一个为 HFB Asset Reuse Matrix v1.0）。

**依据**：

- ADR-0001（独立仓库 + Architecture Greenfield + Capability Brownfield）
- HFM-BOUNDARIES-v0.1（九大边界与数据流契约）
- HFD-PHASE0-BASELINE-AUDIT v1.1（HFB 实测证据，HEAD `2d98b610`）
- HFD-PHASE0-DOMAIN-MAP v1.1（领域映射与验证分层）

**本版本不定义**：数据库表、API 契约、物理部署拓扑、云厂商选择。

## 决策原则

1. **同源复用**：HFM 与 HFB 保持同语言/框架族（Python + FastAPI / Vue 3 + TypeScript），最小化 Port 成本；不因引入新技术而迁移已验证能力。
2. **无 HFB runtime 依赖**：HFM 不得导入、调用 HFB 运行时；HFB 能力以 Port / Adapt 产物进入 HFM（带 Model→Service→API→Test 证据链溯源）。
3. **前端不引入 React**：遵循 AGENTS.md 约束；UI 组件资源选择须兼容 Vue 3 面（shadcn/ui 仅作概念基础，React-only 组件不得直接落入 Vue 面）。
4. **边界契约优先**：技术选型服从 HFM-BOUNDARIES-v0.1 的依赖方向（上层可依赖下层，Domain/Evidence & Provenance 不依赖任何边界）。
5. **先冷冻结、后演进**：冻结后任何变更须经 ADR 裁决并升版，禁止静默替换。

## 技术基线（按层）

| 层 | 选择 | 依据 / 备注 |
| --- | --- | --- |
| 仓库形态 | pnpm workspaces monorepo（`apps/` + `packages/` + `infra/` + `scripts/` + `tests/`） | 与 HFB 同构（BASELINE §2.1）；对齐九边界布局 |
| 后端 | Python 3.12+ · FastAPI · Pydantic v2 · SQLAlchemy 2.0 async · Alembic | REUSE HFB 栈（§2.1/§3）；UUIDv7 + 软删除模式随迁 |
| 前端 | Vue 3 + TypeScript · Vite · Pinia · vue-router | REUSE HFB 栈（§3）；AGENTS.md 禁止 React 迁移 |
| 数据 | PostgreSQL 16（唯一事实源） | REUSE（§2.2，HFB 64 表 PG 实测运行） |
| 检索 | Elasticsearch 8 索引（公开检索 + 研究检索）；PostgreSQL ILIKE 为 MVP fallback | REUSE HFB 检索架构（§3）；P4 fail-closed 查询规则随迁（§5） |
| 缓存 / 限流 / 队列 | Redis | REUSE HFB 角色（§2.2） |
| 对象存储 | MinIO（S3 兼容） | REUSE；承载媒体/PDF/非遗资产（G4，§9） |
| AI | OpenAI / Anthropic 网关 + Evidence-Gate | REUSE（§8）+ EXTEND 医学护栏（G8） |
| 测试 | pytest · vitest · vue-tsc · ESLint/Prettier · ruff · mypy · Playwright · pre-commit | REUSE HFB 门禁体系（§2.3/§12）；mypy 门禁既有 8 errors（G15）须修复或调整范围 |
| CI/CD | GitHub Actions（对齐 HFB CI 门禁清单） | REUSE（§2.3） |
| 本地运行 | Docker Compose（PG + ES + Redis + MinIO） | 解决 G14（pytest E2E 依赖 MinIO/ES 环境） |

## 边界 → 基线映射

| 边界 | 主要技术 | 来源 |
| --- | --- | --- |
| Public Portal | Vue 3 公开面 + 匿名读 API（FastAPI）+ ES 公开索引 + PG 快照投影消费 | REUSE / EXTEND（G2 匿名访问） |
| Content & Research Workbench | Vue 3 工作台 + FastAPI 研究/工作流服务 + 报告导出 | REUSE |
| Publication | FastAPI 发布服务 + PG 快照/投影模型（表结构后续文档定义） | NEW（G3） |
| Domain | SQLAlchemy 模型 + 领域服务 + 治理模式（准入/晋升/撤回） | REUSE |
| Evidence & Provenance | 服务层 + PG 约束/触发器 + 清单哈希 + Fail-Closed 查询 | REUSE |
| Media & Rights | MinIO + 媒体元数据模型 + 权利状态机 + 审计 | NEW（G4，架构模板复用 hfmzl candidate/admission 链） |
| Teaching | V4 education 扩展（分级 + evidence 强制 + 医学合规） | EXTEND（G1/G8） |
| Identity & Access | JWT 双通道 + token_version + RBAC 8 角色 | REUSE / EXTEND（G7 SoD） |
| Shared Infrastructure | PG / ES / Redis / MinIO / 日志 / 审计 | REUSE |

## 明确不选（Rejected / Deferred）

| 项 | 决定 | 理由 |
| --- | --- | --- |
| React / Next.js | **Rejected** | AGENTS.md 约束；Vue 栈已复用且能力已验证 |
| HFB runtime 依赖 | **Rejected（禁止）** | ADR-0001；HFB 仅作能力/数据/参考来源 |
| 统一消息总线（Kafka 等） | Deferred | 基线起步为单体部署；队列需求出现时再评估 |
| 云厂商锁定 | Deferred | 归属 `infra/` 阶段决策 |
| 统一 Assertion 模型 | Deferred | DOMAIN-MAP §1.7 为 PARTIAL；切片验收证明需要再建 |
| 数据库表 / API 契约 | Deferred | 下一阶段（Phase 1 设计）定义 |
| 前端 UI 库完整引入 | Deferred | 按 AGENTS.md 选择顺序按需引入，不预装 |

## 冻结信息

- **版本**：v1.0（Frozen）
- **冻结日期**：2026-08-27（Phase 0）
- **依据**：BASELINE-AUDIT v1.1（HEAD `2d98b610`）+ DOMAIN-MAP v1.1 + ADR-0001 + HFM-BOUNDARIES-v0.1
- **变更规则**：冻结后任何技术基线变更须新增 ADR 并升版本号（v1.1、v2.0 …），不得静默替换。
