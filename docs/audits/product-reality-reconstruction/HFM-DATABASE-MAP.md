# HFM-DATABASE-MAP.md — 数据库实体模型与 Schema Reality Reconstruction

## 1. 数据库引擎与迁移链

- **数据库引擎**：PostgreSQL (生产环境), 支持 SQLite (测试/隔离验证)
- **迁移框架**：Alembic
- **当前迁移 HEAD**：`0014_p2_media_rights` (`0014_p2_media_rights.py`)
- **迁移历史完整链**：
  1. `0001_cd0_foundation`：基础基石表 (Audit, System)
  2. `0002_cd1_entity_person`：核心实体基类、人物模型 (entities, persons)
  3. `0003_cd2_ancient_text`：古籍作品、版本、卷篇、字句 (works, editions, chapters, passages)
  4. `0004_cd3_evidence`：证据模型 (evidence, sources, source_refs)
  5. `0005_cd4_assertion`：学者学术断言 (assertions)
  6. `0006_cd5_citation`：引文与引用链 (citations)
  7. `0007_cd5_withdrawal`：引文撤回状态机
  8. `0008_cd6_event`：历史事件与事件时空关系 (events, event_relations)
  9. `0009_p1_content_admission`：内容准入状态机 (content_artifacts)
  10. `0010_p1_frontier2`：知识对象概念与领域术语 (c_domain_terms, c_domain_relations)
  11. `0011_p1_frontier3`：活态非遗工程与保护主体 (heritage_projects, heritage_relations)
  12. `0012_p1_frontier4`：认证与五级 RBAC 体系 (users, roles, user_roles)
  13. `0013_p1_frontier6_research_workspace`：研究工作台独立实体 (research_projects, research_notes)
  14. `0014_p2_media_rights`：数字媒体资产与版权管理 (media_assets)

---

## 2. 核心实体模型与数据库物理表对应关系

| 业务实体概念 | ORM Model 类名 | 物理数据表名 | 核心字段 | 外键与约束 |
|---|---|---|---|---|
| **实体基类** | `Entity` | `entities` | `id`, `name`, `entity_type`, `description` | 基础实体表，派生人物/机构等 |
| **人物** | `Person` | `persons` | `entity_id`, `courtesy_name`, `birth_year`, `death_year`, `biog` | FK → `entities.id` |
| **机构/学派** | `Institution` | `institutions` | `entity_id`, `location`, `founded_year` | FK → `entities.id` |
| **文献作品** | `Work` | `works` | `id`, `title`, `author_id`, `category` | FK → `entities.id` |
| **版本** | `Edition` | `editions` | `id`, `work_id`, `edition_name`, `dynasty`, `holding_inst` | FK → `works.id` |
| **卷/篇** | `Chapter` | `chapters` | `id`, `work_id`, `title`, `sequence`, `juan_number` | FK → `works.id` |
| **段落条文** | `Passage` | `passages` | `id`, `chapter_id`, `content`, `sequence` | FK → `chapters.id` |
| **证据** | `Evidence` | `evidence` | `id`, `evidence_type`, `content`, `confidence` | 支撑断言与考证 |
| **史料来源** | `Source` | `sources` | `id`, `title`, `author`, `source_type` | 证据溯源来源 |
| **史料索引** | `SourceRef` | `source_refs` | `id`, `source_id`, `locator`, `passage_id` | FK → `sources.id`, `passages.id` |
| **学术断言** | `Assertion` | `assertions` | `id`, `subject_id`, `predicate`, `object_id`, `status` | 支持多学术观点并存 |
| **引用引文** | `Citation` | `citations` | `id`, `assertion_id`, `source_ref_id`, `is_withdrawn` | 可溯源学术引文 |
| **历史纪事** | `Event` | `events` | `id`, `entity_id`, `year`, `title`, `description` | FK → `entities.id` |
| **时空事件关系** | `EventRelation` | `event_relations` | `id`, `source_event_id`, `target_event_id`, `relation_type` | 支持事件前后/因果网络 |
| **知识对象术语** | `CDomainTerm` | `c_domain_terms` | `id`, `name`, `category`, `pinyin`, `definition` | 穴位、经络、病候等 |
| **知识关系网** | `CDomainRelation` | `c_domain_relations`| `id`, `source_term_id`, `target_term_id`, `relation_type` | 经络-穴位、穴位-主治关系 |
| **活态非遗** | `HeritageProject` | `heritage_projects` | `id`, `name`, `level`, `batch`, `inheritor_id` | 非遗名录与传承实体 |
| **非遗传承关系** | `HeritageRelation` | `heritage_relations`| `id`, `project_id`, `person_id`, `generation` | 传承人代际关系谱系 |
| **用户** | `User` | `users` | `id`, `username`, `password_hash`, `token_version`, `is_active` | 平台统一账号 |
| **角色** | `Role` | `roles` | `id`, `code`, `name`, `description` | 冻结 5 级角色 (ANONYMOUS 到 ADMIN) |
| **用户角色关联** | N/A (Table) | `user_roles` | `user_id`, `role_id` | 复合主键，多对多映射 |
| **研究项目** | `ResearchProject` | `research_projects` | `id`, `title`, `owner_id`, `description` | FK → `users.id` (严格所有者隔离) |
| **研究笔记** | `ResearchNote` | `research_notes` | `id`, `project_id`, `owner_id`, `content` | FK → `users.id`, `research_projects.id` |
| **内容发布准入** | `ContentArtifact` | `content_artifacts` | `id`, `admission_state`, `rights_status`, `provenance_status` | 审核工作流第一阶段 |
| **正式发布记录** | `PublicationRecord`| `publication_records`| `id`, `artifact_id`, `publication_status`, `reviewer_id` | 控制公众端只读投影 |
| **媒体资产** | `MediaAsset` | `media_assets` | `id`, `filename`, `content_type`, `byte_size`, `rights_status` | 数字图像与影印资源 |
| **审计日志** | `AuditLog` | `audit_logs` | `id`, `action`, `operator_id`, `payload`, `timestamp` | 全局审计追溯 |
| **对账运行** | `ReconciliationRun`| `reconciliation_runs`| `id`, `status`, `discrepancy_count`, `created_at` | 数据一致性校验 |
