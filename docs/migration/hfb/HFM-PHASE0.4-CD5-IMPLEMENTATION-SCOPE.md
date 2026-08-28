# HFM Phase 0.4 — CD-5 Implementation Scope

Date: 2026-08-27 · Phase 0.4 — Core Domain Implementation CD-5
起始基线：`82505d11d7f0591de1df342f03b4e78c5c4300a7`（CD-4 Implementation Baseline）
Core Domain Contract Baseline：`366df69715613022326eb7a3c06ae7f145ebacb9`
HFB Source Snapshot：`03755b57ec0e4c8023d1447619f7d6ead9e44d73`
唯一准绳：`HFM-PHASE0.4-CORE-MIGRATION-DAG.md`（Frozen）CD-5 节点 + `HFM-EVIDENCE-LINEAGE-CONTRACT-v0.1.md`

## CD-5 Scope Extraction（摘自 Frozen DAG + Evidence Lineage Contract）

```text
CD-5 Identity:
CD-5

Purpose:
Citation（target = Assertion）— 可定位、可复现的引用关系

Included Domain Objects:
Citation（target_assertion / evidence 直接边 / pinned version / passage / quote_text / note）

Included Value Objects:
（无新增枚举；复用 CD-2 Locator 语义 — 不另建第二套 locator）

Included Relationships:
Citation.target_assertion_id → Assertion（CD-4，NOT NULL — 统一 target）
Citation.evidence_id → Evidence（CD-3，SET NULL — 直接证据边，Frozen Lineage §2.3）
Citation.version_id → Version（CD-2，SET NULL — pinned version，I2 可复现）
Citation.passage_id → Passage（CD-2，SET NULL — 文本定位）

Included Guards / Invariants:
I2 Version Reproducibility — DIRECTLY APPLICABLE（version pin 不随 latest 漂移）
I4 No Silent Overwrite — APPLICABLE（引用绑定字段 immutable）
I5 Stable Identity / I6 HFB Independence — APPLICABLE
撤回引用 — 新建 Citation 不得指向 editorial_status=withdrawn 的 Assertion

CD-0 Dependency: Source / DB 基座 / immutable_fields
CD-1 Dependency: —（回归）
CD-2 Dependency: Version / Passage（pinned references）
CD-3 Dependency: Evidence（直接边）
CD-4 Dependency: Assertion（统一 target）

Frozen HFB Assets:
CA-022（Citation — ADAPT：多态 target → 统一 Assertion target）
CA-027（Document rights — ADAPT 判定记录；非 CD-5 target，留权利层 G4/G13）

Frozen Inventory Verdicts:
ADAPT（CA-022 Citation）

Database Scope:
citations 单表（FK/CHECK/索引/迁移）

Migration Scope:
0006（down_revision = 0005；禁止修改 0001-0005）

Repository Scope:
CitationRepository（create 校验 target 非 withdrawn + FK 存在；get_by_target_assertion；immutable 守卫）

Service Scope: 0
API Scope: 0
Frontend Scope: Frontend Business Changes: 0
Data Import Scope: HFB DATA IMPORT: NOT PERFORMED

Applicable Invariants:
I2 — DIRECTLY APPLICABLE（pinned version 可复现；latest 不漂移）
I4 — APPLICABLE（target/evidence/version/passage/quote 绑定 immutable）
I5 / I6 — APPLICABLE
I1 / I3 — 已冻结系统状态（回归 PASS）

Test Gates:
版本固定（create citation vs V1 → create V2 → reload → 仍 V1）
撤回引用（withdrawn Assertion 拒绝被新引用）
I2 回归 + I1/I3 回归 + migration 0005→0006

Explicit Exclusions:
CA-027 Document rights（权利层，G4/G13）
Publication / Snapshot / Public Portal / Auth / Reviewer / Publisher / 前端 / Phase 1（G1-G4/G7）
第二套 locator（复用 CD-2 语义 — 通过 version/passage FK 表达）
API / Service / 数据导入

Downstream Nodes:
CD-6（Person/Event 关系，依赖 CD-1 + CD-4；非本批）
```

**CD-5 SCOPE: CONFIRMED**（无歧义，可唯一解析）。

## Traceability Matrix

| CD-5 Requirement | Frozen Contract/DAG | HFB Asset | Frozen Verdict | HFM Target | Implementation | Test |
| --- | --- | --- | --- | --- | --- | --- |
| Citation（统一 target=Assertion） | EVIDENCE §2.3（Citation → Assertion）+ DAG CD-5 | CA-022 `academic_evidence.py::Citation` | ADAPT | `models/citation.py` | target_assertion_id FK + quote_text/note | test_citation_model.py |
| Assertion target 参照完整性 | §13（Citation != Assertion）+ CD-4 | CA-022 | NEW | target_assertion_id FK RESTRICT NOT NULL | orphan 拒绝 | test_citation_model.py |
| Evidence 直接边 | EVIDENCE §2.3（保留 Citation→Evidence） | CA-021 Evidence | REUSE | evidence_id FK SET NULL | 直接边 + 完整性 | test_citation_evidence.py |
| Pinned Version（I2） | §19/§20（复用 CD-2 pinned Version，latest 不漂移） | CA-012 Version | NEW | version_id FK SET NULL（immutable pin） | 无 latest 漂移测试 | test_citation_reproducibility.py |
| Passage 定位 | §15（复用 CD-2 locator 语义） | CA-015 Passage | NEW | passage_id FK SET NULL | FK 校验 | test_citation_model.py |
| 撤回引用拒绝 | DAG CD-5（撤回引用）+ EVIDENCE §2.5 | CA-022 | NEW | create 校验 target editorial_status != withdrawn | withdrawn 拒绝 | test_citation_withdrawn.py |
| 引用绑定不可变（I4） | §26（protected fields） | CA-022 | NEW | target/evidence/version/passage/quote immutable | 直接 + repository 双层 | test_citation_model.py |
| CitationRepository | DAG CD-5（实现层） | — | ADAPT | `repositories/citation.py` | create/get_by_target_assertion/immutable 守卫 | test_repositories_cd5.py |
| Migration 0006 | DAG CD-5（DB scope） | — | NEW | `alembic/versions/0006` | citations 表 | test_migrations.py |

**Scope/Verdict 计数语义**：Frozen Scope Items = 9（矩阵行数）；资产裁决 = ADAPT 2（CA-022 Citation 模型 + CitationRepository）+ REUSE 1（CA-021 evidence 边 / quote-note 字段）+ NEW 6（target FK / version pin / passage pin / withdrawn 拒绝 / immutable 守卫 / 迁移 0006）；CA-027 判定记录不实施。两套计数分属不同体系。
