# HFD/HFM Phase 0 — Candidate-Bound CI-Compatible Gate Proof

Date: 2026-08-27（Asia/Shanghai）· Mode: read-only verification（未修改 HFB 生产代码/数据）
目的：执行 CODEX-REACCEPTANCE §17 修正 3 所要求的「在可达的候选绑定 CI 兼容环境中关闭 G14/G15」的门禁证明。

## 1. 候选绑定（Candidate Binding）

| 项 | 值 |
| --- | --- |
| HFB 候选 HEAD | `03755b57ec0e4c8023d1447619f7d6ead9e44d73`（branch `main`；G15 修复提交 `03755b5`） |
| HFB 工作树 | `M docs/12-context/project-state-2026-08-26.md`（既有）+ `?? docs/audit/`（既有交付）— 未被 `03755b5` 修改 |
| HFM HEAD | `344821a7b6b9efa395cb96b6d6ecb0dd5c3a95ba`（working tree clean） |
| 环境 | PostgreSQL / Elasticsearch / Redis / MinIO 全部可达（见 §2） |

## 2. G14 — 环境就绪证据（实测）

| 服务 | 端口 | 状态 | 证据 |
| --- | --- | --- | --- |
| PostgreSQL | 5432 | UP | TCP 连通；`hfb` 库 + `hfb_test` 库存在 |
| Elasticsearch | 9200 | UP | TCP 连通（集群 green 于审计 §2.2 已证） |
| Redis | 6379 | UP | TCP 连通 |
| MinIO | 9000 | UP | `/minio/health/live` = HTTP 200（本机二进制实例，非 docker；Docker daemon 本机未运行） |

G14 原阻塞（审计 §2.2/§12.3：MinIO 未运行 → pytest E2E `/ready` 全量健康检查超 10s 探测窗）已解除：MinIO 就绪后 `/ready` 检查即时通过。

## 3. 门禁执行结果（HFB HEAD `03755b5`）

| 套件 | 命令 | 结果 | 对照 |
| --- | --- | --- | --- |
| Mypy（G15） | `mypy --strict`（CI 门禁 22 文件） | **PASS** — Success: no issues found | 上轮 8 errors → 0 |
| Ruff | `ruff check` + `ruff format --check` | **PASS** | CI lint.yml 一致 |
| Backend unit + integration | `pytest tests/unit tests/integration -q` | **2724 passed / 0 failed / 1 deselected**（515.5s） | 与审计官方基线 2724/0/0 一致；1 deselected = `real_llm` |
| pytest E2E（此前被 G14 阻塞） | `pytest tests/e2e/test_critical_journeys.py::TestCrossProjectIsolation` | **6 passed**（27.7s） | CI test.yml 一致；MinIO 就绪后首次通过 |
| Frontend vitest | `pnpm test` | **807 passed**（38.7s） | 与审计一致 |
| vue-tsc | `pnpm typecheck` | **PASS** | CI 一致 |
| ESLint | `pnpm lint` | **PASS** | CI 一致（本机无沙箱 EPERM） |
| Vite build | `pnpm build` | **PASS**（10.2s） | CI build.yml 一致 |

## 4. 结论

- **G15：CLOSED** — strict mypy 22 文件门禁在候选 HEAD 通过，且随 `03755b5` 已入库。
- **G14：ENVIRONMENT READY + 门禁证明已执行** — 四服务可达；此前被阻塞的 pytest E2E 路径现全部通过。
- 候选绑定（candidate-bound）CI-compatible 门禁证明完成；本记录不自行宣布 Frozen，升级裁决依 `docs/governance/BASELINE-MANAGEMENT.md` 由 Codex Re-Acceptance 作出。
