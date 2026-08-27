# HFM Phase 0.3 — Batch 1 Selective Asset Migration — Implementation

Date: 2026-08-27 · Phase 0.3 — SELECTIVE ASSET MIGRATION — BATCH 1
性质：低耦合、非领域核心能力迁移；PI MIGRATION ALLOWED（Batch 1）；PHASE 1 NOT AUTHORIZED

## 1. Starting Baseline

- **Engineering Skeleton Baseline**：`5ba76623c12787005c2cf8cf22e18efde3c15535`（HFM HEAD = origin/main，working tree clean）

## 2. HFB Source Commit

- **HFB Source Commit**：`03755b57ec0e4c8023d1447619f7d6ead9e44d73`（branch main，HEAD）
- 每个迁移资产均记录来源路径（见 §6），未复制 HFB 业务实现

## 3. Migration Inventory

- 完整清单与裁决见 `docs/migration/hfb/HFM-PHASE0.3-BATCH1-INVENTORY.md`
- 汇总：候选 12 项 → **PORT 4 · ADAPT 1 · REFERENCE_ONLY 1 · REJECT 3 · DEFERRED 2**（5 个迁移单元，满足 ≤5 上限）

## 4. Assets Migrated

| # | Asset | Mode | HFM Target |
| --- | --- | --- | --- |
| 1 | Canonical hash utility | PORT | `apps/backend/src/hfm/core/hashing.py` |
| 2 | Structured logging | PORT | `apps/backend/src/hfm/core/logging.py` |
| 3 | API response envelope | PORT | `apps/backend/src/hfm/utils/response.py` |
| 4 | Unified error handling（exceptions + error_handlers + request-id middleware） | ADAPT | `hfm/core/exceptions.py` + `hfm/core/error_handlers.py` + `hfm/middleware/request_id.py` |
| 5 | Generic TS utilities（sleep / generateId） | PORT | `apps/frontend/src/utils/misc.ts` |

接线：`hfm/main.py` 注册 `RequestIDMiddleware` 与 `register_error_handlers`（运行时冒烟验证 X-Request-ID 头）。

## 5. Assets Rejected / Deferred

- **REJECT**：`tests/conftest.py`（领域/DB 强耦合：legacy cutover SQL、Document/users 表、AI 凭证隔离、rate limiter）；`core/status_machine.py`（领域状态机）；领域 composables（useLibrary/useResearch*/useVersionComparison/useApi）
- **DEFERRED**：`core/settings.py`+`config.py`（含 HFB 基础设施假设，PG 按 Frozen 条件在 Phase 1 引入时再建）；`utils/fetchWithRetry.ts`（依赖 axios — 不在 Frozen Technical Baseline；且依赖 HFB API 客户端）
- **REFERENCE_ONLY**：工具链配置（ruff/mypy/pytest/eslint/prettier/vitest/CI）— HFM 保持独立绿色配置，不机械复制历史 exclusions/workaround

## 6. Source → Target Mapping

| HFM Asset | HFB Source Path | HFB Commit | Mode |
| --- | --- | --- | --- |
| `hfm/core/hashing.py` | `apps/backend/app/core/canonical_hash.py` | `03755b5` | PORT |
| `hfm/core/logging.py` | `apps/backend/app/core/logging.py` | `03755b5` | PORT |
| `hfm/utils/response.py` | `apps/backend/app/utils/response.py` | `03755b5` | PORT |
| `hfm/core/exceptions.py` | `apps/backend/app/core/exceptions.py` | `03755b5` | ADAPT |
| `hfm/core/error_handlers.py` | `apps/backend/app/core/error_handlers.py` | `03755b5` | ADAPT |
| `hfm/middleware/request_id.py` | `apps/backend/app/middleware/request_id.py` | `03755b5` | ADAPT |
| `apps/frontend/src/utils/misc.ts` | `packages/utils/src/index.ts`（sleep/generateId） | `03755b5` | PORT |

## 7. Adaptations Performed

- **exceptions.py**：删除 HFB 兼容别名（`ValidationError = ValidationException` 等 — HFB 历史调用方专用）；默认 error_code `DOMAIN_ERROR` → `APP_ERROR`（通用化）
- **error_handlers.py**：删除 `InvalidStatusTransitionError` 处理器（领域状态机依赖）；strict 类型化 — 处理器签名接受 `Exception`（FastAPI `ExceptionHandler` 逆变）并以 `isinstance` 收窄；`_error_envelope` 补 `dict[str, Any]` 类型
- **request_id.py**：HFM namespace import；`call_next: RequestResponseEndpoint` strict 类型化；dispatch 重构消除 `Response | None`（保留 request_failed 日志与成功路径 X-Request-ID 头）
- **logging.py**：保留通用部分，移除 `uvicorn.access`/`httpx`/`httpcore` 特定降噪（HFM 骨架无这些第三方日志假设）
- **misc.ts**：去除 `@hfb` 命名空间，纯 TS 移植

## 8. Dependencies Added

- **无新增运行时/工具链依赖**（hashing/logging/response/exceptions/error_handlers/request-id 均基于 stdlib + 既有 fastapi/starlette；misc.ts 零依赖）
- axios 因不在 Frozen Technical Baseline → fetchWithRetry DEFERRED

## 9. Tests Added

| HFM Test | 覆盖 |
| --- | --- |
| `tests/test_hashing.py` | SHA-256 已知向量、canonical JSON 排序/紧凑、NaN 拒绝、metadata hash 键序无关（4 tests） |
| `tests/test_logging.py` | JSON formatter 结构/异常、Console formatter、configure_logging/get_logger（4 tests） |
| `tests/test_response.py` | 响应封装默认值/data/meta/失败态（3 tests） |
| `tests/test_errors.py` | 422/404/500 统一封装、错误不泄漏、request-id 净化与回显（5 tests） |
| `apps/frontend/src/__tests__/misc.spec.ts` | sleep 延迟解析、generateId 长度/字符集（2 tests） |

全部为 HFM 独立测试，未引用 HFB 测试。

## 10. Quality Gates（迁移后全部重新运行）

| Gate | Result |
| --- | --- |
| Ruff check | PASS |
| Ruff format --check | PASS（19 files） |
| mypy --strict | PASS（19 source files，零 ignore/exemption） |
| pytest | **20 passed**（迁移前 4 → 迁移后 20） |
| ESLint | PASS |
| vue-tsc --noEmit | PASS |
| Vitest | **3 passed**（2 files） |
| Frontend build | PASS |
| Prettier --check | PASS |

无新增 ignore / mypy exemption / eslint disable / test skip。

## 11. Runtime Smoke（迁移后重新验证）

| Runtime | Evidence | Result |
| --- | --- | --- |
| Backend `/health` | HTTP 200 `{"status":"ok","service":"hfm"}` | PASS |
| Backend `/ready` | HTTP 200 `{"status":"ready","service":"hfm"}` | PASS |
| Backend X-Request-ID | `x-request-id: e66175ef-…` 出现在响应头（中间件生效） | PASS |
| Frontend dev | HTTP 200，`<title>HFM · 皇甫谧人文数字平台</title>` | PASS |

零外部基础设施（PG/ES/Redis/MinIO 未启动）。

## 12. HFB Runtime Independence

- 源码扫描：无 `Sites/hfb` / `../hfb` / `from hfb` / `import hfb` / `@hfb/`（apps/、packages/、根配置）
- 无 symlink（.venv 内为标准 venv python 链接，非 HFB）；无 git submodule（无 .gitmodules）；无 local path dependency；无 runtime HTTP 调用 HFB

**Permanent HFB Runtime Dependency: NO**

## 13. Scope Confirmation

- **Core Domain Migration: NO**（Person/Ancient Text/Reader/Library/Search/Knowledge/Workspace/Workflow/Source/Evidence/Citation/Publication/Snapshot/Media/Rights/Teaching/Auth/RBAC/AI Copilot/Reports/Export 业务逻辑均未迁移）
- **Phase 1 Features: NO**
- **Publication: NOT IMPLEMENTED**
- **Medical Compliance: NOT IMPLEMENTED**
- **Anonymous Access: NOT IMPLEMENTED**
- **ICH Media Governance: NOT IMPLEMENTED**
- **SoD: NOT IMPLEMENTED**
