# HFD Phase 0 — Baseline Audit（HFB → HFD 继承差距审计）

> 审计对象：`/Users/likeming/Sites/hfb`（皇甫谧数字人文研究平台，HFB）
> 审计委托：《皇甫谧人文数字平台》（HFD）Phase 0 — 只读审计。
> 状态标记：REUSE / EXTEND / ADAPT / DEPRECATE / NEW / UNKNOWN
> 治理标记：IMPLEMENTED / PARTIAL / DOC_ONLY / NOT_FOUND / CONFLICT
> 验证分层标记：`SPECIFIED`（文档/注释声明）/ `IMPLEMENTED`（代码存在）/ `ENFORCED`（DB 约束/触发器/服务层强制）/ `TESTED`（自动化测试通过）/ `RUNTIME`（真实运行时验证）。文档**不替代** enforcement 证据。
> 修订：v1.1（2026-08-27 15:28 CST，HEAD `2d98b610a63d2b0347ff5ec7fcd1d598913f3521`，branch `main`）— 依 Codex 验收 §17 五项强制修正追加 §3.1（验证分层）、§8.3（快照分类）、§17.1（验证边界）、§20（验收复核）。
> 交付物位置：`/Users/likeming/Sites/hfb/docs/audit/`（与验收同一工作树）。

---

## 1. Executive Summary

**结论：CONDITIONAL PASS**（验收复核后维持；Codex 因交付物缺失判 BLOCK，见 §20 — 交付物已补齐绑定 HEAD）

HFB 是治理深度成熟的系统：候选沙箱（P1）→ 来源准入三级审核（P2）→ 生产晋升 + 哈希锁定（P3）→ 旧数据治理 + Fail-Closed 查询（P4）→ 撤回级联污损（P6）→ FRBR 书目（P7）→ OCR 校勘审计（Gate 4）。

**HFD 继承资产**（REUSE）：Person/Book/Version/Passage/Evidence/Citation/SourceRef/准入/晋升/撤回/审计/清单哈希/RBAC/检索/阅读器/工作流 — 全部有代码与测试证据。

**HFD 必须新建**（NEW，均无 HFB 等价物）：

| # | 缺口 | 等级 | 章节 |
| --- | --- | --- | --- |
| G1 | 医学合规元数据与免责声明全链路（数据/服务/展示/导出/AI） | P0 | §8 |
| G2 | 公众门户匿名访问（读接口全 JWT；Visitor 无匿名绑定） | P0 | §7, §11 |
| G3 | PublishedRepresentation / PublicationSnapshot（发布快照隔离 + 回滚 + 发布审计） | P0 | §10 |
| G4 | 非遗/媒体资产权利治理（视频/图片全链） | P0 | §9 |
| G5 | 内容发布状态机统一（book/version/person） | P1 | §6, §10 |
| G6 | 撤回内容列表面一致过滤（withdrawn version 仍在列表） | P1 | §6, §10 |
| G7 | 同人审核互斥（Leader 可 create+publish；候选 session 自审） | P1 | §11 |

---

## 2. Repository Baseline

| 项 | 值 | 证据 |
| --- | --- | --- |
| 仓库路径 | `/Users/likeming/Sites/hfb` | `pwd` |
| 分支 | `main` | `git branch --show-current` |
| HEAD | `2d98b610a63d2b0347ff5ec7fcd1d598913f3521` — "docs(context): 项目状态记录 2026-08-26" | `git rev-parse HEAD` |
| 生成时间 | 2026-08-27 15:28 CST（v1.1 复核） | `date` |
| 工作树 | `M docs/12-context/project-state-2026-08-26.md`（审计前既有修改）+ `docs/audit/` 新增（本次交付） | `git status --short` |
| 迁移头 | `gate4_ocr_proofreading_audits`（51 revision） | `alembic history` |

### 2.1 Monorepo 目录结构

```
apps/backend    FastAPI + SQLAlchemy 2 async + Alembic
apps/frontend   Vue 3 + Vite + Vitest + Playwright
packages/       config / tcm_kg / tcm_ontology / tcm_rag / tcm_tei / types / ui / utils
docs/           45 目录（00-governance … 17-Platform-Specifications）
tests/          unit/ + integration/ + e2e/
scripts/ infra/ deploy/ docker/ templates/ tools/ hfmzl/（PDF 语料库）
```

### 2.2 数据库与基础设施（实测）

| 组件 | 状态 | 证据 |
| --- | --- | --- |
| PostgreSQL 16 @ 127.0.0.1:5432（hfb/change-me） | 运行中，64 张 public 表，迁移头一致 | `psql \dt` + `alembic_version` |
| 治理 DB 角色 | 63 个 `hfb_gov_*` LOGIN 角色 | `pg_roles` |
| Elasticsearch @ 9200 | 运行中，cluster green | `curl /_cluster/health` |
| Redis | 未单独验证 | — |
| MinIO @ 9000 | **未运行**（连接拒绝）→ 阻塞 pytest E2E 启动 | `curl /minio/health/live` = 000 |

### 2.3 当前测试体系

pytest（`testpaths=["tests"]`，`--cov-fail-under=70`）+ vitest + vue-tsc + eslint/prettier + Playwright + ruff + mypy（CI 门禁文件清单）+ pre-commit。见 §12 实测。

---

## 3. Existing Architecture

| 层 | 技术 | 证据 |
| --- | --- | --- |
| API | FastAPI，v1/v2/v4 路由 + /health /ready | `apps/backend/app/api/` |
| ORM | SQLAlchemy 2.0 async，UUIDv7，软删除 | `db/base.py` |
| 迁移 | Alembic，PG + SQLite 双方言 | `db/migrations/versions/` |
| 治理执行 | SECURITY DEFINER 过程 + 每用户治理角色 + append-only 触发器 | `db/governance_db_roles.py`, `db/candidate_triggers.py`, `db/audit_triggers.py` |
| 检索 | PostgreSQL ILIKE（MVP）+ ES 预留 + RAG（evidence-gated） | `services/search_service.py`, `services/rag_service.py` |
| AI | OpenAI/Anthropic 网关，Evidence-Gated | `services/ai_service.py` |
| 前端 | Vue 3 + Pinia + vue-router + Vitest + Playwright | `apps/frontend/src/` |
| 数据流 | ResearchSession → QueryHistory → ResearchRun → OutputArtifacts | `models/workspace.py`; `services/research_workflow_service.py` |

关键架构事实：

- **前后台未分层**：同一 FastAPI 应用服务研究端与公开端；公开路由要求 JWT（§11）。
- **认证**：JWT Bearer + cookie 双通道，`token_version` 吊销。`middleware/auth.py`。
- **发布隔离**：生产数据必须经 `SourceAdmissionEntry(APPROVED) + ProductionPromotion(SUCCEEDED)` 或 `LegacyProvenanceDecision(legacy_validated)` 才可被生产查询命中（P4）。`services/production_query_policy.py`。

### 3.1 验证分层说明（验收 §17 修正 3）

本报告每项能力按五层标记：`SPECIFIED → IMPLEMENTED → ENFORCED → TESTED → RUNTIME`。规则：

- `SPECIFIED`：仅文档/注释声明（如 Chronology 文档）。
- `IMPLEMENTED`：代码/模型/API 存在。
- `ENFORCED`：存在 DB 约束、触发器、SECURITY DEFINER 过程或服务层强制逻辑（不允许绕过）。
- `TESTED`：有自动化测试通过（本报告 §12 基线）。
- `RUNTIME`：本次审计在真实运行环境验证（Playwright 27/27 对真实 PG 后端；integration 48 对 PG）。

**不得以文档代替 enforcement**：凡标 `SPECIFIED` 而无对应层证据的能力，一律不得按 IMPLEMENTED 处理。

---

## 4. Existing Domain Model

完整映射见 `HFD-PHASE0-DOMAIN-MAP.md`（v1.1 已含五层验证标记与调用链）。要点：

- **已实现**：Person、Work/Edition/Manifestation、Version/ClassicalVersion、Chapter/Passage/Sentence/Token/Variant、SourceRef/Evidence/Citation（含 taint）、Document/DocumentChunk/OCR 审计、Candidate*、SourceAdmissionEntry、ProductionPromotion、LegacyProvenance、AcademicEntity/Relation、TCMEntity、TEI、Commentary、Paper、ResearchSession/Note。
- **未实现**：PublishedRepresentation、PublicationSnapshot、ICH/非遗、媒体资产（视频）、统一 Assertion、医学合规元数据（全缺）、统一 AuditEvent。
- **DOC_ONLY**：Chronology（`0806`）、Geography（`0807`）。

---

## 5. Existing Governance Model

按「documentation → migration → model → service → API → test」六层取证。完整表见 v1.0；核心结论（经 Codex 独立复核一致）：

| 治理能力 | 状态 | 验证分层 | 关键证据 |
| --- | --- | --- | --- |
| Discovery/Candidate | IMPLEMENTED | ENFORCED+TESTED | `models/candidate.py`; `db/candidate_triggers.py`; 迁移 `candidate_foundation` |
| Admission（三级审核） | IMPLEMENTED | ENFORCED+TESTED | `models/source_admission.py:42-51`; `services/source_admission.py`; `test_source_admission_rbac.py` |
| Evidence/Review | IMPLEMENTED | TESTED | `db/candidate_publish_uow.py`; `test_phase_a0_candidate_pipeline.py` |
| Publication（晋升） | IMPLEMENTED | ENFORCED+TESTED | `models/production_promotion.py`（幂等键+唯一索引）; `test_production_query_policy.py` |
| Withdrawal（撤回+污损） | IMPLEMENTED | ENFORCED+TESTED | `models/academic_taint.py`; `test_academic_taint_lifecycle.py` |
| Versioning（清单） | IMPLEMENTED | ENFORCED+TESTED | `models/candidate.py:95-124`（DRAFT/FINALIZED/SUPERSEDED） |
| Provenance/Legacy | IMPLEMENTED | ENFORCED+TESTED | `models/legacy_provenance.py`（append-only evidence package） |
| Immutable/Hash/DAG | IMPLEMENTED | ENFORCED+TESTED | `db/candidate_triggers.py:71-92`; `services/manifest_validator.py:26-58`; `core/canonical_hash.py` |
| Fail-Closed Query | IMPLEMENTED | ENFORCED+TESTED | `services/production_query_policy.py`（不支持模型 raise） |

**无 CONFLICT 项。**

---

## 6. Existing Functional Assets

| 资产 | 判定 | 证据 |
| --- | --- | --- |
| Reader | **REUSE**（研究版）/ EXTEND（公开版） | `pages/reader/ReaderPage.vue`; `repositories/document.py:46-56`（P4） |
| Library | **REUSE** | `pages/library/*`; P4 过滤 |
| Search | **REUSE** | `api/v1/search.py`; `services/search_service.py:288-296` |
| Knowledge | **REUSE** | `pages/knowledge/*`; `api/v4/visualization.py` |
| Workspace | **REUSE** | `layouts/ResearchAppLayout.vue`; `models/workspace.py` |
| Research Projects | **REUSE** | `pages/research/ProjectListPage.vue` |
| Workflow | **REUSE** | `api/v4/research.py:340-640`; `services/research_workflow_service.py` |
| Evidence/Citation | **REUSE** | `services/citation_persistence.py`; Playwright V4-SR01/02/03 |
| Reports | **REUSE** | `pages/reports/*`; `export_run_markdown` |
| AI Copilot | **REUSE** / EXTEND（医学护栏） | `services/ai_service.py`（Evidence-Gated） |
| Authentication | **REUSE** | `api/v1/auth.py`; `middleware/auth.py` |
| RBAC | **REUSE** / EXTEND（SoD、公开 Visitor） | `db/seed_rbac.py`; `middleware/auth.py` |
| Export | **REUSE**（markdown）/ NEW（PDF/打印） | `export_run_markdown` |
| Media | **DEPRECATE**（静态引用）/ NEW | `PersonIntroView.vue:389-404` |
| Admin | **REUSE** | `views/admin/*`; `api/v1/admin.py` |

---

## 7. Public Portal Gap Audit（HFD 公众门户目标逐项）

| HFD 目标 | HFB 现状 | 判定 | 证据 |
| --- | --- | --- | --- |
| 皇甫谧人物档案 | Person + domain admission + 展览静态 JSON；列表默认 verified 过滤 | **EXTEND** | `repositories/person.py:31-36` |
| 著作与古籍阅读 | Book/Version/ClassicalVersion + Reader + hfmzl 准入；阅读页需登录 | **EXTEND** | `router/index.ts` reader requiresAuth; /hfmzl/preview 需 JWT |
| 针灸学术文化展示 | PersonIntroView 展览 | **EXTEND** | `views/PersonIntroView.vue` |
| 非遗数字展示 | 无 ICH 模型/媒体治理 | **NEW** | §9 |
| 教学辅助资源 | V4 `/education/learn`（分级+evidence 强制）但需登录 | **EXTEND** | `api/v4/education.py:158-241` |
| 公众检索 | unified search 完整但需 JWT | **EXTEND** | `api/v1/search.py` |
| 来源与证据查看 | V4 SourceRef 卡片 + trace closure 验证通过 | **REUSE** | Playwright V4-SR01/03 |
| 内容版本 | Version/ClassicalVersion 双轨；无公开版本号 | **EXTEND** | `models/version.py` |
| 医学免责声明 | **不存在**（前后端 0 命中） | **NEW** | grep「免责\|medical advice」= 0 |
| 版权/授权状态 | Document.copyright_status 等；ClassicalVersion.public_domain_status | **REUSE** | `models/document.py:40-58` |
| 发布/撤回 | 文档级准入+撤回+零召回；内容级无发布状态 | **EXTEND** | `production_query_policy.py` |

**Gap 核心**：HFB 公开面 = 登录后 Visitor 只读面；HFD 需真正匿名公众门户。**不得重写研究层**。

---

## 8. Research / Publication Layer Audit（十问）

| # | 问题 | 结论 | 证据 |
| --- | --- | --- | --- |
| 1 | draft/review/approved/published/withdrawn 状态？ | **PARTIAL** — review_status/domain_status/SourceAdmissionStatus/withdrawn_at 分散存在；**无统一 published 状态** | `models/document.py:63-79`; `core/status_machine.py` |
| 2 | 前台是否可读研究草稿？ | **文档：NO**（P4 fail-closed）。**书目/版本：PARTIAL**（列表无 withdrawn/review 过滤） | `repositories/document.py:54-56` |
| 3 | 是否存在发布快照？ | **PARTIAL** — promotion 哈希快照/manifest/检索快照；**无发布时点表达快照** | `models/production_promotion.py:64-71` |
| 4 | 发布后后台修改是否立即影响公众数据？ | **YES** — 原地修改即刻可见 | `db/base.py:38-44` |
| 5 | 能否回滚？ | **内容：NO**；报告可 replay（哈希比对） | `api/v4/research.py` replay |
| 6 | 记录发布人/审核人/时间/版本？ | **PARTIAL** — 准入链完整；**内容发布人/版本号无** | `models/source_admission.py:86-141` |
| 7 | PublishedRepresentation 等价模型？ | **NO** | `models/` 全表扫描 |
| 8 | 反向定位 Evidence/Source？ | **YES（研究面）** — trace closure + Playwright 验证 | `services/trace_lineage.py` |
| 9 | 投影失败可观测？ | **PARTIAL** — fail-closed 404 + traceability 块 | `api/v4/education.py:180-190` |
| 10 | 重试/幂等/一致性？ | **YES** — promotion 幂等键；candidate 单事务+FOR UPDATE；taint 同事务 | `models/production_promotion.py:28-30` |

### 8.3 快照分类学（验收 §17 修正 4）

三种「快照」语义必须区分，HFD 建模决策不得混用：

| 概念 | 定义 | HFB 现状 | 判定 |
| --- | --- | --- | --- |
| **Publication Model**（发布模型） | 公开发布内容的表达结构（PublishedRepresentation）及其状态机（draft→published→withdrawn） | 无独立模型；研究实体即展示实体 | **NOT_FOUND → NEW** |
| **Publication Snapshot**（发布快照） | 发布时点的内容冻结副本，用于快照隔离、回滚、发布审计（who/when/version） | 无；仅 `ProductionPromotion` 的**哈希快照**（锁定 promotion 时字节，非内容表达副本）+ `CandidateManifestRevision`（锁定清单版本）+ `LegacyProvenanceEvidencePackage`（锁定旧数据判定） | **PARTIAL → NEW**（哈希快照可作种子） |
| **Research Replay Snapshot**（研究回放快照） | 研究运行的可复现输入快照（retrieval_snapshot），用于 replay 哈希比对 | `GenerationProof.retrieval_snapshot` + `replay_research_run`（`api/v4/research.py:1026-1030`） | **IMPLEMENTED（TESTED+RUNTIME）→ REUSE** |

**验收 Counter-Evidence #6 回应**：research replay snapshot 未在本报告中被误称为 publication snapshot；两者在 §8.3 明确分离。

---

## 9. Rights & Media Baseline（版权与媒体治理）

### 9.1 Media/Video/Image 字段覆盖

| 要求字段 | HFB 现状 | 证据 |
| --- | --- | --- |
| 来源 | Image.source（单文本） | `models/image.py:18` |
| 所有者/提供方 | **缺** | — |
| 版权依据 | Image.license_info；Document 系字段不覆盖媒体 | `models/image.py:19` |
| 授权证明/公众展示/教学/衍生权限 | **缺** | — |
| 有效期/撤回状态/文件哈希/版本/审计 | **缺**（candidate_artifacts.sha256 仅覆盖 hfmzl PDF） | `models/candidate.py:63-64` |

### 9.2 非遗视频全链（素材登记→权利确认→审核→发布→撤回）

| 环节 | 状态 | 证据 |
| --- | --- | --- |
| 素材登记 | **NOT_FOUND**（2 mp4 仅前端静态 JSON） | `data/huangfu_mi_exhibition.json` |
| 权利确认/审核/发布/撤回 | **NOT_FOUND** | — |

**例外**：hfmzl PDF 语料是治理完备路径（candidate → admission → promotion → 哈希复验），可作 HFD 媒体治理**架构模板**（`hfmzl_storage.py` + /hfmzl/preview）。

---

## 10. Publication Architecture Baseline（发布架构基线）

| 能力 | 状态 | 证据 |
| --- | --- | --- |
| 研究数据与公众表达分离 | **NOT_IMPLEMENTED** | 同库同表 |
| 发布时点快照 | **NOT_IMPLEMENTED**（有哈希快照非表达快照） | §8.3 |
| 发布后变更隔离 | **NOT_IMPLEMENTED** | §8 Q4 |
| 回滚 | **NOT_IMPLEMENTED**（内容） | §8 Q5 |
| 发布审计 | PARTIAL（准入链有；内容无） | §8 Q6 |
| 反向追溯 | **IMPLEMENTED**（研究面闭环） | §8 Q8 |
| 投影失败可观测 | PARTIAL | §8 Q9 |
| 重试/幂等/一致性 | **IMPLEMENTED** | §8 Q10 |

---

## 11. RBAC & Security Baseline

### 11.1 角色（8 个）

`Platform Administrator` / `Academic Administrator` / `Steering Committee` / `Research Leader` / `Researcher` / `Reviewer` / `Student` / `Visitor`。权限 = 21 资源 ×（create/read/update/delete/export + publish/review/approve）+ source_admission 五动作。`db/seed_rbac.py:28-55`。

### 11.2 权限链验证

| 问题 | 结论 | 证据 |
| --- | --- | --- |
| 录入→编辑→审核→发布→撤回链可表达 | **YES** | `seed_rbac.py` |
| 同用户绕过审核自行发布 | **PARTIAL YES** — Leader 持 create+update+publish；候选为 session 自审；无「审核人≠提交人」约束 | `seed_rbac.py:170-200`; `router/index.ts` /candidate-review |
| 公众访问 draft/rejected/withdrawn | **文档：NO**（P4）；**版本：PARTIAL**（withdrawn 仍在列表）；**人物：NO** | `production_query_policy.py`; `repositories/person.py:31-36` |
| 跨用户/跨项目隔离 | **YES**（session 属主门 + session_id 双维度 + ACL fail-closed + 治理角色防 impersonation） | `repositories/document.py:58-84`; `db/governance_db_roles.py` |
| 匿名访问 | **NO** — 读接口全 JWT；仅 /health /ready /exhibition JSON 匿名 | `middleware/auth.py:37-63` |

测试：`test_api_rbac.py`（55 passed 单独运行）、`test_source_admission_rbac.py`、`test_classical_versions_rbac.py`、`test_ocr_cross_session_auth.py`、Playwright canonical_rbac_real 12 项 — 通过。

---

## 12. Test Baseline（实测 2026-08-27，PG 可达环境）

### 12.1 官方基线（CI 匹配：unit + integration 同进程）

| 套件 | 命令 | pass | fail | error | duration |
| --- | --- | --- | --- | --- | --- |
| Backend unit + integration | `.venv/bin/pytest tests/unit tests/integration -q` | **2724** | 0 | 0 | 714.8s |
| 其中 unit（含 ingestion） | 含 `test_ingestion_service.py` 85 passed | 2676 | 0 | 0 | — |
| 其中 integration | PG 真实连接 | 48 | 0 | 0 | 112.2s |
| deselected | `-m "not real_llm"`（`test_day4_generation.py::test_real_llm_*`） | 1 deselected | — | — | — |

### 12.2 前端与静态门禁

| 套件 | 结果 | duration |
| --- | --- | --- |
| vitest `pnpm test` | **807 passed**（35 files） | 49.6s |
| vue-tsc `pnpm typecheck` | PASS | <60s |
| eslint `pnpm lint` | PASS | <60s |
| vite build `pnpm build` | PASS | 13.0s |
| ruff `ruff check apps/backend packages tests` | PASS | — |
| mypy（CI 门禁 22 文件，--strict） | **8 errors（既有失败）**：`api/v1/source_admissions.py:184,203` `Missing type arguments for generic type "dict"`（mypy 2.1.0） | — |

### 12.3 E2E

| 套件 | 结果 | 说明 |
| --- | --- | --- |
| Playwright `pnpm test:e2e` | **27/27 passed**（2.3m，真实 PG 后端 :8000） | RUNTIME 验证：canonical_rbac 12 + critical-journeys 12 + v4-real-sourceref 3 |
| pytest E2E `tests/e2e/test_critical_journeys.py` 等 | **环境受限**：MinIO 未运行 → `/ready` 全量健康检查（ES/MinIO 重试 ~13s）超 10s 探测窗口 → setup errors | 需 MinIO/ES 就绪环境 |

### 12.4 验收口径差异解释（验收 §16 P1 修正 3）

Codex 报告「2561 passed / 9 failed / 106 errors」与本次「2724 passed / 0 fail」的差异根因：

1. **验收环境 PostgreSQL 被沙箱拦截**（`PermissionError: [Errno 1] Operation not permitted`）→ 全部 PG 依赖测试在 setup 阶段 error（106 errors 主体）。
2. **全量单进程收集干扰**：`pytest tests/`（含 tests/e2e 同进程）在本环境实测产生 562 failed / 2438 errors 级联（跨文件 PG fixture 干扰），而**官方基线为分套件运行**；项目状态文档已记载该隔离敏感性（「破坏性 PG fixture 精确白名单」`afb2d9d` / `6382bdf`）。单文件验证：`test_api_rbac.py` 独立运行 55 passed（全量中 110 errors）。
3. **环境版本**：本机 Python 3.13（验收亦为 3.13.7；CI 声明 3.12 — 验收 P3 观察项），mypy 2.1.0 严格性触发既有 8 errors。

**结论**：在匹配 CI 的 PG 可达环境下，官方分套件基线 = **2724 passed / 0 failed / 0 errors（unit+integration）+ 807 vitest + 27 Playwright**。验收中的失败/错误已定位为环境限制与既有全量收集干扰，非 Phase 0 引入的代码回归。

---

## 13. HFB → HFD Reuse Matrix

| 资产 | 判定 | 理由（证据） |
| --- | --- | --- |
| 数据治理引擎 | **REUSE** | §5 全 IMPLEMENTED |
| Person/Book/Version/Passage | **REUSE** | §4 |
| Evidence/Citation/SourceRef/溯源 | **REUSE** | §4, §8 Q8 |
| 检索 + P4 过滤 | **REUSE** | §6 |
| Reader/Library/Knowledge/Workspace/Workflow/Reports | **REUSE** | §6 |
| RBAC + 治理角色 | **REUSE** | §11 |
| AI Evidence-Gated 网关 | **REUSE**（医学护栏 EXTEND） | §8 |
| 教学（V4 education） | **EXTEND** | §7 |
| 人物档案/展览 | **EXTEND** | §7 |
| 古籍阅读公开化 | **EXTEND** | §7 |
| 内容发布状态机 + 快照 | **NEW** | §8, §10 |
| 医学合规元数据 + 免责链路 | **NEW** | §8 |
| 非遗/媒体资产治理 | **NEW** | §9 |
| 匿名公众门户 | **NEW** | §11 |
| Chronology/Geography | **ADAPT** | DOMAIN-MAP §3 |
| 静态媒体引用 | **DEPRECATE** | §9 |

---

## 14. Gap Register

### P0（阻断公众上线）

| ID | 缺口 | 证据 |
| --- | --- | --- |
| G1 | 医学合规字段全缺；免责声明 0 命中；导出无免责 | §8；grep 0 |
| G2 | 匿名公众访问缺失 | §11.2 |
| G3 | PublishedRepresentation/PublicationSnapshot 缺失 | §8 Q3/Q4/Q5/Q7 |
| G4 | 非遗视频全链无实现 | §9.2 |

### P1（正确性/合规）

| ID | 缺口 | 证据 |
| --- | --- | --- |
| G5 | 统一内容发布状态机 | §8 Q1 |
| G6 | 列表面一致过滤（withdrawn version） | §11.2 |
| G7 | 同人审核互斥 | §11.2 |
| G8 | AI 医疗语境护栏（教育接口无分级限制字段） | `api/v4/education.py` |
| G9 | 免责在导出/打印保留机制 | §6 |

### P2（体验/能力）

| ID | 缺口 | 证据 |
| --- | --- | --- |
| G10 | Chronology DOC_ONLY 未落地 | DOMAIN-MAP §3 |
| G11 | 展览数据静态化不可审计 | §7 |
| G12 | 统一 AuditEvent 视图 | DOMAIN-MAP §1.13 |
| G13 | 媒体字段覆盖 | §9.1 |

### P3（工程/环境）

| ID | 缺口 | 证据 |
| --- | --- | --- |
| G14 | pytest E2E 依赖 MinIO/ES；/ready 全量检查超 10s 窗口 | §12.3 |
| G15 | mypy CI 门禁既有 8 errors | §12.2 |
| G16 | apps/backend/tests 收集失败（ModuleNotFoundError: app，不在基线内） | §12.4 |
| G17 | 全量单进程收集干扰（tests/e2e 同进程引发 fixture 级联） | §12.4 |

---

## 15. 3+1 Vertical Slice Feasibility

| 切片 | 可行性 | 依据 |
| --- | --- | --- |
| **古籍条文** | **高** — 代码与测试链最完整（Codex 独立复核建议 Phase 1 首条） | `models/passage.py`; `trace_lineage.py`; Playwright V4-SR01/03 |
| **人物事件** | **中** — Person/entity/graph 原语完整；缺 Chronology 数据模型与事件语义（Codex：event domain likely NEW） | `models/person.py`; `0806`（DOC_ONLY） |
| **非遗视频** | **低** — 缺 Media/Video 模型 + 权利链 + 播放器；Codex：rights-complete chain BLOCKED | §9.2 |
| **发布快照** | **低** — 缺 public projection/versioned release/rollback/audit contract；Codex：BLOCKED until public snapshot proven | §8.3 |

---

## 16. Role-chain Feasibility

| 环节 | 可行性 | 证据 |
| --- | --- | --- |
| 录入（create） | ✅ Researcher/Leader | `seed_rbac.py` |
| 编辑（update） | ✅ Researcher/Leader | 同上 |
| 审核（review/approve） | ✅ Reviewer/Academic Admin | `_REVIEWER_PERMS` |
| 发布（publish） | ✅ Leader/Academic Admin | `_LEADER_PERMS` |
| 撤回（withdraw） | ✅ Steering + 内容撤回方法 | `_STEERING_PERMS`; `Version.withdraw` |
| 闭环互斥 | ⚠️ 权限链可表达，无 SoD 强制 | §11.2 |

---

## 17. Blocking Issues（Phase 1 前置条件）

1. **G1 医学合规** — 公众医疗内容上线前必须完成数据/服务/展示/导出四层执行。
2. **G2 匿名访问** — 确定 Visitor 自动绑定策略与公开接口清单。
3. **G3 发布快照** — 先定义 PublishedRepresentation 概念模型（§8.3 分类）。
4. **G4 非遗媒体治理** — 复用 candidate/admission 模板。
5. **G14 测试环境** — MinIO/ES 就绪或 /ready 窗口放宽。
6. **G15 mypy 门禁** — 修复或调整门禁范围。
7. **G7 SoD** — 职责分离约束。

### 17.1 验证边界声明（验收 §17 修正 5）

| 边界 | 本次验证状态 | 未验证项 |
| --- | --- | --- |
| PostgreSQL 真实连接 | ✅ RUNTIME（integration 48 + Playwright 27 对真实 PG） | — |
| 匿名公众访问 | ⚠️ NOT_IMPLEMENTED（接口需 JWT）— 无法运行时验证「匿名草稿泄露」，按**未验证安全**处理 | 匿名读面 |
| 触发器/治理过程（PG） | ✅ ENFORCED（代码+迁移存在）+ TESTED（SQLite 路径）；PG 触发器运行时未逐条触发 | PG 专用 SECURITY DEFINER 过程运行时行为 |
| RBAC 负向路径 | ✅ TESTED（`test_api_rbac.py` 55 独立通过） | 多角色组合 SoD |
| Rights/Media 全链 | ❌ 不存在（§9） | — |
| 医学展示层强制 | ❌ NOT ENFORCED（§8） | — |
| 公开 URI 版本稳定 | ❌ PARTIAL（UUIDv5 trace/哈希稳定；公开 canonical URI 未定义） | — |

---

## 18. Recommended Phase 1 Scope（仅范围建议，不实施）

**继承（REUSE，零开发）**：以 HFB 后端+前端为基座；研究层/证据链/准入晋升链/RBAC/检索/阅读器/工作流原样复用。

**扩展（EXTEND）**：① 匿名 Visitor 读面；② 内容发布状态机覆盖 book/version/person（列表一致过滤）；③ V4 education 医学合规分级与免责返回；④ Chronology 落地。

**新建（NEW）**：① 医学合规元数据 + 免责全链路；② PublishedRepresentation + PublicationSnapshot（§8.3 分类）；③ 非遗/媒体资产治理；④ 匿名公众门户页面。

**验收**：以 §15 的 3+1 切片定义 DoD（古籍条文 = 首条，Codex 独立建议一致）。

**不在 Phase 1**：不迁移框架、不替换治理引擎、不新建统一 Assertion（除非切片验收证明需要）、不做数据迁移。

---

## 19. 审计结论

**CONDITIONAL PASS**（v1.1 复核维持）

进入 Phase 1 前置条件：

1. G1 医学合规方案与四层执行路径确认；
2. G2 匿名访问与 Visitor 绑定策略确认；
3. G3 发布快照概念模型（§8.3）建模决策确认；
4. G4 非遗媒体治理架构（复用 candidate/admission 模板）确认；
5. G14/G15 测试环境与门禁恢复；
6. G7 SoD 约束进入范围并验收。

未满足任一条件前，HFD 不得对公众开放医疗相关内容。

---

## 20. Codex 验收复核（v1.1 追加，回应验收 §17 五项强制修正 + §15 反证表）

### 20.1 交付物缺失的根因与修复（验收 P0 Blocker 1-3）

- **根因**：交付物初版写入 `/Users/likeming/Sites/hfm/docs/audit/`（非 git 工作树），而验收在 `/Users/likeming/Sites/hfb`（唯一 git 工作树）执行并在此查找 → 判定「报告缺失」。
- **修复**：本报告与 `HFD-PHASE0-DOMAIN-MAP.md`（均 v1.1）已置于 `/Users/likeming/Sites/hfb/docs/audit/`，绑定 HEAD `2d98b610a63d2b0347ff5ec7fcd1d598913f3521`（branch main，生成时间 2026-08-27 15:28 CST）。工作树状态：`M docs/12-context/project-state-2026-08-26.md`（审计前既有）+ `docs/audit/` 新增交付。

### 20.2 五项强制修正逐项回应（验收 §17）

| 修正 | 回应 | 位置 |
| --- | --- | --- |
| 1. 提供并锁定两份报告，记录 branch/HEAD/status/时间/证据路径 | ✅ v1.1 头部绑定；§2 记录 | §0/§2（本报告 §2, Domain Map §0） |
| 2. 每个 REUSE/EXTEND/ADAPT/NEW 补 Model→Service→API→Test 或 DB→Query→Frontend 调用链 | ✅ Domain Map §1 全部条目带调用链；§6 资产带证据 | Domain Map §1 |
| 3. SPECIFIED/IMPLEMENTED/ENFORCED/TESTED/RUNTIME 分列，不以文档代 enforcement | ✅ §3.1 分层规则 + 全报告五层标记；DOC_ONLY 项显式标注 | §3.1 |
| 4. 单独说明 publication model / publication snapshot / research replay snapshot 差异 | ✅ §8.3 分类学 | §8.3 |
| 5. 补齐 PostgreSQL/真实 HTTP/匿名/RBAC/rights-media/医学展示层可验证边界 | ✅ §17.1 边界声明（RUNTIME 已验证 vs 未验证） | §17.1 |

### 20.3 验收 §15 Counter-Evidence Register 12 项回应

| # | 反证点 | 本报告处理 |
| --- | --- | --- |
| 1 | Version/VersionRelation/version center 是否被写成「无版本控制」 | 未写；判定 REUSE（Domain Map §1.4） |
| 2 | SourceRef→Evidence→Citation 是否被写成「无证据链」 | 未写；判定 IMPLEMENTED/REUSE（§1.3） |
| 3 | candidate manifest/artifact immutable/hash 是否被写成「无不可变制品」 | 未写；判定 IMPLEMENTED/ENFORCED（§1.12） |
| 4 | admission 三层审批是否被写成「仅一个 published 字段」 | 未写；三级状态机完整记录（§1.8/§5） |
| 5 | production query policy 是否真排除 withdrawn/orphan/candidate | 是（`document_allowed_clause` 实测代码路径，§5） |
| 6 | replay snapshot 是否被误称 publication snapshot 或反之 | 已分离（§8.3 分类学） |
| 7 | Reader 是否误判不存在或因页面存在误判完整古籍发布能力 | 未误判：REUSE（研究版）/ EXTEND（公开版）（§6/§7） |
| 8 | RBAC/跨 workspace/跨项目负向测试是否被忽略 | 未忽略：§11 + `test_api_rbac.py` 等 |
| 9 | rights 字段 vs 完整 Asset rights governance 是否混为一谈 | 已区分：字段 REUSE / 全链 NEW（§9） |
| 10 | AI evidence gate 是否被误判为医疗合规闭环 | 未误判：Evidence-Gated REUSE，医疗合规 NOT ENFORCED（§8/§17.1） |
| 11 | SourceAdmissionAudit/CandidateResourceAudit append-only 是否只引用文档 | 未只引用文档：迁移+触发器+模型+测试（§1.11/§5） |
| 12 | UUID/hash/replay 可复现是否被误判为全部公开 URI 稳定 | 未误判：§17.1 明确公开 URI 未定义 |

### 20.4 测试差异复核记录（验收 §16 P1 修正 3）

见 §12.4：验收环境 PG 沙箱拦截 + 全量单进程收集干扰；本环境（PG 可达）官方分套件基线 **2724 passed / 0 failed / 0 errors**（unit+integration）+ **807 vitest + 27 Playwright**。mypy 8 errors 为既有（G15）。

---

## Terminal Summary

```text
HFD PHASE 0 BASELINE AUDIT v1.1
===============================

Repository: /Users/likeming/Sites/hfb
Branch: main | HEAD: 2d98b610a63d2b0347ff5ec7fcd1d598913f3521
Generated: 2026-08-27 15:28 CST
Working Tree: M docs/12-context/project-state-2026-08-26.md (pre-existing) + docs/audit/ (deliverables)

Verdict: CONDITIONAL PASS
（Codex acceptance BLOCK 根因 = 交付物缺失；已修复并绑定 HEAD，见 §20.1）

Test Baseline (PG-reachable, CI-matching):
  pytest unit+integration  2724 passed / 0 failed / 0 errors (1 deselected real_llm)
  vitest                    807 passed
  vue-tsc / eslint / build / ruff  PASS
  mypy CI gate              8 errors (existing, G15)
  Playwright E2E            27/27 passed (real PG backend)
  pytest E2E                env-limited (MinIO down, G14)

P0 Gaps: G1 medical compliance | G2 anonymous portal | G3 publication snapshot | G4 ICH media governance
Phase 1 Entry: NOT ALLOWED until §19 conditions confirmed
```
