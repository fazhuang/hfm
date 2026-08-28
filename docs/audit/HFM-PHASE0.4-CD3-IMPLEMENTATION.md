# HFM Phase 0.4 — CD-3 Implementation Report

Date: 2026-08-27 · Phase 0.4 — Core Domain Implementation CD-3
性质：Core Domain 第四批实施（Frozen DAG CD-3 节点唯一准绳）

## 1. Acceptance Target

HFM Phase 0.4 — Core Domain Implementation CD-3（Evidence + taint + content_hash）

## 2. Starting CD-2 Baseline

- **CD-2 Implementation Baseline**：`b545e5babfc8aa4b89f1488112c544afd927b4ba`（HFM HEAD = origin/main，working tree clean）

## 3. Core Domain Contract Baseline

- `366df69715613022326eb7a3c06ae7f145ebacb9`

## 4. HFB Source Snapshot

- `03755b57ec0e4c8023d1447619f7d6ead9e44d73`（固定只读）

## 5. Frozen CD-3 Scope

- 详见 `docs/migration/hfb/HFM-PHASE0.4-CD3-IMPLEMENTATION-SCOPE.md`（**CD-3 SCOPE: CONFIRMED**）
- 对象：Evidence + EvidenceLevel + taint + content_hash
- 依赖：CD-0（SourceRef/Source + hashing + immutable 守卫）+ CD-2（Passage 锚点）
- 排除：AcademicTaintAuditLog 独立表（后续）、GenerationProof（CA-028 判定记录不实施）、Assertion/Citation（CD-4/CD-5）、Publication/Snapshot/API/Auth/前端/Phase 1、数据导入 NOT PERFORMED

## 6. Traceability Matrix

- 见 Scope 文档（9 项 Requirement → Contract → HFB → Verdict → Target → Implementation → Test）

## 7. Implemented Domain Objects

```text
apps/backend/src/hfm/models/evidence.py      # Evidence + EvidenceLevel（LEVEL_1..4）+ taint + content_hash
apps/backend/src/hfm/repositories/evidence.py
apps/backend/alembic/versions/0004_cd3_evidence.py
```

## 8. Relationships

```text
Evidence.source_ref_id → SourceRef（RESTRICT，可空）
Evidence.source_passage_id → Passage（SET NULL，可空）
CHECK: source_ref_id IS NOT NULL OR source_passage_id IS NOT NULL（至少一锚点，I1）
```

## 9–12. REUSE / EXTEND / ADAPT / NEW

```text
REUSE: 2（CA-021 Evidence / CA-024 Taint — Frozen Inventory 裁决；CA-028 GenerationProof 判定记录但不实施）
EXTEND: 0
ADAPT: 1（EvidenceRepository — create 计算 content_hash + 锚点校验 + mark_tainted）
NEW: 3（content_hash 字段、at-least-one-anchor CHECK、Migration 0004）
```

Scope/Verdict Count Semantics: **CLEAR** — Frozen Scope Items = 9（矩阵行数）；资产裁决 = REUSE 2；NEW/ADAPT 为 HFM 原生实现单元，与资产裁决分属不同计数体系。

## 13. Database Changes

- `evidences` 单表（description/evidence_level/source_ref_id/source_passage_id/content_hash/taint_*）+ CHECK（evidence_level 4 值 / taint_status 3 值 / at-least-one-anchor）+ FK（source_ref RESTRICT / passage SET NULL）+ 索引（source_ref_id / source_passage_id）

## 14. Migration Changes

- `0004_cd3_evidence.py`（down_revision = 0003；未修改 0001-0003）
- 验证：fresh head upgrade PASS；**既有 CD-2 DB（0003）→ head（0004）原地升级 PASS**；0004 downgrade 保留 CD-0/1/2 表 PASS

## 15. Repository Changes

- `EvidenceRepository`：create（锚点校验 + content_hash 确定性计算）、update（immutable 守卫：id/content_hash/source_ref_id/source_passage_id 拒绝变更）、mark_tainted（clean→source_withdrawn/quarantined）、get_by_source_ref、get_by_id/list/count/delete（BaseRepository）

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

## 20. Applicable Invariants

```text
I1 Provenance — APPLICABLE（Evidence → SourceRef → Source 溯源；至少一锚点；orphan 拒绝）
I4 No Silent Overwrite — APPLICABLE（id/content_hash/锚点 protected）
I5 Stable Identity — APPLICABLE（Evidence 稳定 UUIDv7）
I6 HFB Runtime Independence — APPLICABLE
I2 / I3 — NOT IN CD-3 SCOPE（I2 已由 CD-2 验收，回归保持；I3 属 CD-4）
```

## 21. Invariant Tests

- I1：Evidence→SourceRef→Source 全链溯源（test_invariant_i1_evidence_source_ref_source_traceability）、Passage 锚点（test_invariant_i1_evidence_passage_anchor）、orphan 拒绝（repository + DB CHECK 双层）、content_hash 确定性（test_evidence_content_hash_deterministic）
- I4：content_hash / 锚点 protected（test_evidence_content_hash_protected / test_evidence_immutable_fields_declared）
- I5：稳定 ID（test_evidence_construction_with_source_ref）

## 22. Negative Tests

- orphan Evidence（repository ValueError + DB CHECK IntegrityError 双层）
- 非法 source_ref（FK IntegrityError）
- source_ref RESTRICT（删除锚定 Evidence 的 SourceRef 失败）
- 非法 taint status（ValueError）
- 缺 description（ValueError）

## 23. CD-0 Regression

- CD-0 全部测试原样通过（Source immutable key / repository guard / model guard）；pytest 全量含 CD-0 60 项

**CD-0 Regression: PASS**

## 24. CD-1 Regression

- CD-1 全部测试原样通过（Entity/Person/转写契约）

**CD-1 Regression: PASS**

## 25. CD-2 Regression

- CD-2 全部测试原样通过（Work/Edition/Version/Chapter/Passage + I2 谱系 + cross-work + protected guard + 迁移 0003）

**CD-2 Regression: PASS**

## 26. Phase 0.3 Regression

- /health /ready /version /live /config 200；X-Request-ID 正常；/config Secret Exposure NO；前端 Vitest 24 / build PASS

**Phase 0.3 Regression: PASS**

## 27. Quality Gates

| Gate | Result |
| --- | --- |
| Ruff | PASS |
| Ruff format | PASS（83 files） |
| mypy --strict | PASS（78 source files，零豁免） |
| pytest | **130 passed**（前 112 + CD-3 18） |
| ESLint | PASS |
| Prettier | PASS |
| vue-tsc | PASS |
| Vitest | **24 passed / 8 files**（无前端变更，回归） |
| Build | PASS |

## 28. Runtime Smoke

- /health /ready /version /live /config 全部 200；X-Request-ID 正常；/config Secret Exposure NO

## 29. HFB Independence

- 无 `Sites/hfb` / `../hfb` / `from hfb` / `import hfb` / `@hfb/` / `03755b57`（docs provenance 除外）；无 symlink/submodule/path dep/HTTP/共享 DB/运行时文件读取

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

（未授权扫描命中仅为已冻结字段 `research_relation_role`（CD-1）/`publisher_block`（CD-2），非 Role/Publisher 语义；无 CD-4+/Publication/Snapshot/PublicPortal/Medical/ICH/Anonymous/JWT 实现。）

## 32. Existing P3 Status

```text
Existing P3:
Starlette/httpx deprecation warning

Status:
OPEN / NON-BLOCKING
```

未因 CD-3 改变严重性；未顺手修复、未升级依赖。

## 33. Phase 1 Boundary

- 未实现 G1/G2/G3/G4/G7；无 Publication/Medical/Auth/前端泄漏；Evidence 与 Admission/Publication 完全解耦（无 review_status/publication_status 字段）

## 34. Scope Closure

```text
CD-3 Frozen Scope Items:
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
