# HFM Phase 0.3 — Batch 4 Remaining Asset Audit

Date: 2026-08-27 · Phase 0.3 — SELECTIVE ASSET MIGRATION — BATCH 4（末轮）
起始基线：`c7ec91ac6dc8667dc1c2b9cd73e386a8745024eb`（Batch 3 Migration Baseline）
HFB Source Snapshot：`03755b57ec0e4c8023d1447619f7d6ead9e44d73`（固定只读）
授权：BATCH 4 AUTHORIZED BY THIS TASK；PHASE 1 BUSINESS CODING NOT AUTHORIZED

## 审计目的

Frozen Reuse Matrix（22 项能力）中哪些已由 Batch 1/2/3 覆盖、哪些仍未处理、哪些值得在 Phase 0.3 迁移、哪些应留到领域/Phase 1 阶段。

## 1. Frozen Reuse Matrix 能力覆盖矩阵

| Asset Family | Matrix Verdict | B1 | B2 | B3 | Remaining | Coupling | Phase | Decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Authentication | REUSE | — | — | — | YES | HIGH | Phase 1 | DOMAIN_DEFERRED（§12 Auth/RBAC 红线） |
| RBAC | EXTEND | — | — | — | YES | HIGH | Phase 1 | DOMAIN_DEFERRED（§12） |
| Person | REUSE | — | — | — | YES | HIGH | 领域实现 | DOMAIN_DEFERRED |
| Ancient Text | EXTEND | — | — | — | YES | HIGH | 领域实现 | DOMAIN_DEFERRED |
| Source | REUSE | — | — | — | YES | HIGH | 领域实现 | DOMAIN_DEFERRED |
| Evidence | REUSE | — | — | — | YES | HIGH | 领域实现 | DOMAIN_DEFERRED |
| Citation | REUSE | — | — | — | YES | HIGH | 领域实现 | DOMAIN_DEFERRED |
| Reader | EXTEND | — | — | — | YES | HIGH | 领域实现 | DOMAIN_DEFERRED |
| Library | EXTEND | — | — | — | YES | HIGH | 领域实现 | DOMAIN_DEFERRED |
| Search | EXTEND | — | — | — | YES | HIGH | 领域实现 | DOMAIN_DEFERRED |
| Knowledge | REUSE | — | — | — | YES | HIGH | 领域实现 | DOMAIN_DEFERRED |
| Workspace | REUSE | — | — | — | YES | HIGH | 领域实现 | DOMAIN_DEFERRED |
| Workflow | REUSE | — | — | — | YES | HIGH | 领域实现 | DOMAIN_DEFERRED |
| Reports | REUSE | — | — | — | YES | HIGH | 领域实现 | DOMAIN_DEFERRED |
| Export | EXTEND | — | — | — | YES | HIGH（业务逻辑） | 领域实现 | DOMAIN_DEFERRED |
| AI Copilot | EXTEND | — | — | — | YES | HIGH | 领域实现 | DOMAIN_DEFERRED |
| Audit | EXTEND | — | — | — | YES | HIGH（领域审计模型） | 领域实现 | DOMAIN_DEFERRED（B3 已审计，无通用原语） |
| Media | DEPRECATE/NEW | — | — | — | YES | HIGH | Phase 1（G4） | PHASE1_DEFERRED |
| Rights | EXTEND | — | — | — | YES | HIGH | Phase 1（G4/G13） | PHASE1_DEFERRED |
| Publication | NEW | — | — | — | YES | HIGH | Phase 1（G3） | PHASE1_DEFERRED |
| Snapshot | EXTEND | — | — | — | YES | HIGH | Phase 1（G3） | PHASE1_DEFERRED |
| Teaching | EXTEND | — | — | — | YES | HIGH | Phase 1（G1） | PHASE1_DEFERRED |

结论：22 项矩阵能力全部为**核心领域或 Phase 1 Deliverables**，无一项属于 Phase 0.3 可迁移的 LOW-coupling shared asset。

## 2. 共享基础能力覆盖（Batch 1–3 已建 + A–J 区域审计）

| Asset Family（A–J 区域） | B1 | B2 | B3 | Remaining | Coupling | Phase | Decision |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Hashing / canonical serialization（A/B） | ✓ hashing.py | — | — | NO | — | — | ALREADY_COVERED |
| Structured logging / observability 基础（I） | ✓ logging.py | — | — | NO（无独立 observability 栈；仅基础 logging） | — | — | ALREADY_COVERED |
| API response envelope（F） | ✓ response.py | ✓ types/api.ts | — | NO | — | — | ALREADY_COVERED |
| Exceptions / error handlers / request-id（F） | ✓ exceptions/error_handlers/request_id | — | — | NO | — | — | ALREADY_COVERED |
| Pagination / query contract（F） | — | ✓ schemas/common.py | — | NO | — | — | ALREADY_COVERED |
| Frontend presentation-independent utils（G） | ✓ misc.ts | ✓ useToast/useTheme/useFocusTrap | ✓ errors.ts | NO（剩余均领域） | — | — | ALREADY_COVERED |
| System / runtime primitives（F） | — | — | ✓ system.py | NO | — | — | ALREADY_COVERED |
| Test infrastructure（H） | — | — | ✓ test-setup.ts | NO | — | — | ALREADY_COVERED |
| Generic validation primitives（A） | — | — | — | NO（HFB 无独立通用验证原语；校验内嵌领域 schema） | — | — | REJECT |
| Generic temporal/date primitives（D） | — | — | — | NO（HFB 无独立日期工具；_now_iso 已随 B1 迁移） | — | — | REJECT |
| Generic identifier primitives（E） | ✓ misc.ts（generateId） | — | — | uuid7 位于 `db/base.py`（DB 耦合） | MEDIUM | Phase 1（PG 基座） | DOMAIN_DEFERRED |
| Generic safe file/path primitives（C） | — | — | — | NO（MIME/filename 均内嵌领域端点，B2/B3 已审计 REJECT） | HIGH | — | REJECT |
| Generic test/assertion helpers（H） | — | — | — | NO（conftest 领域耦合 B1 REJECT；test-setup 已迁） | HIGH | — | REJECT |
| BaseRepository CRUD | — | — | — | 依赖 SQLAlchemy async + soft-delete Base | MEDIUM | Phase 1（PG） | DOMAIN_DEFERRED |
| Settings / config pattern | — | — | — | HFB 基础设施设置 | MEDIUM | Phase 1 | DOMAIN_DEFERRED（B1–B3 结转） |
| Frontend HTTP client / fetchWithRetry | — | — | — | axios + auth 语义 | HIGH | — | DOMAIN_DEFERRED（B1–B3 结转，axios 不在 Frozen 基线） |
| Infra check framework / ready 聚合 | — | — | — | PG/Redis/ES/MinIO 检查 | HIGH | Phase 1（infra） | PHASE1_DEFERRED（B3 结转） |
| packages/ui placeholder | — | — | — | 空占位 | LOW | — | REFERENCE_ONLY（B3 已记录） |

## Audit Population Definition

本轮审计对象为两个可复核集合：

```text
Set A — Frozen Reuse Matrix capabilities:
22（RA-001 … RA-022）

Set B — Shared-asset source search findings（A–J 区域 + 共享基础家族）:
18（RA-023 … RA-040）

Intersection（A ∩ B）:
0（矩阵能力为领域能力，共享家族为基础设施，无重叠；无 BOTH 项）

Unique audit entries（A ∪ B）:
40（RA-001 … RA-040）
```

集合语义：同一能力若同时出现在 Matrix 与 A–J 搜索，标记 Source Set = BOTH 且只计一次；本审计无 BOTH 项，故 unique = 22 + 18 = 40。

## 逐项审计表（RA-001 … RA-040）

| Audit ID | Asset / Capability | Source Set | HFB Evidence | Previous Batch | Category | Coupling | Phase | Final Decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RA-001 | Authentication | FROZEN_MATRIX | `api/v1/auth.py` + `middleware/auth.py` | NONE | CORE_DOMAIN | HIGH | Phase 1（§12 Auth/RBAC 红线） | DOMAIN_DEFERRED |
| RA-002 | RBAC | FROZEN_MATRIX | `db/seed_rbac.py` | NONE | CORE_DOMAIN | HIGH | Phase 1（§12） | DOMAIN_DEFERRED |
| RA-003 | Person | FROZEN_MATRIX | `models/person.py` | NONE | CORE_DOMAIN | HIGH | 领域实现 | DOMAIN_DEFERRED |
| RA-004 | Ancient Text | FROZEN_MATRIX | `models/bibliographic.py` | NONE | CORE_DOMAIN | HIGH | 领域实现 | DOMAIN_DEFERRED |
| RA-005 | Source | FROZEN_MATRIX | `models/source_admission.py` | NONE | CORE_DOMAIN | HIGH | 领域实现 | DOMAIN_DEFERRED |
| RA-006 | Evidence | FROZEN_MATRIX | `models/academic_evidence.py` | NONE | CORE_DOMAIN | HIGH | 领域实现 | DOMAIN_DEFERRED |
| RA-007 | Citation | FROZEN_MATRIX | `models/academic_evidence.py` | NONE | CORE_DOMAIN | HIGH | 领域实现 | DOMAIN_DEFERRED |
| RA-008 | Reader | FROZEN_MATRIX | `pages/reader/ReaderPage.vue` | NONE | CORE_DOMAIN | HIGH | 领域实现 | DOMAIN_DEFERRED |
| RA-009 | Library | FROZEN_MATRIX | `pages/library/*` | NONE | CORE_DOMAIN | HIGH | 领域实现 | DOMAIN_DEFERRED |
| RA-010 | Search | FROZEN_MATRIX | `services/search_service.py` | NONE | CORE_DOMAIN | HIGH | 领域实现 | DOMAIN_DEFERRED |
| RA-011 | Knowledge | FROZEN_MATRIX | `pages/knowledge/*` | NONE | CORE_DOMAIN | HIGH | 领域实现 | DOMAIN_DEFERRED |
| RA-012 | Workspace | FROZEN_MATRIX | `models/workspace.py` | NONE | CORE_DOMAIN | HIGH | 领域实现 | DOMAIN_DEFERRED |
| RA-013 | Workflow | FROZEN_MATRIX | `services/research_workflow_service.py` | NONE | CORE_DOMAIN | HIGH | 领域实现 | DOMAIN_DEFERRED |
| RA-014 | Reports | FROZEN_MATRIX | `pages/reports/*` | NONE | CORE_DOMAIN | HIGH | 领域实现 | DOMAIN_DEFERRED |
| RA-015 | Export | FROZEN_MATRIX | `export_run_markdown` | NONE | CORE_DOMAIN | HIGH | 领域实现 | DOMAIN_DEFERRED |
| RA-016 | AI Copilot | FROZEN_MATRIX | `services/ai_service.py` | NONE | CORE_DOMAIN | HIGH | 领域实现 | DOMAIN_DEFERRED |
| RA-017 | Audit | FROZEN_MATRIX | `models/*audit*.py`（领域审计模型） | NONE | CORE_DOMAIN | HIGH | 领域实现（B3 已审计，无通用原语） | DOMAIN_DEFERRED |
| RA-018 | Media | FROZEN_MATRIX | `PersonIntroView.vue`（静态媒体引用） | NONE | PHASE1_DELIVERABLE | HIGH | Phase 1（G4） | PHASE1_DEFERRED |
| RA-019 | Rights | FROZEN_MATRIX | `models/document.py`（权利字段） | NONE | PHASE1_DELIVERABLE | HIGH | Phase 1（G4/G13） | PHASE1_DEFERRED |
| RA-020 | Publication | FROZEN_MATRIX | `models/production_promotion.py` | NONE | PHASE1_DELIVERABLE | HIGH | Phase 1（G3） | PHASE1_DEFERRED |
| RA-021 | Snapshot | FROZEN_MATRIX | `services/generation_proof.py` | NONE | PHASE1_DELIVERABLE | HIGH | Phase 1（G3） | PHASE1_DEFERRED |
| RA-022 | Teaching | FROZEN_MATRIX | `api/v4/education.py` | NONE | PHASE1_DELIVERABLE | HIGH | Phase 1（G1） | PHASE1_DEFERRED |
| RA-023 | Hashing / canonical serialization | SHARED_ASSET_SEARCH | `core/canonical_hash.py` | B1 | ALREADY_COVERED | LOW | 已迁移 | ALREADY_MIGRATED |
| RA-024 | Structured logging / observability base | SHARED_ASSET_SEARCH | `core/logging.py` | B1 | ALREADY_COVERED | LOW | 已迁移 | ALREADY_MIGRATED |
| RA-025 | API response envelope | SHARED_ASSET_SEARCH | `utils/response.py` | B1/B2 | ALREADY_COVERED | LOW | 已迁移 | ALREADY_MIGRATED |
| RA-026 | Exceptions / error handlers / request-id | SHARED_ASSET_SEARCH | `core/exceptions.py` + `core/error_handlers.py` + `middleware/request_id.py` | B1 | ALREADY_COVERED | LOW | 已迁移 | ALREADY_MIGRATED |
| RA-027 | Pagination / query contract | SHARED_ASSET_SEARCH | `schemas/common.py` | B2 | ALREADY_COVERED | LOW | 已迁移 | ALREADY_MIGRATED |
| RA-028 | Frontend presentation-independent utils | SHARED_ASSET_SEARCH | `packages/utils` + `composables/useToast\|useTheme\|useFocusTrap` | B1/B2 | ALREADY_COVERED | LOW | 已迁移 | ALREADY_MIGRATED |
| RA-029 | Error normalization | SHARED_ASSET_SEARCH | `api/client.ts`（getApiErrorDetail） | B3 | ALREADY_COVERED | LOW | 已迁移 | ALREADY_MIGRATED |
| RA-030 | System / runtime endpoints | SHARED_ASSET_SEARCH | `api/version.py` | B3 | ALREADY_COVERED | LOW | 已迁移 | ALREADY_MIGRATED |
| RA-031 | Test infrastructure | SHARED_ASSET_SEARCH | `test-setup.ts` | B3 | ALREADY_COVERED | LOW | 已迁移 | ALREADY_MIGRATED |
| RA-032 | Generic validation primitives | SHARED_ASSET_SEARCH | 无独立通用实现（校验内嵌领域 schema） | NONE | REJECTED_AS_NON_REUSABLE | N/A | — | NOT_A_MIGRATION_ASSET |
| RA-033 | Generic temporal/date primitives | SHARED_ASSET_SEARCH | 无独立日期工具（_now_iso 已随 B1 迁移） | NONE | REJECTED_AS_NON_REUSABLE | N/A | — | NOT_A_MIGRATION_ASSET |
| RA-034 | Generic identifier primitives | SHARED_ASSET_SEARCH | `packages/utils`（generateId）+ `db/base.py`（uuid7） | B1 | ALREADY_COVERED（generateId；uuid7 属 DB 基座） | LOW | 已迁移（部分） | ALREADY_MIGRATED |
| RA-035 | Generic safe file/path primitives | SHARED_ASSET_SEARCH | MIME/filename 均内嵌领域端点 | NONE | REJECTED_AS_NON_REUSABLE | HIGH | — | NOT_A_MIGRATION_ASSET |
| RA-036 | Generic test/assertion helpers | SHARED_ASSET_SEARCH | `tests/conftest.py`（领域耦合） | NONE | REJECTED_AS_NON_REUSABLE | HIGH | — | NOT_A_MIGRATION_ASSET |
| RA-037 | BaseRepository CRUD | SHARED_ASSET_SEARCH | `repositories/base.py` | NONE | PHASE1_DELIVERABLE（依赖 SQLAlchemy async + soft-delete Base） | MEDIUM | Phase 1（PG 基座） | PHASE1_DEFERRED |
| RA-038 | Settings / config pattern | SHARED_ASSET_SEARCH | `core/settings.py` + `config.py` | NONE | PHASE1_DELIVERABLE | MEDIUM | Phase 1 | PHASE1_DEFERRED |
| RA-039 | Frontend HTTP client / fetchWithRetry | SHARED_ASSET_SEARCH | `api/client.ts`（主体）+ `utils/fetchWithRetry.ts` | NONE | CORE_DOMAIN（auth 语义；axios 超 Frozen 基线） | HIGH | Phase 1 | DOMAIN_DEFERRED |
| RA-040 | packages/ui placeholder | SHARED_ASSET_SEARCH | `packages/ui/src/index.ts`（空占位） | NONE | REJECTED_AS_NON_REUSABLE | LOW | — | NOT_A_MIGRATION_ASSET |

统计：ALREADY_COVERED 10 · CORE_DOMAIN 18 · PHASE1_DELIVERABLE 7 · REJECTED_AS_NON_REUSABLE 5 = 40；Final Decision：ALREADY_MIGRATED 10 · DOMAIN_DEFERRED 18 · PHASE1_DEFERRED 7 · NOT_A_MIGRATION_ASSET 5 = 40。

## 3. 审计结论

**Unique Remaining-Asset Audit Entries: 40**（RA-001 … RA-040，逐项见上表）

- 共享基础层（RA-023–031、RA-034）已由 Batch 1–3 完整迁移（ALREADY_MIGRATED）。
- A–J 十区域无额外可分离 LOW-coupling 通用资产（RA-032/033/035/036/040 = NOT_A_MIGRATION_ASSET；RA-037/038 = PHASE1_DEFERRED；RA-039 = DOMAIN_DEFERRED）。
- 22 项矩阵能力（RA-001–022）全部属于核心领域或 Phase 1，Phase 0.3 不得迁移。
- **SHARED_ASSET_REMAINING = 0**

**PHASE0.3_SHARED_ASSET_COVERAGE = SUFFICIENT**
