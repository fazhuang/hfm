# HFM Phase 0.4 — CD-5 Acceptance Archive

Date: 2026-08-27 · Phase 0.4 — Core Domain Implementation CD-5
性质：GOVERNANCE-ONLY ACCEPTANCE ARCHIVE — 仅归档 Codex 最终独立验收事实，不重新解释、不重新设计 CD-5

## 1. Acceptance Identity

```text
Phase:
HFM Phase 0.4 — Core Domain Implementation CD-5

Acceptance Type:
FINAL INDEPENDENT IMPLEMENTATION ACCEPTANCE

Final Verdict:
PASS

HFM CD-5:
ACCEPTED

Starting CD-4 Implementation Baseline:
82505d11d7f0591de1df342f03b4e78c5c4300a7

Initial CD-5 Implementation Candidate:
c8a1be9552e51052b3dc483af8cc2ce6ddd2b14e

Accepted CD-5 Implementation Candidate:
523294a292dc34ce69841355e9a6b3c7dd79dad0

Core Domain Contract Baseline:
366df69715613022326eb7a3c06ae7f145ebacb9

HFB Source Snapshot:
03755b57ec0e4c8023d1447619f7d6ead9e44d73
```

## 2. Candidate History（如实归档）

- `c8a1be9` = **Initial CD-5 Implementation Candidate**（pre-fix）。
- 首次 Codex 独立验收发现 P1×2（① Version 无撤回状态 — Frozen Canonical §2；② Source 撤回→Evidence taint→Citation 拒绝级联缺失 — Lineage §2.5）+ P2×1（Ruff Format 计数）→ **BLOCK / REJECTED**。
- Pi 完成修正（Version/Source 撤回状态 + mark_withdrawn 级联 + Citation 撤回门禁 + 迁移 0007 + 计数修正）→ 修正提交 `523294a`。
- Codex 复验（Withdrawn Version Gate / Source Withdrawal→Taint→Citation Rejection / Citation Binding Immutability 全部 PASS）：**FINAL VERDICT: PASS / HFM CD-5: ACCEPTED**。
- 不掩盖初始 Candidate 历史；不将修正过程描述为一次性 PASS。

## 3. Scope Closure

```text
CD-5 Scope:
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
1

EXTEND:
0

ADAPT:
2

NEW:
6

Scope/Verdict Count Semantics:
CLEAR
```

Scope Item 与 asset verdict 属不同计数体系；未重新计算、未重新裁决 Frozen Inventory。

## 4. Accepted Core Objects

```text
Citation（target_assertion / evidence 直接边 / pinned version / passage / quote_text / note）
Version.withdrawn_at（Frozen Canonical §2 撤回状态）
Source.withdrawn_at + 撤回级联（Lineage §2.5）
Migration 0006_cd5_citation + 0007_cd5_withdrawal
```

以上仅代表 **Frozen CD-5 Scope**（含撤回语义补全），不构成 Core Domain Complete。

## 5. Closed Findings（最终修正闭环）

```text
P1-1 Withdrawn Version Gate:
CLOSED — Version.withdrawn_at + VersionRepository.mark_withdrawn +
CitationRepository.create 拒绝 withdrawn Version（I2）

P1-2 Source Withdrawal → Evidence Taint → Citation Rejection:
CLOSED — Source.withdrawn_at + SourceRepository.mark_withdrawn（级联标记
锚定 Evidences source_withdrawn）+ CitationRepository.create 拒绝 tainted
evidence（直接边 + 目标 Assertion 的 evidence[]）

P2 Ruff Format Count:
CLOSED — 以官方门禁 `ruff format --check .` 为准（99 files）

复验：Withdrawn Version Gate PASS / Source Withdrawal→Taint→Citation Rejection PASS /
Citation Binding Immutability PASS / I2 PASS
```

## 6. Core Invariant Status

```text
I1 Provenance:
PASS（CD-3 已冻结实现；回归）

I2 Version Reproducibility:
PASS（CD-5 本批 DIRECTLY APPLICABLE：withdrawn Version 拒绝 + pinned no-latest-drift + pin immutable）

I3 Assertion Coexistence:
PASS（CD-4 已冻结实现；回归）

I4 No Silent Overwrite:
PASS（Citation 引用绑定 immutable + @validates）

I5 Stable Identity:
PASS

I6 HFB Independence:
PASS
```

## 7. Database / Migration Acceptance

```text
Migration:
0006_cd5_citation + 0007_cd5_withdrawal

Database Migration Gate:
PASS

Fresh DB Migration:
PASS

0001 → 0007: PASS（逐级验证）

Historical Migration Integrity:
UNCHANGED（未修改 0001-0007 任何 migration 文件）
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

Unauthorized CD-6+ Implementation:
NO
```

## 9. Quality & Runtime Evidence（`523294a` 最终复验）

```text
Ruff: PASS
Ruff Format: PASS — 99 files
mypy: PASS — 91 files
pytest: PASS — 170
ESLint: PASS
Prettier: PASS
vue-tsc: PASS
Vitest: PASS — 24 passed
Build: PASS

/health: 200 · /ready: 200 · /version: 200 · /live: 200 · /config: 200
/config Secret Exposure: NO
X-Request-ID: PASS

CD-0 Regression: PASS
CD-1 Regression: PASS
CD-2 Regression: PASS
CD-3 Regression: PASS
CD-4 Regression: PASS
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

HFM CD-5:
ACCEPTED
```

## 12. Freeze Semantics

CD-5 Accepted/Frozen 表示：Frozen CD-5 Scope 9/9（Citation，target=Assertion）已完成并通过 Codex 独立验收；I2 Version Reproducibility 在本批 DIRECTLY APPLICABLE 并验收（withdrawn Version 拒绝 + pinned no-latest-drift）；Source 撤回→Evidence taint→Citation 拒绝级联已验收；可作为未来 CD-6 的依赖基础。

**不表示**：Entire Core Domain complete / Event/Place implemented / All HFB core data migrated / Public Portal / Publication Snapshot / Phase 1 started / CD-6 authorized。

## 13. Authorization Boundary

```text
CD-6:
NOT AUTHORIZED

CORE DOMAIN MIGRATION BEYOND CD-5:
NOT AUTHORIZED

PHASE 1 BUSINESS CODING:
NOT AUTHORIZED
```

Phase 1 Deliverables（G1–G4/G7）继续冻结，不属于本轮。
