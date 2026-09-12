# HFM 独立架构审计报告（2026-09-13）

> 本报告为独立穿透式审计，基于代码、生产库 `hfm_prod` 实测、测试套件实跑，
> 不依赖既有审计文档的结论。与仓库内 `HFM-FULL-ARCHITECTURE-AUDIT.md`（2026-09-10）
> 并列，本报告对其做两处修正与若干补充（见第 5 节）。

## 0. 执行摘要

```text
HFM_INDEPENDENT_AUDIT=PASS_WITH_GAPS

SOFTWARE_DELIVERY_SCOPE=COMPLETE            # 可本地运行，软件闭环成立
CONTENT_PRODUCTION_SCOPE=NOT_COMPLETE       # 全文 / 知识对象 / 发布流水线均空
ARCHITECTURE_HEALTH=PASS_WITH_GAPS
DATA_BASELINE_HEALTH=PASS                   # 675/31/17/14/87，0 Orphan、0 断裂 FK
PUBLIC_PORTAL=PARTIAL                       # UI 完整，但生产数据未发布，依赖静态降级
RESEARCH_WORKSPACE=PARTIAL                  # 项目+笔记闭环成立，标注/证据链缺失
PUBLICATION_READINESS=NOT_READY
UI_CONTENT_PROPAGATION_READINESS=NOT_READY

R0=0  R1=3  R2=5  R3=1  R4=1
BLOCKER=NONE
```

**一句话结论**：工程底座与权威元数据基线已建成且质量高，但“数据 → 公众展示”
的最后一步发布流水线从未通水，知识图谱层与全文层基本为空。

---

## 1. 审计方法与证据来源

| 维度 | 方法 | 结果 |
| :--- | :--- | :--- |
| 代码结构 | `find` 目录树、`grep` 路由/服务/模型 | 后端 101 `.py`（~12,095 行）；前端 20 视图 + 18 E2E spec |
| 数据库 | `psql -d hfm_prod` 逐表 `count(*)`、`\d` 结构、FK 约束 | 见第 3 节 |
| 测试 | 实际运行后端 pytest、前端 vitest | 后端 565 passed / 0 failed；前端 262 passed / 0 failed |
| 内容流水线 | 目录盘存 + ledger/CSV 抽样 | 见第 4 节 |

---

## 2. 已完成功能（实证）

### 2.1 后端工程底座（apps/backend）

- 技术栈：FastAPI + SQLAlchemy Async + PostgreSQL 17，`requires-python >=3.12`。
- Alembic 迁移 `0001`–`0015`，head = `0015`；ORM 模型与数据库 schema 一致。
- 完整 API 面（`src/hfm/api/v1/phase1.py`，1081 行路由实现）：

| 前缀 | 能力 |
| :--- | :--- |
| `/api/v1/auth` | login / logout / change-password |
| `/api/v1/public` | home / works / works/{id}/editions / works/{id}/structure / persons / heritage / c-terms / media / search / reader/resolve |
| `/api/v1/research` | persons / works / editions / versions / chapters / passages / c-terms / c-relations / heritage / artifacts / evidence-chain / projects / notes |
| `/api/v1/admin` | users / role / search / reconciliation / audit-log / lineage / publication review·publish·withdraw |

### 2.2 认证与权限（真实可用）

- scrypt 加盐哈希（stdlib，无新依赖）；HMAC 签名无状态 token，携带 `token_version`，
  登出/改密即失效。
- RBAC：5 角色（`SYSTEM_ADMIN` / `CONTENT_REVIEWER` / `SCHOLAR_RESEARCHER` /
  `STUDENT_RESEARCHER` / `ANONYMOUS_VISITOR`）、34 权限、默认拒绝。
- 密码策略单一来源：≥12 位、禁默认口令、禁含用户名。
- 研究工作台写入 owner 隔离：`owner_id` 永不接受客户端传入（防 IDOR），权限 + 归属双重校验。

### 2.3 前端门户（apps/frontend）

- Vue 3 + Vite，20 个视图路由：公众 15 + 研究 3（ResearchHome / Search / Entity）+ 管理 2（AdminHome / AuditLog）。
- 公众页面真实调用 `/api/v1/public/*`（persons / works / work-detail / search / reader / media / home），
  并带**优雅降级**：后端无已发布数据时回退到静态权威基线（`src/data/*.ts`，共 ~2,489 行），页面永不空白。
- 路由守卫：公众匿名只读；研究/管理要求鉴权 + 角色匹配（deny-by-default）。

### 2.4 研究工作台闭环（真实读写）

- `POST/GET /api/v1/research/projects`、`/notes` 真实入库并读回。
- 前端 `ResearchWorkspacePanel.vue` 已接通创建/列表（`createResearchProject` / `createResearchNote`）。
- 权限分角色：project 仅学者（`research:project:*`）；note 学生 + 学者（`research:note:*`）。

### 2.5 元数据基线（生产库实测）

```
documents      675   （PDF 672 + PLANNING_DOC 3；100% 携带 source_asset_id + source_sha256）
entities       31
persons        17
person_aliases 1
works          14
editions       87
数据完整性      PASS（0 Orphan、0 断裂 FK、无重复风险）
```

### 2.6 治理 / 门禁 / 部署骨架

- Phase2：负面边界守卫（禁 clinical / AI / 3D / VR / HFB 运行时耦合）、媒体版权模型
  （字节哈希绑定、S3 元数据）、导出服务、可追溯性、契约校验、范围校验。
- `infra/`：nginx `.example`、systemd `.example`、release-gate / golden-runtime-gate /
  health-check 等脚本；`.github/workflows/release-gate.yml`；生产环境预检脚本
  （`validate-production-env.py`、`check-secrets.py` 等）。

---

## 3. 生产数据库全表实测（hfm_prod, alembic head = 0015）

| 表 | 行数 | 表 | 行数 |
| :--- | :--- | :--- | :--- |
| documents | **675** | c_domain_terms | **0** |
| entities | **31** | c_domain_relations | **0** |
| persons | **17** | assertions | **0** |
| person_aliases | **1** | evidences | **0** |
| works | **14** | citations | **0** |
| editions | **87** | events | **0** |
| versions | **0** | event_assertions / event_relations | **0** |
| chapters | **0** | institutions | **0** |
| passages | **0** | sources | **0** |
| media_assets | **0** | source_refs | **0** |
| heritage_projects | **0** | publication_records | **0** |
| heritage_relations | **0** | content_artifacts | **0** |
| research_projects | **0** | reconciliation_runs | **0** |
| research_notes | **0** | audit_log | **0** |
| users | **1**（SYSTEM_ADMIN） | roles / role_permissions | 5 / 34 |

关键分布：

- `documents.review_status`：675 全为 `NEEDS_REVIEW`（无一进入可发布状态）。
- `documents.processing_status`：`SUCCESS` 544 / `PARTIAL` 131。
- `documents.doc_type`：`PDF` 672 / `PLANNING_DOC` 3。

---

## 4. 内容生产流水线现状（盘存）

| 阶段 | 目录 | 状态 |
| :--- | :--- | :--- |
| 01 分类 | `01-classification/content-classification.csv` | 有 |
| 02 元数据 | `02-metadata/content-object-map.csv` | 有 |
| 03 文本抽取 | `03-text-extraction/` | **空（0 文件）** |
| 04 实体 | `04-entities/` | **空** |
| 05 关系 | `05-relations/` | **空** |
| 06 媒体 | `06-media/` | **空** |
| 07 审核 | `07-review/rights-review.csv` | 有 |
| 08 批准 | `08-approved/` | **空** |
| 09 导入包 | `09-import-packages/` | **空** |

关键事实：

- `corpus/extracted-text/`、`corpus/raw-ocr/`、`corpus/rendered-pages/`、
  `batches/*/extracted-text/`、`batches/*/raw-ocr/` **磁盘上均为 0 文件**
  （这些目录在 `.gitignore` 中被排除，但实际为空——全文抽取未真正落地）。
- `corpus/document-production-ledger.csv`：613 条 B03 + 49 条 B02 + 5 条 B01，
  ledger 中记录了 `TEXT_OUTPUT` 路径，但对应文件不存在。
- `normalized/` 已有候选数据但未进库：
  - `knowledge-object-candidates.csv`：26 个穴点候选（合谷等）
  - `evidence.csv`：24 条证据候选
  - `papers.csv`：473 篇论文元数据
  - `jiayi-structure.csv`：空（仅表头）
  - `citations-candidates.csv`：空（仅表头）

---

## 5. 缺口（按严重性）

### R1 — 阻断“生产数据 → 公众展示”的最后一步（3 项）

| ID | 缺口 | 实证 | 影响 |
| :--- | :--- | :--- | :--- |
| R1-1 | 发布流水线为空 | `publication_records`=0、`content_artifacts`=0 | 公共 API 全部返回空；前端只能静态降级 |
| R1-2 | **sources 注册表断开（本报告新增）** | `content_artifacts.source_id` → `sources(id)` ON DELETE RESTRICT，但 `sources`=0 行；675 篇 `documents` 只带 `source_asset_id`，与 `sources` 无关联 | 即使想发布，须先补 `sources` 行，否则工件创建被 FK 拒绝 |
| R1-3 | 675 篇文献全部未审 | `review_status` 全为 `NEEDS_REVIEW` | 无一篇可进入发布状态 |

### R2 — 结构化知识与全文层（模型有、数据无）（5 项）

| ID | 缺口 | 实证 |
| :--- | :--- | :--- |
| R2-1 | 正文/篇章/段落为空 | `chapters`=0、`passages`=0；磁盘抽取产物目录全空 |
| R2-2 | 中医知识图谱为空 | `c_domain_terms`=0、`c_domain_relations`=0（26 穴点候选未进库） |
| R2-3 | 证据链/断言/引文为空 | `assertions`/`evidences`/`citations`/`events` 全 0 |
| R2-4 | 非遗/媒体为空 | `heritage_projects`=0、`media_assets`=0（前端非遗为静态映射） |
| R2-5 | `versions`=0 | 87 为 editions；“具体文本版本”这一 FRBR 层未启用 |

### R3 — 研究工作台范围有限（1 项）

- 目前只有项目 + 笔记闭环；未提供对 675 篇文献的在线全文阅读 + 高亮标注 + 引文生成链路。
  后端端点已具备（`POST /persons/{id}/assertions`、`evidence-chain` 等），但前端无交互界面，
  且无正文可标注。

### R4 — 部署仍为“本地可运行”形态（1 项）

- 无公网域名/证书/生产服务器；nginx、systemd 仅为 `.example`；`hfm_prod` 为本机库，非生产实例。

---

## 6. 对既有审计文档的修正与补充

1. **修正“文本抽取未入库”**：既有 `HFM-FULL-ARCHITECTURE-AUDIT.md` 表述为“未入库”，
   实际更严重——磁盘抽取产物目录本身是空的（`corpus/extracted-text`、`batches/*/extracted-text`
   均 0 文件）。即全文处理尚未真正执行，而非“执行了没入库”。

2. **补充 `sources` 注册表脱节**：既有文档未识别到 `sources` 表（0 行）与
   `documents.source_asset_id`（675 行全有）的脱节——这是发布流水线的隐藏前置阻断，
   因为 `content_artifacts.source_id` 的 RESTRICT 外键会拒绝没有 `sources` 行的工件。

---

## 7. 结论与建议

```text
下一阶段唯一正确路径 = CONTROLLED_CONTENT_ADMISSION_AND_PUBLICATION

前置条件：
  1. 先修复 sources 注册表脱节（documents.source_asset_id → sources 建立受控注册）。
  2. 执行全文抽取（当前磁盘产物为空，需真实跑 OCR/文本提取并落盘）。
  3. 对 675 篇文献完成 review（RIGHTS / 合规复核）。
  4. 生成 ContentArtifact + PUBLISHED PublicationRecord。

退出条件：
  - /api/v1/public/home 与 /works 稳定返回真实生产数据。
  - 零数据泄露（草稿/私有数据严格隐匿）。

禁止范围：
  - 不改冻结的 PWE 映射基线与导入逻辑。
  - 不直接开放外网 PUBLICATION。
  - 不在授权前改动前端 UI 渲染逻辑。

AUTO_START=FORBIDDEN
EXPLICIT_USER_AUTHORIZATION_REQUIRED=YES
```

**审计角色**：独立架构审计（只读、基于事实、穿透式全量审计）
**审计日期**：2026-09-13
**分支 / HEAD**：`hfm-canonical` @ `603c420`
