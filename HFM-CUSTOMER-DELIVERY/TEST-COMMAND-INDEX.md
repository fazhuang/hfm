# TEST-COMMAND-INDEX — 测试命令索引

> 命令均来自仓库既有工具链。执行环境与结果以实际运行为准。

## 前端

在 `apps/frontend` 下执行：

| 命令 | 用途 |
| --- | --- |
| `pnpm vitest run` | 前端单元测试（Vitest） |
| `pnpm vue-tsc --noEmit` | 前端类型检查 |
| `pnpm eslint .` | 前端代码规范检查（0 错误为基线） |
| `pnpm build` | 前端构建（类型检查 + Vite 构建） |
| `pnpm exec playwright test` | 浏览器端到端测试（需要本地运行环境与数据） |

## 后端

在 `apps/backend` 下执行（使用项目虚拟环境）：

| 命令 | 用途 |
| --- | --- |
| `PYTHONPATH=src .venv/bin/python -m pytest tests/test_phase1_portal.py -q` | 公共门户相关后端测试 |
| `PYTHONPATH=src .venv/bin/python -m pytest tests/test_phase1_research_workspace.py -q` | 研究工作台（项目/笔记）后端测试 |
| `PYTHONPATH=src .venv/bin/python -m pytest -q` | 后端全量测试 |
| `.venv/bin/python -m ruff check src tests` | 后端代码规范 |
| `.venv/bin/python -m mypy src tests` | 后端类型检查 |

## 迁移与运行核对

| 命令 | 用途 |
| --- | --- |
| `HFM_DATABASE_URL=<dsn> .venv/bin/python -m alembic -c alembic.ini current` | 查看当前迁移版本 |
| `… alembic -c alembic.ini heads` | 查看迁移头（应为单一 0014） |
| `bash scripts/database-dependency-probe.sh --api-base <base> --db-url <dsn> --backend-dir apps/backend/alembic` | 进程+数据库依赖探针 |

## 复用范围说明

- 上表为核心核验命令；交付验收时可结合 `00-START-HERE/ACCEPTANCE-CHECKLIST.md`
  与 `DEMO-GUIDE.md` 使用。
- 如个别命令在接收环境中因工具链版本差异不可用，请记录并以仓库文档为准，
  不要以「示意通过」代替实际执行。
