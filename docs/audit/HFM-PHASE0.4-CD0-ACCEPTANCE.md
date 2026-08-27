# HFM Phase 0.4 — CD-0 Acceptance Archive

Date: 2026-08-27 · Phase 0.4 — Core Domain Implementation CD-0
性质：GOVERNANCE-ONLY ACCEPTANCE ARCHIVE — 仅归档 Codex 已完成验收事实，不重新设计 CD-0、不修改 Core Domain Contract

## 1. Acceptance Identity

```text
Phase:
HFM Phase 0.4 — Core Domain Implementation CD-0

Acceptance Type:
FINAL IMPLEMENTATION ACCEPTANCE

Final Verdict:
PASS

Accepted Implementation Candidate:
e1c33afd8c2ea4f8962145d4398535c49cbad088

Starting Core Domain Contract Baseline:
366df69715613022326eb7a3c06ae7f145ebacb9
```

## 2. P1 修复闭环归档

```text
P1 Immutable Source Identity:
CLOSED
```

双层防护（不同层面，非同义重复）：

```text
Repository Guard:
immutable_fields rejects id/source_key
（BaseModel.immutable_fields 默认 {id}；Source 增加 source_key；BaseRepository.update() 对 immutable 字段显式 ValueError — 阻止持久化更新路径修改 immutable identity）

Model Guard:
Source @validates("source_key") rejects direct mutation
（ORM 属性赋值层守卫 — 阻止直接对象属性 mutation）
```

## 3. Test Evidence

```text
New P1 Tests:
3

pytest:
PASS — 60 passed

Ruff:
PASS

Ruff Format:
PASS — 50 files

mypy:
PASS — 48 source files

Vitest:
PASS — 24

Frontend Build:
PASS

Runtime Smoke:
PASS

X-Request-ID:
PASS

git diff --check:
PASS
```

## 4. Core Contract Status

```text
Core Domain Contract:
FROZEN

CD-0 Implementation:
ACCEPTED

CD-1:
NOT AUTHORIZED

CORE DOMAIN MIGRATION BEYOND CD-0:
NOT AUTHORIZED

PHASE 1 BUSINESS CODING:
NOT AUTHORIZED
```

## 5. CD-0 Scope Closure（引用已验收实施报告）

```text
Frozen Scope Items:
8

Implemented:
8

Deferred:
0

Unauthorized Additions:
0

Contract Deviations:
0
```

依据：`docs/audit/HFM-PHASE0.4-CD0-IMPLEMENTATION.md`（未重算、未修改）。

## 6. Core Invariants Status（按 CD-0 实际覆盖范围）

```text
I1 Provenance（SourceRef → Source 锚定）:
PASS（test_invariant_i1_provenance_seed）

I2 Version Reproducibility:
NOT IN CD-0 SCOPE（CD-2/CD-5 批次）

I3 Assertion Coexistence:
NOT IN CD-0 SCOPE（CD-4 批次）

I4 No Silent Overwrite / Idempotency:
PASS（create_idempotent + I4 不变量测试）

I5 Stable Source Identity:
PASS（source_key 唯一 + immutable_fields + @validates 双层守卫）

I6 HFB Runtime Independence:
PASS（独立性审计：无 HFB path/import/共享 DB）
```

## 7. Phase 1 Boundary（仍为后续 Deliverables）

```text
G1 Medical Compliance
G2 Anonymous/Public Access
G3 Publication Snapshot
G4 ICH Media Governance
G7 Separation of Duties
```

未在 CD-0 中实现，也不得在归档中描述为已完成能力。
