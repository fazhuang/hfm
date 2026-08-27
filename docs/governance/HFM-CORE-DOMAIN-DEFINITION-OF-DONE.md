# HFM Core Domain Definition of Done

Status: Draft for Contract Review · Date: 2026-08-27 · Phase 0.4

## 1. DoD 清单（Core Domain 每个 CD 批次）

```text
Schema/model complete
Migration complete
Service/API complete
Tests complete
Provenance complete
Version reproducibility complete
No HFB runtime dependency
Data migration dry-run complete
Regression green
```

## 2. 语义说明

- **Provenance complete**：该批次所有 Assertion/记录可追踪 Source/Evidence（I1）。
- **Version reproducibility complete**：Citation/引用固定可复现版本（I2）。
- **No HFB runtime dependency**：迁移完成后 HFM runtime 不依赖 HFB（I6）。
- **Data migration dry-run complete**：dry-run 报告通过且 reconciliation 计数满足契约（§6）。
- **Regression green**：既有 HFM 全量门禁（ruff/mypy/pytest/vitest/eslint/vue-tsc/build）+ 前序 CD 批次回归通过。

## 3. 边界

- DoD **不要求** Phase 1 功能已实现（G1/G2/G3/G4/G7）。
- 每批验收经 Codex 独立裁决后冻结，方可进入下一 CD 批次。
