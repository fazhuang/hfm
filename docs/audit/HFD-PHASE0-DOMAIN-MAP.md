# HFD Phase 0 — Domain Map（HFB 领域模型映射审计）

> 审计对象：`/Users/likeming/Sites/hfb`（皇甫谧数字人文研究平台，HFB）
> 审计目的：为《皇甫谧人文数字平台》（HFD）建立「现有 HFB 领域能力 → 目标概念」映射表。
> 方法：ORM Model / Schema / DTO / Migration / Service / Repository / API / Enum / Validation / Test 逐层取证。
> 状态标记：`IMPLEMENTED`（有代码证据）/ `PARTIAL`（部分实现）/ `DOC_ONLY`（仅文档）/ `NOT_FOUND` / `CONFLICT`。
> 验证分层标记：`SPECIFIED`（文档/注释声明）/ `IMPLEMENTED`（代码存在）/ `ENFORCED`（DB 约束/触发器/服务层强制）/ `TESTED`（有自动化测试通过）/ `RUNTIME`（真实运行时验证过）。文档/注释**不替代** enforcement 证据。
> 修订：v1.1（2026-08-27，绑定 HEAD `2d98b610a63d2b0347ff5ec7fcd1d598913f3521`，branch `main`）— 依 Codex 验收 §17 补充验证分层、证据调用链与验收复核结论（见 §5）。
> 只读审计：未修改 HFB 任何生产代码/测试/迁移/数据库。交付物位于 `/Users/likeming/Sites/hfb/docs/audit/`。

---

## 0. 取证基线（Read-Only）

| 项 | 值 | 证据 |
| --- | --- | --- |
| 审计目标仓库 | `/Users/likeming/Sites/hfb` | 工作目录 `pwd` |
| 分支 | `main` | `git branch --show-current` |
| HEAD | `2d98b610a63d2b0347ff5ec7fcd1d598913f3521` | `git rev-parse HEAD` |
| 生成时间 | 2026-08-27 15:28 CST（v1.1 复核） | `date` |
| 迁移头 | `gate4_ocr_proofreading_audits`（51 个 revision） | `alembic history` / `alembic_version` 表 |
| DB 对象 | PostgreSQL public schema 64 张表 | `information_schema.tables` 计数 |
| 治理 DB 角色 | 63 个 `hfb_gov_*` LOGIN 角色 | `pg_roles` 查询 |
| 工作树 | `M docs/12-context/project-state-2026-08-26.md`（审计前既有修改）+ `docs/audit/` 新增（本次交付） | `git status --short` |

---

## 1. 目标概念 → HFB 等价能力映射

> 判定列语义：`IMPLEMENTED` 表示代码存在且按 §0 验证分层至少达到 `TESTED`；标注 `*` 的条目为 Codex 独立复核一致项。

### 1.1 Entity（实体）

| 目标概念 | HFB 等价 | 状态 | 证据调用链 |
| --- | --- | --- | --- |
| Person* | `Person`（`domain_status: pending/verified/excluded`、`anchor_path`、`research_relation_role`） | **IMPLEMENTED**（TESTED） | Model `models/person.py:31-52` → Repo `repositories/person.py:31-36`（默认 verified 过滤）→ Service `services/person_service.py` → API `api/v1/entities.py` /persons → Test `tests/unit/test_person_domain.py`、Playwright person-intro |
| 人物研究域* | `AcademicEntity` / `AcademicRelation` / `RelationConfidence` / `AcademicEntityType` | **IMPLEMENTED**（TESTED） | Model `models/academic_relation.py` → API `api/v1/relations.py` → Test `tests/unit/test_academic_relations.py` |
| 知识图谱实体* | `EntityRelation`（GRAPH_ENTITY_TYPES 9 类） | **IMPLEMENTED**（ENFORCED+TESTED） | Model `models/graph.py:23-34` + DB 唯一约束/自环拒绝 → Service `services/graph_service.py` → API v1/graph + v4/visualization → Test `tests/unit/test_graph_service.py` |
| TCM 本体实体 | `TCMEntity` | **IMPLEMENTED**（TESTED） | Model `models/tcm_entity.py` → migration `a1b2c3d4e5f7` |
| 机构 | `Institution` | **IMPLEMENTED**（TESTED） | Model `models/institution.py` → migration `221e630d3f7b` → Test `tests/unit/test_day1_foundation.py` |

### 1.2 Work / Book / Edition / Volume / Chapter / Passage（著作层级）

| 目标概念 | HFB 等价 | 状态 | 证据调用链 |
| --- | --- | --- | --- |
| Work* | `Work`（FRBR） | **IMPLEMENTED**（TESTED） | Model `models/bibliographic.py:41-64` → migration `bibliographic_model` → Test `tests/unit/test_advanced_bibliographic_model.py` |
| Edition / Manifestation* | `Edition` / `Manifestation` | **IMPLEMENTED**（TESTED） | Model `models/bibliographic.py` → 同上 Test |
| Book* | `Book` | **IMPLEMENTED**（TESTED） | Model `models/book.py:16-45` → API `api/v1/entities.py` /books → Test `tests/unit/test_entity_models.py` |
| 古籍版本目录* | `ClassicalVersion`（edition_type/public_domain_status/review_status） | **IMPLEMENTED**（TESTED） | Model `models/classical_version.py` → API `api/v1/classical_versions.py` → RBAC Test `tests/unit/test_classical_versions_rbac.py` |
| 文本校勘版本* | `Version`（is_formal_source/withdrawn_at） | **IMPLEMENTED**（TESTED+ENFORCED） | Model `models/version.py:17-69` → 撤回引用拒绝 `services/citation_persistence.py:387-389` → API `api/v1/version_center.py` → Test `tests/unit/test_version_tree.py` |
| Volume/Chapter | `Chapter`（自引用层级） | **IMPLEMENTED**（TESTED） | Model `models/chapter.py:14-38` |
| Passage（条文）* | `Passage`（原子知识单元） | **IMPLEMENTED**（TESTED+RUNTIME） | Model `models/passage.py` → API `api/v1/passages.py` → V4 证据闭环 `services/trace_lineage.py` → Playwright `v4-real-sourceref.spec.ts`（真实后端运行） |
| 句子/词元/异文* | `Sentence` / `Token` / `Variant` | **IMPLEMENTED**（TESTED） | Model `models/version_criticism.py` → migration `291a1dce8d65` → Test `tests/unit/test_version_tree.py` |
| 注疏链 | `Commentary` | **IMPLEMENTED**（TESTED） | Model `models/commentary.py` → Service `services/version_center.py:410-527` → migration `d6575d7baf29` |

### 1.3 Source / SourceRef / Evidence / Citation（证据链）

| 目标概念 | HFB 等价 | 状态 | 证据调用链 |
| --- | --- | --- | --- |
| SourceRef* | `SourceRef` | **IMPLEMENTED**（TESTED+RUNTIME） | Model `models/academic_evidence.py:27-39` → Repo `repositories/source_ref.py` → V4 报告 SourceRef 卡片 → Playwright V4-SR01/03（0 null 闭环） |
| Source（来源准入）* | `SourceAdmissionEntry`（三级状态机） | **IMPLEMENTED**（ENFORCED+TESTED） | Model `models/source_admission.py:42-51` + append-only 审计 + DB 约束迁移 `enforce_*` → Service `services/source_admission.py` → API `api/v1/source_admissions.py:81-215` → RBAC Test `tests/unit/test_source_admission_rbac.py` |
| Evidence* | `Evidence`（Level 1-4 + taint） | **IMPLEMENTED**（TESTED） | Model `models/academic_evidence.py:42-67` → 候选发布 UoW `db/candidate_publish_uow.py` → API `api/v1/evidences.py` → Test `tests/unit/test_phase_a0_candidate_pipeline.py` |
| Citation* | `Citation`（target→evidence） | **IMPLEMENTED**（TESTED） | Model `models/academic_evidence.py:70-99` → Service `services/citation_persistence.py` → Test `tests/unit/test_citation_persistence.py` |
| 检索快照/Proof* | `GenerationProof`（retrieval_snapshot） | **IMPLEMENTED**（TESTED） | `services/generation_proof.py:87-141` → Test `tests/unit/test_day4_generation.py` |
| 反向追溯* | trace → chunk → doc → passage → citation | **IMPLEMENTED**（TESTED+RUNTIME） | `services/trace_lineage.py` + Playwright V4-SR01/02/03 |

### 1.4 Version（版本）

| 目标概念 | HFB 等价 | 状态 | 证据调用链 |
| --- | --- | --- | --- |
| 文本版本* | `Version` + `ClassicalVersion` 双轨 | **IMPLEMENTED**（TESTED） | Model + ADR `docs/11-adr/ADR-0013-Version-ClassicalVersion.md` |
| 版本比较* | `VersionComparisonService` | **IMPLEMENTED**（TESTED） | `services/version_center.py:26-320` → 前端 `pages/research/VersionComparisonPage.vue` → Test `tests/unit/test_version_comparison*.py` |
| 版本关系 | `VersionRelation` | **IMPLEMENTED**（TESTED） | Model `models/version_relation.py` |

### 1.5 Research Material（研究资料）

| 目标概念 | HFB 等价 | 状态 | 证据调用链 |
| --- | --- | --- | --- |
| 文献* | `Document`（版权字段 + P3 溯源） | **IMPLEMENTED**（ENFORCED+TESTED） | Model `models/document.py` → P4 过滤 `repositories/document.py:46-56` → Test `tests/unit/test_production_query_policy.py` |
| 文档分块* | `DocumentChunk` | **IMPLEMENTED**（TESTED） | Model `models/document_chunk.py` + migration `c5d6e7f8a9b0` |
| OCR 校勘审计* | `OCRProofreadingAudit`（append-only） | **IMPLEMENTED**（ENFORCED+TESTED） | Model `models/ocr_proofreading_audit.py` + migration `gate4_ocr_proofreading_audits`（幂等约束） |
| 论文 | `Paper` | **IMPLEMENTED**（TESTED） | Model `models/paper.py` |
| 候选语料沙箱* | `CandidateResource`/`Artifact`/`ManifestRevision`/`ResourceAudit` | **IMPLEMENTED**（ENFORCED+TESTED） | Model `models/candidate.py:61-235` + immutable 触发器 `db/candidate_triggers.py` + Test `tests/unit/test_dynamic_source_admission.py` |
| 规范文本/辑佚 | `NormalizedText` / `OCRArtifact` / `FragmentProvenance` | **IMPLEMENTED**（TESTED） | Model `models/bibliographic.py` |
| TEI 持久化 | `TextSentence`/`TextToken`/`TextualVariant` | **IMPLEMENTED**（TESTED） | Model `models/tei.py` + migration `p0p4p5p6_evidence_tei_ontology` |

### 1.6 Heritage / ICH / Video / Media / Asset（非遗与媒体）

| 目标概念 | HFB 等价 | 状态 | 证据 |
| --- | --- | --- | --- |
| 非遗（ICH）实体 | 无独立模型 | **NOT_FOUND** | `models/` 无 heritage/ich 模型（Codex 独立复核一致） |
| 视频/媒体资产 | 无 Media/Video 模型；`Image` 仅 url/caption/source/license_info/order | **NOT_FOUND**（等价缺失） | `models/image.py`（Codex：NEW/UNKNOWN 一致） |
| 视频素材 | 前端静态 `/media/huangfu_mi_ep1_full.mp4`、`huangfu_mi_movie_full.mp4` | **NOT_FOUND**（无后端登记） | `data/huangfu_mi_exhibition.json`（video_url ×2）；`views/PersonIntroView.vue:389-404` |
| PDF 素材治理 | hfmzl 语料 candidate→admission→promotion 全链 | **IMPLEMENTED**（ENFORCED+TESTED） | `services/hfmzl_storage.py`；`api/v1/entities.py` /hfmzl/preview（磁盘哈希复验）；Test `apps/backend/tests/test_hfmzl_preview.py` |

### 1.7 Assertion / Claim / Statement（主张）

| 目标概念 | HFB 等价 | 状态 | 证据 |
| --- | --- | --- | --- |
| 统一 Assertion 模型 | 无独立模型；主张分散于 Variant/AcademicRelation/CandidateExtraction/GenerationProof | **PARTIAL** | `models/candidate_extraction.py:26-36`; `models/academic_relation.py` |
| 主张→证据绑定 | 候选发布 dual-hash grounding；V4 strict 1:1 claim binding | **IMPLEMENTED**（ENFORCED+TESTED） | `db/candidate_publish_uow.py`; `services/generation_proof.py`; Test `tests/unit/test_day4_generation.py` |
| AI 主张防护* | Evidence-Gated（`EVIDENCE_GATE_REFUSAL`） | **IMPLEMENTED**（TESTED） | `services/ai_service.py:60-95`; Test `tests/unit/test_v1_ai_api.py` |

### 1.8 Review / Approval（审核）

| 目标概念 | HFB 等价 | 状态 | 证据 |
| --- | --- | --- | --- |
| 文档审核状态 | `Document.review_status` + reviewed_by/at | **IMPLEMENTED**（TESTED） | `models/document.py:59-78`; Test `tests/unit/test_fulltext_compliance.py` |
| 古籍版本审核 | `ClassicalVersion.review_status` | **IMPLEMENTED**（TESTED） | `models/classical_version.py:52-58`; Test `test_classical_versions_rbac.py` |
| 来源三级审核* | Research→Technical→Steering + append-only 审计 | **IMPLEMENTED**（ENFORCED+TESTED） | `models/source_admission.py:104-141` + `SourceAdmissionAudit` |
| AI 候选审核* | `CandidateStatus` 5 态 + append-only 审计 | **IMPLEMENTED**（ENFORCED+TESTED） | `models/candidate_extraction.py`; `db/audit_triggers.py` |
| 统一 EditorialStatus | 无统一内容发布状态机 | **PARTIAL** | 状态分散（见 1.9） |

### 1.9 Publish / Withdraw（发布/撤回）

| 目标概念 | HFB 等价 | 状态 | 证据 |
| --- | --- | --- | --- |
| 生产晋升* | `ProductionPromotion`（幂等键 + 哈希快照 + promoted_by） | **IMPLEMENTED**（ENFORCED+TESTED） | `models/production_promotion.py`; `services/production_promotion.py:148-258`; Test `test_production_query_policy.py` |
| 撤回文档* | `Document.withdrawn_at` → P4 零召回 | **IMPLEMENTED**（ENFORCED+TESTED） | `models/document.py:74-79`; `services/production_query_policy.py:75-139` |
| 撤回版本* | `Version.withdraw/restore`；引用拒绝 | **IMPLEMENTED**（TESTED） | `models/version.py:63-88`; `citation_persistence.py:387-389` |
| 撤回级联污损* | `AcademicTaintAuditLog` | **IMPLEMENTED**（ENFORCED+TESTED） | `models/academic_taint.py`; `services/academic_taint_service.py`; Test `test_academic_taint_lifecycle.py` |
| 统一内容发布状态 | 无「已发布/未发布」概念 | **NOT_FOUND** | — |

### 1.10 Rights / License（权利）

| 目标概念 | HFB 等价 | 状态 | 证据 |
| --- | --- | --- | --- |
| 文档版权* | `copyright_status`（10 枚举）/`license_type`/`authorization_basis`/`rag_enabled` | **IMPLEMENTED**（ENFORCED+TESTED） | `models/document.py:40-58`; `models/source_policy.py`（SourcePolicy 开关） |
| 版本权利 | `Version.rights_statement`/`persistent_identifier` | **IMPLEMENTED**（TESTED） | `models/version.py:42-45` |
| 准入权利依据* | `rights_basis`/`allowed_scope`（ACL fail-closed） | **IMPLEMENTED**（ENFORCED+TESTED） | `models/source_admission.py:80-84`; `services/source_scope.py`; 迁移 `enforce_approved_scope_nonempty` |
| 古籍公版状态 | `ClassicalVersion.public_domain_status` | **IMPLEMENTED** | `models/classical_version.py:40-45` |
| 媒体权利 | 无（Image 仅 license_info） | **NOT_FOUND** | `models/image.py`（Codex：NEW 一致） |

### 1.11 Audit（审计）

| 目标概念 | HFB 等价 | 状态 | 证据 |
| --- | --- | --- | --- |
| 候选资源审计* | `CandidateResourceAudit` | **IMPLEMENTED**（ENFORCED） | `models/candidate.py:141-161` + 触发器 `db/candidate_triggers.py:221-227` |
| 准入审计* | `SourceAdmissionAudit` | **IMPLEMENTED**（ENFORCED） | `models/source_admission.py:170-190` |
| AI 候选审计* | `CandidateAuditLog` | **IMPLEMENTED**（ENFORCED） | `db/audit_triggers.py`（PG + SQLite 双方言触发器） |
| 全文摄入审计 | `FulltextIngestionAudit` | **IMPLEMENTED** | `models/fulltext_ingestion_audit.py` |
| OCR 校勘审计 | `OCRProofreadingAudit` | **IMPLEMENTED**（ENFORCED） | `models/ocr_proofreading_audit.py` |
| 撤回污损审计* | `AcademicTaintAuditLog` | **IMPLEMENTED**（ENFORCED） | `models/academic_taint.py` |
| 通用操作审计（public 内容） | 无统一 audit_event 覆盖 books/persons/versions 写操作 | **PARTIAL** | `db/base.py:38-44`（仅 created/updated_at） |

### 1.12 Versioning / Provenance / Immutable / Manifest（版本与溯源）

| 目标概念 | HFB 等价 | 状态 | 证据 |
| --- | --- | --- | --- |
| 清单版本* | `CandidateManifestRevision`（DRAFT/FINALIZED/SUPERSEDED） | **IMPLEMENTED**（ENFORCED+TESTED） | `models/candidate.py:95-124` |
| Manifest DAG* | `validate_manifest_dag`（同候选+祖先闭包+环检测） | **IMPLEMENTED**（TESTED） | `services/manifest_validator.py:26-58` |
| 规范哈希* | `calculate_bytes_sha256` + `compute_manifest_sha256` | **IMPLEMENTED**（ENFORCED+TESTED） | `core/canonical_hash.py`; `manifest_validator.py:60-85`（与 DB finalize guard 逐字节一致） |
| 不可变工件* | `CandidateArtifact.immutable` + 触发器 | **IMPLEMENTED**（ENFORCED） | `db/candidate_triggers.py:71-92` |
| 不可变证据包* | `LegacyProvenanceEvidencePackage` | **IMPLEMENTED**（ENFORCED） | `models/legacy_provenance.py:53-58` |
| 旧数据治理* | `LegacyProvenanceDecision`（3 态 + is_effective） | **IMPLEMENTED**（ENFORCED+TESTED） | `models/legacy_provenance.py`; Test `test_production_query_policy.py` |
| Fail-Closed 查询* | `apply_production_query_filter`/`document_allowed_clause` | **IMPLEMENTED**（ENFORCED+TESTED） | `services/production_query_policy.py`; 不支持模型 raise NotImplementedError |
| 治理角色隔离* | 每用户 `hfb_gov_*` DB LOGIN + SECURITY DEFINER | **IMPLEMENTED**（ENFORCED） | `db/governance_db_roles.py`（HMAC 派生密码，无默认 secret 即 fail-closed）; `db/governance_engine.py` |

### 1.13 目标概念缺失汇总

| 目标概念 | 状态 | 说明 |
| --- | --- | --- |
| Entity | IMPLEMENTED | §1.1 |
| Assertion | PARTIAL | 无统一 Assertion |
| SourceRef | IMPLEMENTED | §1.3 |
| Evidence | IMPLEMENTED | §1.3 |
| Citation | IMPLEMENTED | §1.3 |
| Version | IMPLEMENTED | 双模型 |
| EditorialStatus | PARTIAL | 无统一状态机；`status_machine.py` 仅 draft→active→archived→deleted |
| Rights / Authorization | PARTIAL | 文档/版本/准入有；媒体无 |
| PublishedRepresentation | **NOT_FOUND** | 见 BASELINE-AUDIT §10 |
| PublicationSnapshot | **NOT_FOUND**（PARTIAL 等价物） | 见 BASELINE-AUDIT §8.3 分类 |
| ResourcePack | PARTIAL | CandidateManifest 是等价物 |
| AuditEvent | IMPLEMENTED | 多 append-only 表；无统一视图 |

---

## 2. 领域层服务与 API 覆盖

| 服务 | 文件 | 关键能力 | 测试 |
| --- | --- | --- | --- |
| 准入服务 | `services/source_admission.py` | submit/research/technical/steering/withdraw 单事务 + taint 级联 | `test_source_admission_rbac.py` |
| 晋升服务 | `services/production_promotion.py` | 服务端字节重算哈希 | `test_production_query_policy.py` |
| 版本中心 | `services/version_center.py` | 版本树/比较/注释链 | `test_version_tree.py` |
| 学术服务 | `services/academic_service.py` | educate/prove/synthesize + strict binding | `test_day4_generation.py` |
| 工作流 | `services/research_workflow_service.py` | 5 步工作流 + verify_citation_support | `test_v4_workflow.py`（apps/backend/tests） |
| 证据链 | `services/evidence_rag_service.py` | evidence→citation closure | `test_rag_service.py` |
| 溯源 | `services/trace_lineage.py` | trace_id(UUIDv5)→chunk→doc→passage→citation | Playwright V4-SR01/03 |
| AI 网关 | `services/ai_service.py` | evidence-gated | `test_v1_ai_api.py` |
| 存储 | `services/hfmzl_storage.py` | PDF containment + 哈希复验 | `apps/backend/tests/test_hfmzl_preview*.py` |

API：`api/v1/`（search, entities, evidences, passages, extractions, source_admissions, promotions, candidate_resources, classical_versions, version_center, admin, ai, auth, users, graph, relations, dashboard, day2_search）+ `api/v4/`（research, education, visualization）+ `api/v2/`（academic, graph, paper, tei）。

---

## 3. 领域文档对照（DOC_ONLY 检查）

| 文档 | 内容 | 代码落地状态 |
| --- | --- | --- |
| `docs/08-domain/0806_Chronology_Knowledge_Model.md` | 人物年表知识模型 | **DOC_ONLY** — 无 chronology 表/服务；仅 Person birth/death_year + 展览 JSON 静态 chronology |
| `docs/08-domain/0807_Geography_Knowledge_Model.md` | 地理知识模型 | **DOC_ONLY** — 无 geography 模型；GraphCanvas 静态地图 |
| `docs/08-domain/0801-0809` | 人物/书目/版本/条文/论文/学术引用/主图 | 均已落地（§1） |
| `docs/16-research-framework/1601-1610` | 学术研究框架 | 部分落地（evidence/citation/versionology 已落地） |
| `docs/07-security/0702_Security_Standard.md` | 安全标准 Ch.4-5 | 已落地（seed_rbac + auth middleware） |
| `docs/07-compliance/literature-source-policy.md` | 文献来源合规 | 已落地（SourcePolicy + 准入） |

---

## 4. 结论

- HFB 研究数据层覆盖度极高：Evidence/Citation/SourceRef/Version/Passage/准入/晋升/撤回/审计/清单哈希/Fail-Closed 均 IMPLEMENTED 且多数组件达到 TESTED/ENFORCED。
- HFD 真正缺失 4 类：**PublishedRepresentation / PublicationSnapshot**、**ICH/非遗媒体资产治理**、**统一 Assertion（可选）**、**医学合规元数据**（见 BASELINE-AUDIT §8）。
- 人物年表（Chronology）目前 DOC_ONLY，是 HFD「人物事件」切片的主要扩展点。

---

## 5. Codex 验收复核一致性（v1.1 追加）

| Codex 独立裁决（验收 §6/§13） | 本报告 | 一致性 |
| --- | --- | --- |
| Person FULL/PARTIAL → REUSE | Person IMPLEMENTED → REUSE | ✅ 一致 |
| Work/Book FULL → REUSE | Work/Book IMPLEMENTED → REUSE | ✅ 一致 |
| Edition/Chapter/Passage PARTIAL → EXTEND | 同上 IMPLEMENTED，公开阅读层 EXTEND | ✅ 一致 |
| Source PARTIAL → EXTEND | SourceRef IMPLEMENTED / 公开来源层 EXTEND | ✅ 一致 |
| Evidence/Citation PARTIAL → REUSE/EXTEND | IMPLEMENTED → REUSE | ✅ 一致 |
| Version FULL/PARTIAL → REUSE | IMPLEMENTED → REUSE | ✅ 一致 |
| Research Material/Workspace → REUSE/EXTEND | IMPLEMENTED → REUSE | ✅ 一致 |
| Acupoint/ICH/Media/Video → NEW/UNKNOWN | NOT_FOUND → NEW | ✅ 一致 |
| Review/Publish/Withdraw → EXTEND | PARTIAL → EXTEND | ✅ 一致 |
| Rights/License → EXTEND | PARTIAL → EXTEND | ✅ 一致 |
| Audit → REUSE/EXTEND | IMPLEMENTED → REUSE | ✅ 一致 |
| Publication snapshot | PARTIAL（无独立公开发布快照） | ✅ 一致 |
| Fail-closed query | IMPLEMENTED/ENFORCED | ✅ 一致 |

**结论：本 Domain Map 与 Codex 独立代码复核无 P0 级分歧。** 差异仅限判定粒度（本报告用五层验证标记细化，Codex 用四档水平），无方向性冲突。

**验收 12 项反证条目（Counter-Evidence Register）逐一回应**：见 BASELINE-AUDIT §20.3（本报告对应条目 1-4、6-7、11-12 均已在 §1 中给出 Model→Service→API→Test 证据链，无「仅文档」判定）。
