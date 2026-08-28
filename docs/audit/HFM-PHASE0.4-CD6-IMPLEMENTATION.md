# HFM Phase 0.4 — CD-6 Implementation Report

Date: 2026-08-27 · Phase 0.4 — Core Domain Implementation CD-6

## 1. Acceptance Target

```text
HFM PHASE 0.4 — CORE DOMAIN IMPLEMENTATION CD-6
Person/Event 关系（Event NEW + AcademicRelation ADAPT）
```

## 2. Starting CD-5 Implementation Baseline

```text
834ad1b47c6b5583dd840e670d9c7a65fad55356
```

## 3. Core Domain Contract Baseline

```text
366df69715613022326eb7a3c06ae7f145ebacb9
```

## 4. HFB Source Snapshot

```text
03755b57ec0e4c8023d1447619f7d6ead9e44d73
```

## 5. Frozen CD-6 Scope（唯一来源：Frozen DAG）

```text
CD-6  Person/Event 关系（Event NEW + AcademicRelation ADAPT；依赖 CD-1 + CD-4）
| CD-6 | CD-1, CD-4 | CA-004（NEW）+ CA-001（relation）| Event + Person/Event 关系 |
NEW/ADAPT | 事件证据链 + 时间区间 | 无（事件为新增） | CD-1, CD-4 |

Frozen Scope Items: 3
1. Event 对象（NEW，CA-004）— 稳定身份 + event_type + 时间区间帧
   （year/month/day/approximate/range/unknown 全精度，start<=end）
2. Event 基于 Assertion 聚合（事件证据链 Event→Assertion→Evidence→SourceRef→Source）
3. Person/Event 关系（ADAPT CA-001 AcademicRelation）— entity_relations 表
```

## 6. Traceability Matrix

| CD-6 Requirement | Frozen Contract/DAG | HFB Asset | Frozen Verdict | HFM Target | Implementation | Automated Test |
| --- | --- | --- | --- | --- | --- | --- |
| Event 对象（稳定身份 + 时间区间帧） | DAG CD-6 + CANONICAL §1/§2（Event NEW — 基于 Assertion 聚合）+ Scope v0.1 §6.1 | CA-004（无 HFB 模型；Chronology DOC_ONLY 0806） | NEW | `models/event.py::Event` + `EventType` + `EventBoundPrecision` | entity_id 1:1 → entities.id（typed-Entity，I5）；event_type；start/end 帧（year/month/day + precision unknown/year/month/day + approximate；start<=end；开放区间允许） | test_event_model.py（10）+ test_event_db_probes.py（11） |
| Event 基于 Assertion 聚合（事件证据链） | CANONICAL §1 + DAG gate「事件证据链」+ Assertion Contract §1（subject_entity 含 Event） | CA-004 | NEW | `event_assertions` M:N join + `EventRepository.attach_assertion` | Event→Assertion→Evidence→SourceRef→Source 全链；attach 拒绝 withdrawn Assertion（withdrawn-reference gate 一致性）；幂等 | test_repositories_cd6.py::test_event_assertion_aggregation_and_evidence_chain / test_attach_assertion_rejects_withdrawn / test_attach_assertion_idempotent |
| Person/Event 关系 | DAG CD-6 + CD-1 Scope（entity_relations = CD-6 Person/Event 关系）+ CA-001 AcademicRelation | CA-001 `models/academic_relation.py` | ADAPT | `models/event_relation.py::EventRelation` + `EventRelationRole` | entity_id（CD-1 稳定身份，§17 无第二套 person id）+ event_id + relation_role + UNIQUE + entity_id<>event_id；绑定 immutable（I4） | test_repositories_cd6.py（Person/Event 关系 6 项）+ test_event_db_probes.py（UNIQUE/FK/self） |
| Assertion subject=Event | Assertion Contract §1 | — | — | 既有 CD-4 能力（subject_entity_id FK entities；Event 经 Entity 身份表达） | 无 CD-4 模型变更；测试证明 | test_repositories_cd6.py::test_assertion_subject_can_be_event_entity |

## 7. Implemented Objects

```text
Event（NEW）— events 表
EventRelation（Person/Event 关系，ADAPT CA-001）— event_relations 表
event_assertions（NEW）— Event → Assertion 聚合边
EventType（NEW 枚举）— birth/death/study/career/marriage/travel/composition/meeting/other
EventBoundPrecision（NEW 枚举）— unknown/year/month/day
EventRelationRole（NEW 枚举，ADAPT HFB relation_type）— actor/participant/witness/other
validate_event_frame（NEW 域函数）— 帧一致性 + 范围 + start<=end
```

## 8. Relationships

```text
events.entity_id 1:1 → entities.id（RESTRICT；EntityType.event，I5）
event_relations.entity_id → entities.id（RESTRICT；参与者 CD-1 身份）
event_relations.event_id → events.entity_id（RESTRICT）
event_assertions.event_id → events.entity_id（CASCADE）
event_assertions.assertion_id → assertions.id（CASCADE）
事件证据链: Event → event_assertions → Assertion → assertion_evidences → Evidence → source_ref → source（I1）
Assertion.subject_entity_id = Event Entity id（既有 CD-4 能力）
```

## 9. REUSE / EXTEND / ADAPT / NEW

```text
REUSE: 0
EXTEND: 0
ADAPT: 1（CA-001 AcademicRelation → EventRelation）
NEW: 2（CA-004 Event；event_assertions 聚合边）
（Frozen Inventory Verdicts 未重估；计数 = 本批实际裁决）
```

## 10. Database

```text
新表: events / event_relations / event_assertions（仅 CD-6 必需）
FK: 见 §8（RESTRICT/RESTRICT/RESTRICT/CASCADE/CASCADE）
CHECK: ck_events_event_type / ck_events_start_precision / ck_events_end_precision /
       ck_events_start_consistency / ck_events_end_consistency（4 分支 precision↔空值模式）/
       ck_events_month_range / ck_events_day_range / ck_events_year_range /
       ck_events_start_le_end / ck_event_relations_role / ck_event_relations_not_self
UNIQUE: uq_event_relations（entity_id, event_id, relation_role）
无 CD-7+ / Phase 1 / auth / publication / media / teaching schema；无 catch-all JSON；无 GIS
```

## 11. Migration

```text
新 migration: 0008_cd6_event（down_revision = 0007 — 真实 Alembic head）
历史 migration 0001-0007: UNCHANGED
Database Migration Gate:
fresh DB → head: PASS
0001 → 0008: PASS（逐级验证）
0002 → 0008: PASS
0003 → 0008: PASS
0004 → 0008: PASS
0005 → 0008: PASS
0006 → 0008: PASS
0007 → 0008: PASS
downgrade 0008 → 0007: PASS
FK/CHECK/UNIQUE/nullable/on-delete/enum persistence: PASS（迁移约束探针）
```

## 12. Repository

```text
EventRepository: create（entity 存在 + entity_type='event' 校验；帧验证）/ get_by_id（按 entity_id）
                 / attach_assertion（存在 + 非 withdrawn + 幂等）/ assertion_ids / evidence_ids
EventRelationRepository: create（entity/event 存在 + entity_id<>event_id + role 校验）
                         / get_by_id / update（description note 可变；绑定 immutable）/ list_by_event / list_by_entity
禁止模式: 无 arbitrary setattr / 无 dict patch / 无 silent invalid field / 无 upsert overwrite
```

## 13. Service

```text
Service Changes: 0
```

## 14. Data Import

```text
Data Import: NOT PERFORMED（CD-6 非 import 节点；无 seed 真实 HFB 数据；HFB 事件数据不存在 — Chronology DOC_ONLY）
```

## 15. API

```text
API Changes: 0（未为测试新增 business routes）
```

## 16. Frontend

```text
Frontend Business Changes: 0（无 Event UI）
```

## 17. Invariant Matrix

| Invariant | CD-6 Applicability | Current Core Status | Test Evidence |
| --- | --- | --- | --- |
| I1 Provenance | DIRECTLY APPLICABLE（事件证据链） | PASS | test_event_assertion_aggregation_and_evidence_chain（Event→Assertion→Evidence→SourceRef→Source） |
| I2 Version Reproducibility | 回归保持 | PASS | test_citation_*/ test_i2_*（CD-5 全量回归） |
| I3 Assertion Coexistence | SUPPORTED（冲突日期主张并存并聚合） | PASS | test_assertion_coexistence.py + attach_assertion 多主张聚合 |
| I4 No Silent Overwrite | DIRECTLY APPLICABLE（帧字段 + 关系绑定 immutable） | PASS | test_event_frame_immutable_after_persist / test_event_relation_binding_immutable |
| I5 Stable Identity | DIRECTLY APPLICABLE（Event 经 Entity 行；EventRelation UUIDv7） | PASS | test_event_typed_entity_identity / test_event_relation（create→persist→reload） |
| I6 HFB Runtime Independence | 回归保持 | PASS | §28 I6 扫描 |

## 18. Negative Tests

```text
invalid construction: test_event_create_rejects_non_event_entity / _missing_entity
invalid enum: test_db_probe_invalid_event_type_enum / _invalid_precision_enum / relation_role 非法值
invalid FK: test_db_probe_invalid_fk_entity / test_db_probe_relation_invalid_fk
duplicate: test_person_event_relation_duplicate_role_rejected + test_db_probe_relation_duplicate_unique
orphan: test_event_delete_requires_entity_restrict
protected mutation: test_event_frame_immutable_after_persist / test_event_relation_binding_immutable
direct ORM mutation: test_event_frame_immutable_after_persist（repository.update → ValueError）
invalid relationship: test_person_event_relation_guards（entity 缺失/event 缺失/self/invalid role）
persistence: test_event_typed_entity_identity（reload）/ test_event_assertion_aggregation（fresh repo reload）
repository: test_repositories_cd6.py 全量
migration: test_migration_0008_event_tables / _fresh_chain_preserves_history
temporal invalid precision: test_event_frame_validation_rejects_invalid（parametrized 7 项）
temporal invalid range: test_event_frame_start_after_end_rejected + test_db_probe_end_before_start
temporal invalid precision（DB）: test_db_probe_precision_year_requires_year / _unknown_requires_nulls
temporal invalid month: test_db_probe_invalid_month
serialization: 枚举 StrEnum 值持久化（String + CHECK，非 native enum 名）
DB 强探针（绕过 repository）: test_event_db_probes.py（11 项）
```

## 19. CD-0 Regression

```text
PASS（sources/source_refs/institutions + base + identifiers + locator 全量）
```

## 20. CD-1 Regression

```text
PASS（entities/persons + I5 + typed-entity 模式）
```

## 21. CD-2 Regression

```text
PASS（works/editions/versions/chapters/passages + locator + I2 谱系）
```

## 22. CD-3 Regression

```text
PASS（evidences + taint + content_hash + I1）
```

## 23. CD-4 Regression

```text
PASS（assertions + I3/I4）
```

## 24. CD-5 Regression

```text
Citation target Assertion: PASS
Pinned reference: PASS
No latest drift: PASS
Withdrawn Version rejection: PASS
Source withdrawal: PASS
Evidence taint propagation: PASS
Citation rejection after taint: PASS
Migration 0006/0007: PASS
（CD-6 未绕过任何 Citation protections；全部 CD-5 测试回归通过）
```

## 25. Phase 0.3 Regression

```text
PASS（/health /ready /config 200 + X-Request-ID + /config 零敏感）
```

## 26. Quality Gates

```text
Ruff: PASS
Ruff Format: PASS — 107 files（`ruff format --check .`）
mypy: PASS — 98 source files
pytest: PASS — 211 passed（170 + 41 CD-6 新增）
ESLint: PASS
Prettier: PASS
vue-tsc: PASS
Vitest: PASS — 24 passed
Build: PASS
CD-6 Newly Introduced Quality Waivers: 0（P2 `type: ignore` 已移除）
```

## 27. Runtime Smoke

```text
/health: 200 · /ready: 200 · /version: 200 · /live: 200 · /config: 200
X-Request-ID: PASS（1944cd36-… 回显）
/config Secret Exposure: NO
```

## 28. HFB Independence

```text
扫描: from hfb / import hfb / ../hfb / /Users/likeming/Sites/hfb / @hfb/ — 0 命中
symlink: 仅 .venv python shim（环境自身，非 HFB）
submodule: 0
path dependency: 0
runtime HTTP / shared DB / runtime file read: 0
Permanent HFB Runtime Dependency: NO
```

## 29. Contract Deviations

```text
Contract Deviations:
0
```

## 29.1 Codex CD-6 Acceptance BLOCK → P1×1 + P2×1 修正记录

Codex 独立验收判定 BLOCK：① P1 — `attach_assertion` 未强制 `Assertion.subject_entity_id = event Entity id`（事件域边界 + I1 语义）；② P2 — `models/event.py:120` 含未报告的 `# type: ignore[assignment]`。

| 阻塞 | 修复 | 证据 |
| --- | --- | --- |
| **P1** 聚合 subject 门禁 | `EventRepository.attach_assertion` 拒绝 `subject_entity_id != event_id` 的主张（Frozen CD-6 Scope：事件证据聚合 = 关于事件的 Assertion）；SQLite 层 `trg_event_assertions_subject_match` 触发器兜底（CHECK 无法表达 join；§35 探针模式；PostgreSQL 依赖仓库守卫） | test_attach_assertion_rejects_subject_mismatch / test_db_probe_aggregation_subject_mismatch / test_db_probe_aggregation_subject_match_allowed / test_event_aggregate_contract_invariant（查询级不变量）+ 迁移 0008 触发器 |
| **P2** `type: ignore` | 移除 `id = None  # type: ignore[assignment]`；events 表改为标准 BaseModel 形状（id UUIDv7 PK + entity_id UNIQUE NOT NULL FK — 1:1 typed-Entity 由 UNIQUE 保证，FK 指向 entity_id 合法）；迁移 0008 同步（id PK + uq_events_entity_id） | mypy 98 files 零豁免；`git diff` 新引入 type: ignore = 0；迁移门禁 PASS |
| 测试重构 | 证据链/幂等/缺失目标/级联测试改为 subject=event 主张（符合域边界）；新增 4 项门禁测试 | 见上 |

- **I1 Event Provenance Chain 修正后**：PASS（聚合断言 subject=event；Event→Assertion→Evidence→SourceRef→Source 全链验证）
- **Event Assertion Aggregation 修正后**：PASS（subject 匹配强制 + DB 触发器 + 契约不变量查询）
- **Assertion Subject = Event Entity Integrity 修正后**：PASS
- pytest 207 → **211 passed**（+4）；mypy 98 files / ruff 全绿 / Ruff Format 107 files
- 未改变 CD-0-5 冻结语义；迁移 0001-0007 UNCHANGED（仅本批 0008 修正）

## 30. Unauthorized Additions

```text
Unauthorized Additions:
0
（无 CD-7+ / Phase 1 / auth / publication / media / teaching / GIS / API / Frontend / Service / Data Import）
```

## 31. Existing P3

```text
Starlette/httpx deprecation warning — OPEN / NON-BLOCKING（未修复；无实际 failure → P3: 1）
```

## 32. Phase 1 Boundary

```text
Phase 1 Business Coding: NO
G1 / G2 / G3 / G4 / G7: 未实现（红线保持）
Publication Leakage 扫描: 0（无 publication/published/release/public_visible/snapshot/reviewer/publisher 语义）
Withdrawal 语义: 未改写为 publication workflow；无自动删除 Assertion/Citation；无 Phase 1 publisher/reviewer
```

## Scope Closure

```text
CD-6 Frozen Scope Items: 3
Implemented: 3
Deferred: 0
Unauthorized Additions: 0
Contract Deviations: 0
Scope Completion: PASS

REUSE: 0 · EXTEND: 0 · ADAPT: 1 · NEW: 2
Scope/Verdict Count Semantics: CLEAR（Scope Item 与 asset verdict 计数体系独立）

CD-6 Newly Applicable Invariants: I1 / I4 / I5（DIRECTLY APPLICABLE）；I3（SUPPORTED）
I1 Provenance: PASS（P1 修正后：聚合 subject 门禁 + 触发器 + 契约查询）
I2 Version Reproducibility: PASS
I3 Assertion Coexistence: PASS
I4 No Silent Overwrite: PASS
I5 Stable Identity: PASS
I6 HFB Independence: PASS

Invariant Tests: PASS
Negative Tests: PASS
CD-0 Regression: PASS
CD-1 Regression: PASS
CD-2 Regression: PASS
CD-3 Regression: PASS
CD-4 Regression: PASS
CD-5 Regression: PASS
Phase 0.3 Regression: PASS
Database Migration Gate: PASS
Data Import: NOT PERFORMED
API Scope: COMPLIANT
Frontend Scope: COMPLIANT
HFB Independence: PASS
Unauthorized CD-7+ Implementation: 0
Quality Gates: PASS
Runtime: PASS
git diff --check: PASS
```
