# HFM Phase 0.4 — CD-2 Implementation Report

Date: 2026-08-27 · Phase 0.4 — Core Domain Implementation CD-2
性质：Core Domain 第三批实施（Frozen DAG CD-2 节点唯一准绳）

## 1. Acceptance Target

HFM Phase 0.4 — Core Domain Implementation CD-2（Work/Edition/Version/Chapter/Passage + Locator）

## 2. Starting CD-1 Baseline

- **CD-1 Implementation Baseline**：`5d4790e7b4f5675def3811144f6b718fce20a064`（HFM HEAD = origin/main，working tree clean）

## 3. Core Domain Contract Baseline

- `366df69715613022326eb7a3c06ae7f145ebacb9`

## 4. HFB Source Snapshot

- `03755b57ec0e4c8023d1447619f7d6ead9e44d73`（固定只读）

## 5. Frozen CD-2 Scope

- 详见 `docs/migration/hfb/HFM-PHASE0.4-CD2-IMPLEMENTATION-SCOPE.md`（**CD-2 SCOPE: CONFIRMED**）
- 对象：Work / Edition / Version / Chapter / Passage + Locator（CD-0 复用）
- 依赖：CD-0（Locator/DB 基座/immutable 守卫）+ CD-1（Entity — Work.author_entity_id）
- 排除：Manifestation/Book/ClassicalVersion/VersionRelation/NormalizedText/Sentence/Token/Variant/Commentary/TEI（留待后续）；Assertion/Evidence/Citation；Publication/Snapshot；API/Auth/前端/Phase 1；数据导入 NOT PERFORMED

## 6. Traceability Matrix

- 见 Scope 文档（9 项 Requirement → Contract → HFB → Target → Verdict → Implementation → Test）

## 7. Implemented Objects

```text
apps/backend/src/hfm/models/{work,edition,version,chapter,passage}.py
apps/backend/src/hfm/repositories/{work,edition,version,chapter,passage}.py
apps/backend/alembic/versions/0003_cd2_ancient_text.py
```

## 8. Relationships

```text
Edition.work_id → Work（CASCADE）
Version.edition_id → Edition（CASCADE）
Version.parent_version_id → Version（SET NULL，谱系）
Chapter.work_id → Work（CASCADE）
Chapter.parent_id → Chapter（CASCADE，层级）
Passage.chapter_id → Chapter（CASCADE）
Passage.version_id → Version（SET NULL，pinned fixed reference）
Work.author_entity_id → entities.id（SET NULL，CD-1 Entity person）
```

## 9–12. REUSE / EXTEND / ADAPT / NEW

```text
REUSE: 5（Work CA-007 / Edition CA-008 / Version CA-012 / Chapter CA-014 / Passage CA-015 — Frozen Inventory 裁决）
EXTEND: 0
ADAPT: 0
NEW: 6（5 repositories + Migration 0003 — 实现单元，非资产裁决）
```

Scope/Verdict Count Semantics: **CLEAR** — Frozen Scope Items = 9（矩阵行数）；资产裁决 = REUSE 5（无 EXTEND/ADAPT/NEW 资产裁决，沿用 Frozen Inventory）；NEW 6 = HFM 原生实现单元（repositories + migration），与资产裁决分属不同计数体系。

## 13. Database Changes

五表：works / editions / versions / chapters / passages（FK/约束/索引见迁移 0003）。

## 14. Migration Changes

- `0003_cd2_ancient_text.py`（down_revision = 0002；未修改 0001/0002）
- 验证：fresh head upgrade PASS；**既有 CD-1 DB（0002）→ head（0003）原地升级 PASS**；0003 downgrade 保留 CD-0/CD-1 表 PASS

## 15. Repository Changes

- WorkRepository / EditionRepository / VersionRepository（含 get_by_edition + lineage_has_cycle）/ ChapterRepository / PassageRepository（含 get_by_chapter）— 均基于 BaseRepository（immutable 守卫沿用）

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

## 18. Data Import

```text
HFB DATA IMPORT:
NOT PERFORMED
```

## 19. Applicable Invariants

```text
I2 Version Reproducibility — APPLICABLE（immutable identity / lineage / pinned reference / no latest swap / cycle detection）
I4 No Silent Overwrite — APPLICABLE（immutable id 守卫沿用）
I5 Stable Identity — APPLICABLE（五对象稳定 UUIDv7）
I6 HFB Runtime Independence — APPLICABLE
I1 / I3 — NOT IN CD-2 SCOPE（CD-3/CD-4）
```

## 20. Invariant Tests

- I2：lineage 无环（test_invariant_i2_version_lineage_acyclic）、cycle 检测（test_invariant_i2_cycle_detection）、pinned version 可复现（test_invariant_i2_pinned_version_reproducible）、无 latest 替换（test_passage_pinned_version_not_swapped）
- I5：稳定 ID（test_invariant_i5_stable_identity）
- I4：immutable id 守卫（test_work_update_rejects_immutable_id）

## 21. Negative Tests

- FK 缺失父：Edition/Version/Chapter/Passage 孤儿创建拒绝（IntegrityError）
- 错误父类型：跨域无效引用拒绝
- 级联删除：Edition→Version、Chapter→Passage
- 谱系缺失父拒绝

## 22. CD-0 Regression

- CD-0 全部测试原样通过（Source immutable key / repository guard / model guard）；pytest 全量含 CD-0 60 项

**CD-0 Regression: PASS**

## 23. CD-1 Regression

- CD-1 全部测试原样通过（Entity/Person/转写契约）；pytest 全量含 CD-1 17 项

**CD-1 Regression: PASS**

## 24. Phase 0.3 Regression

- /health /ready /version /live /config 200；X-Request-ID 正常；/config Secret Exposure NO；前端 Vitest 24 / build PASS

**Phase 0.3 Regression: PASS**

## 25. Quality Gates

| Gate | Result |
| --- | --- |
| Ruff | PASS |
| Ruff format | PASS（77 files） |
| mypy --strict | PASS（73 source files，零豁免） |
| pytest | **104 passed**（CD-0/1 77 + CD-2 27） |
| ESLint | PASS |
| Prettier | PASS |
| vue-tsc | PASS |
| Vitest | **24 passed / 8 files**（无前端变更，回归） |
| Build | PASS |

## 26. Runtime Smoke

- /health /ready /version /live /config 全部 200；X-Request-ID 正常；/config Secret Exposure NO

## 27. HFB Independence

- 无 `Sites/hfb` / `../hfb` / `from hfb` / `import hfb` / `@hfb/` / `03755b57`（docs provenance 除外）；无 symlink/submodule/path dep/HTTP/共享 DB

**Permanent HFB Runtime Dependency: NO**

## 28. Contract Deviations

```text
Contract Deviations:
0
```

## 29. Unauthorized Additions

```text
Unauthorized Additions:
0
```

（未授权扫描：仅 `publisher_block`（Edition 刻板/藏版机构书目字段，CA-008 REUSE）与 .pyc 字节码产物命中关键词；无 Publication/PublicPortal/Anonymous/Medical/ICH/SoD/Publisher 角色实现。）

## 30. Phase 1 Boundary

- 未实现 G1/G2/G3/G4/G7；无 API/Auth/RBAC/前端业务

## 31. Scope Closure

```text
CD-2 Frozen Scope Items:
9（Scope 文档 Traceability Matrix 行数）

Implemented:
9

Deferred:
0

Unauthorized Additions:
0

Contract Deviations:
0
```
