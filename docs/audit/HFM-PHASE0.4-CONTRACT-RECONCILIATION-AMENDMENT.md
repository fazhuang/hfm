# HFM Phase 0.4 — Contract Reconciliation Amendment（Governance Candidate Report）

Date: 2026-08-28 · Phase 0.4 — Core Domain Contract Reconciliation Amendment
性质：GOVERNANCE CANDIDATE REPORT — 汇总 Amendment v0.2 候选的触发、裁决与门禁；**非冻结**

## 1. Amendment Identity

```text
Amendment:
docs/governance/HFM-PHASE0.4-CORE-DOMAIN-CONTRACT-AMENDMENT-v0.2.md

Type:
CONTRACT RECONCILIATION（治理语义修订；无生产代码/测试/迁移/数据变更）

Status:
IMPLEMENTED / AWAITING CODEX ACCEPTANCE（非 ACCEPTED / 非 FROZEN / 非 BASELINE）
```

## 2. Triggering Block

```text
Completion Final Audit:
BLOCK

Root-Cause Reconciliation Audit:
GOVERNANCE DECISION REQUIRED

CD Implementation Scope（Layer A）:
PASS

Frozen DAG:
EXHAUSTED（CD-0…CD-6；无 CD-7 定义）

Inventory Closure（Layer B）:
FAIL

Definition of Done（Layer C）:
FAIL

Frozen Contract Internal Consistency:
FAIL

P0: 1 — 无唯一、合法、可完成的 Phase 0.4 target
P1-1: CONTRACT INTERNAL CONFLICT / DAG DESIGN OMISSION
P1-2: DOD ASSIGNMENT OMISSION / EVIDENCE-ONLY GAP
```

## 3. Original Contract

```text
Core Domain Contract Baseline:
366df69715613022326eb7a3c06ae7f145ebacb9

8 份 v0.1 冻结文档（Scope / Canonical / Assertion / Lineage / Inventory / Migration Strategy / DAG / DoD）:
自 366df69 起零修改（diff 验证：Original Frozen File Changes: 0）
```

## 4. Conflict Matrix（摘要；详见 Amendment §4/§16）

```text
1. Inventory 28 verdicts ↔ DAG 6 节点不对齐（无 completion 归属）
2. Canonical 13 概念 ↔ DAG 无节点（Place/Concept/Acupoint/Manifestation/Book/…）
3. DoD dry-run obligation ↔ 无 execution owner（CD-7 不存在）
4. CA-002 EntityRelation 命名/排除/EventRelation/DAG 冲突
5. CA-026 桥 ownership 模糊
6. "CD-0…CD-6 PASS ⇒ Phase 0.4 PASS" 推导无效（缺三层闭合证明）
```

## 5. Inventory Reconciliation（28/28）

```text
IMPLEMENTED_CORE:                15（CA-001/003/004/005/007/008/012/014/015/019/020/021/022/023/024）
POST_PHASE_DEFERRED:             11（CA-002/006/009/010/011/013/016/017/018/027/028）
NON_RUNTIME_GOVERNANCE:           1（CA-025）
BRIDGE_FROZEN:                    1（CA-026）
COMPLETION_EVIDENCE:              0（作为独立 CA 行；义务整体承载于 CORE-COMPLETION evidence）
COMPLETION_IMPLEMENTATION_REQUIRED: 0（无 Frozen evidence 支撑的 mandatory missing runtime object）
                                 ———
合计:                             28 ✓

禁止使用的模糊态（不再使用）: DEFERRED / TBD / LATER / MAYBE
POST_PHASE_DEFERRED 语义（§12）: 非 Phase 0.4 completion 要求；本轮未授权；非静默放弃；
                                保留为未来受治理资产；后续需显式授权；不从历史 Inventory 删除
```

## 6. Canonical Boundary Reconciliation（12/12）

```text
Canonical Concepts Reconciled:  12
Canonical Concepts Ambiguous:    0

Place:        POST_PHASE_DEFERRED（Phase 0.4 要求 NO；post-Phase governed domain extension）
Concept:      POST_PHASE_DEFERRED
Acupoint:     POST_PHASE_DEFERRED（TCM/G1）
Manifestation: POST_PHASE_DEFERRED（Edition 承载）
Book:         POST_PHASE_DEFERRED（Work 承载）
ClassicalVersion: POST_PHASE_DEFERRED（Version 承载）
VersionRelation: POST_PHASE_DEFERRED（parent_version_id 承载 I2）
Sentence:     POST_PHASE_DEFERRED（Passage 覆盖）
Token:        POST_PHASE_DEFERRED（Passage 覆盖）
Variant:      POST_PHASE_DEFERRED（TEXTUAL Assertion 承载）
TextUnit:     Locator IMPLEMENTED_CORE；TextUnit model POST_PHASE_DEFERRED
Legacy Provenance: NON_RUNTIME_GOVERNANCE（migration-only）

SourceRef:    CLOSED（CA-020 IMPLEMENTED_CORE；不再进入待实现列表）
```

## 7. CA-026 Decision

```text
CA-026 Final Disposition:
BRIDGE_FROZEN

- opaque created_by 引用对 Phase 0.4 足够；无 User model；无 Auth/RBAC
- 未来身份绑定需另行显式治理
- Phase 1 G7 Separation of Duties: NOT IMPLEMENTED
```

## 8. Migration / DoD Decision

```text
Actual HFB Data Import Required for Phase 0.4 Completion: NO
Dry-Run Required: YES（DoD MANDATORY）
Reconciliation Required: YES（Migration Strategy §6）
Dry-Run Owner: CORE-COMPLETION
Isolation: 隔离测试库 / 临时一次性库 / 事务回滚；不写 live HFM；dry-run 报告通过后才允许 commit/import
Source Identity: 03755b57ec0e4c8023d1447619f7d6ead9e44d73（禁用 HFB current HEAD）
Reconciliation Counts（Strategy §6）: source / accepted / transformed / rejected / duplicate / target
                                      + hash/checksum（适用处）
Idempotency（Strategy §5）: CORE-COMPLETION acceptance gate（不暗示 actual import）
DoD obligation: 保留（Data migration dry-run complete 仍 MANDATORY）；owner 迁移至 CORE-COMPLETION
```

## 9. CORE-COMPLETION Definition

```text
治理标识: CORE-COMPLETION（唯一化；非 CD-7；不扩展 Frozen CD 序列）
性质: 仅用于关闭 inventory / migration evidence / 显式裁决的遗漏，在 Phase 0.4 Completion Freeze 之前
未来授权 Scope（精确定义）: governance/evidence assets · data migration dry-run · reconciliation ·
                          idempotency evidence · inventory closure evidence ·
                          （仅当治理裁决确认 mandatory missing runtime object 时）窄域补实现
禁止: Phase 1 / actual import / public portal / publication snapshot / medical compliance /
      Auth/RBAC / ICH media / teaching / "finish whatever is missing"

本轮状态:
CORE-COMPLETION: NOT AUTHORIZED
```

## 10. Phase Boundary

```text
Phase 1: NOT AUTHORIZED（Amendment 被 ACCEPTED 也不自动开始）
Phase 0.4 Completion Freeze Gate（未来）: CD-0…CD-6 FROZEN + CORE-COMPLETION ACCEPTED +
  Inventory CLOSED + Canonical Boundary CLOSED + Dry-Run PASS + Reconciliation PASS +
  DoD PASS + I1-I6 PASS + Phase 1 Leakage NO
本轮: PHASE 0.4 COMPLETION FREEZE NOT AUTHORIZED
```

## 11. Precedence

```text
Amendment 显式裁决的事项: v0.2 治理
未触及的语义: 原 v0.1 Frozen Contract 保持权威
CD-7: NONEXISTENT（不新增；未来 DAG 扩展走独立 architecture change）
CD-0…CD-6: 保持有效冻结实现节点（不重新验收；过往 PASS 不伪造）
```

## 12. Consistency Gates

```text
Amended Inventory ↔ Completion Model: PASS
Amended Canonical Model ↔ Completion Model: PASS
Migration Strategy ↔ Completion Model: PASS
DoD ↔ Completion Model: PASS
Frozen Contract Internal Consistency After Amendment: PASS
```

## 13. File Scope

```text
Production Code Changes: 0
Test Changes: 0
Migration Changes: 0
Dependency Changes: 0
Configuration Changes: 0
Original Frozen File Semantic Changes: 0
Original Frozen File Changes: 0
git diff --check: PASS
```

## 14. Candidate Status

```text
PHASE 0.4 CONTRACT AMENDMENT:
IMPLEMENTED / AWAITING CODEX ACCEPTANCE

CORE-COMPLETION:
NOT AUTHORIZED

PHASE 0.4 COMPLETION FREEZE:
NOT AUTHORIZED

CD-7:
NONEXISTENT / NOT AUTHORIZED

PHASE 1:
NOT AUTHORIZED
```
