# HFM Phase 0.2 — Monorepo Skeleton Implementation

Date: 2026-08-27 · Phase 0.2 — Monorepo Skeleton Bootstrap
性质：ENGINEERING SKELETON BOOTSTRAP（非业务功能开发；无 HFB 资产迁移授权）

## Baseline

| 项 | 值 |
| --- | --- |
| Starting SHA（Frozen Architecture Baseline） | `7e109201e250dd5843add2249a24afa699766dd0` |
| Result SHA | 本轮提交（`docs: freeze validated HFM architecture baseline` 之后的新提交，SHA 见提交后状态） |
| 工作树起点 | clean，HEAD = origin/main = `7e10920` |

## Created Structure

```text
hfm/
├── apps/
│   ├── backend/            # Python FastAPI skeleton（src layout）
│   └── frontend/           # Vue 3 + TS + Vite skeleton
├── packages/README.md      # 共享包目录（空，占位）
├── infra/README.md         # 基础设施设计空间（条件性能力记录，无 compose 文件）
├── scripts/README.md       # 脚本目录（空，占位）
├── tests/README.md         # 仓库级集成测试目录（空，占位）
├── package.json            # pnpm 工作区编排
├── pnpm-workspace.yaml     # apps/* + packages/*
├── pnpm-lock.yaml
└── README.md               # 阶段更新为 Phase 0.2
```

## Backend Skeleton

- `apps/backend/pyproject.toml` — hatchling src-layout；依赖 fastapi>=0.115 / uvicorn[standard]>=0.34；dev: httpx/mypy/pytest/pytest-cov/ruff（版本族参考 HFB 工具链，配置全新）
- `src/hfm/main.py` — FastAPI 应用（title=HFM, version=0.1.0）
- `src/hfm/api/health.py` — 仅 `GET /health` 与 `GET /ready`（零外部依赖）
- 无数据库模型、无 Alembic、无业务 API（测试断言 /person /books /evidence /citations /search /auth /publication /media /teaching 均不存在）
- `.env.example` — 仅 `HFM_ENV=development`，无秘密

## Frontend Skeleton

- `apps/frontend/` — Vue 3.5 + TypeScript 5.7 + Vite 6 + vue-router 4.5 + Pinia 2.3（依赖就位，Pinia 已在 main.ts 接线）
- `src/main.ts` / `src/App.vue`（RouterView shell）/ `src/router/index.ts`（`/` → HomeView）/ `src/views/HomeView.vue`（仅工程验证文案「HFM · 皇甫谧人文数字平台 / Repository Skeleton Ready」）
- 无业务页面（无人物/古籍/非遗/教学/Workspace/Reader/Search/Login/Admin/Publication UI）；无正式视觉设计

## Tooling

| 工具 | 配置 | 门禁 |
| --- | --- | --- |
| TypeScript | `tsconfig.json`（strict, noEmit, bundler resolution） | `vue-tsc --noEmit` PASS |
| ESLint | `eslint.config.js`（flat：@eslint/js + typescript-eslint + eslint-plugin-vue flat/recommended） | `eslint .` PASS |
| Prettier | `.prettierrc.json`（semi off, singleQuote, width 100） | `prettier --check` PASS |
| Vitest | `vite.config.ts`（jsdom） | `vitest run` 1 passed |
| Ruff | `apps/backend/pyproject.toml`（E/F/W/I/UP/B/ASYNC, line 100） | `ruff check` + `ruff format --check` PASS |
| mypy | `--strict`（src + tests，从绿色开始，无历史豁免） | PASS（6 files） |
| pytest | `testpaths=["tests"]` | 4 passed |

## Tests

- Backend：`tests/test_health.py`（/health、/ready 断言）+ `tests/test_app.py`（应用可导入 + 无业务路由断言）→ **4 passed**
- Frontend：`src/__tests__/app.smoke.spec.ts`（App 挂载 + 骨架文案断言）→ **1 passed**
- 根编排：`pnpm check`（lint → typecheck → test → build）PASS

## Runtime Smoke

- Backend：`uvicorn hfm.main:app --port 8100` → `GET /health` **200** `{"status":"ok","service":"hfm"}`；`GET /ready` **200** `{"status":"ready","service":"hfm"}`
- Frontend：`vite dev`（port 5199）→ **HTTP 200**，`<title>HFM · 皇甫谧人文数字平台</title>`
- 全程无需启动 PostgreSQL / Elasticsearch / Redis / MinIO（符合 JUSTIFIED_WITH_CONDITIONS，零强制基础设施）

## HFB Reuse Confirmation

- 参考（允许）：工具链版本族（vue/vite/vitest/vue-tsc/eslint 版本、fastapi/uvicorn/ruff/mypy 版本）、工程组织方式（apps+packages、src layout、门禁命令形态）
- 未复制：domain models、services、API implementation、Vue pages、research components、migrations、business tests、data、Evidence/Citation/Auth 等业务代码
- **HFB BUSINESS CODE COPIED: NO**（29 个新增文件全部为 NEW HFM SKELETON CODE）

## Scope Confirmation

- 本轮未实现：G1 Medical Compliance / G2 Anonymous Access / G3 Publication Snapshot / G4 ICH Media Governance / G7 Separation of Duties
- 本轮未引入：JWT / User model / RBAC / Observability 平台（Prometheus/Grafana/OTel/ELK/Loki/Sentry） / 业务数据库模型 / compose 文件
- **PHASE 1 BUSINESS FEATURES IMPLEMENTED: NO**

## Final Gate

```text
HFM PHASE 0.2
=============

Starting Frozen Baseline:
7e109201e250dd5843add2249a24afa699766dd0

Monorepo Skeleton:
IMPLEMENTED

Backend:
PASS

Frontend:
PASS

Lint:
PASS

Type Check:
PASS

Tests:
PASS

Build:
PASS

Runtime Smoke:
PASS

HFB Business Migration:
NOT PERFORMED

Phase 1 Business Coding:
NOT PERFORMED

Working Tree:
CLEAN

Result SHA:
<commit sha recorded after commit>

READY FOR CODEX SKELETON ACCEPTANCE:
YES
```
