# HFM Baseline Management（基线管理）

Status: Active · Date: 2026-08-27 · Phase 0.3

## 基线关系（2026-08-27 冻结后）

| 基线 | 提交 | 含义 | 状态 |
| --- | --- | --- | --- |
| Repository Init Baseline（仓库初始化基线） | `82f5e64` | 仓库引导：README / AGENTS / 架构边界 v0.1 / ADR-0001 / 审计文档骨架 | Stable |
| Original Provisional Architecture Baseline（原始暂定架构基线） | `ba4f615` | HFM 技术基线 v1.0 + HFB Asset Reuse Matrix v1.0 | Historical（已被验证的治理进程取代） |
| Validated Phase 0 Governance HEAD（已验证 Phase 0 治理 HEAD） | `a6a83c0` | Codex 修正对齐（`344821a`）+ 候选绑定门禁证明（`a6a83c0`，G14/G15 关闭） | Validated |
| **Frozen Architecture Baseline（冻结架构基线）** | **本轮治理提交** | 通过 Codex 复验（Frozen Eligibility: ELIGIBLE）后正式冻结的 Phase 0 架构与技术决策 | **Frozen** |
| **Engineering Skeleton Baseline（工程骨架基线）** | **本轮治理提交** | 通过 Codex Skeleton Acceptance（VALIDATED_WITH_CORRECTIONS，P2 闭环）后正式冻结的 Phase 0.2 工程骨架 | **Frozen** |
| **Selective Migration Batch 1（选择性迁移批 1）** | **本轮治理提交** | Accepted Candidate `981030f`（PASS）归档后形成；后续 Batch 2 如获授权，必须从该治理提交开始 | **ACCEPTED / FROZEN** |
| **Selective Migration Batch 2（选择性迁移批 2）** | **本轮治理提交** | Accepted Candidate `c2f61d5`（PASS）归档后形成；后续 Batch 3 如获授权，必须从该治理提交开始 | **ACCEPTED / FROZEN** |
| **Selective Migration Batch 3（选择性迁移批 3）** | **本轮治理提交** | Final Acceptance Record `702211c`（PASS，P0/P1/P2=0）归档后形成；后续 Batch 4 如获授权，必须从该治理提交开始 | **ACCEPTED / FROZEN** |
| **Phase 0.3 Selective Shared Asset Migration（Phase 0.3 选择性共享资产迁移）** | **本轮治理提交** | Final Batch = Batch 4（PASS，零代码完成审计）；Phase 0.3 停止条件已满足，无 Batch 5 | **COMPLETE / FROZEN** |

## 冻结记录（Promotion Record）

- **日期**：2026-08-27（Phase 0）
- **验证方**：Codex Re-Acceptance — HFB Re-Acceptance: PASS；Reuse Matrix: VALID；Technical Baseline: VALID；Architecture Greenfield + Capability Brownfield: ALIGNED；Frozen Baseline Eligibility: **ELIGIBLE**
- **候选绑定**：HFB `03755b57ec0e4c8023d1447619f7d6ead9e44d73`；HFM 验证 HEAD `a6a83c06d3679373e710121746149553e49e0562`
- **冻结动作**：通过治理提交 `docs: freeze validated HFM architecture baseline` 完成；`ba4f615` 保持历史身份（Provisional），不改写历史。

## Engineering Skeleton 冻结记录（2026-08-27，Phase 0.2）

- **验证方**：Codex Skeleton Acceptance — VALIDATED_WITH_CORRECTIONS；P2 条件（Result SHA、frontend 5199 端口证据）全部 CLOSED；七项复验全部通过
- **Validated Candidate Record（已验证候选记录）**：`e7ac52bc3df9d8a7b6de4174de9bb2e3ae6c1aa7` — 身份为 **validated acceptance record**，非 Engineering Skeleton Baseline
- **Skeleton Implementation**：`6697529`
- **历史链**（未改写，无 squash/rebase/amend/force push）：`7e10920`（Frozen Architecture Baseline）→ `6697529`（Skeleton Implementation）→ `960cb3a`（P2 Correction）→ `ae3d4c6`（Terminal Acceptance Record）→ `4bf2d28`（Rebinding Record）→ `e7ac52b`（Self-Referenced Final Acceptance Record）
- **冻结动作**：治理提交 `docs: freeze validated HFM engineering skeleton baseline`；Engineering Skeleton Baseline SHA 采用自引用模式（this commit），提交后经 `git rev-parse HEAD` 记录实际 SHA 作为后续迁移任务的固定起始 SHA。

## Batch 1 迁移归档（2026-08-27，Phase 0.3）

```text
Selective Migration Batch 1
Accepted Candidate:
981030f61c2a8ef9fc524891de7be3e61cd7aae4

Acceptance:
PASS

Governance Record:
this commit
```

- **HFB Source**：`03755b57ec0e4c8023d1447619f7d6ead9e44d73`（完整 SHA）
- **验收依据**：`docs/audit/HFM-PHASE0.3-BATCH1-ACCEPTANCE.md`（FINAL VERDICT: PASS）
- **治理动作**：提交 `docs: archive accepted HFM migration batch 1`；本治理提交完成后其实际 SHA 为 **Batch 1 Migration Baseline**，后续 Batch 2（如获授权）必须从该基线开始，而非直接从 `981030f` 开始。

## Batch 2 迁移归档（2026-08-27，Phase 0.3）

```text
Selective Migration Batch 2

Starting Baseline:
45e6cc1e3bb91c3df5569fffade9bd95d48e5936

Accepted Candidate:
c2f61d51bc113f966f988eeb772036ad35412746

Acceptance:
PASS

Governance Record:
this commit
```

- **HFB Source Snapshot**：`03755b57ec0e4c8023d1447619f7d6ead9e44d73`（完整 SHA，与 Batch 1 一致）
- **验收依据**：`docs/audit/HFM-PHASE0.3-BATCH2-ACCEPTANCE.md`（FINAL VERDICT: PASS）
- **治理动作**：提交 `docs: archive accepted HFM migration batch 2`；本治理提交完成后其实际 SHA 为 **Batch 2 Migration Baseline**，后续 Batch 3（如获授权）必须从该基线开始，而非直接从 `c2f61d5` 开始。

## Batch 3 迁移归档（2026-08-27，Phase 0.3）

```text
Selective Migration Batch 3

Starting Migration Baseline:
b5388af0490f9d7b3e14b9a6f1f1ccff781e81c1

Implementation Candidate:
b3207edd16ed2478f6229fdc15dfafb21aec83ad

Final Acceptance Record:
702211cfa40075bc1ca4d5a0bef44450016c38e2

Acceptance:
PASS

P0:
0

P1:
0

P2:
0

Governance Record:
this commit
```

- **HFB Source Snapshot**：`03755b57ec0e4c8023d1447619f7d6ead9e44d73`（完整 SHA，与 Batch 1/2 一致）
- **验收依据**：`docs/audit/HFM-PHASE0.3-BATCH3-ACCEPTANCE.md`（FINAL VERDICT: PASS；P0/P1/P2=0）
- **Batch 3 摘要**：Candidates Audited 11 · Migrated Assets 3 · PORT 2 · ADAPT 1 · REFERENCE_ONLY 1 · DEFER 4 · REJECT 3 · HIGH Coupling Migrated 0 · Core Domain Migration NO · Phase 1 Business Coding NO · Permanent HFB Runtime Dependency NO
- **质量归档**：Ruff/Ruff Format/mypy/pytest/ESLint/Prettier/vue-tsc/Vitest/Build 全部 PASS；Batch 1/2 Regression PASS；Runtime Smoke PASS
- **非阻塞观察项（保留）**：Starlette/httpx Deprecation Warning — OPEN / NON-BLOCKING（不属 Batch 3 未关闭条件；禁止未经授权升级依赖解决）
- **治理动作**：提交 `docs: archive accepted HFM migration batch 3`；本治理提交完成后其实际 SHA 为 **Batch 3 Migration Baseline**，后续 Batch 4（如获授权）必须从该基线开始，而非直接从 `b3207ed` 或 `702211c` 开始。

## Phase 0.3 完成归档（2026-08-27）

```text
Phase 0.3 Selective Shared Asset Migration

Status:
COMPLETE / FROZEN

Final Batch:
Batch 4

Batch 4 Final Acceptance:
PASS

Final Acceptance Record:
docs/audit/HFM-PHASE0.3-BATCH4-ACCEPTANCE.md

Phase 0.3 Completion Governance Record:
this commit
```

- **Phase 0.3 Completion Baseline: this commit**（自引用；提交完成后经 `git rev-parse HEAD` 记录实际 SHA）
- **BATCH 5: NOT REQUIRED** — shared/foundation selective migration 已无继续批次的必要
- **CORE DOMAIN MIGRATION: NOT AUTHORIZED** · **PHASE 1 BUSINESS CODING: NOT AUTHORIZED** — Phase 0.3 COMPLETE 不自动授权下一阶段；下一阶段编号与范围由后续独立治理指令决定
- 非阻塞观察项（保留）：Starlette/httpx Deprecation Warning — OPEN / NON-BLOCKING（不属 Phase 0.3 未完成项）

## 冻结语义

**Frozen 表示**：当前 Phase 0 架构与技术决策已经冻结，可作为后续 Skeleton 和迁移工作的开发输入。

**Frozen 不表示**：

- 所有 Phase 1 功能已实现；
- G1/G2/G3/G4/G7 已完成；
- HFB 代码可以无条件迁移；
- HFM 可以开始业务开发。

## Gate 状态

### 已关闭 Entry Gates（Phase 1 编码准入门禁）

- **G14**：PG/ES/MinIO 可达的候选绑定验证环境 — CLOSED（四服务实测可达 + 候选绑定门禁证明，见 `docs/audit/HFD-PHASE0-GATE-PROOF.md`）
- **G15**：CI strict mypy 门禁 — CLOSED（HFB `03755b5` 修复，22 文件 PASS）

### Phase 1 Deliverables（不属于 Phase 0 未完成项）

- **G1** Medical Compliance（医学合规元数据与免责链路）
- **G2** Anonymous Access（匿名公众访问）
- **G3** Publication Snapshot（发布快照）
- **G4** ICH Media Governance（非遗媒体治理）
- **G7** Separation of Duties（职责分离）

## 后续准入（2026-08-27 更新）

- **MONOREPO SKELETON**：**FROZEN / VALIDATED**
- **HFB → HFM PI MIGRATION**：**BATCH 1 · 2 · 3 ACCEPTED / FROZEN**；**BATCH 4 NOT AUTHORIZED** — Batch 4 必须由后续独立指令明确授权（不得将 BATCH 4 = ELIGIBLE 自动改写为 ALLOWED）；仅允许执行已授权的独立迁移任务，不意味着可自行选择迁移内容、一次迁移多个业务域、开始 Phase 1、或创建 Publication / Media / Medical / Teaching 新业务实现
- **PHASE 1 BUSINESS CODING**：**NOT AUTHORIZED** — G1 / G2 / G3 / G4 / G7 仍为 Phase 1 Deliverables
- **BATCH 5**：**NOT REQUIRED**（shared/foundation selective migration 完成，无继续批次必要）；**CORE DOMAIN MIGRATION**：**NOT AUTHORIZED**（下一阶段编号与范围由后续独立治理指令决定）

## 变更规则（Frozen 之后）

- 任何架构基线变更须新增 ADR 并升版本号（v1.1、v2.0 …）；
- 不得静默替换；冻结期间变更走 ADR 裁决。

## 引用

- `docs/architecture/HFM-TECHNOLOGY-BASELINE.md`
- `docs/migration/hfb/HFB-ASSET-REUSE-MATRIX.md`
- `docs/audit/HFD-PHASE0-BASELINE-AUDIT.md` v1.1（HFB HEAD `2d98b610`）
- `docs/audit/HFD-PHASE0-DOMAIN-MAP.md` v1.1
- `docs/audit/HFD-PHASE0-CODEX-REACCEPTANCE.md`（VALIDATED_WITH_CORRECTIONS，2026-08-27）
- `docs/audit/HFD-PHASE0-GATE-PROOF.md`（G14/G15 关闭证明，2026-08-27）
- `docs/audit/HFM-PHASE0.2-SKELETON-IMPLEMENTATION.md`（Phase 0.2 骨架实现，2026-08-27）
- `docs/audit/HFM-PHASE0.2-CODEX-SKELETON-ACCEPTANCE.md`（CONDITIONAL PASS / VALIDATED_WITH_CORRECTIONS，P2 CLOSED，2026-08-27）
- `docs/migration/hfb/HFM-PHASE0.3-BATCH1-INVENTORY.md`（Batch 1 迁移清单，2026-08-27）
- `docs/audit/HFM-PHASE0.3-BATCH1-MIGRATION-IMPLEMENTATION.md`（Batch 1 实施报告，2026-08-27）
- `docs/audit/HFM-PHASE0.3-BATCH1-ACCEPTANCE.md`（Batch 1 验收归档，FINAL VERDICT: PASS，2026-08-27）
- `docs/migration/hfb/HFM-PHASE0.3-BATCH2-INVENTORY.md`（Batch 2 迁移清单，2026-08-27）
- `docs/audit/HFM-PHASE0.3-BATCH2-MIGRATION-IMPLEMENTATION.md`（Batch 2 实施报告，2026-08-27）
- `docs/audit/HFM-PHASE0.3-BATCH2-ACCEPTANCE.md`（Batch 2 验收归档，FINAL VERDICT: PASS，2026-08-27）
- `docs/migration/hfb/HFM-PHASE0.3-BATCH3-INVENTORY.md`（Batch 3 迁移清单，2026-08-27）
- `docs/audit/HFM-PHASE0.3-BATCH3-MIGRATION-IMPLEMENTATION.md`（Batch 3 实施报告，2026-08-27）
- `docs/audit/HFM-PHASE0.3-BATCH3-ACCEPTANCE.md`（Batch 3 验收归档，FINAL VERDICT: PASS，2026-08-27）
- `docs/migration/hfb/HFM-PHASE0.3-BATCH4-REMAINING-ASSET-AUDIT.md`（Batch 4 剩余资产审计，RA-001…RA-040，2026-08-27）
- `docs/audit/HFM-PHASE0.3-BATCH4-MIGRATION-IMPLEMENTATION.md`（Batch 4 实施报告，NO_MIGRATION_REQUIRED，2026-08-27）
- `docs/audit/HFM-PHASE0.3-BATCH4-ACCEPTANCE.md`（Batch 4 验收归档，FINAL VERDICT: PASS，2026-08-27）
