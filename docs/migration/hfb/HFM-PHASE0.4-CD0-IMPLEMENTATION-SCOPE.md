# HFM Phase 0.4 — CD-0 Implementation Scope

Date: 2026-08-27 · Phase 0.4 — Core Domain Implementation CD-0
起始基线：`366df69715613022326eb7a3c06ae7f145ebacb9`（Core Domain Contract Baseline）
HFB Source Snapshot：`03755b57ec0e4c8023d1447619f7d6ead9e44d73`
唯一准绳：`HFM-PHASE0.4-CORE-MIGRATION-DAG.md`（Frozen）CD-0 节点

## CD-0 Scope Extraction（摘自 Frozen DAG）

```text
CD-0 ID:
CD-0

Purpose:
Foundation identity / value objects + Source / SourceRef（身份、locator 基元、stable ID）

Included domain objects:
Source（身份 + rights 元数据）
SourceRef
Institution

Included value objects:
Stable Identifier（UUIDv7 基元）
Locator（结构化文本定位基元）

Dependencies:
—（无前置节点）

HFB source assets:
CA-019（SourceAdmissionEntry identity/rights 部分 — 状态机排除）
CA-020（SourceRef）
CA-005（Institution）

Reuse verdict:
REUSE / EXTEND / ADAPT（逐资产见下）

HFM targets:
apps/backend/src/hfm/core/identifiers.py
apps/backend/src/hfm/core/locator.py
apps/backend/src/hfm/models/{source,source_ref,institution}.py
apps/backend/src/hfm/repositories/{base,source,source_ref,institution}.py
apps/backend/src/hfm/db/{base,session}.py + config.py
apps/backend/alembic（迁移基础设施 + 0001 初始迁移）

DB scope:
sources / source_refs / institutions 三表（含约束/索引/迁移）

API scope:
无（Frozen CD-0 未列 API；不新增业务 endpoint）

Data migration scope:
HFB DATA IMPORT: NOT PERFORMED（Frozen CD-0 未明确包含数据导入执行；data dependency「source identity 导出」记录为后续授权输入，按 HFM-CORE-DATA-MIGRATION-STRATEGY dry-run 流程另行执行）

Test gates:
unit（identifiers/locator/models）+ 稳定 ID 幂等 + repository 行为 + 迁移 fresh/upgrade + 不变量（I1 种子 / I5 稳定身份）

Explicit exclusions:
SourceAdmissionEntry 状态机（治理层）
Assertion / Evidence / Citation / Work / Version / Passage（CD-1+）
Event（CD-6）
Auth / RBAC / 权限（§20）
Phase 1（G1-G4/G7）
前端（无 frontend node）

Blocked downstream nodes:
CD-1（依赖 CD-0）
```

**CD-0 SCOPE: CONFIRMED**（无歧义，可唯一解析）。

## Traceability Matrix

| CD-0 Requirement | Frozen Contract Source | HFB Source | HFM Target | Implementation | Test |
| --- | --- | --- | --- | --- | --- |
| Stable identifier（UUIDv7） | CANONICAL §4（I5）+ DAG CD-0 | `db/base.py::uuid7`（通用纯函数） | `core/identifiers.py` | uuid7 生成 + 校验 | test_identifiers.py |
| Locator 基元 | SCOPE §6.2 + EVIDENCE §3（结构化定位） | `SourceRef.page_location`（字符串） | `core/locator.py` | 结构化 Locator 值对象（work/edition/version/chapter/passage + 卷/篇/页/行） | test_locator.py |
| Source（身份 + rights 元数据） | CANONICAL（Source）+ INVENTORY CA-019 ADAPT | `SourceAdmissionEntry` identity/rights 字段 | `models/source.py` | 不可变 source_key + rights 字段；无状态机 | test_source_model.py |
| SourceRef | CANONICAL（SourceRef）+ INVENTORY CA-020 REUSE/EXTEND | `models/academic_evidence.py::SourceRef` | `models/source_ref.py` | title/author/edition_info/url + source FK + 结构化 locator | test_source_ref_model.py |
| Institution | CANONICAL（Institution）+ INVENTORY CA-005 REUSE | `models/institution.py` | `models/institution.py` | name/type/location/description/status | test_institution_model.py |
| DB foundation（Base/迁移） | TECH BASELINE（SQLAlchemy 2 async + Alembic + PG） | `db/base.py`（Base/TimestampMixin） | `db/base.py` + `db/session.py` + alembic | async engine + DeclarativeBase + 迁移 0001 | test_migrations.py |
| Repository 行为 | DAG CD-0（实现层）+ DoD（repository） | `repositories/base.py`（通用 CRUD，ADAPT） | `repositories/*.py` | 通用 async CRUD + 领域 repository | test_repositories.py |
| 不变量 I1/I5/幂等 | ASSERTION（I1/I5）+ DAG（稳定 ID 幂等） | — | models + repos | source_key 唯一/幂等；SourceRef→Source 必达 | test_invariants.py |

未进入矩阵的生产代码不得实施。
