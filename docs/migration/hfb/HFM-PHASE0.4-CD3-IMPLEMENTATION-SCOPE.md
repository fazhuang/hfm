# HFM Phase 0.4 — CD-3 Implementation Scope

Date: 2026-08-27 · Phase 0.4 — Core Domain Implementation CD-3
起始基线：`b545e5babfc8aa4b89f1488112c544afd927b4ba`（CD-2 Implementation Baseline）
Core Domain Contract Baseline：`366df69715613022326eb7a3c06ae7f145ebacb9`
HFB Source Snapshot：`03755b57ec0e4c8023d1447619f7d6ead9e44d73`
唯一准绳：`HFM-PHASE0.4-CORE-MIGRATION-DAG.md`（Frozen）CD-3 节点

## CD-3 Scope Extraction（摘自 Frozen DAG）

```text
CD-3 ID:
CD-3

Purpose:
Evidence + taint + content_hash（论据层；I1 Provenance 首次 APPLICABLE）

Included Domain Objects:
Evidence

Included Value Objects:
EvidenceLevel（LEVEL_1..4，REUSE）
content_hash（完整性哈希 — 由 hfm.core.hashing 计算）

Required Relationships:
Evidence.source_ref_id → SourceRef（CD-0，RESTRICT，可空）
Evidence.source_passage_id → Passage（CD-2，SET NULL，可空）
至少一个锚点（source_ref_id 或 source_passage_id 非空 — DB CHECK，I1）

Dependencies on CD-0:
Source / SourceRef / Institution + DB 基座 + immutable_fields + hashing

Dependencies on CD-1:
（无直接依赖；Entity 非必需）

Dependencies on CD-2:
Passage（evidence.source_passage_id）/ Work-Edition-Version-Chain（经 Passage）

HFB Source Assets:
CA-021（Evidence）REUSE
CA-024（AcademicTaint 污损字段）REUSE
CA-028（GenerationProof — REUSE 判定记录；非 CD-3 target，不实施）

Frozen Inventory Verdicts:
REUSE（CA-021 Evidence / CA-024 Taint）

Target HFM Modules:
apps/backend/src/hfm/models/evidence.py
apps/backend/src/hfm/repositories/evidence.py
apps/backend/alembic/versions/0004_cd3_evidence.py

Database Scope:
evidences 单表（FK/CHECK/索引/迁移）

Migration Scope:
0004（down_revision = 0003；禁止修改 0001-0003）

Repository Scope:
EvidenceRepository（create 计算 content_hash + 锚点校验；mark_tainted；get_by_source_ref）

Service Scope:
0（Frozen CD-3 未列 service）

API Scope:
0

Data Import Scope:
HFB DATA IMPORT: NOT PERFORMED

Frontend Scope:
Frontend Business Changes: 0

Applicable Core Invariants:
I1 Provenance — APPLICABLE（Evidence → SourceRef → Source；至少一锚点；orphan 拒绝）
I4 No Silent Overwrite — APPLICABLE（id / content_hash / 锚点字段 protected）
I5 Stable Identity — APPLICABLE（Evidence 稳定 UUIDv7）
I6 HFB Runtime Independence — APPLICABLE
I2 / I3 — NOT IN CD-3 SCOPE（CD-2 已验收 I2；I3 属 CD-4；回归保持）

Test Gates:
lineage（Evidence→SourceRef→Source 溯源 + orphan 拒绝 + 锚点校验）
integrity（content_hash 确定性 + 不可变）
taint 生命周期（clean → source_withdrawn/quarantined）
migration 0003→0004 + 0004 downgrade

Explicit Exclusions:
AcademicTaintAuditLog 独立审计表（后续；本轮仅 taint 字段 + mark_tainted）
GenerationProof / retrieval_snapshot（研究层，非 Publication Snapshot）
Assertion / Citation（CD-4/CD-5）
Publication / Snapshot / Public Portal / Auth / 前端 / Phase 1（G1-G4/G7）
API / Service

Blocked Downstream Nodes:
CD-4（依赖 CD-3）
```

**CD-3 SCOPE: CONFIRMED**（无歧义，可唯一解析）。

## Traceability Matrix

| CD-3 Requirement | Frozen Contract | HFB Source | Frozen Verdict | HFM Target | Implementation | Test |
| --- | --- | --- | --- | --- | --- | --- |
| Evidence（description/evidence_level） | CANONICAL + EVIDENCE §2 | CA-021 `academic_evidence.py::Evidence` | REUSE | `models/evidence.py` | Evidence 模型 | test_evidence_model.py |
| EvidenceLevel 枚举 | EVIDENCE §2（Level 1-4） | CA-021 `EvidenceLevel` | REUSE | `models/evidence.py` | LEVEL_1..4 | test_evidence_model.py |
| Evidence→SourceRef 锚点（I1） | EVIDENCE（SourceRef→Evidence） | CA-021 source_ref_id | REUSE | evidence.source_ref_id FK RESTRICT | FK + 溯源测试 | test_evidence_provenance.py |
| Evidence→Passage 锚点 | EVIDENCE（Evidence↔Passage） | CA-021 source_passage_id | REUSE | evidence.source_passage_id FK SET NULL | FK | test_evidence_provenance.py |
| 至少一锚点（orphan 拒绝） | EVIDENCE I1（无孤儿） | — | NEW | DB CHECK（source_ref_id OR source_passage_id NOT NULL） | CHECK + orphan 测试 | test_evidence_provenance.py |
| content_hash 完整性 | EVIDENCE §2.6（canonical hash） | hfm.core.hashing（B1）+ CA-028 判定 | REUSE | evidence.content_hash（protected） | create 计算 + 不可变 | test_evidence_model.py |
| Taint 生命周期 | CA-024 + EVIDENCE（taint） | CA-024 taint 字段 | REUSE | evidence.taint_status/tainted_at/taint_reason + mark_tainted | 状态转换测试 | test_evidence_model.py |
| EvidenceRepository | DAG CD-3（实现层） | — | ADAPT | `repositories/evidence.py` | create/get_by_source_ref/mark_tainted/update | test_repositories_cd3.py |
| Migration 0004 | DAG CD-3（DB scope） | — | NEW | `alembic/versions/0004` | evidences 表 + CHECK/FK/索引 | test_migrations.py |

**Scope/Verdict 计数语义**：Frozen Scope Items = 9（矩阵行数）；资产裁决 = REUSE 2（CA-021 Evidence / CA-024 Taint；CA-028 判定记录但不实施）；NEW 实现单元 = 3（content_hash 字段 + at-least-one-anchor CHECK + 迁移 0004）；ADAPT 实现单元 = 1（EvidenceRepository）。详见实施报告。
