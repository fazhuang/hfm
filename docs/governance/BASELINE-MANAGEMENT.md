# HFM Baseline Management（基线管理）

Status: Active · Date: 2026-08-27 · Phase 0

## 基线定义

| 基线 | 提交 | 含义 | 状态 |
| --- | --- | --- | --- |
| HFM 仓库初始化基线（Repository Init Baseline） | `82f5e64` | 仓库引导：README / AGENTS / 架构边界 v0.1 / ADR-0001 / 审计文档骨架 | 稳定 |
| Provisional Architecture Baseline（暂定架构基线） | `ba4f615` | HFM 技术基线 v1.0 + HFB Asset Reuse Matrix v1.0 | **Provisional（暂定）** |

## 升级规则

- `ba4f615`（Provisional Architecture Baseline）在 **Codex HFB Re-Acceptance 通过**后升级为 **Frozen Architecture Baseline**；
- Codex 复核对象：`BASELINE-AUDIT v1.1` + `DOMAIN-MAP v1.1` 的结论与 `ba4f615` 暂定裁决的一致性（判定、证据链、验证分层）；
- 升级动作：将本页与两份交付物中的状态从 Provisional 改为 Frozen，并记录 Codex 复核绑定信息。

## 变更规则（升级为 Frozen 之后）

- 任何架构基线变更须新增 ADR 并升版本号（v1.1、v2.0 …）；
- 不得静默替换；冻结期间变更走 ADR 裁决。

## 引用

- `docs/architecture/HFM-TECHNOLOGY-BASELINE.md`
- `docs/migration/hfb/HFB-ASSET-REUSE-MATRIX.md`
- `docs/audit/HFD-PHASE0-BASELINE-AUDIT.md` v1.1（HFB HEAD `2d98b610`）
- `docs/audit/HFD-PHASE0-DOMAIN-MAP.md` v1.1
