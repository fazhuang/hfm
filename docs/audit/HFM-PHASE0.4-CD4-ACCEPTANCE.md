# HFM Phase 0.4 — CD-4 Acceptance Archive

Date: 2026-08-27 · Phase 0.4 — Core Domain Implementation CD-4
性质：GOVERNANCE-ONLY ACCEPTANCE ARCHIVE — 仅归档 Codex 最终独立验收事实，不重新解释、不重新设计 CD-4

## 1. Acceptance Identity

```text
Phase:
HFM Phase 0.4 — Core Domain Implementation CD-4

Acceptance Type:
FINAL INDEPENDENT IMPLEMENTATION ACCEPTANCE

Final Verdict:
PASS

HFM CD-4:
ACCEPTED

Starting CD-3 Implementation Baseline:
3e3945d754630e25b2f4c65228dbdb5d4beef35f

Initial CD-4 Implementation Candidate:
503a5adad919c2f16ca83e36ce8bed233a275531

Accepted CD-4 Implementation Candidate:
79cf3f7af2976c7b76fe0d15946922095c4ec9fa

Core Domain Contract Baseline:
366df69715613022326eb7a3c06ae7f145ebacb9

HFB Source Snapshot:
03755b57ec0e4c8023d1447619f7d6ead9e44d73
```

## 2. Candidate History（如实归档）

- `503a5ad` = **Initial CD-4 Implementation Candidate**（pre-fix）。
- 首次 Codex 独立验收发现 P1×2（① 内容字段直接 ORM 突变 + repository 改 confidence；② revision 可变）→ **BLOCK / REJECTED**。
- Pi 完成修正（value/object_entity_id/assertion_type/confidence/revision/created_by 纳入 immutable_fields + id-based @validates 守卫）→ 修正提交 `79cf3f7`。
- Codex 复验（Assertion Protected Content Guard / Revision-Mutation Semantics / Mutable Field Boundary 全部 PASS）：**FINAL VERDICT: PASS / HFM CD-4: ACCEPTED**。
- 不掩盖初始 Candidate 历史；不将修正过程描述为一次性 PASS。

## 3. Scope Closure

```text
CD-4 Scope:
CONFIRMED

Frozen Scope Items:
9

Implemented:
9

Deferred:
0

Unauthorized Additions:
0

Scope Completion:
PASS

REUSE:
0

EXTEND:
0

ADAPT:
1

NEW:
8

Scope/Verdict Count Semantics:
CLEAR
```

Scope Item 与 asset verdict 属不同计数体系；未重新计算、未重新裁决 Frozen Inventory。

## 4. Accepted Core Objects

```text
Assertion（subject_entity / predicate / value / object_entity / assertion_type /
          confidence / editorial_status / created_by / revision）
AssertionType / EditorialStatus / Confidence（枚举 + CHECK）
Assertion ↔ Evidence M:N（assertion_evidences join）
AssertionRepository
Migration 0005_cd4_assertion
```

以上仅代表 **Frozen CD-4 Scope**，不构成 Core Domain Complete。

## 5. Closed P1 Findings（最终修正闭环）

```text
P1-1 Protected Content Guard:
CLOSED — value / object_entity_id / assertion_type / confidence / created_by 纳入
immutable_fields + 统一 @validates（id-based：persisted 后任何变更拒绝，含 nullable
None→value 后期赋值）；repository 与直接 ORM 双层拒绝

P1-2 Revision Mutation Semantics:
CLOSED — revision 纳入 immutable_fields + @validates（修订 = 新建 Assertion，
永不在位修改）；editorial_status 保持唯一可变字段（研究编辑态转换）

复验：Assertion Protected Content Guard PASS / Assertion Mutable Field Boundary PASS /
Assertion Revision / Mutation Semantics PASS / I4 PASS
```

## 6. Core Invariant Status

```text
I1 Provenance:
PASS（CD-3 已冻结实现；回归）

I2 Version Reproducibility:
PASS（CD-2 已冻结实现；回归）

I3 Assertion Coexistence:
PASS（本批实现：冲突并存 / 不覆盖 / 无 UNIQUE(subject,predicate) / evidence 不静默替换）

I4 No Silent Overwrite:
PASS（全部内容字段 + confidence + revision + created_by protected — repository + model 双层）

I5 Stable Identity:
PASS

I6 HFB Independence:
PASS

Assertion → Subject Silent Projection:
NO（无回写唯一真值）
```

## 7. Database / Migration Acceptance

```text
Migration:
0005_cd4_assertion

Database Migration Gate:
PASS

Fresh DB Migration:
PASS

0001 → 0005: PASS
0002 → 0005: PASS
0003 → 0005: PASS
0004 → 0005: PASS

Historical Migration Integrity:
UNCHANGED（未修改 0001-0005 任何 migration 文件）
```

## 8. Boundary Compliance

```text
Data Import:
NOT PERFORMED

API Changes:
0

Frontend Business Changes:
0

Phase 1 Business Coding:
NO

Permanent HFB Runtime Dependency:
NO

HFB Auth Dependency:
NO（created_by 为引用占位，无 User FK）
```

## 9. Quality & Runtime Evidence（`79cf3f7` 最终复验）

```text
Ruff: PASS
Ruff Format: PASS — 90 files
mypy: PASS — 84 files
pytest: PASS — 152
ESLint: PASS
Prettier: PASS
vue-tsc: PASS
Vitest: PASS — 24 passed / 8 files
Build: PASS

/health: 200 · /ready: 200 · /version: 200 · /live: 200 · /config: 200
/config Secret Exposure: NO
X-Request-ID: PASS

CD-0 Regression: PASS
CD-1 Regression: PASS
CD-2 Regression: PASS
CD-3 Regression: PASS
```

## 10. Remaining P3 Observation

```text
Severity:
P3

Status:
OPEN / NON-BLOCKING

Acceptance Impact:
NONE

Observation:
Starlette/httpx deprecation warning
```

属非阻塞工程维护观察项；仍为 OPEN P3，不修复、不升级依赖。

## 11. Final Verdict

```text
P0: 0
P1: 0
P2: 0
P3: 1

FINAL VERDICT:
PASS

HFM CD-4:
ACCEPTED
```

## 12. Freeze Semantics

CD-4 Accepted/Frozen 表示：Frozen CD-4 Scope 9/9（Assertion 契约）已完成并通过 Codex 独立验收；I3 Assertion Coexistence 首次 APPLICABLE 并验收（冲突并存 / 不覆盖 / 无唯一约束 / evidence 不静默替换）；I4 内容字段 + confidence + revision + created_by 全部 protected；可作为未来 CD-5 的依赖基础。

**不表示**：Entire Core Domain complete / Citation implemented / Event/Place implemented / All HFB core data migrated / Public Portal / Publication Snapshot / Phase 1 started / CD-5 authorized。

## 13. Authorization Boundary

```text
CD-5:
NOT AUTHORIZED

CORE DOMAIN MIGRATION BEYOND CD-4:
NOT AUTHORIZED

PHASE 1 BUSINESS CODING:
NOT AUTHORIZED
```

Phase 1 Deliverables（G1–G4/G7）继续冻结，不属于本轮。
