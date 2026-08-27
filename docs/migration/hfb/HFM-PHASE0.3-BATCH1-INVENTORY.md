# HFM Phase 0.3 — Batch 1 Selective Asset Migration Inventory

Date: 2026-08-27 · Phase 0.3 — SELECTIVE ASSET MIGRATION — BATCH 1
起始基线：`5ba76623c12787005c2cf8cf22e18efde3c15535`（Engineering Skeleton Baseline）
HFB Source Commit：`03755b57ec0e4c8023d1447619f7d6ead9e44d73`（branch main）
授权：PI MIGRATION ALLOWED（限 Batch 1 低耦合非领域资产）；PHASE 1 BUSINESS CODING NOT AUTHORIZED

## 裁决词汇

- **PORT**：低耦合、可原样（或仅 namespace/import 调整）迁入 HFM
- **ADAPT**：低耦合但需裁剪 HFB-specific 假设（领域依赖、命名、历史 workaround）
- **REFERENCE_ONLY**：仅作为模式参考，不迁入代码
- **REJECT**：领域耦合 / 依赖超基线 / 不符合 Batch 1 边界
- **DEFERRED**：本身低耦合，但需新增超出 Frozen Technical Baseline 的依赖，或时机未到（标记后本批停止）

## 候选资产清单

| Candidate Asset | HFB Path | Coupling | Verdict | HFM Target | Reason |
| --- | --- | --- | --- | --- | --- |
| Canonical hash utility（bytes SHA-256 / canonical JSON / metadata hash） | `apps/backend/app/core/canonical_hash.py` | 无（纯 hashlib/json） | **PORT** | `apps/backend/src/hfm/core/hashing.py` | 通用哈希/规范化序列化，零领域依赖，可单测 |
| Structured logging（JSON/Console formatter + configure_logging） | `apps/backend/app/core/logging.py` | 无（stdlib logging） | **PORT** | `apps/backend/src/hfm/core/logging.py` | 通用结构化日志，零领域依赖 |
| API response envelope（api_response） | `apps/backend/app/utils/response.py` | 无（纯函数） | **PORT** | `apps/backend/src/hfm/utils/response.py` | 通用响应封装，零领域依赖 |
| Unified error handling（异常层次 + 错误处理器 + request-id 中间件） | `apps/backend/app/core/exceptions.py` + `apps/backend/app/core/error_handlers.py` + `apps/backend/app/middleware/request_id.py` | 低（仅剥离 status_machine 依赖） | **ADAPT** | `apps/backend/src/hfm/core/exceptions.py` + `hfm/core/error_handlers.py` + `hfm/middleware/request_id.py` | 统一错误封装 + 请求关联；裁剪 `InvalidStatusTransitionError` 处理器（领域状态机）并修正 strict 类型 |
| Generic TS utilities（sleep / generateId） | `packages/utils/src/index.ts` | 无 | **PORT** | `apps/frontend/src/utils/misc.ts` | 通用前端工具（去除 @hfb 命名空间） |
| pytest shared fixtures | `tests/conftest.py` | 高（legacy cutover SQL、Document/users 表、AI 凭证隔离、rate limiter） | **REJECT** | — | 与 HFB 领域模型/数据库强耦合，不可独立迁移 |
| Settings pattern（pydantic-settings） | `apps/backend/app/core/settings.py` + `config.py` | 中（含 PG/ES/MinIO/AI/领域设置） | **DEFERRED** | — | 配置内容含 HFB 基础设施假设；PG 设置按 Frozen 条件在 Phase 1 引入时再建（模式 REFERENCE_ONLY） |
| Frontend fetch retry wrapper | `apps/frontend/src/utils/fetchWithRetry.ts` | 依赖 `@/api/client`（HFB API 客户端）+ axios | **DEFERRED** | — | axios 不在 Frozen Technical Baseline；依赖 HFB API 客户端（含认证语义） |
| Status machine | `apps/backend/app/core/status_machine.py` | 领域 | **REJECT** | — | 领域状态机（Version 等业务状态），Batch 1 边界外 |
| Domain composables（useLibrary/useResearch*/useVersionComparison/useApi） | `apps/frontend/src/composables/*` | 领域 | **REJECT** | — | 研究/图书馆/版本领域耦合 |
| Toolchain configs（ruff/mypy/pytest/eslint/prettier/vitest/CI） | 根配置 + `.github/workflows/*` | 工具链 | **REFERENCE_ONLY** | — | HFM 已有独立绿色配置；仅参考 HFB 模式，不机械复制历史 exclusions/workaround |

## 本批迁移单元（5 个，满足数量上限）

| # | 单元 | 模式 |
| --- | --- | --- |
| 1 | Canonical hash utility | PORT |
| 2 | Structured logging | PORT |
| 3 | API response envelope | PORT |
| 4 | Unified error handling（exceptions + error_handlers + request-id middleware） | ADAPT |
| 5 | Generic TS utilities（sleep / generateId） | PORT |

优先级依据（§7）：通用后端工具优先（1–4），通用前端工具次之（5）；测试基础设施无低耦合候选（REJECT）；工程配置 REFERENCE_ONLY。
