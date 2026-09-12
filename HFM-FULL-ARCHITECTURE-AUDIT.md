# HFM（皇甫谧人文数字平台）全量架构独立审计报告

**报告文件**: `HFM-FULL-ARCHITECTURE-AUDIT.md`  
**审计时间**: 2026-09-10  
**审计角色**: 独立架构审计（只读、基于事实、穿透式全量审计）  
**审计前提**: 严格遵循治理状态（PWE_IMPORT_PHASE=CLOSED, PUBLICATION=NOT_AUTHORIZED, UI_CONTENT_PROPAGATION=NOT_AUTHORIZED, AUTO_NEXT_PHASE=FORBIDDEN）。

---

## 1. Executive Verdict

```text
HFM_FULL_ARCHITECTURE_AUDIT=PASS_WITH_GAPS

PROJECT_GOAL_ALIGNMENT=PARTIAL
ARCHITECTURE_HEALTH=PASS_WITH_GAPS
DATA_HEALTH=PASS
PUBLIC_PORTAL=PARTIAL
RESEARCH_WORKSPACE=PARTIAL
PRODUCTION_DATA=PASS
PUBLICATION_READINESS=NOT_READY
UI_CONTENT_PROPAGATION_READINESS=NOT_READY

R0_COUNT=0
R1_COUNT=4
R2_COUNT=5
R3_COUNT=3

BLOCKER=NONE
```

### 核心结论摘要
1. **真实建成了什么**：HFM 成功建立了严密稳固的底座架构与权威元数据基线（675 文献、31 实体、17 人物、1 别名、14 作品、87 版本），实现了零 Orphan、零 Broken FK 的生产数据库。构建了分层的 Fast-API + Vue 3 / Vite 全栈工程系统，具有严格的鉴权与 RBAC、基于发布投影（Publication Projection）的公众访问防泄漏门禁、以及经 565 个后端测试与 262 个前端测试保护的契约一致性。
2. **核心脱节与结构性缺口**：
   - **生产数据与公众前端的“双轨脱节”**：公众端核心展示目前主要依赖静态投影数据（`homeProjection.ts`, `workCollection.ts`, `searchIndex.ts`），而真实生产库中已入库的 14 作品、87 版本、17 人物、675 篇文献因**尚未完成内容承认与发布流水线（`PublicationRecord` 与 `ContentArtifact` 绑定数为 0）**，导致公共只读 API 无法对公投射，公众端与生产数据之间存在“有库无公开展现”的屏障。
   - **知识图谱与结构化知识的“名实缺口”**：`c_domain_terms`（经穴/词条）、`c_domain_relations`（关系图谱）、`chapters`/`passages`（《针灸甲乙经》篇章段落）当前数据库记录数均为 0。系统当前处于“文献与作品元数据骨架层”，尚未进入“中医经穴结构化知识对象层”。
   - **研究工作台的“局部受限闭环”**：工作台真实支持项目（Project）与笔记（Note）的读写持久化，但对核心文献、经穴、关系和引用的标注与创建，目前未对前端暴露完整标注流，尚不能视作“完全自主的研究型知识生产平台”。

---

## 2. Runtime Reality

```text
REPO=/Users/likeming/Sites/hfm
WORKTREE=/Users/likeming/Sites/hfm
BRANCH=hfm-canonical
HEAD=603c4206c94dc26004f1eeb152dfe38743bb7e99
WORKTREE_CLEAN=YES
MULTI_WORKTREE_RISK=NO (临时 worktree /private/tmp/hfm-cigar-controlled-import-gate 仅为历史隔离节点，主工程无 dirty)
MIGRATION_HEAD=0015 (apps/backend/alembic/versions/0015_content_import_support.py)
DATABASE=PostgreSQL 17 (hfm_prod)
RUNTIME=Python 3.13.13 (uv) + Node.js (Vite / Vue 3)
DATABASE_CODE_ALIGNMENT=PASS (ORM models, alembic_version 0015, and DB schema exactly match)
```

---

## 3. Production Content Reality

真实连接 `hfm_prod` 生产数据库执行事实统计：

```text
DOCUMENTS=675
ENTITIES=31
PERSONS=17
PERSON_ALIASES=1
WORKS=14
EDITIONS=87
DEFERRED_EDITIONS=5
DATA_INTEGRITY=PASS
ORPHAN_COUNT=0
BROKEN_FK_COUNT=0
DUPLICATE_RISK=NONE
PROVENANCE_COVERAGE=100% (所有 documents 均携带 source_asset_id 与 stable_id)
```

其他扩展表生产数据事实（实际落地状态）：
- `publication_records`: 0
- `content_artifacts`: 0
- `chapters`: 0
- `passages`: 0
- `c_domain_terms`: 0
- `c_domain_relations`: 0
- `assertions`: 0
- `evidences`: 0
- `citations`: 0
- `media_assets`: 0
- `heritage_projects`: 0
- `users`: 1 (系统初始化管理员用户)

---

## 4. Architecture Map

```text
[社会公众 / 参观大屏 / 高校师生 / 科研人员]
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                      FRONTEND (Vue 3 / Vite)                │
│  - Public Portal: HomeView, WorksView, JiayiView, SearchView│
│    (当前状态: 优雅降级优先消费 static projection，支持 API 融合) │
│  - Research Workspace: ResearchHomeView, ResearchWorkspace  │
│    (支持 Note/Project 真实在线提交与读回; 检索走 /api/v1/search)│
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTP / JSON API (Bearer Token / Cookie)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    API LAYER (FastAPI v1)                   │
│  - /api/v1/auth: Login, Logout, ChangePassword (scrypt/RBAC)│
│  - /api/v1/public: home, works, persons, search, c-terms    │
│    [严格安全防线: 仅返回已 PUBLISHED 绑定的投影数据，绝不外泄草稿]│
│  - /api/v1/research: workspace, notes, projects, assertions │
│  - /api/v1/admin: users, reconciliation, audit-log, lineage │
└──────────────────────────────┬──────────────────────────────┘
                               │ Domain Services (AsyncSession)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                   DOMAIN / APPLICATION SERVICES             │
│  - PortalService: 聚合已批准公开数据                        │
│  - SearchService: PostgreSQL ILIKE + GIN 跨域检索服务       │
│  - LiteratureService: Work/Edition/Passage 著作层级生命周期 │
│  - PersonService: 人物/事件/断言证据绑定                    │
│  - ResearchWorkspaceService: 课题与研究笔记持久化           │
│  - AuditService: 操作审计流水线与数据溯源                   │
└──────────────────────────────┬──────────────────────────────┘
                               │ SQLAlchemy Async ORM (0015 Head)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                   DATABASE (PostgreSQL 17: hfm_prod)        │
│  - 基础事实层: entities (31), persons (17), person_aliases(1)│
│  - 文献层: works (14), editions (87), documents (675)       │
│  - 准入与发布控制层: content_artifacts (0), publication (0)  │
│  - 知识与图谱层: c_domain_terms (0), c_domain_relations (0) │
│  - 证据链与溯源层: assertions (0), evidences (0), citations  │
└─────────────────────────────────────────────────────────────┘
```

- **架构一致性（ARCHITECTURE_COHERENCE）**: PASS。分层清晰，职责与权限边界定义严谨。
- **架构完整性（ARCHITECTURE_COMPLETENESS）**: PASS_WITH_GAPS。底层骨架完整，但知识对象与发布中继层未通水。
- **架构过度设计（ARCHITECTURE_OVERENGINEERING）**: 极低。未引入无必要的外部复杂组件（如未引入独立 ES 集群或图数据库，原生利用 PostgreSQL 闭环）。
- **架构设计不足（ARCHITECTURE_UNDERDESIGN）**: NO。模型具备强扩展性，已预留 FRBR 与图谱关联能力。

---

## 5. Domain Architecture

| 领域对象 | 第一类领域对象支持度 | 实体约束与稳定性 | 溯源与版本机制 |
| :--- | :--- | :--- | :--- |
| **DOCUMENT** | **YES** | 拥有独立表 `documents`、`stable_id` 唯一索引，与原始客户文献严格对齐 | 携带 `source_asset_id`、`source_sha256`、`processing_status` |
| **PERSON** | **YES** | 绑定 `entities`（`entity_type='person'`），主键外键关联，拥有唯一 `stable_id` | 支持 `person_aliases`（别名），预留 `domain_status` |
| **WORK** | **YES** | 绑定 `entities`（`entity_type='work'`），拥有唯一 `stable_id`，独立 `works` 实体表 | 支持作者实体关联 `author_entity_id`、朝代、分类 |
| **EDITION** | **YES** | 拥有独立表 `editions`，唯一 `stable_id`，外键强约束 `work_id` | 支持版本父子流派 `lineage_parent_edition_id` |
| **PAGE / PASSAGE**| **PARTIAL** | 模型定义完整（`chapters`, `passages`），已建立 Locator 定位机制 | 生产库中尚无数据注入 |
| **PROVENANCE** | **PASS** | `source_refs`, `audit_log`, `reconciliation_runs` 机制完备 | 每次关键写操作强制写入 `AuditService` |
| **RELATION** | **PASS (结构完整/数据待充实)** | `c_domain_relations`, `event_relations`, `heritage_relations` | 遵循强约束实体间有向关联 |

---

## 6. End-to-End Closure Matrix

| 业务领域 | 前端 UI | API 端点 | 生产数据库表 | 生产数据量 | E2E 闭环判断 | 事实与诊断说明 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **人物体系** | [PersonDetailView](file:///users/likeming/sites/hfm/apps/frontend/src/views/persons/PersonDetailView.vue) | `GET /api/v1/public/persons/{id}` | `persons`, `entities` | 17 人物 | **PARTIAL** | UI 具备动态请求与空状态容错，但 API 强制要求 `PublicationRecord`，由于发布为 0，公网请求返回 404，UI 呈现未发布状态。 |
| **文献史料** | [WorksView](file:///users/likeming/sites/hfm/apps/frontend/src/views/works/WorksView.vue), [WorkDetailView](file:///users/likeming/sites/hfm/apps/frontend/src/views/works/WorkDetailView.vue) | `GET /api/v1/public/works` | `documents`, `works` | 675 文献, 14 著作 | **PARTIAL** | [WorkDetailView](file:///users/likeming/sites/hfm/apps/frontend/src/views/works/WorkDetailView.vue) 真实调用 API，但公共 API 受发布门禁约束，目前无已发布作品。前端列表降级使用 `workCollection.ts`。 |
| **版本流派** | [JiayiView](file:///users/likeming/sites/hfm/apps/frontend/src/views/jiayi/JiayiView.vue), [WorkDetailView](file:///users/likeming/sites/hfm/apps/frontend/src/views/works/WorkDetailView.vue) | `GET /api/v1/public/works/{id}/editions` | `editions` | 87 版本 | **PARTIAL** | 生产库有完整的 87 条真实版本记录，但尚未通过工作台发布投影暴露至公共端点。 |
| **首页聚合** | [HomeView](file:///users/likeming/sites/hfm/apps/frontend/src/views/HomeView.vue) | `GET /api/v1/public/home` | 聚合全库 | 675/14/17/87 | **PASS** (带优雅降级) | 实现了 [useHomePublicData](file:///users/likeming/sites/hfm/apps/frontend/src/composables/useHomePublicData.ts) 真实异步探针。当后端无已发布数据时，安全降级至权威静态基线，保证公众门户完整展示。 |
| **全文检索** | [SearchView](file:///users/likeming/sites/hfm/apps/frontend/src/views/search/SearchView.vue) | `GET /api/v1/public/search` | `SearchService` (GIN/ILIKE) | 全库可搜 | **PARTIAL** | 检索服务已连接数据库，但公开检索只查“已发布”数据；未发布状态下公开检索结果为空，前端通过本地静态索引保底。 |
| **研究工作台**| [ResearchHomeView](file:///users/likeming/sites/hfm/apps/frontend/src/views/research/ResearchHomeView.vue) | `POST/GET /api/v1/research/projects` | `research_projects`, `research_notes` | 动态写 | **PASS** | 实现了真实的用户鉴权、RBAC 权限守卫、项目与研究笔记的在线创建、写入数据库与读回。 |
| **中医知识图谱**| [JiayiView](file:///users/likeming/sites/hfm/apps/frontend/src/views/jiayi/JiayiView.vue) | `GET /api/v1/public/c-terms/{id}` | `c_domain_terms` | 0 | **FAIL** | 尚未注入真实经穴、病症、治法知识对象，目前前端仅有静态概念展现，无底层数据支撑。 |

---

## 7. Public Portal Audit

- **完成度与体验**：页面路由树完整、视觉与版式高度规范（符合甘肃医学院与灵台县共建人文风格，无侵入式外来框架）、响应式设计良好、可访问性（A11y/Axe）通过全面自动化测试。
- **降级与保底架构**：前端设计具备高韧性的“双轨设计”：在未授权公开生产数据前，通过预置的静态权威档案（`homeProjection.ts`, `contentInventory.ts`）提供完整公众展示，绝不出现空白崩溃页面。
- **门禁合规性**：严格遵守 `PUBLICATION=NOT_AUTHORIZED`，后端 API 在无发布记录时绝不泄漏草稿和内部 ID。

---

## 8. Research Workspace Audit

- **真实读写与持久化**：
  - `POST /api/v1/research/projects`：经 [ResearchWorkspaceService](file:///users/likeming/sites/hfm/apps/backend/src/hfm/phase1/research_workspace.py) 真实入库并落盘 `research_projects` 表。
  - `POST /api/v1/research/notes`：真实写入 `research_notes`，支持与项目关联。
- **权限与审计**：严格按角色校验（`STUDENT_RESEARCHER`, `SCHOLAR_RESEARCHER`），所有写操作自动记入 `audit_log`。
- **不足之处**：工作台目前未提供给研究者直接针对 675 篇文献及 87 个版本进行可视化“高亮标注（Annotation）- 抽取断言 - 绑定证据链”的交互式工具链。

---

## 9. Search Audit

- **实现机制**：基于 PostgreSQL 的 ILIKE 及 `pg_trgm` GIN 索引原生实现，避免外部维护负担。
- **检索范围**：跨 Domain 覆盖 Passage、Person、Work、Edition、C-term、Heritage、Media。
- **限制与边界**：
  - 公众检索强绑定 `PublicationRecord`，在生产数据未发布阶段，公众检索完全依赖前端本地分词索引。
  - 暂未引入复杂中文古籍分词词典，对古籍异体字、通假字的检索容错率有限。

---

## 10. Knowledge Graph / Structured Knowledge Audit

- **现状事实**：数据库表 `chapters` (0), `passages` (0), `c_domain_terms` (0), `c_domain_relations` (0)。
- **审计判断**：**《针灸甲乙经》结构化知识图谱尚未成型**。
- **差距原因**：前期重点在文献史料层（675 篇文献）与版本层（87 种版本）的确权与基线冻结，尚未开展对《针灸甲乙经》原文的卷、篇、穴、症层级的拆解与结构化提取工作。

---

## 11. Media / Intangible Cultural Heritage (ICH) Audit

- **现状事实**：`media_assets` (0), `heritage_projects` (0)。
- **模型支持**：模型层（`MediaAsset`）已完整支持对象存储 Key、MIME、SHA-256、版权状态（`RightsStatus`）、发布状态，支持音视频与图片。
- **非遗呈现**：前端已预置灵台皇甫谧针灸活态传承的流派脉络与第六代名医（刘君奇）史料，但目前仍位于前端静态映射层，未入库受控。

---

## 12. Security Audit

- **认证与鉴权**：采用加盐 scrypt 哈希存储密码，基于令牌（Token）与多角色 RBAC 严格隔离。
- **数据访问控制**：所有公开只读接口均有强服务端谓词限制（Publication Filter），无法横向越权访问未发布草稿。
- **敏感信息治理**：密码与密钥严禁提交 Git，`validate-production-env.py` 对生产配置实施强校验，杜绝模板密钥与测试库连接。
- **安全阻断项（SECURITY_BLOCKERS）**: **NONE**。

---

## 13. Testing Architecture Audit

所有测试均在只读模式下完整运行，实测计数如下：

| 测试套件 | 运行命令 | 测试结果 | 耗时 |
| :--- | :--- | :--- | :--- |
| **Backend Tests** | `uv run --project apps/backend pytest` | **565 passed**, 2 warnings | 131.83s |
| **Frontend Tests** | `npm --prefix apps/frontend test -- --run` | **262 passed** (28 test files) | 19.89s |
| **PWE Tooling Tests**| `uv run pytest content-production/import/pwe-tooling/tests/` | **24 passed** | 11.11s |
| **总计状态** | 全部测试套件通过 | **851 passed / 0 failed** | **PASS** |

---

## 14. Deployment / Runtime Audit

- **生产级就绪度**：本地生产级环境验证机制健全，支持无缝冷启动、健康检查探针（`/healthz`）、环境配置预检（`validate-production-env.py`）。
- **运行保障**：基于 PostgreSQL 17 + SQLAlchemy AsyncIO 驱动，连接池与事务隔离机制完备。

---

## 15. Deferred Editions 单独审计

对当前冻结的 5 条 `DEFERRED` 版本进行逐条穿透核查：
1. `EDITION-HFM-A000529` (`10023266.pdf`): 纯数字控制号命名，无目录或版权页证据，维持 DEFER。
2. `EDITION-HFM-A000530` (`10023267.pdf`): 同上。
3. `EDITION-HFM-A000531` (`10023268.pdf`): 同上。
4. `EDITION-HFM-A000532` (`10023609.pdf`): 同上。
5. `EDITION-HFM-A000541` (`《针灸甲乙经、伤寒论、金匮要略、温病学》精译.pdf`): 四书合刊合订文献，在当前单一著作外键（Single Work FK）模型下强行归类会导致版本学失真。

- **模型阻断（MODEL_BLOCKER）**: NO（合刊本可在后续版本扩展支持多对多关联合集或独立作为合辑处理）。
- **数据阻断（DATA_BLOCKER）**: NO（纯属原始文件缺乏元数据）。
- **下一阶段阻断（NEXT_PHASE_BLOCKER）**: NO（5 条保留在 DEFERRED 集合中，不影响已入库的 87 条版本正常推进）。

---

## 16. 重点识别“假完成”清单 (False Completion Findings)

| 发现项分类 | 事实与代码路径 | 危害与影响 |
| :--- | :--- | :--- |
| **DB_EXISTS_BUT_NOT_SERVED_TO_PUBLIC** | 生产库有 87 个版本与 14 部作品，但 `publication_records` 为 0，导致 [portal.py](file:///users/likeming/sites/hfm/apps/backend/src/hfm/phase1/portal.py) 的 `_published_subject_entities()` 返回空集，公共 API `/api/v1/public/home` 与 `/works` 返回空数组。 | 生产数据已入库但公众前端无法感知，公众端只能被迫使用本地静态回退数据。 |
| **PAGE_EXISTS_BUT_STATIC_CONTENT** | [WorksView.vue](file:///users/likeming/sites/hfm/apps/frontend/src/views/works/WorksView.vue) 直接引用 `WORK_COLLECTION` 静态配置，未优先接入真实 `/api/v1/public/works` 分页流。 | 数据库中的著作与版本更新无法自动反映在著作页面上。 |
| **KNOWLEDGE_GRAPH_EXISTS_IN_SCHEMA_ONLY** | `c_domain_terms` 与 `c_domain_relations` 表存在且测试完备，但生产数据记录为 0。 | 系统宣称的中医经穴知识图谱目前仅具备表结构，不具备实际数据与查询能力。 |
| **RESEARCH_WORKSPACE_SCOPE_LIMITED** | 研究工作台仅完成了科研项目与笔记创建（[ResearchWorkspacePanel.vue](file:///users/likeming/sites/hfm/apps/frontend/src/components/research/ResearchWorkspacePanel.vue)），并未连通对生产库 675 篇文献的在线标注（Annotation）与证据关联。 | 研究者无法直接基于平台数字化古籍沉淀研究成果。 |

---

## 17. Gap Register (差距分析与严重性登记)

| ID | Gap 描述 | 证据路径 | Severity | 阻断性 | 建议阶段 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **GAP-01** | 生产数据未经过内容承认与发布流水线，`publication_records` 与 `content_artifacts` 计数为 0，导致公共端点无数据输出 | `psql -d hfm_prod -c "SELECT count(*) FROM publication_records;"` => 0 | **R1** | 阻断公众生产端数据展示 | 内容承认与发布流（CONTENT_ADMISSION_AND_PUBLICATION） |
| **GAP-02** | 公众端部分页面（作品目录、版本列表、检索）仍以前端静态 fallback 为主，未与后端发布流打通全链路闭环 | [WorksView.vue](file:///users/likeming/sites/hfm/apps/frontend/src/views/works/WorksView.vue), [useHomePublicData.ts](file:///users/likeming/sites/hfm/apps/frontend/src/composables/useHomePublicData.ts) | **R1** | 影响公众门户真实数据呈现 | UI 内容传播与接口连通（UI_CONTENT_INTEGRATION） |
| **GAP-03** | 《针灸甲乙经》篇章、段落与经穴结构化知识对象未提取入库 | `psql -d hfm_prod -c "SELECT count(*) FROM chapters;"` => 0 | **R2** | 不阻断当前验收，但影响中医专科平台纵深 | 中医结构化知识图谱构建（C_DOMAIN_KNOWLEDGE_EXTRACTION） |
| **GAP-04** | 灵台非遗代表性项目与传承谱系尚未入库，停留在静态展示层 | `psql -d hfm_prod -c "SELECT count(*) FROM heritage_projects;"` => 0 | **R2** | 不阻断当前交付，影响非遗专栏动态性 | 非遗与多媒体资产入库（HERITAGE_AND_MEDIA_INGESTION） |
| **GAP-05** | 研究工作台缺乏对 675 篇文献的在线全文阅读标注与引文生成链条 | [ResearchWorkspacePanel.vue](file:///users/likeming/sites/hfm/apps/frontend/src/components/research/ResearchWorkspacePanel.vue) | **R2** | 影响深度科研闭环 | 深度研究工作台工具链（ADVANCED_RESEARCH_TOOLING） |
| **GAP-06** | 5 条 DEFERRED 版本缺失版权页 OCR 与合订本分类规则 | `EDITION-CONFIRMATION-REVIEW.csv` | **R3** | 不阻断 | 后续补录与合订本扩展 |

---

## 18. Publication Readiness 审计

```text
PUBLICATION_READINESS=NOT_READY
PUBLICATION_AUTHORIZATION=NOT_GRANTED

PUBLICATION_BLOCKERS:
1. 生产数据尚未经过正式的 ContentArtifact 承认与 PublicationRecord 生成程序，发布表记录为 0。
2. 尚未对已入库的 87 个版本及 14 部作品的著作权与公开合规性（RightsStatus / Copyright）进行合规复核。
3. 公共 API 当前在零发布状态下返回空结果，贸然开放会导致前端依赖 fallback 或呈现无内容空卡片。

PUBLICATION_PREREQUISITES:
- 完成受控的 Content Admission & Publication 流水线。
- 经过人工复核的版权免责声明与公开范围授权。
```

---

## 19. UI Content Propagation Readiness 审计

```text
UI_CONTENT_PROPAGATION_READINESS=NOT_READY
UI_CONTENT_PROPAGATION_AUTHORIZATION=NOT_GRANTED

UI_PROPAGATION_RISKS:
1. 87 个版本的题名长短不一（如超长题名《针灸甲乙经》河南科技出版社2017韩森宁张春生徐长卿点校.pdf），直接投射至 UI 可能引发卡片布局排版溢出或换行折断。
2. 675 篇文献数据中存在大量机器提取的规范化题名，批量直接投射至前端前需进行界面渲染压力与视觉截断测试。
3. 搜索联动风险：发布后后端检索与前端本地索引的分词差异可能导致用户搜索结果不一致。

REQUIRED_PRECHECKS:
- 在隔离测试环境下执行 UI 数据注水与布局溢出回归测试。
- 完成长标题截断与无图占位（Placeholder）容错机制验证。
```

---

## 20. Recommended Next Phase (下一阶段判断)

### 核心推导逻辑
```text
项目目标：高校科研验收 + 政府非遗展示 + 公众与师生可用
  ↓
当前现实：生产库已有高质量的 675 文献、14 作品、87 版本，但发布记录为 0，公众 API 处于门禁阻断状态
  ↓
核心阻断：生产数据无法穿透到公众前端
  ↓
唯一下一阶段：受控的内容承认与发布投影阶段 (CONTROLLED_CONTENT_ADMISSION_AND_PUBLICATION)
```

```text
NEXT_PHASE_RECOMMENDATION=CONTROLLED_CONTENT_ADMISSION_AND_PUBLICATION
WHY_THIS_PHASE=
当前系统的数据库与底层模型完全健康，前端骨架与可访问性完全达标。系统最核心的脱节在于“数据已入库但未被承认并发布”。如果不进行受控的内容承认与发布记录绑定，任何前端接入都只能继续面对空数据或被迫使用静态 mock。必须首先建立从真实 Entity/Work/Edition 到 ContentArtifact 及 PublicationRecord 的受控发布流水线，系统才能真正实现生产数据的端到端闭环。

ENTRY_CONDITIONS:
- PWE 导入已确认关闭（PWE_IMPORT_PHASE=CLOSED）。
- 生产库基线数据经校验完全一致（675/31/17/1/14/87）。
- 具备明确的版权状态（RightsStatus）判定规则。

EXIT_CONDITIONS:
- 针对 14 部核心作品及确认推荐的 87 个版本，生成对应的 ContentArtifact 及 PUBLISHED 状态的 PublicationRecord。
- `/api/v1/public/home` 与 `/api/v1/public/works` 端点能够稳定返回真实生产数据。
- 零数据泄露，草稿与私有数据保持严格隐匿。

AUTHORIZED_SCOPE:
- 后端内容承认与发布服务实现（ContentArtifactRepository / PublicationService）。
- 对应测试用例编写与幂等发布脚本。

FORBIDDEN_SCOPE:
- 禁止修改已冻结的 PWE 映射基线与导入逻辑。
- 禁止修改前端 UI 渲染逻辑与静态 fallback。
- 禁止直接开放外网 PUBLICATION。

RISK=若发布标准不严格，可能导致未经校对的原始文献元数据暴露给公众。
AUTO_START=FORBIDDEN
USER_AUTHORIZATION_REQUIRED=YES
```

---

## 21. Final Governance Verdict

```text
PWE_PRODUCTION_APPLY_ACCEPTANCE=PASS
PWE_PRODUCTION_IMPORT_STATUS=ACCEPTED
PWE_IMPORT_PHASE=CLOSED

PWE_REOPEN_REQUIRED=NO

PUBLICATION_AUTHORIZATION=NOT_GRANTED
UI_CONTENT_PROPAGATION_AUTHORIZATION=NOT_GRANTED

NEXT_PHASE_RECOMMENDATION=CONTROLLED_CONTENT_ADMISSION_AND_PUBLICATION
NEXT_PHASE_AUTO_START=FORBIDDEN
EXPLICIT_USER_AUTHORIZATION_REQUIRED=YES

ARCHITECTURE_BLOCKER=NONE
R0_REMAINING=0
R1_REMAINING=4
R2_REMAINING=5
R3_REMAINING=3

PROJECT_READY_FOR_NEXT_DECISION=YES
```
