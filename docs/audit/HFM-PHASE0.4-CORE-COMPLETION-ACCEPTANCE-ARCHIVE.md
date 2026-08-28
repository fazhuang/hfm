# HFM Phase 0.4 — CORE-COMPLETION Acceptance Archive

Date: 2026-08-28 · Phase 0.4 — Core Domain Completion（CORE-COMPLETION ACCEPTANCE ARCHIVE & FREEZE）
性质：GOVERNANCE-ONLY ACCEPTANCE ARCHIVE — 归档 Codex 独立验收事实并将 Accepted Candidate 冻结为 Phase 0.4 Completion Baseline

## 1. Archive Identity

```text
Archive Type:
CORE-COMPLETION ACCEPTANCE ARCHIVE & FREEZE

Accepted Candidate:
7960fb64a43250573d436898d45c7aa615bff1f6

Archive Purpose:
将 Accepted CORE-COMPLETION Candidate 冻结为 FORMAL HFM PHASE 0.4 COMPLETION BASELINE
（仅治理归档；非实现/迁移执行/actual import/contract amendment）
```

## 2. Governing Baselines

```text
Original Core Domain Contract Baseline:
366df69715613022326eb7a3c06ae7f145ebacb9

Phase 0.4 Amended Contract Baseline:
00ed3ff244578d975c2748fa9d85a8d14e4c7c37

CD-6 Implementation Baseline:
d08e343dbbc52dedfcbd5bba69918e6a4b74256d

HFB Source Snapshot:
03755b57ec0e4c8023d1447619f7d6ead9e44d73
```

## 3. Candidate Lineage

```text
Accepted CORE-COMPLETION Candidate:
7960fb64a43250573d436898d45c7aa615bff1f6

Phase 0.4 Completion Baseline:
this archive/freeze commit（7960fb6 本身不含归档事件；新提交 = 正式完成基线）

Final lineage:
Governance 00ed3ff → Implementation d08e343 → Source 03755b5 →
Completion Candidate 7960fb6 → Completion Baseline <archive commit>
```

## 4. Historical Failed Candidate（如实归档，不删除）

```text
Failed CORE-COMPLETION Candidate:
e26598f3be8b3e8b9decd902c9a5e929f0e59e2a

Failed Candidate Verdict:
FAIL（substantive acceptance）

P1 Findings:
3

P1-1:
synthetic absent biography candidate

P1-2:
Edition.file_path incorrectly substituted for SourceRef.page_location

P1-3:
insufficient record-level dedup identity（work_title, version_name）

Corrected by:
7960fb6

Final status:
all three CLOSED
```

## 5. Corrected Candidate

```text
Accepted CORE-COMPLETION Candidate:
7960fb64a43250573d436898d45c7aa615bff1f6

Candidate Set SHA256:
94179e7e11a95612dfbfbb1d1fa378aa469abea15bf9829241e7d54cdaf413cb

Frozen Source SHA256:
94467890f99ebe7d77e1498d04238d460cf80c5cc1ef5b66892397d4a9062cdb

Accepted evidence files:
artifacts/audit/hfm-phase0.4-core-completion.json
docs/audit/HFM-PHASE0.4-CORE-COMPLETION-EVIDENCE.md
```

## 6. Clean-Room Acceptance Environment

```text
Audit Environment:
FRESH CLEAN-ROOM CLONE

Entry Gate:
PASS

Repository Mutation Avoided:
YES（前端依赖安装会变异审计环境 → 未重装重跑；记录此前独立结果）

Unexpected Untracked Files:
0

Final Working Tree:
PRISTINE
```

## 7. Source Universe Closure

```text
Frozen Source Universe:
96

Person actual applicable fields:
4（birth_year / death_year / birth_place / dynasty）

Edition records:
92

Other:
0

Synthetic Person Candidates:
0

Transformation Input:
4

Edition C2 Rows:
0

Unaccounted Source Items:
0

Universe-to-Disposition:
PASS
```

## 8. Migration Class Closure

```text
C1:
4 actual rows → 4 transformed（assertion candidates）
synthetic absent-field candidates = 0
PASS

C2:
real frozen rows = 0
zero-row implementation/test coverage SUPPORTED
Edition.file_path substitution removed（Edition Records Counted As C2: 0）
PASS

C3:
real frozen rows = 0
zero-row implementation/test coverage SUPPORTED
PASS

Edition contract role:
source-preservation candidate — non-transforming（Frozen Strategy §7 无 Edition 转换类；
验证后保留为源证据）
```

## 9. Reconciliation Closure

```text
Universe:
96（= 4 transformation + 92 preserved editions）

Transformation reconciliation:
source: 4
accepted: 4
transformed: 4
rejected: 0
duplicate: 0
target: 4

Arithmetic Reconciliation:
PASS

Semantic Reconciliation:
PASS

Universe-to-Disposition:
PASS

Dedup Identity（superseded 旧规则）:
migration_version + source_sha256 + immutable source_record_id
（旧 (work_title, version_name) 部分元组已记录为被取代/移除）

Duplicate Identity Semantics:
PASS

Deterministic UUID:
PASS

Whole-source-hash future snapshot note:
DERIVED_BUT_SAFE_FOR_FROZEN_SNAPSHOT（未来治理事项，非本轮 blocker）
```

## 10. Reproducibility

```text
Run A:
universe 96 · reconciliation 4/4/4/0/0/4

Run B:
universe 96 · reconciliation 4/4/4/0/0/4

Candidate Set SHA256（A == B）:
94179e7e11a95612dfbfbb1d1fa378aa469abea15bf9829241e7d54cdaf413cb

Reproducibility:
PASS
```

## 11. Same-Target Idempotency

```text
same source snapshot + same migration version + same disposable target:

First application target:
4

Second application new rows:
0

Final target:
4

Same-Target Idempotency:
PASS
```

## 12. Hash / Checksum Integrity

```text
Frozen Source SHA256:
94467890f99ebe7d77e1498d04238d460cf80c5cc1ef5b66892397d4a9062cdb

Candidate Set SHA256:
94179e7e11a95612dfbfbb1d1fa378aa469abea15bf9829241e7d54cdaf413cb

Hash / Checksum:
PASS（sha256，hfm.core.hashing 仓库既定算法）
```

## 13. Inventory Closure

```text
Frozen Inventory Assets:
28

Final Dispositions:
28/28

IMPLEMENTED_CORE:                 15
POST_PHASE_DEFERRED:              11
NON_RUNTIME_GOVERNANCE:            1
BRIDGE_FROZEN:                     1
COMPLETION_EVIDENCE:               0 independent CA rows
COMPLETION_IMPLEMENTATION_REQUIRED: 0

Inventory Contractually Reconciled:
YES

Inventory Completion Evidence:
PASS

Phase 0.4 Inventory Closure:
COMPLETE
```

## 14. Canonical Boundary Closure

```text
Mandatory Missing Runtime Requirements:
0

New Core Runtime Models:
0

New SQLAlchemy Models:
0

New Alembic Migrations:
0

Unauthorized Canonical Expansion:
NO

CA-026:
BRIDGE_FROZEN

Identity/Auth Expansion:
NO

SourceRef:
CLOSED
```

## 15. I1-I6 Closure

```text
I1 Provenance: PASS（真实字段溯源 — source_artifact + source_field/source_record_id + migration_rule）
I2 Version Reproducibility: PASS
I3 Assertion Coexistence: PASS
I4 No Silent Overwrite: PASS
I5 Stable Identity: PASS（确定性 uuid5 candidate identity）
I6 HFB Independence: PASS（completion 模块零 hfb 引用）
```

## 16. Test / Regression Results

```text
Relevant Tests:
24/0/0

Backend Regression:
235/0/0

Type Check:
PASS（mypy 101 files）

Lint:
PASS（ruff）

Format:
PASS（ruff format --check 110 files）

Frontend:
独立于修正候选验收时 24/0/0 PASS；
最终 pristine 克隆未重装重跑（依赖安装会变异审计环境）
→ 如实记录为"此前独立通过"，非"frontend untested"
```

## 17. Evidence Acceptance

```text
Machine-Readable Evidence:
PASS

Markdown Evidence:
PASS

Material Evidence Mismatches:
0

Accepted evidence files:
artifacts/audit/hfm-phase0.4-core-completion.json
docs/audit/HFM-PHASE0.4-CORE-COMPLETION-EVIDENCE.md
```

## 18. Definition of Done

```text
Mandatory DoD Requirements:
9

Passed:
9

Blocked:
0

Definition of Done:
PASS

Phase 0.4 Completion Evidence Closed:
YES
```

## 19. Findings / Severity

```text
P0: 0
P1: 0
P2: 0
P3: 1（non-blocking Starlette/httpx deprecation warning — 既有，未修复）

BLOCKERS:
NONE
```

## 20. Final Acceptance Verdict

```text
FINAL VERDICT:
PASS

CORE-COMPLETION ACCEPTED:
YES
```

## 21. Freeze Semantics

```text
Phase 0.4 Completion Baseline =
Accepted CORE-COMPLETION Candidate（7960fb6）+ 本归档/冻结事件

Accepted Candidate（7960fb6）≠ 完成基线（其不含归档事件）；
本归档提交 = 正式 Phase 0.4 Completion Baseline（self-reference 约定，
SHA 由 git rev-parse HEAD 记录）。

本冻结不授权 actual production data import（Production Records Imported: 0；
Actual Persistent HFB Import: NO；Persistent State: NONE）。
```

## 22. Authorization Boundary

```text
Phase 1 Implementation:
NOT PART OF THIS TASK（Phase 1 Changes In This Commit: 0）

Actual HFB production import:
NOT PERFORMED

CD-7:
NONEXISTENT / NOT REQUIRED / NOT AUTHORIZED

CORE-COMPLETION Is CD-7:
NO
```

## 23. Phase 0.4 Final State

```text
PHASE 0.4 CONTRACT: ACCEPTED / FROZEN
CD-0 THROUGH CD-6: ACCEPTED / FROZEN
CORE-COMPLETION: ACCEPTED / ARCHIVED / FROZEN
FROZEN INVENTORY: CLOSED
COMPLETION EVIDENCE: CLOSED
DEFINITION OF DONE: PASS / CLOSED
PHASE 0.4: COMPLETE / ACCEPTED / ARCHIVED / FROZEN
```

## 24. Traceability Matrix

| Requirement | Frozen Authority | Execution Evidence | Codex Result | Final Disposition |
| --- | --- | --- | --- | --- |
| Source universe | Migration Strategy §3/§6 | 96 = 4 person + 92 editions | Universe-to-Disposition PASS | CLOSED |
| C1 Person→Assertion | Strategy §7 rule 1 | 4/4 transformed; synthetic 0 | PASS | CLOSED |
| C2 SourceRef.page_location→Locator | Strategy §7 rule 2 | 0 real rows; rule tested | PASS | CLOSED |
| C3 Citation target 映射 | Strategy §7 rule 3 + Lineage §2.3 | 0 real rows; rule tested | PASS | CLOSED |
| Reconciliation | Strategy §6 counts | 4/4/4/0/0/4 + universe 96 | Arithmetic + Semantic PASS | CLOSED |
| Reproducibility | Amendment CORE-COMPLETION | Run A == Run B | PASS | CLOSED |
| Same-target Idempotency | Strategy §5 | 2nd application new rows 0 | PASS | CLOSED |
| Dedup identity | Amendment §16-17 | source-grounded key | PASS | CLOSED |
| Hash/Checksum | Amendment §19 | sha256 source + candidate set | PASS | CLOSED |
| Isolation / no import | Amendment §37 + §34 | disposable target; 0 import | PASS | CLOSED |
| Inventory | Amendment 28 dispositions | 28/28 preserved | PASS | CLOSED |
| Canonical boundary | Amendment §31 | 0 new models/migrations | NO expansion | CLOSED |
| CA-026 | Amendment BRIDGE_FROZEN | created_by opaque | BRIDGE_FROZEN | CLOSED |
| SourceRef | CD-0 CLOSED | source_refs implemented | CLOSED | CLOSED |
| I1-I6 | Canonical §3 | 全部 PASS | PASS | CLOSED |
| Tests | DoD Tests complete | 24/0/0 + 235/0/0 | PASS | CLOSED |
| Machine evidence | Amendment §36 | JSON artifact | PASS | CLOSED |
| Markdown evidence | Amendment §35 | evidence doc | PASS | CLOSED |
| DoD | DoD 9 项 | 9/9 | PASS | CLOSED |
| Phase 1 leakage | Amendment §36/§43 | none | NO | CLOSED |
