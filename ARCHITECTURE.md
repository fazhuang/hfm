# HFM Architecture

HFM（Huangfu Mi Humanities Digital Platform）采用
**Architecture Greenfield + Capability Brownfield** 策略：领域架构按客户需求全新设计，
能力层最大化复用 HFB 已验证资产，且不继承 HFB 不必要的历史兼容负担。

## 技术栈

- **Monorepo**：pnpm workspace（`apps/*`、`packages/*`）
- **Backend**（`apps/backend`）：Python ≥ 3.12 · FastAPI · SQLAlchemy 2.0 · Alembic · asyncpg（PostgreSQL）· Uvicorn
- **Frontend**（`apps/frontend`）：Vue 3 · TypeScript · Vite · Pinia · Vue Router

## 部署拓扑（ADR-01）

单体模块化部署：1 × Nginx + 1 × FastAPI + 1 × PostgreSQL。单一可部署单元内做严格
逻辑与鉴权隔离，保留按命名空间微服务化的演进路径。

## 关键架构决策（ADR）

| ADR | 领域 | 决策 |
| --- | --- | --- |
| ADR-01 | 物理部署拓扑 | 单体模块化部署 + 严格逻辑/鉴权隔离 |
| ADR-02 | 检索实现 | PostgreSQL 原生全文检索（`pg_trgm` + GIN）+ 多维过滤 |
| ADR-03 | 知识关系存储 | HFM 关系表 + PostgreSQL 外键/索引承载，不引入图数据库 |
| ADR-04 | 对象/媒体存储 | 本地磁盘 + SHA-256 内容寻址目录 + Nginx 静态加速，不引入对象存储集群 |
| ADR-05 | 公开/研究 API 隔离 | 显式路由命名空间 `/api/v1/public/*` 与 `/api/v1/research/*` + 仓储层强制过滤 |
| ADR-06 | HFB 适配/迁移 | 离线阶段化迁移 CLI（M0–M7），失败即关闭，幂等对账，零运行时依赖 |
| ADR-07 | 身份/RBAC | HFM 原生 5 角色 RBAC 引擎 + 可插拔机构认证接口 |

详细裁决见 `docs/governance/adr/` 与
`docs/audit/HFM-PHASE1-BLOCKING-ADR-RESOLUTION-AUDIT.md`。
