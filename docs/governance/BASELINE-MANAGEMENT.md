# HFM Baseline Management（基线管理）

Status: Active · Date: 2026-08-27 · Phase 0.4

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
| **Phase 0.4 Core Domain Contract（Core Domain 契约）** | **本轮治理提交** | Accepted Candidate `39b2a91`（FINAL CONTRACT ACCEPTANCE，PASS，P0/P1/P2=0）归档后形成；后续 CD-0 如获授权，必须从该治理提交开始 | **ACCEPTED / FROZEN** |
| **Phase 0.4 — Core Domain Implementation CD-0** | **本轮治理提交** | Accepted Candidate `e1c33af`（FINAL IMPLEMENTATION ACCEPTANCE，PASS，P0/P1/P2=0）归档后形成；后续 CD-1 如获授权，必须从该治理提交开始 | **ACCEPTED / FROZEN** |
| **Phase 0.4 — Core Domain Implementation CD-1** | **本轮治理提交** | Accepted Candidate `7402ce5`（FINAL INDEPENDENT IMPLEMENTATION ACCEPTANCE，PASS，P0/P1/P2/P3=0）归档后形成；后续 CD-2 如获授权，必须从该治理提交开始 | **ACCEPTED / FROZEN** |
| **Phase 0.4 — Core Domain Implementation CD-2** | **本轮治理提交** | Accepted Candidate `2288979`（FINAL INDEPENDENT IMPLEMENTATION ACCEPTANCE，PASS，P0/P1/P2=0，P3=1 非阻塞）归档后形成；后续 CD-3 如获授权，必须从该治理提交开始 | **ACCEPTED / FROZEN** |
| **Phase 0.4 — Core Domain Implementation CD-3** | **本轮治理提交** | Accepted Candidate `6528ab0`（FINAL INDEPENDENT IMPLEMENTATION ACCEPTANCE，PASS，P0/P1/P2=0，P3=1 非阻塞）归档后形成；后续 CD-4 如获授权，必须从该治理提交开始 | **ACCEPTED / FROZEN** |
| **Phase 0.4 — Core Domain Implementation CD-4** | **本轮治理提交** | Accepted Candidate `79cf3f7`（FINAL INDEPENDENT IMPLEMENTATION ACCEPTANCE，PASS，P0/P1/P2=0，P3=1 非阻塞）归档后形成；后续 CD-5 如获授权，必须从该治理提交开始 | **ACCEPTED / FROZEN** |
| **Phase 0.4 — Core Domain Implementation CD-5** | **本轮治理提交** | Accepted Candidate `523294a`（FINAL INDEPENDENT IMPLEMENTATION ACCEPTANCE，PASS，P0/P1/P2=0，P3=1 非阻塞）归档后形成；后续 CD-6 如获授权，必须从该治理提交开始 | **ACCEPTED / FROZEN** |

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

## Phase 0.4 Core Domain Contract 冻结（2026-08-27）

```text
Phase 0.4 Core Domain Contract

Status:
ACCEPTED / FROZEN

Accepted Candidate:
39b2a91e1f2bb0719202705636ce3a2bed0ee7f9

Final Acceptance:
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

- **Core Domain Contract Baseline: this commit**（自引用；提交完成后经 `git rev-parse HEAD` 记录实际 SHA）
- **First Recommended Core Batch: CD-0** — Authorization: **NOT AUTHORIZED**（不得出现 CD-0 ALLOWED）
- **冻结语义**：Core Domain Scope / Canonical Model / Assertion Contract / Evidence Lineage / Migration DAG / Migration Strategy / Definition of Done 已完成独立验收，可作为后续 Core Domain 实施的形式规范输入。**不表示**：Core Domain 已实现、DB schema 已建立、数据已迁移、CD-0 已授权、Phase 1 已开始、Public API 已确定、Publication 已实现。
- **验收归档**：`docs/audit/HFM-PHASE0.4-CORE-DOMAIN-CONTRACT-ACCEPTANCE.md`

## Phase 0.4 CD-0 冻结（2026-08-27）

```text
Phase 0.4 — Core Domain Implementation CD-0

Status:
ACCEPTED / FROZEN

Starting Contract Baseline:
366df69715613022326eb7a3c06ae7f145ebacb9

Accepted Candidate:
e1c33afd8c2ea4f8962145d4398535c49cbad088

Final Acceptance:
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

- **CD-0 Implementation Baseline: this commit**（自引用；提交完成后经 `git rev-parse HEAD` 记录实际 SHA）
- **冻结语义**：CD-0 Frozen Scope 已完成实现并通过独立验收，可作为下一 Core Domain 批次的稳定基础。**不表示**：整个 Core Domain 已完成、CD-1 已授权、Assertion/Evidence 全部实现、HFB Core 数据已全部迁移、Public Portal 已实现、Phase 1 已启动。
- **验收归档**：`docs/audit/HFM-PHASE0.4-CD0-ACCEPTANCE.md`（P1 Immutable Source Identity CLOSED；Scope 8/8；I1/I4/I5/I6 PASS，I2/I3 NOT IN CD-0 SCOPE）

## Phase 0.4 CD-1 冻结（2026-08-27）

```text
Phase 0.4 — Core Domain Implementation CD-1

Status:
ACCEPTED / FROZEN

Starting Baseline:
504e45e2d707b7e439e8b2610c109f30fa581f65

Accepted Candidate:
7402ce5e6a86a11b9526e8985bc82957b04b7009

Final Acceptance:
PASS

P0:
0

P1:
0

P2:
0

P3:
0

Governance Record:
this commit
```

- **CD-1 Implementation Baseline: this commit**（自引用；提交完成后经 `git rev-parse HEAD` 记录实际 SHA）
- **冻结语义**：Frozen CD-1 Scope（Entity/EntityType/Person + repository + migration 0002 + invariants I4/I5/I6）已完成并通过 Codex 独立验收，可作为下一 Core Domain 批次的稳定基础。**不表示**：整个 Core Domain 已完成、I1/I2/I3 已实现、Assertion/Evidence/Citation/SourceRef 已实现、CD-2 已授权、Core Domain 全量迁移已授权、Phase 1 已启动。
- **验收归档**：`docs/audit/HFM-PHASE0.4-CD1-ACCEPTANCE.md`（Scope 8/8；Scope/Verdict Count Semantics CLEAR；I1/I2/I3 NOT IN CD-1 SCOPE）

## Phase 0.4 CD-2 冻结（2026-08-27）

```text
Phase 0.4 — Core Domain Implementation CD-2

Status:
ACCEPTED / FROZEN

Starting Baseline:
5d4790e7b4f5675def3811144f6b718fce20a064

Initial Candidate:
4b5bccc8ef034612f45c328edee59ef401df6951

Accepted Candidate:
2288979e7519833aea65707e45ad9c8f670a9c6f

Final Acceptance:
PASS

P0:
0

P1:
0

P2:
0

P3:
1 — non-blocking Starlette/httpx deprecation warning

Governance Record:
this commit

CD-2 Implementation Baseline:
this commit
```

- **CD-2 Implementation Baseline: this commit**（自引用；提交完成后经 `git rev-parse HEAD` 记录实际 SHA；后续 CD-3 如获授权必须从此基线开始，不得从 `4b5bccc` 或 `2288979` 直接开始）
- **冻结语义**：Frozen CD-2 Scope 9/9（Work/Edition/Version/Chapter/Passage + Locator 复用）已完成并通过 Codex 独立验收；Version reproducibility / pinned reference / lineage enforcement / cross-work consistency / protected guard 已验收。**不表示**：Core Domain 完成、I1/I3 实现、Assertion/Evidence/SourceRef/Citation 实现、数据全部迁移、Public Portal、Publication Snapshot、Phase 1 启动、CD-3 授权。
- **验收归档**：`docs/audit/HFM-PHASE0.4-CD2-ACCEPTANCE.md`（P0/P1 修正闭环；I2/I4/I5/I6 PASS；I1/I3 NOT IN SCOPE；P3=1 OPEN/NON-BLOCKING）

## Phase 0.4 CD-3 冻结（2026-08-27）

```text
Phase 0.4 — Core Domain Implementation CD-3

Status:
ACCEPTED / FROZEN

Starting Baseline:
b545e5babfc8aa4b89f1488112c544afd927b4ba

Initial Candidate:
7a4e080c7b754f307bd7af64a804adb0199afc48

Accepted Candidate:
6528ab02e61461c739f029fedbcb7db2635c7647

Final Acceptance:
PASS

P0:
0

P1:
0

P2:
0

P3:
1 — non-blocking Starlette/httpx deprecation warning

Governance Record:
this commit

CD-3 Implementation Baseline:
this commit
```

- **CD-3 Implementation Baseline: this commit**（自引用；提交完成后经 `git rev-parse HEAD` 记录实际 SHA；后续 CD-4 如获授权必须从此基线开始，不得从 `7a4e080` 或 `6528ab0` 直接开始）
- **冻结语义**：Frozen CD-3 Scope 9/9（Evidence + EvidenceLevel + taint + content_hash）已完成并通过 Codex 独立验收；I1 Provenance 首次 APPLICABLE 并验收；content_hash 完整性 / protected guard / orphan 拒绝 / Evidence-Admission 解耦已验收。**不表示**：Core Domain 完成、I3 实现、Assertion/Citation 实现、数据全部迁移、Public Portal、Publication Snapshot、Phase 1 启动、CD-4 授权。
- **验收归档**：`docs/audit/HFM-PHASE0.4-CD3-ACCEPTANCE.md`（P1 content-hash 修正闭环；I1/I4/I5/I6 PASS；I3 NOT IN SCOPE；P3=1 OPEN/NON-BLOCKING）

## Phase 0.4 CD-4 冻结（2026-08-27）

```text
Phase 0.4 — Core Domain Implementation CD-4

Status:
ACCEPTED / FROZEN

Starting Baseline:
3e3945d754630e25b2f4c65228dbdb5d4beef35f

Initial Candidate:
503a5adad919c2f16ca83e36ce8bed233a275531

Accepted Candidate:
79cf3f7af2976c7b76fe0d15946922095c4ec9fa

Final Acceptance:
PASS

P0:
0

P1:
0

P2:
0

P3:
1 — non-blocking Starlette/httpx deprecation warning

Governance Record:
this commit

CD-4 Implementation Baseline:
this commit
```

- **CD-4 Implementation Baseline: this commit**（自引用；提交完成后经 `git rev-parse HEAD` 记录实际 SHA；后续 CD-5 如获授权必须从此基线开始，不得从 `503a5ad` 或 `79cf3f7` 直接开始）
- **冻结语义**：Frozen CD-4 Scope 9/9（Assertion 契约）已完成并通过 Codex 独立验收；I3 Assertion Coexistence 首次 APPLICABLE 并验收；I4 内容字段 + confidence + revision + created_by 全部 protected。**不表示**：Core Domain 完成、Citation/Event/Place 实现、数据全部迁移、Public Portal、Publication Snapshot、Phase 1 启动、CD-5 授权。
- **验收归档**：`docs/audit/HFM-PHASE0.4-CD4-ACCEPTANCE.md`（P1×2 修正闭环；I3/I4/I5/I6 PASS；I1/I2 回归 PASS）

## Phase 0.4 CD-6 冻结（2026-08-28）

```text
Phase 0.4 — Core Domain Implementation CD-6

Status:
ACCEPTED / FROZEN

Starting Baseline:
834ad1b47c6b5583dd840e670d9c7a65fad55356

Initial Candidate:
b593b93edf8665139b19b5d3829957c651ebbc0e

Accepted Candidate:
7bb6e2e1c15d62989e890cb36e97290df4142692

Final Acceptance:
PASS

P0:
0

P1:
0

P2:
0

P3:
1 — non-blocking Starlette/httpx deprecation warning

Governance Record:
this commit

CD-6 Implementation Baseline:
this commit
```

- **CD-6 Implementation Baseline: this commit**（自引用；提交完成后经 `git rev-parse HEAD` 记录实际 SHA；后续 CD-7 如获授权必须从此基线开始，不得从 `b593b93` 或 `7bb6e2e` 直接开始）
- **冻结语义**：Frozen CD-6 Scope 3/3（Event NEW + Person/Event 关系 ADAPT + 事件证据链）已完成并通过 Codex 独立验收；I1 本批 DIRECTLY APPLICABLE 并验收（聚合 subject 门禁 + SQLite 触发器）；I3 SUPPORTED。**不表示**：Core Domain 完成、Place 实现、数据全部迁移、Public Portal、Publication Snapshot、Phase 1 启动、CD-7 授权。
- **验收归档**：`docs/audit/HFM-PHASE0.4-CD6-ACCEPTANCE.md`（P1×1+P2×1 修正闭环；I1 本批验收；I2/I3/I4/I5/I6 PASS）

## Phase 0.4 CD-5 冻结（2026-08-27）

```text
Phase 0.4 — Core Domain Implementation CD-5

Status:
ACCEPTED / FROZEN

Starting Baseline:
82505d11d7f0591de1df342f03b4e78c5c4300a7

Initial Candidate:
c8a1be9552e51052b3dc483af8cc2ce6ddd2b14e

Accepted Candidate:
523294a292dc34ce69841355e9a6b3c7dd79dad0

Final Acceptance:
PASS

P0:
0

P1:
0

P2:
0

P3:
1 — non-blocking Starlette/httpx deprecation warning

Governance Record:
this commit

CD-5 Implementation Baseline:
this commit
```

- **CD-5 Implementation Baseline: this commit**（自引用；提交完成后经 `git rev-parse HEAD` 记录实际 SHA；后续 CD-6 如获授权必须从此基线开始，不得从 `c8a1be9` 或 `523294a` 直接开始）
- **冻结语义**：Frozen CD-5 Scope 9/9（Citation，target=Assertion）已完成并通过 Codex 独立验收；I2 Version Reproducibility 本批 DIRECTLY APPLICABLE 并验收；Source 撤回级联与 withdrawn Version 门禁已验收。**不表示**：Core Domain 完成、Event/Place 实现、数据全部迁移、Public Portal、Publication Snapshot、Phase 1 启动、CD-6 授权。
- **验收归档**：`docs/audit/HFM-PHASE0.4-CD5-ACCEPTANCE.md`（P1×2+P2 修正闭环；I2 本批验收；I1/I3/I4/I5/I6 PASS）

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
- **CD-0**：**NOT AUTHORIZED**（Core Domain Contract 已 FROZEN，但实施须另行独立授权）
- **CD-1**：**NOT AUTHORIZED**；**CORE DOMAIN MIGRATION BEYOND CD-0**：**NOT AUTHORIZED**（CD-0 已 ACCEPTED/FROZEN，后续批次须另行独立授权）
- **CD-2**：**NOT AUTHORIZED**；**CORE DOMAIN MIGRATION BEYOND CD-1**：**NOT AUTHORIZED**（CD-1 已 ACCEPTED/FROZEN，后续批次须另行独立授权）
- **CD-3**：**NOT AUTHORIZED**；**CORE DOMAIN MIGRATION BEYOND CD-2**：**NOT AUTHORIZED**（CD-2 已 ACCEPTED/FROZEN，后续批次须另行独立授权）
- **CD-4**：**NOT AUTHORIZED**；**CORE DOMAIN MIGRATION BEYOND CD-3**：**NOT AUTHORIZED**（CD-3 已 ACCEPTED/FROZEN，后续批次须另行独立授权）
- **CD-5**：**NOT AUTHORIZED**；**CORE DOMAIN MIGRATION BEYOND CD-4**：**NOT AUTHORIZED**（CD-4 已 ACCEPTED/FROZEN，后续批次须另行独立授权）
- **CD-6**：**NOT AUTHORIZED**；**CORE DOMAIN MIGRATION BEYOND CD-5**：**NOT AUTHORIZED**（CD-5 已 ACCEPTED/FROZEN，后续批次须另行独立授权）
- **CD-7**：**NOT AUTHORIZED**；**CORE DOMAIN MIGRATION BEYOND CD-6**：**NOT AUTHORIZED**（CD-6 已 ACCEPTED/FROZEN，后续批次须另行独立授权；Frozen DAG 仅定义 CD-0…CD-6）

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
- `docs/audit/HFM-PHASE0.4-CORE-DOMAIN-CONTRACT-ACCEPTANCE.md`（Phase 0.4 Core Domain Contract 验收归档，FINAL VERDICT: PASS，2026-08-27）
- `docs/migration/hfb/HFM-PHASE0.4-CD0-IMPLEMENTATION-SCOPE.md`（CD-0 Scope 提取 + Traceability Matrix，2026-08-27）
- `docs/audit/HFM-PHASE0.4-CD0-IMPLEMENTATION.md`（CD-0 实施报告，Scope 8/8，2026-08-27）
- `docs/audit/HFM-PHASE0.4-CD0-ACCEPTANCE.md`（CD-0 验收归档，FINAL VERDICT: PASS，P1 CLOSED，2026-08-27）
- `docs/migration/hfb/HFM-PHASE0.4-CD1-IMPLEMENTATION-SCOPE.md`（CD-1 Scope 提取 + Traceability Matrix，2026-08-27）
- `docs/audit/HFM-PHASE0.4-CD1-IMPLEMENTATION.md`（CD-1 实施报告，Scope 8/8，2026-08-27）
- `docs/audit/HFM-PHASE0.4-CD1-ACCEPTANCE.md`（CD-1 验收归档，FINAL VERDICT: PASS，2026-08-27）
- `docs/migration/hfb/HFM-PHASE0.4-CD2-IMPLEMENTATION-SCOPE.md`（CD-2 Scope 提取 + Traceability Matrix，2026-08-27）
- `docs/audit/HFM-PHASE0.4-CD2-IMPLEMENTATION.md`（CD-2 实施报告，Scope 9/9 + P0/P1 修正记录，2026-08-27）
- `docs/audit/HFM-PHASE0.4-CD2-ACCEPTANCE.md`（CD-2 验收归档，FINAL VERDICT: PASS，2026-08-27）
- `docs/migration/hfb/HFM-PHASE0.4-CD3-IMPLEMENTATION-SCOPE.md`（CD-3 Scope 提取 + Traceability Matrix，2026-08-27）
- `docs/audit/HFM-PHASE0.4-CD3-IMPLEMENTATION.md`（CD-3 实施报告，Scope 9/9 + P1 修正记录，2026-08-27）
- `docs/audit/HFM-PHASE0.4-CD3-ACCEPTANCE.md`（CD-3 验收归档，FINAL VERDICT: PASS，2026-08-27）
- `docs/migration/hfb/HFM-PHASE0.4-CD4-IMPLEMENTATION-SCOPE.md`（CD-4 Scope 提取 + Traceability Matrix，2026-08-27）
- `docs/audit/HFM-PHASE0.4-CD4-IMPLEMENTATION.md`（CD-4 实施报告，Scope 9/9 + P1×2 修正记录，2026-08-27）
- `docs/audit/HFM-PHASE0.4-CD4-ACCEPTANCE.md`（CD-4 验收归档，FINAL VERDICT: PASS，2026-08-27）
- `docs/migration/hfb/HFM-PHASE0.4-CD5-IMPLEMENTATION-SCOPE.md`（CD-5 Scope 提取 + Traceability Matrix，2026-08-27）
- `docs/audit/HFM-PHASE0.4-CD5-IMPLEMENTATION.md`（CD-5 实施报告，Scope 9/9 + P1×2+P2 修正记录，2026-08-27）
- `docs/audit/HFM-PHASE0.4-CD5-ACCEPTANCE.md`（CD-5 验收归档，FINAL VERDICT: PASS，2026-08-27）
- `docs/migration/hfb/HFM-PHASE0.4-CD6-IMPLEMENTATION-SCOPE.md`（CD-6 Scope 提取 + Traceability Matrix，2026-08-27）
- `docs/audit/HFM-PHASE0.4-CD6-IMPLEMENTATION.md`（CD-6 实施报告，Scope 3/3 + P1×1+P2×1 修正记录，2026-08-28）
- `docs/audit/HFM-PHASE0.4-CD6-ACCEPTANCE.md`（CD-6 验收归档，FINAL VERDICT: PASS，2026-08-28）
- `docs/domain/HFM-CORE-DOMAIN-SCOPE-v0.1.md` + `HFM-ASSERTION-CONTRACT-v0.1.md` + `HFM-EVIDENCE-LINEAGE-CONTRACT-v0.1.md` + `HFM-CANONICAL-DOMAIN-MODEL-v0.1.md`（Core Domain 契约集，2026-08-27）
- `docs/migration/hfb/HFM-PHASE0.4-CORE-ASSET-INVENTORY.md` + `HFM-CORE-DATA-MIGRATION-STRATEGY-v0.1.md` + `HFM-PHASE0.4-CORE-MIGRATION-DAG.md`（Core 迁移规划，2026-08-27）
- `docs/governance/HFM-CORE-DOMAIN-DEFINITION-OF-DONE.md` + `docs/audit/HFM-PHASE0.4-CORE-DOMAIN-RISK-REGISTER.md` + `docs/audit/HFM-PHASE0.4-CORE-DOMAIN-CONTRACT-AUDIT.md`（DoD/风险/审计，2026-08-27）
