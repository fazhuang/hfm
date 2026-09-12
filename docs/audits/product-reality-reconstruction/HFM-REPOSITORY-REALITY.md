# HFM-REPOSITORY-REALITY.md — 仓库物理结构与运行职责重建

## 1. 仓库顶层与管理模式

| 维度 | 当前事实 | 证据 |
|---|---|---|
| **代码库性质** | Monorepo (pnpm workspace) | `pnpm-workspace.yaml`, `package.json` |
| **Node 包管理** | `pnpm` (lockfile: `pnpm-lock.yaml`) | 根目录 `pnpm-lock.yaml` |
| **Python 环境** | Python 3.13 / pyproject.toml / uv/pip-compatible venv | `apps/backend/pyproject.toml`, `apps/backend/.venv` |
| **工作区路径** | `/private/tmp/recovery/hfm-foundation` | `git rev-parse --show-toplevel` |
| **活动分支** | `recovery/hfm-foundation` | `git branch --show-current` |
| **当前 HEAD** | `1e9336e0b530764da3754de5c1c58650dc38fa60` | `git rev-parse HEAD` |

---

## 2. 核心目录及其在运行时承担的职责

### 2.1 `apps/frontend/` (前端应用)
- **职责**：Vue 3 + Vite + Pinia + Vue Router SPA。负责向公众和研究人员提供界面。
- **入口**：`apps/frontend/src/main.ts`, `apps/frontend/index.html`。
- **运行方式**：开发时 `vite dev` (5173 端口)，生产构建 `vite build` 生成纯静态 bundle 到 `apps/frontend/dist`。
- **与后端关系**：通过 `apps/frontend/src/services/api.ts` 与后端 `/api/v1` 交互；同时包含本地静态 Projection/Inventory 数据集 (`apps/frontend/src/data/`)。

### 2.2 `apps/backend/` (后端应用)
- **职责**：FastAPI + SQLAlchemy 2.0 (Async) + Alembic 数据服务。负责提供 RESTful API、RBAC 认证鉴权、实体仓储、版本与审计链。
- **入口**：`apps/backend/src/hfm/main.py` (`app = FastAPI(...)`)。
- **运行方式**：`uvicorn hfm.main:app --host 0.0.0.0 --port 8000`。
- **数据库支撑**：默认连接 PostgreSQL (`HFM_DATABASE_URL`)，测试时兼容 SQLite。

### 2.3 `apps/backend/alembic/` (数据库迁移)
- **职责**：Alembic 迁移脚本仓库。维护从 `0001` 到 `0014` 的版本演进。
- **HEAD 状态**：`0014_p2_media_rights.py`。
- **运行命令**：`alembic upgrade head`。

### 2.4 `infra/` (基础设施与部署配置)
- **职责**：生产/本地运行环境契约。
- **内容**：
  - `infra/env/prod.env.example`：生产环境变量规范与强校验基准。
  - `infra/nginx/hfm.conf.example`：Nginx 反向代理配置（SPA 路由分发 + API 代理 + 媒体字节流直传）。
  - `infra/systemd/hfm-backend.service.example`：Systemd 后端守护进程模板。
  - `infra/scripts/golden-runtime-gate.sh` / `fast-runtime-gate.sh`：端到端本地/CI 门禁脚本。

### 2.5 `scripts/` (运维、发布与验证脚本)
- **职责**：提供离线/运维任务及发布门禁：
  - `scripts/build-release.sh`：自动化执行静态检查、测试、前端打包、构建发布 tarball。
  - `scripts/initialize-production.py`：生产数据库安全初始化（创建首个且唯一的 SYSTEM_ADMIN，幂等无害）。
  - `scripts/validate-production-env.py`：生产环境变量 Fail-closed 严苛验证器。
  - `scripts/production-smoke.sh`：生产线上或演练环境真实探针验证。
  - `scripts/database-dependency-probe.sh`：探测并验证外部 PostgreSQL / SQLite 连接。

### 2.6 `docs/` (文档与审计资产)
- **职责**：
  - `docs/decisions/`：记录架构决策 (ADR-01 ~ ADR-07)。
  - `docs/audit/`：历史各阶段验收记录归档。
  - `docs/operations/`：发布与部署操作手册 (如 ND1-RELEASE-QUALIFICATION.md)。
  - `docs/audits/product-reality-reconstruction/`：本次全量产品现实审计产物。

### 2.7 `packages/`
- **职责**：当前仅含 `packages/README.md`，处于预留状态，核心逻辑全在 `apps/frontend` 与 `apps/backend` 中。
