# HFM Phase 0.4 — CD-6 Acceptance Archive

Date: 2026-08-28 · Phase 0.4 — Core Domain Implementation CD-6
性质：GOVERNANCE-ONLY ACCEPTANCE ARCHIVE — 仅归档 Codex 最终独立验收事实，不重新解释、不重新设计 CD-6

## 1. Acceptance Identity

```text
Phase:
HFM Phase 0.4 — Core Domain Implementation CD-6

Acceptance Type:
FINAL INDEPENDENT IMPLEMENTATION ACCEPTANCE

Final Verdict:
PASS

HFM CD-6:
ACCEPTED

Starting CD-5 Implementation Baseline:
834ad1b47c6b5583dd840e670d9c7a65fad55356

Initial CD-6 Implementation Candidate:
b593b93edf8665139b19b5d3829957c651ebbc0e

Accepted CD-6 Implementation Candidate:
7bb6e2e1c15d62989e890cb36e97290df4142692

Core Domain Contract Baseline:
366df69715613022326eb7a3c06ae7f145ebacb9

HFB Source Snapshot:
03755b57ec0e4c8023d1447619f7d6ead9e44d73
```

## 2. Candidate History（如实归档）

- `b593b93` = **Initial CD-6 Implementation Candidate**（pre-fix）。
- 首次 Codex 独立验收发现 P1×1（① `attach_assertion` 未强制 `Assertion.subject_entity_id = event Entity id` — 事件域边界 + I1 语义）+ P2×1（② `models/event.py:120` 含未报告的 `# type: ignore[assignment]`）→ **BLOCK / REJECTED**。
- Pi 完成修正（聚合 subject 门禁 + SQLite 触发器兜底 + 负向仓库/直接DB/契约测试；移除 type: ignore，events 改标准 BaseModel 形态 id PK + entity_id UNIQUE）→ 修正提交 `7bb6e2e`。
- Codex 复验（Event Assertion Aggregation / Assertion Subject = Event Entity Integrity / I1 Event Provenance Chain 全部 PASS；DB Direct-Probe Gate 13 probes）：**FINAL VERDICT: PASS / HFM CD-6: ACCEPTED**。
- 不掩盖初始 Candidate 历史；不将修正过程描述为一次性 PASS。

## 3. Scope Closure

```text
CD-6 Scope:
CONFIRMED

Frozen Scope Items:
3

Implemented:
3

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
2

Scope/Verdict Count Semantics:
CLEAR
```

Scope Item 与 asset verdict 属不同计数体系；未重新计算、未重新裁决 Frozen Inventory。

## 4. Accepted Core Objects

```text
Event（NEW，CA-004）— typed-Entity（id PK + entity_id UNIQUE FK → entities.id，I5）
                  + event_type + 时间区间帧（year/month/day/approximate/range/unknown；start<=end；开放区间）
EventRelation（Person/Event 关系，ADAPT CA-001）— entity_relations（role + UNIQUE + entity_id<>event_id）
event_assertions（NEW）— Event → Assertion 聚合（subject_entity_id == event_id 强制 + SQLite 触发器兜底）
Migration 0008_cd6_event（修正版：id PK + uq_events_entity_id + trg_event_assertions_subject_match）
```

以上仅代表 **Frozen CD-6 Scope**，不构成 Core Domain Complete。

## 5. Closed Findings（最终修正闭环）

```text
P1 Event Aggregation Subject Gate:
CLOSED — EventRepository.attach_assertion 拒绝 subject_entity_id != event_id
（事件证据聚合 = 关于事件的 Assertion，域边界 + I1）；SQLite 触发器
trg_event_assertions_subject_match 兜底（CHECK 无法表达 join；PostgreSQL 依赖仓库守卫）；
负向仓库测试 + 直接DB探针（raw INSERT 不匹配 → IntegrityError）+ 契约不变量 JOIN 查询

P2 Unreported type: ignore:
CLOSED — `id = None  # type: ignore[assignment]` 移除；events 表 = id UUIDv7 PK
+ entity_id UNIQUE NOT NULL FK（标准 BaseModel 形态，1:1 由 UNIQUE 保证）；
CD-6 Newly Introduced Quality Waivers: 0

复验：Event Assertion Aggregation PASS / Assertion Subject = Event Entity Integrity PASS /
I1 Event Provenance Chain PASS / DB Direct-Probe Gate PASS（13 probes）
```

## 6. Core Invariant Status

```text
I1 Provenance:
PASS（CD-6 本批 DIRECTLY APPLICABLE：事件证据链 Event→Assertion→Evidence→SourceRef→Source，
聚合 subject 门禁验收）

I2 Version Reproducibility:
PASS（回归保持）

I3 Assertion Coexistence:
PASS（SUPPORTED：冲突日期主张并存并聚合到同一 Event）

I4 No Silent Overwrite:
PASS（帧字段与关系绑定 immutable）

I5 Stable Identity:
PASS（Event 经 Entity 行稳定身份；EventRelation UUIDv7）

I6 HFB Independence:
PASS
```

## 7. Database / Migration Acceptance

```text
Migration:
0008_cd6_event（修正版）

Database Migration Gate:
PASS

Fresh DB Migration:
PASS

0001 → 0008: PASS（逐级验证）
0002 → 0008: PASS
0003 → 0008: PASS
0004 → 0008: PASS
0005 → 0008: PASS
0006 → 0008: PASS
0007 → 0008: PASS

Downgrade 0008 → 0007:
PASS

Historical Migration Integrity:
UNCHANGED（未修改 0001-0007 任何 migration 文件）

DB Direct-Probe Gate:
PASS — 13 probes（invalid FK / enum / precision / month / start>end / self / duplicate / CASCADE /
subject mismatch trigger / subject match allowed / ...）
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

Unauthorized CD-7+ Implementation:
NO
```

## 9. Quality & Runtime Evidence（`7bb6e2e` 最终复验）

```text
Ruff: PASS
Ruff Format: PASS — 107 files
mypy: PASS — 98 files
pytest: PASS — 211
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
CD-5 Regression: PASS
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

HFM CD-6:
ACCEPTED
```

## 12. Freeze Semantics

CD-6 Accepted/Frozen 表示：Frozen CD-6 Scope 3/3（Event NEW + Person/Event 关系 ADAPT + 事件证据链）已完成并通过 Codex 独立验收；I1 在本批 DIRECTLY APPLICABLE 并验收（聚合 subject 门禁 + 触发器）；I3 SUPPORTED；可作为未来 CD-7+ 的依赖基础（若另行授权）。

**不表示**：Entire Core Domain complete / Place implemented / All HFB core data migrated / Public Portal / Publication Snapshot / Phase 1 started / CD-7 authorized。

## 13. Authorization Boundary

```text
CD-7:
NOT AUTHORIZED

CORE DOMAIN MIGRATION BEYOND CD-6:
NOT AUTHORIZED

PHASE 1 BUSINESS CODING:
NOT AUTHORIZED
```

Phase 1 Deliverables（G1–G4/G7）继续冻结，不属于本轮。Frozen DAG 仅定义 CD-0…CD-6 节点；无 CD-7 定义。
