# HFM Phase 0.4 — CD-3 Acceptance Archive

Date: 2026-08-27 · Phase 0.4 — Core Domain Implementation CD-3
性质：GOVERNANCE-ONLY ACCEPTANCE ARCHIVE — 仅归档 Codex 最终独立验收事实，不重新解释、不重新设计 CD-3

## 1. Acceptance Identity

```text
Phase:
HFM Phase 0.4 — Core Domain Implementation CD-3

Acceptance Type:
FINAL INDEPENDENT IMPLEMENTATION ACCEPTANCE

Final Verdict:
PASS

HFM CD-3:
ACCEPTED

Starting CD-2 Implementation Baseline:
b545e5babfc8aa4b89f1488112c544afd927b4ba

Initial CD-3 Implementation Candidate:
7a4e080c7b754f307bd7af64a804adb0199afc48

Accepted CD-3 Implementation Candidate:
6528ab02e61461c739f029fedbcb7db2635c7647

Core Domain Contract Baseline:
366df69715613022326eb7a3c06ae7f145ebacb9

HFB Source Snapshot:
03755b57ec0e4c8023d1447619f7d6ead9e44d73
```

## 2. Candidate History（如实归档）

- `7a4e080` = **Initial CD-3 Implementation Candidate**（pre-fix）。
- 首次 Codex 独立验收发现 P1×1（content_hash 覆盖可变内容 → 旧哈希残留；直接 ORM 可改 content_hash）→ **BLOCK / REJECTED**。
- Pi 完成修正（description/evidence_level 纳入 immutable_fields + @validates 三重守卫；pytest 130→131）→ 修正提交 `6528ab0`。
- Codex 复验（含直接 ORM probes：content_hash/description/evidence_level mutation 均 REJECTED）：**FINAL VERDICT: PASS / HFM CD-3: ACCEPTED**。
- 不掩盖初始 Candidate 历史；不将修正过程描述为一次性 PASS。

## 3. Scope Closure

```text
CD-3 Scope:
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
2

EXTEND:
0

ADAPT:
1

NEW:
3

Scope/Verdict Count Semantics:
CLEAR
```

Scope Item 与 asset verdict 属不同计数体系；未重新计算、未重新裁决 Frozen Inventory。

## 4. Accepted Core Objects

```text
Evidence（description + evidence_level LEVEL_1..4）
EvidenceLevel（REUSE）
SourceRef anchor（FK RESTRICT）
Passage anchor（FK SET NULL）
At-least-one-anchor（DB CHECK + repository guard）
content_hash（canonical hash integrity，protected）
Taint lifecycle（clean / source_withdrawn / quarantined）
EvidenceRepository
Migration 0004_cd3_evidence
```

以上仅代表 **Frozen CD-3 Scope**，不构成 Core Domain Complete。

## 5. Closed P1 Finding（最终修正闭环）

```text
P1 Content-Hash Integrity:
CLOSED

修复：
- description / evidence_level 纳入 immutable_fields（I4：修订 = 新建 evidence，非静默编辑）→ content_hash 永不过期
- 模型 @validates("content_hash") 守卫 — 直接 ORM 突变拒绝
- 防御纵深：@validates("description") / @validates("evidence_level")

复验（Codex 直接 ORM probes）：
content_hash mutation: REJECTED
description mutation: REJECTED
evidence_level mutation: REJECTED
repository content-field update: REJECTED
```

## 6. Core Invariant Status

```text
I1 Provenance:
PASS（Evidence → SourceRef → Source 溯源；至少一锚点；orphan 拒绝）

I2 Version Reproducibility:
PASS（CD-2 回归保持）

I3 Assertion Coexistence:
NOT IN CD-3 SCOPE（CD-4）

I4 No Silent Overwrite:
PASS（content/anchors/hash 全部 protected — repository + model 双层）

I5 Stable Identity:
PASS

I6 HFB Independence:
PASS
```

## 7. Database / Migration Acceptance

```text
Migration:
0004_cd3_evidence

Database Migration Gate:
PASS

Fresh DB Migration:
PASS

0001 → 0004: PASS
0002 → 0004: PASS
0003 → 0004: PASS

Historical Migration Integrity:
UNCHANGED（未修改 0001-0004 任何 migration 文件）
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

Evidence / Admission Decoupling:
PASS（无 review_status / publication_status 字段）
```

## 9. Quality & Runtime Evidence（`6528ab0` 最终复验）

```text
Ruff: PASS
Ruff Format: PASS — 83 files
mypy: PASS — 78 files
pytest: PASS — 131
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

属非阻塞工程维护观察项，不影响 CD-3 Contract correctness、Core invariants、migration correctness 或 acceptance；仍为 OPEN P3，不修复、不升级依赖。

## 11. Final Verdict

```text
P0: 0
P1: 0
P2: 0
P3: 1

FINAL VERDICT:
PASS

HFM CD-3:
ACCEPTED
```

## 12. Freeze Semantics

CD-3 Accepted/Frozen 表示：Frozen CD-3 Scope 9/9（Evidence + EvidenceLevel + taint + content_hash）已完成并通过 Codex 独立验收；I1 Provenance 首次 APPLICABLE 并验收；content_hash 完整性 / protected guard / orphan 拒绝 / Evidence-Admission 解耦已验收；P0/P1/P2=0，P3=1 非阻塞；可作为未来 CD-4 的依赖基础。

**不表示**：Entire Core Domain complete / I3 implemented / Assertion implemented / Citation implemented / All HFB core data migrated / Public Portal / Publication Snapshot / Phase 1 started / CD-4 authorized。

## 13. Authorization Boundary

```text
CD-4:
NOT AUTHORIZED

CORE DOMAIN MIGRATION BEYOND CD-3:
NOT AUTHORIZED

PHASE 1 BUSINESS CODING:
NOT AUTHORIZED
```

Phase 1 Deliverables（G1–G4/G7）继续冻结，不属于本轮。
