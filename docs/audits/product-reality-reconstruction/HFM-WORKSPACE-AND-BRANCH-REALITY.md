# HFM-WORKSPACE-AND-BRANCH-REALITY.md — 工作区与分支拓扑事实报告

## 1. 核心工作区事实核对

| 维度 | 当前事实 | 证据来源 |
|---|---|---|
| **ACTIVE_WORKTREE** | `/private/tmp/recovery/hfm-foundation` | `git rev-parse --show-toplevel` |
| **ACTIVE_BRANCH** | `recovery/hfm-foundation` | `git branch --show-current` |
| **ACTIVE_HEAD** | `1e9336e0b530764da3754de5c1c58650dc38fa60` | `git rev-parse HEAD` |
| **WORKTREE_CLEANLINESS** | CLEAN (无任何未提交修改，已提交审计文件除外) | `git status --short` |
| **OTHER_WORKTREES** | 无其他 git worktree (`git worktree list` 仅此 1 个) | `git worktree list --porcelain` |

---

## 2. 分支拓扑与恢复分支属性确认

经扫描远程及本地分支历史：
1. **远程跟踪的主线分支**：`origin/phase1/frontier-6-integration` (commit `40254eb`)。
2. **当前分支的演进关系**：
   - 当前分支 `recovery/hfm-foundation` 是由基线 `6efea54c7`（已冻结的实现基线）经治理修复演进而来。
   - 自 `6efea54` 之后累积了 7 个关键加固与运维补丁，最终指向 HEAD `1e9336e`。
   - 与历史的 `phase1/frontier-6-integration` 相比，`recovery/hfm-foundation` 包含了最新修正的运维门禁、生产发布初始化、单前端端口契约等修复，具备极高的稳定性和闭环度。

---

## 3. 双重现实风险裁决 (`RISK_OF_DUAL_REALITY`)

- **是否存在另一份并行竞争代码？**：
  历史分支中存在一些治理和过程归档分支，但其代码实现均早于基线 `6efea54`。
- **裁决结论**：
  **当前工作区 `/private/tmp/recovery/hfm-foundation` 上的 `recovery/hfm-foundation` 分支（HEAD: `1e9336e`）是当前唯一有效、最完整、最严密的 Release Candidate (候选发布版)。**
  不存在“另一份更新且正在竞争的产品实现”。
