# HFM Phase 0.4 — CD-1 Implementation Scope

Date: 2026-08-27 · Phase 0.4 — Core Domain Implementation CD-1
起始基线：`504e45e2d707b7e439e8b2610c109f30fa581f65`（CD-0 Implementation Baseline）
HFB Source Snapshot：`03755b57ec0e4c8023d1447619f7d6ead9e44d73`
唯一准绳：`HFM-PHASE0.4-CORE-MIGRATION-DAG.md`（Frozen）CD-1 节点

## CD-1 Scope Extraction（摘自 Frozen DAG）

```text
CD-1 ID:
CD-1

Purpose:
Entity + EntityType + Person

Included objects:
Entity
EntityType（值对象枚举）
Person（身份 + 研究域字段；单值生平字段转写契约）

Included value objects:
EntityType（person/work/place/institution/concept/acupoint/event）
PersonDomainStatus（pending/verified/excluded）

Depends on CD-0 objects:
Source / SourceRef / Institution
DB 基座（BaseModel / immutable_fields / async session / alembic）
Repository 基座（BaseRepository immutable 守卫）

HFB source assets:
CA-001（AcademicEntity / AcademicEntityType — ADAPT）
CA-002（EntityRelation GRAPH_ENTITY_TYPES — EntityType 值来源 REUSE/ADAPT）
CA-003（Person — ADAPT；单值生平字段 → CD-4 Assertion 转写输入）

Frozen inventory verdicts:
Entity + EntityType: ADAPT（CA-001）
EntityType 值: REUSE/ADAPT（CA-002）
Person: ADAPT（CA-003）

HFM target modules:
apps/backend/src/hfm/models/entity.py
apps/backend/src/hfm/models/person.py
apps/backend/src/hfm/repositories/entity.py
apps/backend/src/hfm/repositories/person.py
apps/backend/alembic/versions/0002_cd1_entity_person.py

Database scope:
entities / persons 两表（含约束/索引/迁移）

API scope:
无（Frozen CD-1 未列 API；API Changes = 0）

Data migration scope:
HFB DATA IMPORT: NOT PERFORMED（Frozen CD-1 未明确包含数据导入执行）

Invariant scope:
I5 Stable Identity — APPLICABLE（Entity id = 稳定标识；Person.entity_id 1:1）
I4 No Silent Overwrite — APPLICABLE（BaseModel.immutable_fields id 守卫复用；单值字段不建真值列）
I3 Assertion Coexistence — NOT IN CD-1 SCOPE（CD-4；本批以「单值字段转写契约」负向守卫准备）
I1 / I2 — NOT IN CD-1 SCOPE（CD-3/CD-5）
I6 HFB Runtime Independence — APPLICABLE（独立性审计）

Test gates:
domain invariant（Entity 类型校验 / Person-Entity 1:1 / I5）
单值字段转写断言（Person 无 birth_year/death_year/birth_place/biography/notable_works 真值列）
migration 0001→0002（既有 CD-0 DB 升级 + fresh）

Explicit exclusions:
entity_relations 表（CD-6 Person/Event 关系）
Work / Version / Passage（CD-2）
TCM 专表（concept/acupoint 仅 EntityType 值；专表 CD-2+/G1 边界）
Person 单值生平字段（CD-4 Assertion）
Assertion / Evidence / Citation（CD-3/CD-4/CD-5）
API / Auth/RBAC / 前端 / Phase 1（G1-G4/G7）

Blocked downstream CD nodes:
CD-2（依赖 CD-1）
```

**CD-1 SCOPE: CONFIRMED**（无歧义，可唯一解析）。

## Traceability Matrix

| CD-1 Requirement | Contract Source | HFB Source | HFM Target | Verdict | Implementation | Test |
| --- | --- | --- | --- | --- | --- | --- |
| Entity + EntityType | CANONICAL §2（Entity+EntityType ADAPT） | CA-001 `models/academic_relation.py` + CA-002 `models/graph.py` | `models/entity.py` | ADAPT/REUSE | EntityType 枚举（7 族）+ Entity 模型（typed，非 catch-all） | test_entity_model.py |
| Person（身份 + 研究域字段） | CANONICAL §2（Person ADAPT） | CA-003 `models/person.py` | `models/person.py` | ADAPT | entity_id 1:1 + name 变体 + domain_status/anchor_path/research_relation_role | test_person_model.py |
| Person-Entity 1:1 | CANONICAL §1（Entity ◄— Person） | CA-003 | `models/person.py`（entity_id PK/FK RESTRICT） | ADAPT | FK 约束 + 解析测试 | test_person_model.py |
| 单值字段转写契约（负向守卫） | ASSERTION（I3/I4）+ MIGRATION STRATEGY §7 | CA-003 单值字段（birth_year 等） | `models/person.py`（**不建真值列**） | ADAPT | 无 birth_year/death_year/birth_place/biography/notable_works 列断言 | test_person_model.py::test_single_value_field_transcription_guard |
| EntityType 值来源 | CANONICAL §2（EntityType） | CA-002 GRAPH_ENTITY_TYPES（10 类）+ CA-001 AcademicEntityType（5 类） | `models/entity.py::EntityType` | REUSE/ADAPT | 归并为 7 族（医学专类 herb/prescription/symptom/... 属 G1 边界，不入） | test_entity_model.py |
| DB 基座复用（不可退化 CD-0） | CD-0 | — | `db/base.py` BaseModel / immutable_fields | REUSE | — | test_repositories.py（既有） |
| Repository | DAG CD-1（实现层） | — | `repositories/entity.py` + `repositories/person.py` | ADAPT | create/get_by_id/update(immutable 守卫)/delete | test_repositories_cd1.py |
| Migration 0002 | DAG CD-1（DB scope） | — | `alembic/versions/0002_cd1_entity_person.py` | NEW | entities/persons 表 + 约束；0001→0002 升级 | test_migrations.py |

未进入矩阵的生产代码不得实施。
