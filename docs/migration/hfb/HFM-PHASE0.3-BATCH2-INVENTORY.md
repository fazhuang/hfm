# HFM Phase 0.3 — Batch 2 Selective Asset Migration Inventory

Date: 2026-08-27 · Phase 0.3 — SELECTIVE ASSET MIGRATION — BATCH 2
起始基线：`45e6cc1e3bb91c3df5569fffade9bd95d48e5936`（Batch 1 Migration Baseline）
HFB Source Snapshot：`03755b57ec0e4c8023d1447619f7d6ead9e44d73`（固定只读，未修改 HFB）
授权：BATCH 2 AUTHORIZED BY THIS TASK；PHASE 1 BUSINESS CODING NOT AUTHORIZED

## 裁决词汇

- **PORT**：真正通用、几乎无 HFB-specific semantics、目标行为一致
- **ADAPT**：算法/结构值得复用但携带项目假设（须记录 what/removed/rewritten/independence）
- **REFERENCE_ONLY**：仅模式参考
- **DEFER**：依赖超出 Frozen 基线 / 需领域基座 / 无法安全分离业务语义
- **REJECT**：领域高耦合

## 候选清单

| Candidate | HFB Source Path | Matrix Verdict | Domain Coupling | Dependencies | Proposed Mode | HFM Target | Decision |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Generic pagination primitives（PaginationParams / PaginatedResponse） | `apps/backend/app/schemas/common.py` | —（通用） | LOW | pydantic（fastapi 既有） | PORT | `apps/backend/src/hfm/schemas/common.py` | **PORT** |
| Generic TS API/pagination types（ApiResponse/ApiMeta/PaginatedList/DeepPartial/Await/NonNullableArray） | `packages/types/src/index.ts`（通用子集） | — | LOW | 无 | ADAPT | `apps/frontend/src/types/api.ts` | **ADAPT** |
| Toast composable（useToast） | `apps/frontend/src/composables/useToast.ts` | — | LOW | vue（既有） | ADAPT | `apps/frontend/src/composables/useToast.ts` | **ADAPT** |
| Theme composable（useTheme） | `apps/frontend/src/composables/useTheme.ts` | — | LOW | vue（既有） | ADAPT | `apps/frontend/src/composables/useTheme.ts` | **ADAPT** |
| Focus trap composable（useFocusTrap） | `apps/frontend/src/composables/useFocusTrap.ts` | — | LOW | vue（既有） | PORT | `apps/frontend/src/composables/useFocusTrap.ts` | **PORT** |
| BaseRepository CRUD | `apps/backend/app/repositories/base.py` | — | MEDIUM（依赖 SQLAlchemy async + soft-delete Base） | sqlalchemy（Phase 1 PG） | DEFER | — | **DEFER** |
| Frontend HTTP client | `apps/frontend/src/api/client.ts` | — | HIGH（auth token/refresh 语义） | axios（不在 Frozen 基线） | DEFER | — | **DEFER** |
| Frontend fetch retry wrapper | `apps/frontend/src/utils/fetchWithRetry.ts` | — | MEDIUM（依赖 HFB API client） | axios | DEFER | — | **DEFER**（Batch 1 结转） |
| useApi composable | `apps/frontend/src/composables/useApi.ts` | — | HIGH（包装 auth 客户端） | axios | REJECT | — | **REJECT** |
| Export/FileResponse helpers | `apps/backend/app/api/v1/entities.py`（hfmzl preview）+ `api/v1/ai.py`（streaming） | Export=EXTEND | HIGH（candidate/AI 领域端点内嵌） | — | REJECT | — | **REJECT**（无可分离通用导出原语） |
| MIME/filename helpers | `apps/backend/app/services/candidate_fetcher.py` / `candidate_service.py` | Media=NEW | HIGH（candidate sandbox 领域） | — | REJECT | — | **REJECT** |
| Test fixtures | `tests/fixtures/gold_benchmark_v03.json` | — | HIGH（领域 benchmark 数据） | — | REJECT | — | **REJECT** |
| Settings pattern | `apps/backend/app/core/settings.py` + `config.py` | — | MEDIUM（HFB 基础设施设置） | pydantic-settings（Phase 1） | DEFER | — | **DEFER**（Batch 1 结转） |

## 本批迁移单元（5 个，达到上限但全部真实达标）

| # | 单元 | 模式 | Coupling |
| --- | --- | --- | --- |
| 1 | Generic pagination primitives | PORT | LOW |
| 2 | Generic TS API/pagination types | ADAPT | LOW |
| 3 | useToast composable | ADAPT | LOW |
| 4 | useTheme composable | ADAPT | LOW |
| 5 | useFocusTrap composable | PORT | LOW |

优先级依据（§4）：Shared Application Primitives（1–2）→ Generic Frontend Infrastructure（3–5）。零 HIGH coupling 迁移；零新增依赖。
