# HFM Phase 0.4 — CD-2 Implementation Scope

Date: 2026-08-27 · Phase 0.4 — Core Domain Implementation CD-2
起始基线：`5d4790e7b4f5675def3811144f6b718fce20a064`（CD-1 Implementation Baseline）
Core Domain Contract Baseline：`366df69715613022326eb7a3c06ae7f145ebacb9`
HFB Source Snapshot：`03755b57ec0e4c8023d1447619f7d6ead9e44d73`
唯一准绳：`HFM-PHASE0.4-CORE-MIGRATION-DAG.md`（Frozen）CD-2 节点

## CD-2 Scope Extraction（摘自 Frozen DAG）

```text
CD-2 ID:
CD-2

Purpose:
Work / Edition / Version / Chapter / Passage + Locator（古籍文本层）

Included Domain Objects:
Work
Edition
Version
Chapter
Passage

Included Value Objects:
Locator（CD-0 已建，复用；locator 解析 = 由 FK 链推导，不新增冗余列）

Required Relationships:
Edition.work_id → Work
Version.edition_id → Edition（版本表达；I2）
Version.parent_version_id → Version（谱系，自引用）
Chapter.work_id → Work（HFM 锚点；HFB 为 book_id，CD-2 无 Book）
Chapter.parent_id → Chapter（层级，自引用）
Passage.chapter_id → Chapter
Passage.version_id → Version（可空，版本绑定；fixed reference）

Dependencies on CD-0:
Locator / Source / SourceRef / Institution / DB 基座 / immutable_fields / BaseRepository

Dependencies on CD-1:
Entity（Work.author_entity_id FK → entities.id）

HFB Source Assets:
CA-007（Work）REUSE
CA-008（Edition）REUSE
CA-012（Version）REUSE（I2 谱系/固定引用以 HFM 实现扩展）
CA-014（Chapter）REUSE
CA-015（Passage）REUSE（locator 解析 EXTEND 性质已记于 Inventory 注释）
（CA-009 NormalizedText / CA-010 Book / CA-011 ClassicalVersion / CA-013 VersionRelation /
 CA-016 Sentence/Token/Variant / CA-017 Commentary / CA-018 TEI — 非 CD-2 target，留待后续）

Frozen Inventory Verdicts:
全部 REUSE（CA-007/008/012/014/015）

Target HFM Modules:
apps/backend/src/hfm/models/{work,edition,version,chapter,passage}.py
apps/backend/src/hfm/repositories/{work,edition,version,chapter,passage}.py
apps/backend/alembic/versions/0003_cd2_ancient_text.py

Database Scope:
works / editions / versions / chapters / passages 五表（FK/约束/索引/迁移）

Migration Scope:
0003（down_revision = 0002；禁止修改 0001/0002）

Repository Scope:
WorkRepository / EditionRepository / VersionRepository / ChapterRepository / PassageRepository

Service Scope:
0（Frozen CD-2 未列 service）

API Scope:
0

Data Import Scope:
HFB DATA IMPORT: NOT PERFORMED

Frontend Scope:
Frontend Business Changes: 0

Applicable Invariants:
I2 Version Reproducibility — APPLICABLE（版本身份稳定/谱系/固定引用/latest 不替换 pinned）
I4 No Silent Overwrite — APPLICABLE（immutable id 守卫沿用）
I5 Stable Identity — APPLICABLE（全部对象稳定 UUIDv7 ID）
I6 HFB Runtime Independence — APPLICABLE（独立性审计）
I1 / I3 — NOT IN CD-2 SCOPE（CD-3/CD-4）

Test Gates:
版本可复现（I2）+ locator 解析 + FK 负向测试 + migration 0002→0003

Explicit Exclusions:
Manifestation / Book / ClassicalVersion / VersionRelation（独立表）/ NormalizedText /
OCRArtifact / FragmentProvenance / Sentence / Token / Variant / Commentary / TEI（留待后续）
Assertion / Evidence / Citation（CD-3/CD-4/CD-5）
Publication / Snapshot（G3）
API / Auth/RBAC / 前端 / Phase 1（G1-G4/G7）

Blocked Downstream Nodes:
CD-3（依赖 CD-2）
```

**CD-2 SCOPE: CONFIRMED**（无歧义，可唯一解析）。

## Traceability Matrix

| CD-2 Requirement | Frozen Contract | HFB Asset | Verdict | HFM Target | Implementation | Test |
| --- | --- | --- | --- | --- | --- | --- |
| Work | CANONICAL（Work REUSE） | CA-007 `bibliographic.py::Work` | REUSE | `models/work.py` | title/author_entity_id/dynasty/composition years/category/is_extant/description | test_work_model.py |
| Edition | CANONICAL（Edition REUSE） | CA-008 `bibliographic.py::Edition` | REUSE | `models/edition.py` | work_id/edition_name/era/publisher_block/preface_postscript/lineage_parent_edition_id | test_edition_model.py |
| Version（I2） | CANONICAL（Version REUSE）+ ASSERTION I2 | CA-012 `version.py::Version` | REUSE | `models/version.py` | edition_id/version_name/era/year/repository/shelf_mark/editor/is_formal_source/parent_version_id | test_version_model.py |
| Chapter | CANONICAL（Chapter REUSE） | CA-014 `chapter.py::Chapter` | REUSE | `models/chapter.py` | work_id/parent_id/title/order/description | test_chapter_model.py |
| Passage + Locator | CANONICAL（Passage REUSE）+ EVIDENCE §3 | CA-015 `passage.py::Passage` | REUSE | `models/passage.py` | chapter_id/version_id（fixed reference）/content_text/translation/notes/order/tags + locator 解析 | test_passage_model.py |
| Locator 复用 | CD-0 `core/locator.py` | — | REUSE | `core/locator.py` | 无代码变更；locator 解析测试使用 | test_passage_model.py |
| Author 关联 | CD-1 Entity | CA-003（person entity） | REUSE | work.author_entity_id FK | FK → entities.id | test_work_model.py |
| Repositories | DAG CD-2（实现层） | — | ADAPT | `repositories/*.py` | BaseRepository 派生 + 领域方法 | test_repositories_cd2.py |
| Migration 0003 | DAG CD-2（DB scope） | — | NEW | `alembic/versions/0003` | 五表 + FK/约束/索引；0002→0003 | test_migrations.py |

**Scope/Verdict 计数语义**：Frozen Scope Items = 9（矩阵行数）；资产裁决 = REUSE 5（Work/Edition/Version/Chapter/Passage — 沿用 Frozen Inventory，无 EXTEND/ADAPT/NEW 资产裁决）；NEW 实现单元 = 6（5 repositories + migration 0003，非资产裁决）。两组语义不同，详见实施报告。
