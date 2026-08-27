# HFM Phase 0.3 — Batch 3 Selective Asset Migration — Implementation

Date: 2026-08-27 · Phase 0.3 — SELECTIVE ASSET MIGRATION — BATCH 3
性质：领域外近应用层共享能力迁移；BATCH 3 AUTHORIZED BY THIS TASK；PHASE 1 NOT AUTHORIZED

## 1. Starting Baseline

- **Batch 2 Migration Baseline**：`b5388af0490f9d7b3e14b9a6f1f1ccff781e81c1`（HFM HEAD = origin/main，working tree clean）

## 2. HFB Source Snapshot

- **HFB Source Snapshot（固定只读）**：`03755b57ec0e4c8023d1447619f7d6ead9e44d73`（与 Batch 1/2 一致；未使用新 HEAD，未修改 HFB）

## 3. Candidate Inventory

- 完整清单见 `docs/migration/hfb/HFM-PHASE0.3-BATCH3-INVENTORY.md`
- 汇总：候选 11 项 → **PORT 2 · ADAPT 1 · REFERENCE_ONLY 1 · DEFER 5 · REJECT 3**；迁移 3 个单元（真实达标，少于上限 5）

## 4. PORT Assets

| # | Asset | HFM Target |
| --- | --- | --- |
| 1 | API error normalization（ApiErrorDetail + getApiErrorDetail） | `apps/frontend/src/utils/errors.ts` |
| 2 | Vitest jsdom matchMedia polyfill | `apps/frontend/src/test-setup.ts`（+ `vite.config.ts` setupFiles） |

## 5. ADAPT Assets

| # | Asset | HFM Target |
| --- | --- | --- |
| 3 | System info endpoints（/version /live /config） | `apps/backend/src/hfm/api/system.py` |

## 6. REFERENCE_ONLY

- `packages/ui/src/index.ts`（空占位，无资产可迁）

## 7. DEFER

- `api/ready.py` 服务聚合 + admin health-details（依赖 `check_infrastructure` + auth — Phase 1 infra/认证）
- `startup/check_infrastructure.py`（PG/Redis/ES/MinIO 检查框架 — 条件性基础设施）
- `core/settings.py` + `config.py`（B1/B2 结转）
- `api/client.ts` 主体（auth + axios，B1/B2 结转）

## 8. REJECT

- 领域 audit models（ocr/candidate/taint/source_admission/ingestion — 均领域审计语义）
- download/format helpers（research composables 领域内嵌）
- classifyError（领域 composable 内私有重复实现）

## 9. Source → Target Mapping

| HFM Asset | HFB Source Path | HFB Commit | Mode |
| --- | --- | --- | --- |
| `apps/frontend/src/utils/errors.ts` | `apps/frontend/src/api/client.ts`（ApiErrorDetail/getApiErrorDetail 部分） | `03755b5` | PORT |
| `apps/frontend/src/test-setup.ts` | `apps/frontend/src/test-setup.ts` | `03755b5` | PORT |
| `apps/backend/src/hfm/api/system.py` | `apps/backend/app/api/version.py` | `03755b5` | ADAPT |

## 10. Coupling Assessment

全部 3 个单元 **LOW**（错误归一化零依赖纯函数；matchMedia polyfill 零业务语义；系统端点剥离 settings 后零 HFB 假设）。HIGH 候选全部 DEFER/REJECT，0 HIGH 迁移。

## 11. Adaptation Details

| Asset | What was retained | What was removed | What was rewritten | Removed HFB assumptions |
| --- | --- | --- | --- | --- |
| errors.ts | `ApiErrorDetail` 形状、`getApiErrorDetail` 提取逻辑（status/body.message/detail 回退链） | axios 客户端文件上下文 | 文件头来源说明 | 无（实现本就零 axios 耦合） |
| test-setup.ts | matchMedia stub 实现（matches:false + addEventListener 等） | — | 文件头来源说明 | 无 |
| system.py | `/version` `/live` `/config` 端点模式与 api_response 封装 | `app.core.config.settings` 依赖；`API_V1_PREFIX` 字段 | 改为模块级常量（VERSION=**version**、ENVIRONMENT=HFM_ENV、PROJECT_NAME=HFM）；strict `dict[str, Any]` | HFB 配置对象假设移除 |

## 12. Tests

| HFM Test | 覆盖 |
| --- | --- |
| `src/__tests__/errors.spec.ts` | body.message 提取、detail 回退、message 回退、null/非对象边界（4 tests） |
| `src/__tests__/test-setup.spec.ts` | matchMedia stub 存在性/形状（1 test） |
| `tests/test_system.py` | /version /live /config 状态码与封装结构（3 tests） |

全部为 HFM 独立测试；无 skip/ignore/strictness 降低。

## 13. Quality Gates

| Gate | Result |
| --- | --- |
| Ruff | PASS |
| Ruff format --check | PASS（24 files） |
| mypy --strict | PASS（24 source files，零 ignore/exemption） |
| pytest | **26 passed**（Batch 1+2 23 + 新增 3） |
| ESLint | PASS |
| Prettier --check | PASS |
| vue-tsc --noEmit | PASS |
| Vitest | **24 passed**（8 files；Batch 1+2 19 + 新增 5） |
| Frontend build | PASS |

## 14. Batch 1/2 Regression

- pytest 26 passed 覆盖 Batch 1（hashing/logging/response/errors）+ Batch 2（pagination）测试全绿
- Vitest 24 passed 覆盖 Batch 1（misc/app.smoke）+ Batch 2（types/useToast/useTheme/useFocusTrap）全绿
- request-id 头正常（§15）；/health /ready 不退化

## 15. Runtime Smoke

| Runtime | Evidence | Result |
| --- | --- | --- |
| `/health` | HTTP 200 `{"status":"ok","service":"hfm"}` | PASS |
| `/ready` | HTTP 200 `{"status":"ready","service":"hfm"}` | PASS |
| `/version` `/live` `/config` | HTTP 200（新迁移端点） | PASS |
| X-Request-ID（Batch 1 回归） | `x-request-id: 80cb6895-…` 响应头 | PASS |
| Frontend runtime | **端口 5399**（实际启动端口）：HTTP 200，标题正确 | PASS |

## 16. HFB Independence

- 源码/配置扫描：无 `Sites/hfb`、`../hfb`、`from hfb`、`import hfb`、`@hfb/`、`03755b57`
- 无 symlink（.venv 内为 venv 标准链接）、无 submodule、无 local path dependency、无 HFB runtime HTTP

**Permanent HFB Runtime Dependency: NO**

## 17. Scope Boundary

- **Core Domain Migration: NO**（Person/Book/Evidence/Citation/Publication/Media/Teaching/RBAC/Research/Workspace 均未迁入；唯一关键词命中为 Batch 1 通用 `PermissionException` 异常类，非权限实现）
- **Phase 1 Business Coding: NO**（G1/G2/G3/G4/G7 未实现）
- 新增业务 API：无（/version /live /config 为通用基础设施端点）
