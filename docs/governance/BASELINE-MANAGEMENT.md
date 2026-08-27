# HFM Baseline Management（基线管理）

Status: Active · Date: 2026-08-27 · Phase 0

## 基线关系（2026-08-27 冻结后）

| 基线 | 提交 | 含义 | 状态 |
| --- | --- | --- | --- |
| Repository Init Baseline（仓库初始化基线） | `82f5e64` | 仓库引导：README / AGENTS / 架构边界 v0.1 / ADR-0001 / 审计文档骨架 | Stable |
| Original Provisional Architecture Baseline（原始暂定架构基线） | `ba4f615` | HFM 技术基线 v1.0 + HFB Asset Reuse Matrix v1.0 | Historical（已被验证的治理进程取代） |
| Validated Phase 0 Governance HEAD（已验证 Phase 0 治理 HEAD） | `a6a83c0` | Codex 修正对齐（`344821a`）+ 候选绑定门禁证明（`a6a83c0`，G14/G15 关闭） | Validated |
| **Frozen Architecture Baseline（冻结架构基线）** | **本轮治理提交** | 通过 Codex 复验（Frozen Eligibility: ELIGIBLE）后正式冻结的 Phase 0 架构与技术决策 | **Frozen** |

## 冻结记录（Promotion Record）

- **日期**：2026-08-27（Phase 0）
- **验证方**：Codex Re-Acceptance — HFB Re-Acceptance: PASS；Reuse Matrix: VALID；Technical Baseline: VALID；Architecture Greenfield + Capability Brownfield: ALIGNED；Frozen Baseline Eligibility: **ELIGIBLE**
- **候选绑定**：HFB `03755b57ec0e4c8023d1447619f7d6ead9e44d73`；HFM 验证 HEAD `a6a83c06d3679373e710121746149553e49e0562`
- **冻结动作**：通过治理提交 `docs: freeze validated HFM architecture baseline` 完成；`ba4f615` 保持历史身份（Provisional），不改写历史。

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

## 后续准入

- **MONOREPO SKELETON**：ALLOWED（冻结后）
- **PI MIGRATION**：NOT ALLOWED — 须在 Skeleton 独立验收通过后另行授权
- **PHASE 1 BUSINESS CODING**：NOT ALLOWED

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
