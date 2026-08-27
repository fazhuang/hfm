# HFM Phase 0.4 — Core Asset Inventory（HFB → HFM Core Domain）

Date: 2026-08-27 · Phase 0.4 — Core Domain Contract Audit（READ-ONLY）
HFB Source Snapshot：`03755b57ec0e4c8023d1447619f7d6ead9e44d73`
起始基线：`f495fa07b73f5f1d75b1398f196beadf6618a6bb`

> 逐项按「Model → Migration → Repository/Service → API → Test → Runtime」调用链取证（DOMAIN-MAP v1.1 + 本轮实测）；禁止按类名机械判定。

| ID | HFM Concept | HFB Object | HFB Path | DB Table | Service | API | Tests | Runtime Status | Coupling | Candidate Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CA-001 | Entity + EntityType | AcademicEntity / AcademicEntityType / AcademicRelation | `models/academic_relation.py` | academic_entities / relations | academic_service | v1/relations.py | test_academic_relations.py | TESTED | MEDIUM | ADAPT |
| CA-002 | EntityRelation（graph） | EntityRelation（9 类） | `models/graph.py` | entity_relations | graph_service | v1/graph + v4/visualization | test_graph_service.py | ENFORCED+TESTED | LOW | REUSE |
| CA-003 | Person | Person（单值字段 + domain_status/anchor_path） | `models/person.py` | persons | person_service | v1/entities.py /persons | test_person_domain.py | TESTED | MEDIUM | ADAPT |
| CA-004 | Event | 无（Chronology DOC_ONLY `0806`） | — | — | — | — | — | DOC_ONLY | HIGH（设计） | NEW |
| CA-005 | Institution | Institution | `models/institution.py` | institutions | — | — | test_day1_foundation.py | TESTED | LOW | REUSE |
| CA-006 | Concept / Acupoint | TCMEntity | `models/tcm_entity.py` | tcm_entities | — | — | — | TESTED | MEDIUM | EXTEND |
| CA-007 | Work | Work（FRBR） | `models/bibliographic.py` | works | — | — | test_advanced_bibliographic_model.py | TESTED | LOW | REUSE |
| CA-008 | Edition / Manifestation | Edition / Manifestation | `models/bibliographic.py` | editions / manifestations | — | — | 同上 | TESTED | LOW | REUSE |
| CA-009 | NormalizedText / 辑佚 | NormalizedText / OCRArtifact / FragmentProvenance | `models/bibliographic.py` | normalized_texts / ocr_artifacts / fragment_provenance | — | — | TESTED | MEDIUM | EXTEND |
| CA-010 | Book | Book | `models/book.py` | books | — | v1/entities.py /books | test_entity_models.py | TESTED | LOW | REUSE |
| CA-011 | ClassicalVersion | ClassicalVersion（edition_type/public_domain_status/review_status） | `models/classical_version.py` | classical_versions | — | v1/classical_versions.py | test_classical_versions_rbac.py | TESTED | MEDIUM | EXTEND |
| CA-012 | Version | Version（is_formal_source/withdrawn_at） | `models/version.py` | versions | version_center | v1/version_center.py | test_version_tree.py | TESTED+ENFORCED | LOW | REUSE |
| CA-013 | VersionRelation | VersionRelation | `models/version_relation.py` | version_relations | version_center | — | test_version_tree.py | TESTED | LOW | REUSE |
| CA-014 | Chapter | Chapter（自引用） | `models/chapter.py` | chapters | — | — | — | TESTED | LOW | REUSE |
| CA-015 | Passage | Passage（chapter_id + version_id + order + trace_id UUIDv5） | `models/passage.py` | passages | trace_lineage | v1/passages.py | Playwright V4-SR01/03 | TESTED+RUNTIME | LOW | REUSE |
| CA-016 | Sentence / Token / Variant | version_criticism 模型 | `models/version_criticism.py` | sentences / tokens / variants | version_center | — | test_version_tree.py | TESTED | MEDIUM | ADAPT |
| CA-017 | Commentary | Commentary | `models/commentary.py` | commentaries | version_center | — | — | TESTED | MEDIUM | REUSE |
| CA-018 | TEI 持久化 | TextSentence / TextToken / TextualVariant | `models/tei.py` | tei_* | — | v2/tei | — | TESTED | MEDIUM | REUSE |
| CA-019 | Source（身份 + rights 元数据） | SourceAdmissionEntry（三级准入状态机） | `models/source_admission.py` | source_admission_entries | source_admission | v1/source_admissions.py | test_source_admission_rbac.py | ENFORCED+TESTED | HIGH | ADAPT（身份/rights 入 Core；状态机留治理） |
| CA-020 | SourceRef | SourceRef（page_location 字符串） | `models/academic_evidence.py` | source_refs | — | — | — | TESTED | LOW | REUSE |
| CA-021 | Evidence | Evidence（Level 1-4 + source_ref_id + source_passage_id + taint） | `models/academic_evidence.py` | evidences | candidate_publish_uow | v1/evidences.py | test_phase_a0_candidate_pipeline.py | TESTED | LOW | REUSE |
| CA-022 | Citation | Citation（多态 target → evidence_id） | `models/academic_evidence.py` | citations | citation_persistence | — | test_citation_persistence.py | TESTED | MEDIUM | ADAPT（target → Assertion） |
| CA-023 | Assertion | 无统一模型（Variant/AcademicRelation/CandidateExtraction/GenerationProof） | — | — | — | — | PARTIAL | HIGH（设计） | NEW |
| CA-024 | 学术污损 | AcademicTaintAuditLog | `models/academic_taint.py` | academic_taint_audit_logs | academic_taint_service | — | test_academic_taint_lifecycle.py | ENFORCED+TESTED | LOW | REUSE |
| CA-025 | Legacy Provenance | LegacyProvenanceDecision / EvidencePackage | `models/legacy_provenance.py` | legacy_* | production_query_policy | — | test_production_query_policy.py | ENFORCED+TESTED | MEDIUM | REUSE（数据迁移治理） |
| CA-026 | CandidateExtraction → Assertion 桥 | CandidateExtraction / CandidateStatus（5 态） | `models/candidate_extraction.py` | candidate_extractions | candidate_extraction_service | v1/extractions.py | — | ENFORCED+TESTED | HIGH | ADAPT（审核通过 → Assertion；治理链保留） |
| CA-027 | Document rights 元数据 | Document（copyright_status/license_type/authorization_basis） | `models/document.py` | documents | — | v1/entities.py | test_fulltext_compliance.py | ENFORCED+TESTED | MEDIUM | ADAPT（rights 元数据入 Core；全文摄入留治理） |
| CA-028 | GenerationProof（replay） | GenerationProof（retrieval_snapshot） | `services/generation_proof.py` | — | generation_proof | — | test_day4_generation.py | TESTED | MEDIUM | REUSE（研究回放；非 Publication Snapshot） |

## 统计

```text
HFB Core Assets Audited:
28（CA-001 … CA-028）

REUSE:
16

EXTEND:
3

ADAPT:
7

NEW:
2

DEPRECATE:
0

UNKNOWN:
0
```

注：REUSE/EXTEND 中的 locator 结构化扩展（卷/篇/页/行）以独立 `TextUnit/Locator` 对象纳入 CD-2（EXTEND 性质），不改变上述单裁决计数。
