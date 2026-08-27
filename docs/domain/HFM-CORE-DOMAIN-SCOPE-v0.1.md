# HFM Core Domain Scope v0.1

Status: Draft for Contract Review · Date: 2026-08-27 · Phase 0.4 — Core Domain Contract Audit
起始基线：`f495fa07b73f5f1d75b1398f196beadf6618a6bb`（Phase 0.3 Completion Baseline）
HFB Source Snapshot：`03755b57ec0e4c8023d1447619f7d6ead9e44d73`（只读）

## 目的

界定 HFM Core Domain 的审计范围，作为 Canonical Model / Assertion / Evidence Lineage 契约与迁移 DAG 的依据。Core Domain 同时服务：公众文化传播、高校科研、教学辅助、非遗成果展示、政府成果展示、专业研究。

底层目标模型（不可因复用 HFB 而破坏）：

```text
Entity
→ Assertion
→ Evidence
→ Source
→ Citation
→ Version

Research Layer → editorial decision → Publication Layer → snapshot/projection → Public Portal
```

## 6.1 Person / Biography

- 历史人物（皇甫谧、亲属、师承、关联人物、古今学者）。
- 生平事件、时间（含 uncertain date）、地点、关系。
- HFB 现状：`Person` 为单值字段模型（birth_year/death_year/birth_place/dynasty/biography/notable_works/expertise）；`biography_source` 为单文本；无 Event 模型；`research_relation_role` 枚举串。**单值字段 = 单一真相风险**，多来源分歧无法并存（见 Assertion 契约）。
- 产出：Person 核心模型 **ADAPT**；Biography/Event **NEW**（基于 Assertion）。

## 6.2 Work / Ancient Text

- Work / Book / Edition / Version / Volume / Chapter / Passage / 文本定位 / 图像-页定位。
- HFB 现状：FRBR-like 五层（Work → Edition → Manifestation → Artifact → OCRArtifact → NormalizedText + FragmentProvenance）；Book / ClassicalVersion / Version（is_formal_source / withdrawn_at）/ Chapter（自引用）/ Passage（chapter_id + 可选 version_id + order）/ Sentence / Token / Variant / Commentary / TEI。
- 缺口：结构化 locator（卷/篇/页/行/栏）现为 `SourceRef.page_location` 字符串；Passage 跨版本对齐无显式机制；scan/image 与 text 关联未入 Core（Artifact 属 candidate 沙箱）。
- 产出：FRBR 层 **REUSE/EXTEND**；结构化 locator **EXTEND**（TextUnit / Locator）。

## 6.3 Entity

- Person / Work / Place / Institution / Concept / Acupoint / Heritage-related entity（仅登记，不建 G4 治理）。
- HFB 现状：`AcademicEntity`/`AcademicRelation`/`RelationConfidence`/`AcademicEntityType`；`EntityRelation`（9 类 graph types）；`Institution`；`TCMEntity`。
- 产出：Entity 层 **ADAPT**（泛化 AcademicEntity → Entity + EntityType）；Acupoint 仅历史文本主张（G1 边界）。

## 6.4 Assertion（最高优先级契约）

```text
Entity → multiple Assertions（不同来源 / 版本 / 研究观点可并存，含 conflicting assertion）
```

- HFB 无统一 Assertion：主张分散于 `Variant` / `AcademicRelation` / `CandidateExtraction` / `GenerationProof`（DOMAIN-MAP §1.7 PARTIAL）。
- 禁止退化为 `Entity.field = single truth`。
- 详见 `HFM-ASSERTION-CONTRACT-v0.1.md`。

## 6.5 Source / SourceRef

- Source（来源准入）、provenance、edition/version、locator、rights metadata、immutable source identity。
- HFB 现状：`SourceAdmissionEntry`（三级准入状态机 + append-only 审计）为治理语义；`SourceRef`（title/author/edition_info/page_location/url）为物理出处。
- 边界：Core Domain 使用 SourceRef（来源身份 + locator + rights metadata）；准入/晋升状态机属治理层（B 系列已审计，保留边界）。Source 与 Evidence 边界：Source = 外部出版物/实物身份；Evidence = 论据（挂 SourceRef 与/或系统内 Passage）。

## 6.6 Evidence

```text
Evidence → SourceRef → Artifact / text / image locator
```

- HFB 现状：`Evidence`（description + evidence_level Level 1-4 + source_ref_id + source_passage_id + creator_id + taint_status）。
- Evidence 已有 →SourceRef 与 →Passage 双链（REUSE 基础）；不得与 Publication Admission 再次耦合（准入属治理）。

## 6.7 Citation

- Citation 指向什么：HFB 现为多态 target（Variant/AcademicRelation/Passage）→ evidence_id；HFM 契约：Citation → Assertion（+ Evidence）。
- 固定版本、locator、withdrawn reference（HFB `citation_persistence` 已有撤回引用拒绝 — REUSE）、stable reference identity。

## 6.8 Version

区分：Content Version / Source Version / Edition Version / Entity Revision / Assertion Revision / Publication Version。Core Domain 仅定义前四者中必要部分；Publication Version 属 G3。

## 7. 暂时排除的 Phase 1 领域

- G1 Medical Compliance implementation（允许 Core 保留字段/接口需求）
- G2 Anonymous/Public Access implementation
- G3 Publication Snapshot implementation
- G4 ICH Media Governance implementation
- G7 Separation of Duties implementation

## 8. 明确保留的技术边界（禁止膨胀）

Graph DB / Neo4j / Event Sourcing / CQRS physical split / Elasticsearch / Redis / Kafka / Microservices = **FUTURE OPTION**，不入 Core Domain entry gate。
