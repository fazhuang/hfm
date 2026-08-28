# HFM Phase 0.4 — CD-4 Implementation Report

Date: 2026-08-27 · Phase 0.4 — Core Domain Implementation CD-4
性质：Core Domain 第五批实施（Frozen DAG CD-4 节点唯一准绳）

## 1. Acceptance Target

HFM Phase 0.4 — Core Domain Implementation CD-4（Assertion 契约：I3 冲突并存 / I4 no-silent-overwrite / I1 provenance）

## 2. Starting CD-3 Baseline

- **CD-3 Implementation Baseline**：`3e3945d754630e25b2f4c65228dbdb5d4beef35f`（HFM HEAD = origin/main，working tree clean）

## 3. Core Contract Baseline

- `366df69715613022326eb7a3c06ae7f145ebacb9`

## 4. HFB Snapshot

- `03755b57ec0e4c8023d1447619f7d6ead9e44d73`（固定只读）

## 5. Frozen CD-4 Scope

- 详见 `docs/migration/hfb/HFM-PHASE0.4-CD4-IMPLEMENTATION-SCOPE.md`（**CD-4 SCOPE: CONFIRMED**）
- 对象：Assertion + AssertionType/EditorialStatus/Confidence + Assertion↔Evidence M:N
- 依赖：CD-1（Entity subject/object 锚点）+ CD-3（Evidence）
- 排除：CandidateExtraction 治理链（provenance 占位）、Publication/Snapshot/Auth/Reviewer/Publisher/前端/Phase 1、数据导入 NOT PERFORMED

## 6. Traceability Matrix

- 见 Scope 文档（9 项 Requirement → Contract → HFB → Verdict → Target → Implementation → Test）

## 7. Implemented Domain Objects

```text
apps/backend/src/hfm/models/assertion.py      # Assertion + AssertionType/EditorialStatus/Confidence + assertion_evidences join
apps/backend/src/hfm/repositories/assertion.py
apps/backend/alembic/versions/0005_cd4_assertion.py
```

## 8. Relationships

```text
Assertion.subject_entity_id → Entity（RESTRICT，NOT NULL — 参照完整性，orphan 预防）
Assertion.object_entity_id → Entity（SET NULL，可空）
Assertion ↔ Evidence — assertion_evidences M:N（CASCADE 双向）
CHECK: value OR object_entity_id（至少一个值/对象）
CHECK: assertion_type / editorial_status / confidence 枚举
```

## 9–12. REUSE / EXTEND / ADAPT / NEW

```text
REUSE: 0
EXTEND: 0
ADAPT: 1（AssertionRepository — create 校验/attach_evidence/get_by_subject/immutable 守卫；CA-026 桥 provenance 占位）
NEW: 8（Assertion 模型 + 3 枚举 + M:N join + subject FK + 值/对象表达 + I3 无唯一约束 + 迁移 0005）
```

Scope/Verdict Count Semantics: **CLEAR** — Frozen Scope Items = 9（矩阵行数）；资产裁决 = NEW 8 + ADAPT 1；REUSE/EXTEND 0。两套计数分属不同体系。

## 13. Database

- `assertions` 表（subject/predicate/value/object/type/confidence/editorial_status/created_by/revision）+ `assertion_evidences` join 表 + CHECK/FK/索引

## 14. Migration

- `0005_cd4_assertion.py`（down_revision = 0004；未修改 0001-0004）
- 验证：fresh head upgrade PASS；**既有 CD-3 DB（0004）→ head（0005）原地升级 PASS**；0005 downgrade 保留 CD-0/1/2/3 表 PASS；0001-0004 零语义修改（历史 migration 完整性）

## 15. Repository

- `AssertionRepository`：create（subject 必需 + value/object 至少其一）、attach_evidence/detach_evidence（M:N，重复 no-op，不覆盖他人）、get_by_subject、get_evidence_ids、immutable 守卫（id/subject/predicate/value/object/type 拒绝变更）

## 16. Service Changes

```text
Service Changes:
0
```

## 17. API Changes

```text
API Changes:
0
```

## 18. Frontend Changes

```text
Frontend Business Changes:
0
```

## 19. Data Import

```text
HFB DATA IMPORT:
NOT PERFORMED
```

## 20. Invariant Matrix

| Invariant | CD-4 Applicability | Current System Status | Automated Test |
| --- | --- | --- | --- |
| I1 Provenance | NOT NEWLY APPLICABLE | **PASS**（CD-3 已冻结实现；回归） | test_invariant_i1_evidence_source_ref_source_traceability（CD-3） |
| I2 Version Reproducibility | NOT NEWLY APPLICABLE | **PASS**（CD-2 已冻结实现；回归） | test_invariant_i2_*（CD-2） |
| I3 Assertion Coexistence | **APPLICABLE** | **PASS**（本批实现） | test_i3_*/ test_i4_* |
| I4 No Silent Overwrite | **APPLICABLE** | **PASS** | test_assertion_content_immutable / test_i4_* |
| I5 Stable Identity | APPLICABLE | **PASS** | test_assertion_construction |
| I6 HFB Independence | APPLICABLE | **PASS** | 独立性审计 |

## 21. Negative Tests

- orphan subject（FK IntegrityError）、缺 subject / 缺 value+object（ValueError）、内容字段 update/直接赋值拒绝（I4）、editorial_status 转换保留内容、缺失 evidence/assertion 关联拒绝、重复 evidence 关联 no-op、无 UNIQUE(subject,predicate) 结构断言

## 22. CD-0 Regression

**PASS**（Source immutable / repository guard / model guard 原样通过）

## 23. CD-1 Regression

**PASS**（Entity/Person/转写契约原样通过）

## 24. CD-2 Regression

**PASS**（Work/Edition/Version/Chapter/Passage + I2 谱系 + cross-work + protected guard 原样通过）

## 25. CD-3 Regression

**PASS**（Evidence/EvidenceLevel/I1/orphan/content_hash 确定性/description·evidence_level·content_hash immutable/直接 ORM 突变拒绝/Taint/迁移 0004 原样通过）

## 26. Phase 0.3 Regression

- /health /ready /version /live /config 200；X-Request-ID 正常；/config Secret Exposure NO；前端 Vitest 24 / build PASS

## 27. Quality Gates

| Gate | Result |
| --- | --- |
| Ruff | PASS |
| Ruff format | PASS（90 files） |
| mypy --strict | PASS（84 source files，零豁免） |
| pytest | **152 passed**（前 131 + CD-4 21） |
| ESLint | PASS |
| Prettier | PASS |
| vue-tsc | PASS |
| Vitest | **24 passed / 8 files**（无前端变更，回归） |
| Build | PASS |

## 28. Runtime Smoke

- /health /ready /version /live /config 全部 200；X-Request-ID 正常；/config Secret Exposure NO

## 29. HFB Independence

- 无 `Sites/hfb` / `../hfb` / `from hfb` / `import hfb` / `@hfb/` / `03755b57`；无 symlink/submodule/path dep/HTTP/共享 DB/运行时文件读取

**Permanent HFB Runtime Dependency: NO**

## 30. Contract Deviations

```text
Contract Deviations:
0
```

## 31. Unauthorized Additions

```text
Unauthorized Additions:
0
```

（泄漏扫描仅命中已冻结 `publisher_block`（CD-2 书目字段）；无 published/publication_status/reviewer/publisher/snapshot/JWT/permission 字段；editorial_status 为 Frozen 研究编辑态，非 Phase-1 workflow。）

## 32. Existing P3

```text
Existing P3:
Starlette/httpx deprecation warning — OPEN / NON-BLOCKING
```

未因 CD-4 改变严重性；未顺手修复。

## 33. Phase 1 Boundary

- 未实现 G1/G2/G3/G4/G7；无 Publication/Auth/Reviewer/Publisher/前端泄漏；Assertion 仅含 Frozen 研究编辑态（draft/reviewed/approved/withdrawn），无发布语义

## 34. Scope Closure

```text
CD-4 Frozen Scope Items:
9（Scope 文档 Traceability Matrix 行数）

Implemented:
9

Deferred:
0

Unauthorized Additions:
0

Contract Deviations:
0

Scope Completion:
PASS
```
