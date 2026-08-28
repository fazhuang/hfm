# HFM Phase 0.4 — CD-2 Acceptance Archive

Date: 2026-08-27 · Phase 0.4 — Core Domain Implementation CD-2
性质：GOVERNANCE-ONLY ACCEPTANCE ARCHIVE — 仅归档 Codex 最终独立验收事实，不重新解释、不重新设计 CD-2

## 1. Acceptance Identity

```text
Phase:
HFM Phase 0.4 — Core Domain Implementation CD-2

Acceptance Type:
FINAL INDEPENDENT IMPLEMENTATION ACCEPTANCE

Final Verdict:
PASS

HFM CD-2:
ACCEPTED

Starting CD-1 Implementation Baseline:
5d4790e7b4f5675def3811144f6b718fce20a064

Initial CD-2 Implementation Candidate:
4b5bccc8ef034612f45c328edee59ef401df6951

Accepted CD-2 Implementation Candidate:
2288979e7519833aea65707e45ad9c8f670a9c6f

Core Domain Contract Baseline:
366df69715613022326eb7a3c06ae7f145ebacb9

HFB Source Snapshot:
03755b57ec0e4c8023d1447619f7d6ead9e44d73
```

## 2. Candidate History（如实归档）

- `4b5bccc` = **Initial CD-2 Implementation Candidate**（pre-fix）。
- 首次 Codex 独立验收发现 P0×1（Passage 跨 Work 一致性）/ P1×3（lineage 强制、跨 Work 层级、protected guard）→ **BLOCK / REJECTED**。
- Pi 完成修正（跨 Work 校验、lineage 强制、immutable 守卫扩展；pytest 104→112）→ 修正提交 `2288979`。
- Codex 最终复验：**FINAL VERDICT: PASS / HFM CD-2: ACCEPTED**。
- 不掩盖初始 Candidate 历史；不将修正过程描述为一次性 PASS。

## 3. Scope Closure

```text
CD-2 Scope:
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
5

EXTEND:
0

ADAPT:
0

NEW:
6

Scope/Verdict Count Semantics:
CLEAR
```

Scope Item 与 asset verdict 属不同计数体系，不要求算术相等；未重新计算、未重新裁决 Frozen Inventory。

## 4. Accepted Core Objects

```text
Work
Edition
Version
Chapter
Passage
Locator reuse
```

以上仅代表 **Frozen CD-2 Scope**，不构成 Core Domain Complete。

## 5. Closed P0/P1 Findings（最终修正闭环）

```text
Cross-Work Consistency:
PASS（PassageRepository._validate_cross_work — test_passage_cross_work_version_rejected）

Lineage Enforcement:
PASS（Version/Edition/Chapter lineage 同域校验 + parent immutable — test_version_cross_edition_parent_rejected / test_edition_cross_work_lineage_rejected / test_chapter_cross_work_parent_rejected / test_version_parent_cycle_rejected）

Protected Immutable Guard:
PASS（version_id / parent_version_id / lineage_parent_edition_id / parent_id 纳入 immutable_fields — test_invariant_i4_protected_fields / test_cd2_protected_fields_guard / test_passage_pinned_version_update_rejected）
```

## 6. Core Invariant Status

```text
I1 Provenance:
NOT IN CD-2 SCOPE

I2 Version Reproducibility:
PASS

I3 Assertion Coexistence:
NOT IN CD-2 SCOPE

I4 No Silent Overwrite:
PASS

I5 Stable Identity:
PASS

I6 HFB Independence:
PASS
```

I2 冻结语义（已验收的版本可复现基础）：

```text
Version identity: stable
Version lineage: enforced
Lineage cycle protection: accepted
Passage version reference: pinned
Latest-version silent substitution: not permitted
Cross-work consistency: enforced
```

不扩展为未来 Citation 已实现。

## 7. Database / Migration Acceptance

```text
Migration:
0003_cd2_ancient_text

Database Migration Gate:
PASS

Fresh DB Migration:
PASS

Historical Migration Integrity:
PASS
（迁移链 0001 → 0002 → 0003 逐级验证；未修改任何 migration 文件）
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
```

（计数以 Accepted Candidate `2288979` 真实状态为准。）

## 9. Quality & Runtime Evidence（`2288979` 最终复验）

```text
Ruff: PASS
Ruff Format: PASS — 77 files
mypy: PASS — 73 files
pytest: PASS — 112
ESLint: PASS
Prettier: PASS
vue-tsc: PASS
Vitest: PASS — 24
Build: PASS

/health: PASS
/ready: PASS
/version: PASS
/live: PASS
/config: PASS
/config Secret Exposure: NO
X-Request-ID: PASS

CD-0 Regression: PASS
CD-1 Regression: PASS
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

属非阻塞工程维护观察项，不影响 CD-2 Contract correctness、Core invariants、migration correctness 或 acceptance；仍为 OPEN P3，本轮不修复。

## 11. Final Verdict

```text
P0: 0
P1: 0
P2: 0
P3: 1

FINAL VERDICT:
PASS

HFM CD-2:
ACCEPTED
```

## 12. Freeze Semantics

CD-2 Accepted/Frozen 表示：Frozen CD-2 Scope 9/9 完成；Work / Edition / Version / Chapter / Passage 基础完成；Version reproducibility / pinned version reference / lineage enforcement / cross-work consistency / protected immutable guard 已验收；P0/P1/P2=0，P3=1 非阻塞；可作为未来 CD-3 的依赖基础。

**不表示**：Entire Core Domain complete / I1 implemented / I3 implemented / Assertion / Evidence / SourceRef / Citation implemented / All HFB core data migrated / Public Portal / Publication Snapshot / Phase 1 started / CD-3 authorized。

## 13. Authorization Boundary

```text
CD-3:
NOT AUTHORIZED

CORE DOMAIN MIGRATION BEYOND CD-2:
NOT AUTHORIZED

PHASE 1 BUSINESS CODING:
NOT AUTHORIZED
```

Phase 1 Deliverables（G1–G4/G7）继续冻结，不属于本轮。
