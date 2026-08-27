# HFM Canonical Domain Model v0.1

Status: Draft for Contract Review · Date: 2026-08-27 · Phase 0.4
依据：HFB `03755b5` 模型实测 + DOMAIN-MAP v1.1 + Assertion/Evidence 契约。

## 1. 逻辑关系图

```text
                        EntityType
                            │
Entity ◄───┐  (Person / Work / Place / Institution / Concept / Acupoint)
  │        │
  │        └── AcademicRelation/EntityRelation（ADAPT：Entity ↔ Entity）
  │
  ├──► Event（NEW — 基于 Assertion 聚合）
  │
Work ◄── Edition ◄── Manifestation ◄── (Artifact/OCRArtifact — 治理层)
  │
  ├── Book ──► ClassicalVersion ──► Version ◄── VersionRelation（lineage）
  │                                     │
  └── Chapter ◄── Passage ◄── Sentence ◄── Token / Variant
                    │
                    └──► TextUnit / Locator（EXTEND：work/edition/version/chapter/passage + 卷/篇/页/行）

Source ──► SourceRef ──► Evidence ◄──► Passage
                            │
                            ▼
                         Assertion ◄── Citation（→ Evidence）
```

## 2. 对象清单与 HFB 映射

| HFM 对象 | HFB 对象（03755b5） | Verdict |
| --- | --- | --- |
| Entity + EntityType | `AcademicEntity`/`AcademicEntityType` + `EntityRelation`（9 类） | ADAPT |
| Person | `models/person.py::Person`（单值字段） | ADAPT（值字段 → Assertion） |
| Event | 无（Chronology DOC_ONLY `0806`） | NEW |
| Place / Institution | `Institution`；Place 无独立模型（DOC_ONLY `0807`） | ADAPT/NEW |
| Concept / Acupoint | `TCMEntity` | EXTEND（仅历史文本主张，G1 边界） |
| Work / Edition / Manifestation | `models/bibliographic.py`（FRBR 五层 + NormalizedText + FragmentProvenance） | REUSE/EXTEND |
| Book / ClassicalVersion | `models/book.py` + `models/classical_version.py` | REUSE/EXTEND |
| Version + VersionRelation | `models/version.py`（is_formal_source/withdrawn_at）+ `models/version_relation.py` | REUSE |
| Chapter | `models/chapter.py`（自引用） | REUSE |
| Passage / Sentence / Token / Variant | `models/passage.py` + `models/version_criticism.py` | REUSE/EXTEND（locator） |
| TextUnit / Locator | `SourceRef.page_location`（字符串） | NEW/EXTEND |
| Source（身份） | `SourceAdmissionEntry` identity 部分 | 边界保留 |
| SourceRef | `models/academic_evidence.py::SourceRef` | REUSE/EXTEND |
| Evidence | `models/academic_evidence.py::Evidence` | REUSE |
| Assertion | 无统一模型（Variant/AcademicRelation/CandidateExtraction/GenerationProof） | NEW |
| Citation | `models/academic_evidence.py::Citation` | ADAPT |
| Legacy Provenance | `models/legacy_provenance.py` | REUSE（数据迁移治理） |

## 3. 六个不变量

- **I1 Provenance**：所有 Assertion 可追踪 Source/Evidence（Assertion.evidence[] + Evidence.source_ref_id）。
- **I2 Version Reproducibility**：Citation 固定可复现版本（Citation 记录目标 Content/Source Version；引用拒绝已 withdrawn 版本 — HFB 逻辑 REUSE）。
- **I3 Assertion Coexistence**：冲突主张并存（subject+predicate 无唯一约束）。
- **I4 No Silent Overwrite**：更新 = 新 Assertion/撤回，禁止覆盖唯一字段（迁移 Person 单值字段时必须转写）。
- **I5 Stable Identity**：核心对象稳定 ID（见 §4）。
- **I6 HFB Independence**：迁移后 HFM runtime 不依赖 HFB。

## 4. Stable Identifier Contract

| Object | Stable ID Required | Existing HFB ID | Reusable | HFM Strategy |
| --- | --- | --- | --- | --- |
| Entity | YES | AcademicEntity.id（UUIDv7） | YES | UUIDv7 迁移保留 |
| Person | YES | Person.id | YES | UUIDv7 迁移保留 |
| Event | YES | 无 | — | NEW UUIDv7（内容哈希派生可选） |
| Work | YES | Work.id | YES | UUIDv7 |
| Edition | YES | Edition.id | YES | UUIDv7 |
| Version | YES | Version.id | YES | UUIDv7（含 is_formal_source） |
| Passage | YES | Passage.id + trace_id(UUIDv5) | YES | UUIDv7 + 溯源哈希保留 |
| Source | YES | SourceAdmissionEntry identity | PARTIAL | 迁移 identity；准入记录留治理 |
| SourceRef | YES | SourceRef.id | YES | UUIDv7 |
| Evidence | YES | Evidence.id | YES | UUIDv7 |
| Assertion | YES | 无 | — | NEW UUIDv7 + content hash |
| Citation | YES | Citation.id | YES | UUIDv7 |

注：不设计公众 URL；Public canonical URI 后续单独治理。

## 5. 技术边界（FUTURE OPTION，不入 entry gate）

Graph DB / Neo4j / Event Sourcing / CQRS physical split / Elasticsearch / Redis / Kafka / Microservices。
