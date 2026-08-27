# HFM Phase 0.4 — CD-1 Implementation Report

Date: 2026-08-27 · Phase 0.4 — Core Domain Implementation CD-1
性质：Core Domain 第二批实施（Frozen DAG CD-1 节点唯一准绳）

## 1. Starting Baseline

- **CD-0 Implementation Baseline**：`504e45e2d707b7e439e8b2610c109f30fa581f65`（HFM HEAD = origin/main，working tree clean）

## 2. HFB Source Snapshot

- **HFB Source Snapshot（固定只读）**：`03755b57ec0e4c8023d1447619f7d6ead9e44d73`

## 3. Frozen CD-1 Scope

- 详见 `docs/migration/hfb/HFM-PHASE0.4-CD1-IMPLEMENTATION-SCOPE.md`（**CD-1 SCOPE: CONFIRMED**）
- 对象：Entity + EntityType + Person（身份 + 研究域字段）；值对象：EntityType（7 族）、PersonDomainStatus
- 依赖 CD-0：Source/SourceRef/Institution、DB 基座、immutable_fields 守卫、Repository 基座
- 明确排除：entity_relations（CD-6）、Work 层（CD-2）、TCM 专表、Person 单值生平字段（CD-4）、Assertion/Evidence/Citation、API/Auth/RBAC/前端/Phase 1、数据导入（NOT PERFORMED）

## 4. Traceability Matrix

- 见 Scope 文档（8 项 Requirement → Contract → HFB → Target → Verdict → Implementation → Test）；所有生产代码可映射

## 5. Objects Implemented

```text
apps/backend/src/hfm/models/entity.py     # EntityType（7 族枚举）+ Entity（typed，非 catch-all）
apps/backend/src/hfm/models/person.py     # PersonDomainStatus + Person（entity_id 1:1，无单值生平真值列）
apps/backend/src/hfm/repositories/entity.py
apps/backend/src/hfm/repositories/person.py
apps/backend/alembic/versions/0002_cd1_entity_person.py
```

## 6. REUSE

- `EntityType` 值来源（CA-002 GRAPH_ENTITY_TYPES 归并语义 + CA-001 AcademicEntityType 对齐）
- CD-0 `BaseModel` / `immutable_fields` / `BaseRepository` 基座（未退化）

## 7. EXTEND

- 无（CD-1 无独立 EXTEND 资产；EntityType 归并计入 REUSE/ADAPT）

## 8. ADAPT

- **Entity + EntityType**（CA-001 AcademicEntity/AcademicEntityType）：保留 typed-entity 模式（entity_type + name + description）；移除医学专类类型（meridian/disease/technique/herb/prescription/symptom/syndrome — G1 边界）与图表耦合；重写为 Frozen 7 族枚举 + 显式 CHECK 约束
- **Person**（CA-003）：保留 name 变体/dynasty/研究域字段（domain_status/anchor_path/research_relation_role/domain_relation_summary）；**移除**单值生平真值字段（birth_year/death_year/birth_place/biography/notable_works/expertise — 转写契约，CD-4 Assertion 输入）；重写为 typed Entity 扩展（entity_id 1:1 FK）

## 9. NEW

- `PersonDomainStatus` 枚举、`PersonRepository`/`EntityRepository.get_by_type`、迁移 0002

## 10. Database Changes

```text
tables: entities / persons
constraints: ck_entities_entity_type（CHECK 7 族）、persons.entity_id PK + FK RESTRICT（1:1）
indexes: ix_entities_entity_type
```

## 11. Migrations

- `alembic/versions/0002_cd1_entity_person.py`（revision 0002，down_revision 0001；upgrade/downgrade）
- 验证：fresh head upgrade PASS；**既有 CD-0 DB（0001）→ head（0002）原地升级 PASS**；0002 downgrade 保留 CD-0 表 PASS；replay 幂等 PASS（test_migrations 5 tests）

## 12. Data Import

```text
HFB DATA IMPORT:
NOT PERFORMED
```

（Frozen CD-1 未明确包含数据导入执行。）

## 13. API Changes

```text
API Changes:
0
```

（Frozen CD-1 未列 API。）

## 14. Invariants

```text
I5 Stable Identity — APPLICABLE：Entity id 稳定（UUIDv7）；Person.entity_id = Entity.id（1:1）— test_invariant_i5_entity_person_stable_identity
I4 No Silent Overwrite — APPLICABLE：immutable id 守卫沿用；update 仅改可变字段 — test_invariant_i4_no_silent_overwrite + test_entity_update_rejects_immutable_fields
I3/I4 转写契约 — 负向守卫：Person 无单值生平真值列 — test_single_value_field_transcription_guard / test_transcription_contract_person_columns
I1 / I2 — NOT IN CD-1 SCOPE（CD-3/CD-5）
I3 Assertion Coexistence — NOT IN CD-1 SCOPE（CD-4；本批以转写契约准备）
I6 — APPLICABLE：独立性审计 PASS
```

## 15. Tests

- `test_entity_model.py`（5）：构造、非法类型 CHECK 拒绝、get_by_type、CRUD、EntityType 7 族断言
- `test_person_model.py`（4）：构造 + entity 链接、必需 Entity、默认 domain_status、**单值字段转写守卫**
- `test_repositories_cd1.py`（3）：immutable 守卫沿用、Entity 删除 RESTRICT、跨类型同名允许
- `test_invariants_cd1.py`（3）：I5 稳定身份、I4 无静默覆盖、转写契约列断言
- `test_migrations.py`（+2）：既有 CD-0 DB 升级 0002、0002 downgrade 保留 CD-0

## 16. CD-0 Regression

- CD-0 全部测试原样通过（immutable source_key / repository guard / model guard / Source 测试未修改）；pytest 全量 77 passed 含 CD-0 60 项

**CD-0 Regression: PASS**

## 17. Phase 0.3 Regression

- /health /ready /version /live /config 200；X-Request-ID 正常；/config 无敏感；前端 Vitest 24 / build PASS

**Phase 0.3 Regression: PASS**

## 18. Quality Gates

| Gate | Result |
| --- | --- |
| Ruff | PASS |
| Ruff format | PASS（59 files） |
| mypy --strict | PASS（56 source files，零豁免） |
| pytest | **77 passed**（CD-0 60 + CD-1 17） |
| ESLint | PASS |
| Prettier | PASS |
| vue-tsc | PASS |
| Vitest | **24 passed / 8 files**（无前端变更，回归） |
| Build | PASS |

## 19. Runtime Smoke

- /health /ready /version /live /config 全部 200；X-Request-ID 正常；/config Secret Exposure NO

## 20. HFB Independence

- 源码/配置扫描：无 `Sites/hfb` / `../hfb` / `from hfb` / `import hfb` / `@hfb/` / `03755b57`（docs provenance 除外）
- 无 symlink / submodule / local path dependency / runtime HTTP / 共享 DB

**Permanent HFB Runtime Dependency: NO**

## 21. Contract Deviations

```text
Contract Deviations:
0
```

## 22. Phase 1 Boundary

- 未实现 G1/G2/G3/G4/G7；无 Auth/RBAC；无前端业务；无 API

## 23. Scope Closure

```text
CD-1 Frozen Scope Items:
8（Scope 文档 Traceability Matrix 行数）

Implemented:
8

Deferred:
0

Unauthorized Additions:
0

Contract Deviations:
0
```
