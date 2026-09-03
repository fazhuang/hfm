# Contributing to HFM

## 前置条件

- Python ≥ 3.12（backend）
- Node.js 与 pnpm（frontend / workspace）

## 环境

- 后端：`apps/backend/pyproject.toml`（Hatchling；运行依赖 + `dev` 额外）
- 前端：`apps/frontend/package.json`（pnpm）

## 常用命令

| 层 | 命令 |
| --- | --- |
| 根 | `pnpm check`（lint + typecheck + test + build 全量门禁） |
| 前端 | `pnpm dev` · `pnpm build` · `pnpm test`（Vitest）· `pnpm e2e`（Playwright） |
| 后端 | `ruff check` · `ruff format --check` · `mypy`（strict）· `pytest`（pytest-asyncio） |

## 治理约束

- 冻结架构与验收归档为 `ARCHIVE_READ_ONLY`；不得改写历史、SHA、验收结论。
- 架构基线变更须新增 ADR 并升版本号；不得静默替换。
- 迁移遵循离线阶段化 CLI（M0–M7）；生产 HFB 导入保持 `NOT PERFORMED`。
- 变更须通过对应 Definition of Done 与证据契约门禁，见 `docs/governance/`。
