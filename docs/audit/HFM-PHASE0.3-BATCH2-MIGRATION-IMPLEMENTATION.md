# HFM Phase 0.3 — Batch 2 Selective Asset Migration — Implementation

Date: 2026-08-27 · Phase 0.3 — SELECTIVE ASSET MIGRATION — BATCH 2
性质：共享应用能力迁移（非领域核心）；BATCH 2 AUTHORIZED BY THIS TASK；PHASE 1 NOT AUTHORIZED

## 1. Starting Baseline

- **Batch 1 Migration Baseline**：`45e6cc1e3bb91c3df5569fffade9bd95d48e5936`（HFM HEAD = origin/main，working tree clean）

## 2. HFB Source Snapshot

- **HFB Source Snapshot（固定只读）**：`03755b57ec0e4c8023d1447619f7d6ead9e44d73`（branch main；与 Batch 1 一致，未使用新 HEAD，未修改 HFB）

## 3. Candidate Inventory Summary

- 完整清单见 `docs/migration/hfb/HFM-PHASE0.3-BATCH2-INVENTORY.md`
- 汇总：候选 13 项 → **PORT 2 · ADAPT 3 · DEFER 4 · REJECT 4 · REFERENCE_ONLY 0**；迁移 5 个单元（达到上限且全部真实达标）

## 4. PORT Assets

| # | Asset | HFM Target |
| --- | --- | --- |
| 1 | Generic pagination primitives（PaginationParams / PaginatedResponse） | `apps/backend/src/hfm/schemas/common.py` |
| 2 | Focus trap composable（useFocusTrap） | `apps/frontend/src/composables/useFocusTrap.ts` |

## 5. ADAPT Assets

| # | Asset | HFM Target |
| --- | --- | --- |
| 3 | Generic TS API/pagination types（ApiResponse/ApiMeta/PaginatedList/DeepPartial/Await/NonNullableArray） | `apps/frontend/src/types/api.ts` |
| 4 | Toast composable（useToast） | `apps/frontend/src/composables/useToast.ts` |
| 5 | Theme composable（useTheme） | `apps/frontend/src/composables/useTheme.ts` |

## 6. REFERENCE_ONLY Assets

无（工具链配置在 Batch 1 已 REFERENCE_ONLY；本轮无新增）。

## 7. DEFER Assets

- `repositories/base.py`（BaseRepository CRUD）— 依赖 SQLAlchemy async + soft-delete Base，属 Phase 1 PG 基座
- `api/client.ts`（前端 HTTP 客户端）— auth token/refresh 语义 + axios（不在 Frozen 基线）
- `utils/fetchWithRetry.ts` — axios（Batch 1 结转）
- `core/settings.py`+`config.py` — 基础设施设置（Batch 1 结转）

## 8. REJECT Assets

- `useApi.ts`（包装 auth 客户端）— HIGH
- 导出/FileResponse 端点（`entities.py` hfmzl preview、`ai.py` streaming）— HIGH 领域内嵌
- MIME/filename 辅助（`candidate_fetcher.py`/`candidate_service.py`）— HIGH candidate 领域
- `tests/fixtures/gold_benchmark_v03.json` — HIGH 领域 benchmark 数据

## 9. Source → Target Mapping

| HFM Asset | HFB Source Path | HFB Commit | Mode |
| --- | --- | --- | --- |
| `hfm/schemas/common.py` | `apps/backend/app/schemas/common.py` | `03755b5` | PORT |
| `apps/frontend/src/types/api.ts` | `packages/types/src/index.ts`（通用子集） | `03755b5` | ADAPT |
| `apps/frontend/src/composables/useToast.ts` | `apps/frontend/src/composables/useToast.ts` | `03755b5` | ADAPT |
| `apps/frontend/src/composables/useTheme.ts` | `apps/frontend/src/composables/useTheme.ts` | `03755b5` | ADAPT |
| `apps/frontend/src/composables/useFocusTrap.ts` | `apps/frontend/src/composables/useFocusTrap.ts` | `03755b5` | PORT |

## 10. Domain Coupling Assessment

全部 5 个单元评级 **LOW**（纯通用；无 Person/Ancient Text/Search/Evidence/Auth 等语义）。审计 13 项中 HIGH 项全部 REJECT，无 HIGH 迁移。

## 11. Adaptation Details

| Asset | What was reused | What was removed | What was rewritten | Why HFM result is independent |
| --- | --- | --- | --- | --- |
| TS types | ApiResponse/ApiMeta/PaginatedList/DeepPartial/Await/NonNullableArray 定义 | HFB 领域类型 `Document`/`Person`；`@hfb` namespace 注释 | 文件头来源说明 | 纯类型契约，零运行时依赖 |
| useToast | toast 状态机、variant 帮助函数、自动消失逻辑 | `hfb-toast-` id 前缀 → `hfm-toast-`；HFB provider 命名注释 | 前缀与文档注释 | 仅依赖 vue ref |
| useTheme | theme 类型、localStorage 持久化、dark class 切换、系统偏好监听 | `hfb-theme` key → `hfm-theme` | `matchMedia`/`addEventListener` 加可选调用守卫（jsdom/无 MediaQueryList 环境安全） | 仅依赖 vue + 浏览器标准 API |
| useFocusTrap | FOCUSABLE 选择器、Tab/Shift+Tab 循环、activate/deactivate/恢复焦点 | HFB dialog 提取说明注释 | 移除未使用的 `_triggerEl` 参数（lint 合规；原实现忽略之） | 仅依赖 vue + DOM 标准 |

## 12. Dependencies

- **无新增依赖**（分页原语用 pydantic — fastapi 既有；composables 用 vue — 既有；types 零依赖）
- axios 等未引入（Frozen 基线外 → DEFER）

## 13. Tests

| HFM Test | 覆盖 |
| --- | --- |
| `tests/test_pagination.py` | 默认值、边界校验（page≥1、limit 1..100）、响应封装（3 tests） |
| `src/__tests__/types.spec.ts` | ApiResponse/PaginatedList/Await/DeepPartial/NonNullableArray 编译期类型断言（5 tests） |
| `src/__tests__/useToast.spec.ts` | show/dismiss/自动消失/variant 帮助函数（4 tests） |
| `src/__tests__/useTheme.spec.ts` | 默认 auto、持久化读取、setTheme + dark class（模块级状态用 resetModules 真隔离）（3 tests） |
| `src/__tests__/useFocusTrap.spec.ts` | activate 聚焦首元素、Tab/Shift+Tab 循环、deactivate 移除监听（attachTo body 保证 jsdom focus 生效）（4 tests） |

全部为 HFM 独立测试；无断言占位。

## 14. Full Quality Gates

| Gate | Result |
| --- | --- |
| Ruff | PASS |
| Ruff format --check | PASS（22 files） |
| mypy --strict | PASS（22 source files，零 ignore/exemption） |
| pytest | **23 passed**（Batch 1 20 + 新增 3） |
| ESLint | PASS |
| Prettier --check | PASS |
| vue-tsc --noEmit | PASS |
| Vitest | **19 passed**（6 files；Batch 1 3 + 新增 16） |
| Frontend build | PASS |

## 15. Batch 1 Regression

- Batch 1 后端测试（hashing/logging/response/errors）随 pytest 23 passed 全绿
- request-id 行为：冒烟响应头 `x-request-id` 存在（见 §16）
- /health、/ready 不退化（§16）

## 16. Runtime Smoke

| Runtime | Evidence | Result |
| --- | --- | --- |
| Backend `/health` | HTTP 200 `{"status":"ok","service":"hfm"}` | PASS |
| Backend `/ready` | HTTP 200 `{"status":"ready","service":"hfm"}` | PASS |
| Request-ID（Batch 1 回归） | `x-request-id: 29f663a2-…` 响应头 | PASS |
| Frontend runtime | **端口 5299**（项目实际配置启动）：HTTP 200，`<title>HFM · 皇甫谧人文数字平台</title>` | PASS |

## 17. HFB Independence

- 源码/配置扫描：无 `Sites/hfb`、`../hfb`、`from hfb`、`import hfb`、`@hfb/`、`03755b57`（apps/、packages/、根配置）
- 无 symlink（.venv 内为 venv 标准链接）、无 submodule、无 local path dependency、无 HFB runtime HTTP
- 唯一「hfb」命中为 `types/api.ts` 的来源说明注释（合法 provenance 记录，非依赖）

**Permanent HFB Runtime Dependency: NO**

## 18. Phase 1 Boundary

- **Core Domain Migration: NO**（无 Person/Ancient Text/Evidence/Citation/Publication/Media/Teaching/RBAC/Research/Workspace 实现）
- **Phase 1 Business Coding: NO**（G1/G2/G3/G4/G7 均未实现）
- 新增业务 API：无（仅迁移通用基础资产，未新增业务 endpoint）
