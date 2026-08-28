# HFM Phase 0.4 — CD-6 Implementation Scope

Date: 2026-08-27 · Phase 0.4 — Core Domain Implementation CD-6（Scope Extraction — 生产代码之前）
Scope 唯一执行来源：`docs/migration/hfb/HFM-PHASE0.4-CORE-MIGRATION-DAG.md`（Frozen DAG，本批不重估 Inventory）

## CD-6 Identity

```text
DAG 节点:
CD-6  Person/Event 关系（Event NEW + AcademicRelation ADAPT；依赖 CD-1 + CD-4）

Node 明细:
| CD-6 | CD-1, CD-4 | CA-004（NEW）+ CA-001（relation） | Event + Person/Event 关系 |
NEW/ADAPT | 事件证据链 + 时间区间 | 无（事件为新增） | CD-1, CD-4 |

Purpose:
新增 Event 聚合对象（基于 Assertion 聚合 — Frozen Canonical §1），
并建立 Person/Event 关系（CA-001 AcademicRelation ADAPT），
支持生平事件时间区间（含 uncertain date）与事件证据链
（Event → Assertion → Evidence → SourceRef → Source，I1）。

What exactly is Frozen CD-6?
UNIQUELY RESOLVED — Event（NEW, CA-004）+ Person/Event 关系（ADAPT, CA-001）
非 Place、非 SourceRef 形式化、非数据导入、非 publication precursor、非 GIS。
```

## Baselines

```text
Starting CD-5 Implementation Baseline:
834ad1b47c6b5583dd840e670d9c7a65fad55356

Core Domain Contract Baseline:
366df69715613022326eb7a3c06ae7f145ebacb9

HFB Source Snapshot:
03755b57ec0e4c8023d1447619f7d6ead9e44d73
```

## Frozen Scope Items

| # | Scope Item | Frozen Source | Verdict |
| --- | --- | --- | --- |
| 1 | Event 对象（NEW）— 稳定身份 + event_type + 时间区间帧（year/month/day/approximate/range/unknown） | DAG CD-6 + CANONICAL §1/§2（Event NEW — 基于 Assertion 聚合）+ Scope v0.1 §6.1（生平事件、时间含 uncertain date） | NEW（CA-004） |
| 2 | Event 基于 Assertion 聚合（事件证据链 Event→Assertion→Evidence→SourceRef→Source） | CANONICAL §1 + DAG gate「事件证据链」+ Assertion Contract §1（subject_entity 含 Event） | NEW（CA-004） |
| 3 | Person/Event 关系（entity_relations；Person 参与者 ↔ Event） | DAG CD-6 + CD-1 Scope §Explicit exclusions（entity_relations 表 = CD-6 Person/Event 关系）+ CA-001 AcademicRelation | ADAPT（CA-001） |

Frozen Scope Items: **3**（其余均为 Guard/Invariant，非独立 Scope Item）

## Included Domain Objects

```text
Event（NEW）— events 表；typed-Entity 模式（entity_id PK 1:1 → entities.id，entity_type='event'，
复用 CD-1 稳定身份骨干 I5；Assertion Contract §1 允许 subject = Event 经 Entity 身份表达）
EventRelation（Person/Event 关系，ADAPT CA-001）— event_relations 表
EventAssertion 聚合边（NEW）— event_assertions M:N join（Event → Assertion，事件证据链）
```

## Included Value Objects

```text
EventType（NEW，HFM-native 枚举）— birth/death/study/career/marriage/travel/composition/meeting/other
EventBoundPrecision（NEW）— unknown/year/month/day（§15：不得缩减为 datetime）
EventRelationRole（NEW，ADAPT HFB relation_type 字符串）— actor/participant/witness/other
approximate（circa）标志 — start/end 各自布尔（§15 approximate）
```

## Included Relationships

```text
events.entity_id 1:1 → entities.id（RESTRICT；typed-Entity，I5；§17 复用 CD-1 身份，无第二套 person id）
event_relations.entity_id → entities.id（RESTRICT；参与者，CD-1 Entity 身份）
event_relations.event_id → events.entity_id（RESTRICT；关系对象须为既有 Event 行）
event_assertions.event_id → events.entity_id（CASCADE）
event_assertions.assertion_id → assertions.id（CASCADE）
Event → event_assertions → Assertion → assertion_evidences → Evidence → source_ref → source（I1 事件证据链）
Assertion.subject_entity_id = event Entity id（既有 CD-4 能力；不修改 CD-4 模型）
```

## Included Guards

```text
1. EventRepository.create 校验 entity 存在且 entity_type='event'（防 Event 行挂到非事件实体）
2. EventRelationRepository.create 校验 entity 存在 / event 存在 / entity_id <> event_id
3. attach_assertion 校验 assertion 存在且非 withdrawn（withdrawn-reference gate 与 CD-5 一致性）
4. Event 时间帧一致性（precision ↔ 年月日空值模式）+ month 1-12 + day 1-31 + year 范围 + start<=end（§15/§16）
5. 所有 DB CHECK/UNIQUE 强探针（§35）：绕过 repository 原始 INSERT 验证
6. I4：Event 帧字段与关系绑定 immutable（BaseRepository.update + @validates id 守卫）；display 字段走 Entity/relation description
```

## Included Invariants（本批新 APPLICABLE）

```text
I1 Provenance — DIRECTLY APPLICABLE（事件证据链 Event→Assertion→Evidence→SourceRef→Source）
I5 Stable Identity — DIRECTLY APPLICABLE（Event 经 Entity 行稳定身份；EventRelation UUIDv7）
I4 No Silent Overwrite — DIRECTLY APPLICABLE（时间帧为 canonical anchor 不可静默覆盖；修订 = 新 Assertion）
I3 Assertion Coexistence — SUPPORTED（冲突日期主张并存并聚合到同一 Event）
I2 — 回归保持（本批不改 Version/Citation 语义）
I6 HFB Runtime Independence — 回归保持
```

## Dependencies

```text
CD-0（Source/SourceRef/Institution/DB 基础）
CD-1（Entity/EntityType/Person — Event 身份与参与者复用）
CD-2（Work/Text 层 — 证据链经 SourceRef 可达）
CD-3（Evidence/taint/content_hash）
CD-4（Assertion — 聚合目标与 subject=Event）
CD-5（Citation/withdrawn 语义 — 一致性回归）
```

## HFB Source Assets（只读参考；不重估 Frozen Verdicts）

```text
CA-004 Event — 无 HFB 模型（Chronology DOC_ONLY 0806）— Verdict: NEW
CA-001 AcademicRelation — models/academic_relation.py（source_entity_id/target_entity_id/relation_type/description）— Verdict: ADAPT（relation）
```

## Database Scope

```text
新表（仅 CD-6 必需）:
events（entity_id PK FK entities.id RESTRICT；event_type；时间帧 8 字段 + approximate 2 字段）
event_relations（id；entity_id FK entities.id RESTRICT；event_id FK events.entity_id RESTRICT；relation_role；description）
event_assertions（event_id FK events.entity_id CASCADE；assertion_id FK assertions.id CASCADE；复合 PK）

CHECK:
ck_events_event_type / ck_events_start_precision / ck_events_end_precision
ck_events_start_consistency / ck_events_end_consistency（precision ↔ 空值模式）
ck_events_month_range / ck_events_day_range / ck_events_year_range
ck_events_start_le_end（start<=end；未知边界 = 开放区间允许）
ck_event_relations_role / ck_event_relations_not_self（entity_id <> event_id）

UNIQUE:
uq_event_relations（entity_id, event_id, relation_role）

禁止: CD-7+ schema / Phase 1 schema / auth / publication / media / teaching / catch-all JSON / GIS
```

## Migration Scope

```text
新 migration: 0008_cd6_event（真实 Alembic head = 0007；单向）
历史 migration 0001-0007: UNCHANGED
```

## Repository Scope

```text
EventRepository（create/get_by_id/attach_assertion/assertion_ids 等）
EventRelationRepository（create/get_by_id/update(description)/list_by_event/list_by_entity）
```

## Service / Data Import / API / Frontend Scope

```text
Service Changes: 0
Data Import: NOT PERFORMED（CD-6 非 import 节点；无 seed 真实 HFB 数据）
API Changes: 0（禁止为测试新增 business routes）
Frontend Business Changes: 0（禁止 Event UI）
Auth/RBAC: 禁止（无 User/Role/JWT；created_by 仅引用占位不引入）
```

## Newly Applicable Invariants（最终）

见上「Included Invariants」。

## Explicit Exclusions

```text
Place 模型（无 DAG 节点分配；不在 CD-6）
Event 撤回/发布生命周期（withdrawn 语义仅 Source/Version Frozen；§12）
Publication lifecycle / snapshot / reviewer / publisher（Phase 1 — G3）
GIS / GeoJSON / PostGIS / map tiles（§21）
数据导入（HFB 事件数据不存在 — Chronology DOC_ONLY）
API / Frontend / Service / Auth
Event 单一真值列（event_date/event_place/event_actor/event_description 不作为可静默覆盖真值 — §14）
```

## Downstream Nodes

```text
CD-7+: NOT AUTHORIZED（从 Frozen DAG 解析：DAG 仅 6 个 CD 节点；无 CD-7 定义）
Phase 1: NOT AUTHORIZED
```

## Quality Gates

```text
Ruff / Ruff Format / mypy / pytest（backend 官方门禁）
ESLint / Prettier / vue-tsc / Vitest / Build（frontend 回归）
/health /ready /version /live /config + X-Request-ID + /config Secret Exposure（runtime smoke）
git diff --check
```

## Acceptance Gates

```text
Scope Completion: 3/3
Deferred: 0
Unauthorized Additions: 0
Contract Deviations: 0
I1-I6 全 PASS
CD-0…CD-5 回归 PASS
Phase 0.3 回归 PASS
Negative Tests PASS（含绕过 repository 的 DB 强探针）
Codex 独立验收后冻结
```
