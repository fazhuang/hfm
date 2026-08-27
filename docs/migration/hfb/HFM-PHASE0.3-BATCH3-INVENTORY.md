# HFM Phase 0.3 — Batch 3 Selective Asset Migration Inventory

Date: 2026-08-27 · Phase 0.3 — SELECTIVE ASSET MIGRATION — BATCH 3
起始基线：`b5388af0490f9d7b3e14b9a6f1f1ccff781e81c1`（Batch 2 Migration Baseline）
HFB Source Snapshot：`03755b57ec0e4c8023d1447619f7d6ead9e44d73`（固定只读，未修改 HFB）
授权：BATCH 3 AUTHORIZED BY THIS TASK；PHASE 1 BUSINESS CODING NOT AUTHORIZED

## 裁决词汇

- **PORT**：真正通用、几乎无 HFB-specific semantics
- **ADAPT**：结构值得复用但携带项目假设（须记录语义剥离证明）
- **REFERENCE_ONLY**：仅模式参考
- **DEFER**：依赖超出 Frozen 基线 / 领域基座 / 无法安全解耦
- **REJECT**：领域高耦合

## 候选清单

| Candidate | HFB Source Path | Reuse Matrix Verdict | Coupling | Dependencies | Proposed Mode | HFM Target | Decision |
| --- | --- | --- | --- | --- | --- | --- | --- |
| API error normalization（ApiErrorDetail + getApiErrorDetail） | `apps/frontend/src/api/client.ts`（内嵌于 axios 文件，实现零 axios 耦合） | — | LOW | 无 | PORT | `apps/frontend/src/utils/errors.ts` | **PORT** |
| System info endpoints（/version /live /config） | `apps/backend/app/api/version.py` | — | LOW（ADAPT 后；剥离 settings） | fastapi（既有） | ADAPT | `apps/backend/src/hfm/api/system.py` | **ADAPT** |
| Vitest jsdom matchMedia polyfill | `apps/frontend/src/test-setup.ts` | — | LOW | vitest（既有） | PORT | `apps/frontend/src/test-setup.ts` | **PORT** |
| Readiness infra checks（/ready 服务聚合 + admin health-details） | `apps/backend/app/api/ready.py` | — | HIGH（run_health_checks + auth 依赖） | check_infrastructure + auth（Phase 1） | DEFER | — | **DEFER** |
| Infrastructure check framework | `apps/backend/app/startup/check_infrastructure.py` | — | HIGH（PG/Redis/ES/MinIO 检查） | 基础设施（条件性） | DEFER | — | **DEFER** |
| Settings pattern | `apps/backend/app/core/settings.py` + `config.py` | — | MEDIUM（HFB 基础设施设置） | pydantic-settings（Phase 1） | DEFER | — | **DEFER**（B1/B2 结转） |
| Frontend HTTP client | `apps/frontend/src/api/client.ts`（主体） | — | HIGH（auth token/refresh） | axios | DEFER | — | **DEFER**（B1/B2 结转） |
| Domain audit models | `models/ocr_proofreading_audit.py`、`candidate_audit_log.py`、`academic_taint.py` 等 | Audit=EXTEND | HIGH（领域审计语义） | — | REJECT | — | **REJECT**（无可剥离通用 audit 原语） |
| Download/format helpers | `composables/useResearchReports.ts`、`useResearchResult.ts` 等 | — | HIGH（领域内嵌） | — | REJECT | — | **REJECT** |
| classifyError（领域 composable 内私有重复） | `composables/useResearchWorkflow.ts` / `useVersionComparison.ts` | — | HIGH（领域内私有函数） | — | REJECT | — | **REJECT** |
| packages/ui placeholder | `packages/ui/src/index.ts` | — | LOW | — | REFERENCE_ONLY | — | **REFERENCE_ONLY**（空占位，无资产） |

## 本批迁移单元（3 个，真实达标；少于上限 5）

| # | 单元 | 模式 | Coupling |
| --- | --- | --- | --- |
| 1 | API error normalization（getApiErrorDetail） | PORT | LOW |
| 2 | System info endpoints（/version /live /config） | ADAPT | LOW（剥离 settings） |
| 3 | Vitest jsdom matchMedia polyfill（test-setup） | PORT | LOW |

说明：6.1/6.2 响应与分页契约已在 Batch 1/2 覆盖；6.3 文件/下载、6.4 审计、6.6 前端查询/下载均无可剥离的领域外资产 → DEFER/REJECT。不为凑数降低准入标准。
