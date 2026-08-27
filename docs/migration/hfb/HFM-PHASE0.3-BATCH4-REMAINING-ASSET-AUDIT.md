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

## 3. 审计结论

- 共享基础层（hashing/logging/response/exceptions/error_handlers/request-id/pagination/types/composables/error-normalization/system/test-setup）已由 Batch 1–3 完整覆盖。
- A–J 十个区域在 HFB 固定 snapshot 中**不存在**额外的可分离 LOW-coupling 通用资产（validation/temporal/path 无独立通用实现；identifier 仅 DB 耦合 uuid7；observability 仅基础 logging；前端通用 utils 已全覆盖）。
- 22 项矩阵能力全部属于核心领域或 Phase 1（G1–G4），Phase 0.3 不得迁移。

**PHASE0.3_SHARED_ASSET_COVERAGE = SUFFICIENT**
