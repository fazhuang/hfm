# HFM Phase 0.4 — CD-5 Implementation Report

Date: 2026-08-27 · Phase 0.4 — Core Domain Implementation CD-5
性质：Core Domain 第六批实施（Frozen DAG CD-5 节点唯一准绳）

## 1. Acceptance Target

HFM Phase 0.4 — Core Domain Implementation CD-5（Citation，target = Assertion；撤回引用 + 版本固定）

## 2. Starting CD-4 Baseline

- **CD-4 Implementation Baseline**：`82505d11d7f0591de1df342f03b4e78c5c4300a7`（HFM HEAD = origin/main，working tree clean）

## 3. Core Domain Contract Baseline

- `366df69715613022326eb7a3c06ae7f145ebacb9`

## 4. HFB Source Snapshot

- `03755b57ec0e4c8023d1447619f7d6ead9e44d73`（固定只读）

## 5. Frozen CD-5 Scope

- 详见 `docs/migration/hfb/HFM-PHASE0.4-CD5-IMPLEMENTATION-SCOPE.md`（**CD-5 SCOPE: CONFIRMED**）
- 对象：Citation（target_assertion / evidence 直接边 / pinned version / passage / quote_text / note）
- 依赖：CD-4（Assertion target）+ CD-3（Evidence 直接边）+ CD-2（Version/Passage pinned）
- 排除：CA-027 Document rights（权利层 G4/G13）、第二套 locator（复用 CD-2 语义）、Publication/Snapshot/Auth/前端/Phase 1、数据导入 NOT PERFORMED

## 6. Traceability Matrix

- 见 Scope 文档（9 项 Requirement → Contract → HFB → Verdict → Target → Implementation → Test）

## 7. Implemented Domain Objects

```text
apps/backend/src/hfm/models/citation.py      # Citation（统一 target=Assertion + pinned Version/Passage + Evidence 边）
apps/backend/src/hfm/repositories/citation.py
apps/backend/alembic/versions/0006_cd5_citation.py
```

## 8. Relationships

```text
Citation.target_assertion_id → Assertion（RESTRICT，NOT NULL — 统一 target，orphan 预防）
Citation.evidence_id → Evidence（SET NULL — 直接证据边，Lineage §2.3）
Citation.version_id → Version（SET NULL — pinned version，I2）
Citation.passage_id → Passage（SET NULL — 文本定位）
```

## 9–12. REUSE / EXTEND / ADAPT / NEW

```text
REUSE: 1（quote_text/note 字段 + Evidence 直接边 — CA-022/CA-021）
EXTEND: 0
ADAPT: 2（Citation 模型 CA-022 多态→统一 target；CitationRepository）
NEW: 6（target FK / version pin / passage pin / withdrawn 拒绝 / immutable 守卫 / 迁移 0006）
```

Scope/Verdict Count Semantics: **CLEAR** — Frozen Scope Items = 9（矩阵行数）；资产裁决 = ADAPT 2 + REUSE 1 + NEW 6；CA-027 判定记录不实施。

## 13. Database

- `citations` 表（target_assertion/evidence/version/passage/quote_text/note/created_by）+ FK/索引

## 14. Migration

- `0006_cd5_citation.py`（down_revision = 0005；未修改 0001-0005）
- 验证：fresh head upgrade PASS；**既有 CD-4 DB（0005）→ head（0006）原地升级 PASS**；0006 downgrade 保留 CD-0/1/2/3/4 表 PASS；0001-0005 零语义修改（历史 migration 完整性）

## 15. Repository

- `CitationRepository`：create（target 必需 + 非 withdrawn 门禁 + FK 存在）、get_by_target_assertion、immutable 守卫（id/target/evidence/version/passage/quote/created_by 拒绝变更）

## 16. Service Changes

```text
Service Changes:
0
```

## 17. Data Import

```text
HFB DATA IMPORT:
NOT PERFORMED
```

## 18. API Changes

```text
API Changes:
0
```

## 19. Frontend Changes

```text
Frontend Business Changes:
0
```

## 20. Invariant Matrix

| Invariant | CD-5 Applicability | Current Core Status | Evidence/Test |
| --- | --- | --- | --- |
| I1 Provenance | NOT NEWLY APPLICABLE | **PASS**（CD-3 回归） | test_invariant_i1_*（CD-3） |
| I2 Version Reproducibility | **DIRECTLY APPLICABLE**（Citation pinned Version） | **PASS** | test_i2_citation_pinned_version_no_latest_drift / test_i2_citation_version_pin_immutable |
| I3 Assertion Coexistence | NOT NEWLY APPLICABLE | **PASS**（CD-4 回归） | test_i3_*（CD-4） |
| I4 No Silent Overwrite | APPLICABLE | **PASS** | test_citation_binding_immutable |
| I5 Stable Identity | APPLICABLE | **PASS** | test_citation_construction |
| I6 HFB Independence | APPLICABLE | **PASS** | 独立性审计 |

## 21. Negative Tests

- 缺 target（ValueError）、target FK orphan（ValueError + FK）、binding 字段 update/直接赋值拒绝（I4）、withdrawn Assertion 引用拒绝、缺失 evidence FK 拒绝、target RESTRICT（引用后删除失败）

## 22. CD-0 Regression

**PASS**（Source immutable / repository guard / model guard 原样通过）

## 23. CD-1 Regression

**PASS**（Entity/Person/转写契约原样通过）

## 24. CD-2 Regression

**PASS**（Work/Edition/Version/Chapter/Passage + I2 谱系 + cross-work + protected guard 原样通过）

## 25. CD-3 Regression

**PASS**（Evidence/content_hash 确定性/immutable/直接 ORM 突变拒绝/Taint/迁移 0004 原样通过）

## 26. CD-4 Regression

**PASS**（Assertion 冲突并存/protected fields/revision immutable/Assertion↔Evidence M:N/迁移 0005 原样通过）

## 27. Phase 0.3 Regression

- /health /ready /version /live /config 200；X-Request-ID 正常；/config Secret Exposure NO；前端 Vitest 24 / build PASS

## 28. Quality Gates

| Gate | Result |
| --- | --- |
| Ruff | PASS |
| Ruff format | PASS（98 files） |
| mypy --strict | PASS（91 source files，零豁免） |
| pytest | **167 passed**（前 152 + CD-5 15） |
| ESLint | PASS |
| Prettier | PASS |
| vue-tsc | PASS |
| Vitest | **24 passed / 8 files**（无前端变更，回归） |
| Build | PASS |

## 29. Runtime Smoke

- /health /ready /version /live /config 全部 200；X-Request-ID 正常；/config Secret Exposure NO

## 30. HFB Independence

- 无 `Sites/hfb` / `../hfb` / `from hfb` / `import hfb` / `@hfb/` / `03755b57`；无 symlink/submodule/path dep/HTTP/共享 DB/运行时文件读取

**Permanent HFB Runtime Dependency: NO**

## 31. Contract Deviations

```text
Contract Deviations:
0
```

## 32. Unauthorized Additions

```text
Unauthorized Additions:
0
```

（泄漏扫描仅命中已冻结 `publisher_block`（CD-2 书目字段）；无 published/publication_status/reviewer/publisher/snapshot/JWT 字段；Citation 不承担发布/审核语义。）

## 33. Existing P3

```text
Existing P3:
Starlette/httpx deprecation warning — OPEN / NON-BLOCKING
```

未因 CD-5 改变严重性；未顺手修复。

## 34. Phase 1 Boundary

- 未实现 G1/G2/G3/G4/G7；无 Publication/Auth/Reviewer/Publisher/前端泄漏；Citation 仅为可复现引用（不含 claim/approval/publication 语义）

## 35. Scope Closure

```text
CD-5 Frozen Scope Items:
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
