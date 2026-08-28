# HFM Phase 0.4 — CD-4 Implementation Scope

Date: 2026-08-27 · Phase 0.4 — Core Domain Implementation CD-4
起始基线：`3e3945d754630e25b2f4c65228dbdb5d4beef35f`（CD-3 Implementation Baseline）
Core Domain Contract Baseline：`366df69715613022326eb7a3c06ae7f145ebacb9`
HFB Source Snapshot：`03755b57ec0e4c8023d1447619f7d6ead9e44d73`
唯一准绳：`HFM-PHASE0.4-CORE-MIGRATION-DAG.md`（Frozen）CD-4 节点 + `HFM-ASSERTION-CONTRACT-v0.1.md`

## CD-4 Scope Extraction（摘自 Frozen DAG + Assertion Contract）

```text
CD-4 ID:
CD-4

Purpose:
Assertion 契约（Entity → multiple Assertions；冲突并存；no-silent-overwrite；provenance）

Included Domain Objects:
Assertion（subject_entity / predicate / value / object_entity / assertion_type /
         confidence / editorial_status / evidence[] / provenance / version）

Included Value Objects:
AssertionType（BIOGRAPHICAL / TEXTUAL / RELATIONAL / HISTORICAL / ...）
EditorialStatus（draft / reviewed / approved / withdrawn — 研究编辑态，非发布态）
Confidence（low / medium / high — 研究置信，非发布状态）

Required Relationships:
Assertion.subject_entity_id → Entity（CD-1，NOT NULL — subject 参照完整性，orphan 预防）
Assertion.object_entity_id → Entity（CD-1，SET NULL — 关系型主张目标）
Assertion ↔ Evidence（CD-3）— 多对多 join 表（assertion_evidences）

Dependencies on CD-0: DB 基座 / immutable_fields / BaseRepository
Dependencies on CD-1: Entity（subject/object 锚点）
Dependencies on CD-2: —（经 Evidence→Passage 间接；回归保持）
Dependencies on CD-3: Evidence（evidence[] 关联；I1 回归）

HFB Assets:
CA-023（Assertion — 无统一模型 → NEW，HFM 原生实现）
CA-026（CandidateExtraction→Assertion 桥 — ADAPT 判定；provenance 占位记录；治理链保留）

Frozen Inventory Verdicts:
NEW（CA-023）/ ADAPT（CA-026 桥）

HFM Targets:
apps/backend/src/hfm/models/assertion.py
apps/backend/src/hfm/repositories/assertion.py
apps/backend/alembic/versions/0005_cd4_assertion.py

Database Scope:
assertions 表 + assertion_evidences join 表（FK/CHECK/索引/迁移）

Migration Scope:
0005（down_revision = 0004；禁止修改 0001-0004）

Repository Scope:
AssertionRepository（create 校验 subject/值；attach_evidence；get_by_subject；immutable 守卫）

Service Scope:
0

API Scope:
0

Frontend Scope:
Frontend Business Changes: 0

Data Import Scope:
HFB DATA IMPORT: NOT PERFORMED（person 单值字段转写为数据迁移依赖，非本批导入执行）

Applicable Core Invariants:
I3 Assertion Coexistence — APPLICABLE（高风险验收项：冲突并存 / 不覆盖 / evidence 不静默替换）
I4 No Silent Overwrite — APPLICABLE（Assertion 内容 immutable；修订 = 新建）
I5 Stable Identity — APPLICABLE
I6 HFB Independence — APPLICABLE
I1 / I2 — NOT NEWLY APPLICABLE（CD-3/CD-2 已冻结实现；回归 PASS）

Test Gates:
冲突并存（same subject+predicate 多条）/ no-silent-overwrite / evidence 关联不覆盖 /
subject 参照完整性 / orphan 拒绝 / editorial_status 转换 / 迁移 0004→0005

Explicit Exclusions:
CandidateExtraction 治理链（审核 → Assertion 桥为 governance-layer，ADAPT 判定记录 + provenance 占位）
Publication / Snapshot / Public Portal / Auth / Reviewer / Publisher / 前端 / Phase 1（G1-G4/G7）
统一 Assertion 表仅此一张（禁止 subject_type+subject_id 无限制泛化 — 用 Entity FK）

Blocked Downstream Nodes:
CD-5（依赖 CD-4）
```

**CD-4 SCOPE: CONFIRMED**（无歧义，可唯一解析）。

## Traceability Matrix

| CD-4 Requirement | Frozen Contract | HFB Asset | Verdict | HFM Target | Implementation | Automated Test |
| --- | --- | --- | --- | --- | --- | --- |
| Assertion 模型 | ASSERTION §1（subject/predicate/value/type/confidence/editorial_status/provenance/version） | CA-023（无统一模型） | NEW | `models/assertion.py` | Assertion + enums + join | test_assertion_model.py |
| Subject 参照完整性 | ASSERTION §5（Entity→Assertions）+ 本指令 §12（禁止无限制 subject_type） | CA-001（Entity） | NEW | subject_entity_id FK → entities.id | FK NOT NULL + orphan 拒绝 | test_assertion_provenance.py |
| 值/对象表达 | ASSERTION §1（value / object_entity） | CA-023 | NEW | value Text + object_entity_id FK（SET NULL） | 至少 value 或 object 非空（repository） | test_assertion_model.py |
| I3 冲突并存 | ASSERTION §2（同 subject+predicate 并存，无唯一约束） | CA-023 | NEW | 无 UNIQUE(subject,predicate) | 冲突并存测试 | test_assertion_coexistence.py |
| I4 不覆盖 | ASSERTION §3（I4 无静默覆盖；修订=新建） | CA-023 | NEW | 内容字段 immutable_fields + @validates | 不覆盖测试 | test_assertion_coexistence.py |
| Assertion↔Evidence M:N | EVIDENCE §2.1（多证据/多主张） | CA-021 Evidence | NEW | `assertion_evidences` join 表 | attach_evidence + 不覆盖 | test_assertion_evidence.py |
| EditorialStatus | ASSERTION §1（draft/reviewed/approved/withdrawn 研究编辑态） | CA-023 | NEW | EditorialStatus 枚举 + CHECK + 转换 | 状态转换测试 | test_assertion_model.py |
| Provenance 占位（CA-026 桥） | ASSERTION §1（provenance）+ CA-026 ADAPT | CA-026 | ADAPT | created_by（actor 引用占位，无 User FK — Auth 红线） | created_by 字段 | test_assertion_model.py |
| Migration 0005 | DAG CD-4（DB scope） | — | NEW | `alembic/versions/0005` | assertions + assertion_evidences | test_migrations.py |

**Scope/Verdict 计数语义**：Frozen Scope Items = 9（矩阵行数）；资产裁决 = NEW 8（CA-023 全新建）+ ADAPT 1（CA-026 桥 provenance 占位）；REUSE 0 / EXTEND 0。两套计数分属不同体系。
