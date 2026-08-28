# HFM Phase 0.4 — CD-1 Acceptance Archive

Date: 2026-08-27 · Phase 0.4 — Core Domain Implementation CD-1
性质：GOVERNANCE-ONLY ACCEPTANCE ARCHIVE — 仅归档 Codex 已完成验收事实，不重新解释或重新设计 CD-1

## 1. Acceptance Identity

```text
Phase:
HFM Phase 0.4 — Core Domain Implementation CD-1

Acceptance Type:
FINAL INDEPENDENT IMPLEMENTATION ACCEPTANCE

Final Verdict:
PASS

Accepted Implementation Candidate:
7402ce5e6a86a11b9526e8985bc82957b04b7009

Starting CD-0 Implementation Baseline:
504e45e2d707b7e439e8b2610c109f30fa581f65

Core Domain Contract Baseline:
366df69715613022326eb7a3c06ae7f145ebacb9

HFB Source Snapshot:
03755b57ec0e4c8023d1447619f7d6ead9e44d73
```

## 2. Scope Closure

```text
CD-1 Scope:
CONFIRMED

Frozen Scope Items:
8

Implemented:
8

Deferred:
0

Unauthorized Additions:
0
```

```text
REUSE:
2

EXTEND:
0

ADAPT:
2

NEW:
3
```

**Scope/Verdict Count Semantics: CLEAR** — Frozen Scope Items（8，Traceability Matrix 行数）与资产 reuse verdict 数量（7 = REUSE 2 + ADAPT 2 + NEW 3）属于不同计数体系；7 个资产裁决不等于遗漏第 8 个 scope item（其中「DB 基座复用」项计为 REUSE 且并入矩阵行）。Codex 已独立确认无 scope 缺失。

## 3. Core Objects Acceptance

```text
Entity Contract:
PASS

Person Contract:
PASS

Repository:
PASS
```

实现对象归档（不扩大为完整 Core Domain）：

```text
Entity
EntityType
Person
Repository layer
Migration 0002_cd1_entity_person
```

## 4. Core Invariant Status

```text
I4 No Silent Overwrite:
PASS

I5 Stable Identity:
PASS

I6 HFB Independence:
PASS

I1:
NOT IN CD-1 SCOPE

I2:
NOT IN CD-1 SCOPE

I3:
NOT IN CD-1 SCOPE

Transcription Negative Guard:
PASS
```

（NOT IN SCOPE 不改写为已实现。）

## 5. Database Acceptance

```text
Migration 0002:
PASS

Fresh DB Migration:
PASS

0001 → 0002:
PASS

Unauthorized CD-2 Schema:
NO
```

## 6. Boundaries

```text
Data Import:
NOT PERFORMED

API Changes:
0

Frontend Business Changes:
0

Unauthorized Auth/RBAC:
NO

Phase 1 Business Coding:
NO

Permanent HFB Runtime Dependency:
NO
```

## 7. Quality Gates（Codex 实际复验）

```text
Ruff:
PASS

Ruff Format:
PASS — 59 files

mypy:
PASS — 56 files

pytest:
PASS — 77 passed

ESLint:
PASS

Prettier:
PASS

vue-tsc:
PASS

Vitest:
PASS — 24 passed

Build:
PASS
```

## 8. Runtime Regression

```text
CD-0 Regression:
PASS

/health:
PASS

/ready:
PASS

/version:
PASS

/live:
PASS

/config:
PASS

/config Secret Exposure:
NO

X-Request-ID:
PASS
```

## 9. Finding Status

```text
P0:
0

P1:
0

P2:
0

P3:
0

FINAL VERDICT:
PASS

HFM CD-1:
ACCEPTED
```

## 10. Phase 1 Boundary（仍为后续 Deliverables）

```text
G1 Medical Compliance
G2 Anonymous/Public Access
G3 Publication Snapshot
G4 ICH Media Governance
G7 Separation of Duties
```

未实现、无 partial、无 prototype；须未来单独授权。
