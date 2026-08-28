# HFM Phase 1 ADR-02 — Search Implementation Architecture

- **ADR-ID**: ADR-02
- **Title**: PostgreSQL Native Full-Text and Multi-Dimensional Filtered Search Architecture
- **Status**: `ACCEPTED`
- **Date**: 2026-08-29
- **Governance Baseline**: `29c5b856f221a12bac9de13e1a5043c5d05208e2`
- **Classification**: `PRE_IMPLEMENTATION_BLOCKING` $\rightarrow$ `RESOLVED`
- **Affected Work Packages**: `P1-05` (C Domain Knowledge), `P1-08` (Unified Search), `P1-11` (Public Portal), `P1-12` (Research Experience)

---

## 1. Context (背景)

根据客户需求 (CR-003, CR-009) 与范围定义 (`P1-SEARCH`, 工作包 `P1-08`)，平台必须提供跨 A（人物）、B（文献与思想）、C（《针灸甲乙经》数字知识）、D（非遗传承）四大领域的统一多维检索能力。

检索在 Phase 1 阶段的关键约束包括：
1. **中文古籍与现代学术文本检索**: 支持中文关键词精准匹配、N-gram 分词模糊匹配与多字段元数据（朝代、作者、版本、章节、分类）复合过滤。
2. **严格的发布态与权限过滤**: 公开端检索只能命中已审批发布 (`publication_status = 'PUBLISHED'`) 的内容；研究端检索可在鉴权范围内命中草稿与未公开研究成果。
3. **医学与临床防线 (AB-14, 边界 B-07, `P1-CLINICAL` 拒绝)**: C 域检索仅限历史文献、版本、章节、穴位、经络的客观历史关系定位，**严禁输出任何形式的疾病主配穴处方推荐、临床疗效排序或自动化诊疗建议**。
4. **数据规模事实**: Phase 1 数据集为首批精选典籍版本、史料文献与非遗档案（数据量在数千至数万级记录，文本体积数十 MB 至数百 MB 级别），属于中小型精细化数字人文语料库。

---

## 2. Evidence (现有事实与证据)

1. **现有架构基座 (NPG-003)**: HFM 采用 PostgreSQL 作为规范关系数据库，已具备 `Entity`, `Work`, `Edition`, `Version`, `Passage`, `Evidence`, `Citation` 等规范数据表。
2. **代码库现状 (NPG-003 CAP-011)**: HFM 当前未集成任何搜索引擎客户端，Elasticsearch 仅作为历史 Gemini 提案中的 L3 设想存在。
3. **HFB 检索复用审计 (NPG-004 HFB-007)**: HFB 历史实现中 Elasticsearch 存在与旧版数据模型的严重耦合，且引入了额外的同步队列与集群维护成本。
4. **PostgreSQL 原生能力**: PostgreSQL 内置丰富的全文检索功能（`tsvector`, `tsquery`）以及三元组模糊索引扩展（`pg_trgm` GIN/GiST 索引），在数十万级中文古籍文本片段的毫秒级检索中表现极为优异且稳定。

---

## 3. Options Considered (备选方案评估)

| 方案 | 架构描述 | 额外基础设施 | 事务与发布一致性 | 运维与资源成本 | 风险与综合评价 |
| --- | --- | --- | --- | --- | --- |
| **Option A: PostgreSQL 原生全文检索 + pg_trgm 复合索引 (选定)** | 基于 PostgreSQL 原生 `pg_trgm`（三元组）扩展与 GIN 倒排索引，结合 B-Tree 权限过滤复合索引。 | **无**（完全复用主数据库） | **强一致性**（发布与撤回原子生效，零同步延迟） | 最低（无需额外内存与进程监控） | **最简充分，完美契合 Phase 1 数据规模与一致性要求** |
| **Option B: 独立 Elasticsearch / OpenSearch 集群** | 部署独立 ES/OpenSearch 进程，通过 CDC (Debezium) 或应用层双写实现 DB $\rightarrow$ ES 数据同步。 | 引入 Java/ES 集群、Logstash/Sync 管道 | **最终一致性**（存在同步延迟，撤回下架存在滞后泄漏风险） | 极高（需至少 2~4GB 内存开销及独立集群运维） | 过度设计，违背最简架构原则，增加故障点 |
| **Option C: 内存搜索引擎 (如 Meilisearch / SQLite FTS5)** | 引入轻量级搜索服务或嵌入式 FTS 引擎。 | 需维护额外服务进程或同步机制 | 弱一致性 | 中等 | 相比 Postgres 无明显优势，增加了系统组件 |

---

## 4. Decision (决策内容)

**决定采用 Option A：基于 PostgreSQL 原生全文检索能力 (`pg_trgm` 扩展 + GIN 倒排索引 + 复合 B-Tree 索引) 实现 Phase 1 统一检索体系。**

1. **技术实现机制 (Search Implementation Mechanism)**:
   - 启用 PostgreSQL 的 `pg_trgm` 扩展。
   - 在典籍片段表 (`passages`)、人物档案表 (`persons`)、文献版本表 (`works`/`editions`)、非遗表 (`heritage_projects`) 上，对文本内容与标题字段建立 `gin (column gin_trgm_ops)` 倒排索引。
   - 配合建立 `(publication_status, is_active, rights_status)` 的复合 B-Tree 索引，确保多维过滤与全文检索的高性能联动。
2. **双层检索隔离策略 (Dual-Layer Query Scoping)**:
   - **公开检索服务 (`PublicSearchService`)**: 强制在 SQL 查询谓词中硬编码注入：
     ```sql
     WHERE publication_status = 'PUBLISHED' 
       AND rights_status IN ('PUBLIC', 'AUTHORIZED') 
       AND is_active = TRUE
     ```
   - **研究检索服务 (`ResearchSearchService`)**: 支持根据当前登录研究员身份 (`user_id`) 检索私有草稿、研究笔记以及授权的研究态非公开资料。
3. **典籍阅读器深度联动 (Reader & Evidence Linkage)**:
   - 检索结果直接返回精准定位元数据：`(work_id, edition_id, version_id, passage_id, locator_type, locator_value)`。
   - 前端点击检索结果即可直接在典籍阅读器 (`P1-READER`) 中加载对应版本的正文片段与学术证据链 (`P1-EVIDENCE`)，保证学术引用与查阅的无缝贯通。
4. **绝对医学安全防线 (Absolute Medical Safety Guard)**:
   - C 域检索处理器仅执行纯文本与关系映射查询，严禁根据症状关键词进行任何加权推荐或自动化穴位组合处方计算。

---

## 5. Rationale (决策理由)

1. **零新增基础设施依赖**: 无需额外部署与维护 JVM/Elasticsearch 节点，极大减轻校方或示范中心的基础设施开销与运维复杂度。
2. **秒级下架与撤回事务保障 (AB-07)**: 当内容审核员执行发布撤回（Withdrawal）时，PostgreSQL 在单事务内提交更新，公开检索即刻无法检索到该内容，完全杜绝因搜索引擎同步延迟导致的违规内容残留泄漏。
3. **原生关系关联查询**: 检索服务可直接与实体（Entity）、证据（Evidence）、版本（Version）表进行高效 SQL JOIN，直接输出富证据元数据，无需在跨系统间来回反查组装。

---

## 6. Consequences (决策影响)

### 正向影响 (Positive)
- 架构极度纯粹精简，开发与测试体验极佳。
- 保证 100% ACID 事务一致性，发布与撤回状态绝对可靠。
- 降低服务器硬件配置门槛，2核4G 标准服务器即可轻松支撑 Phase 1 需求。

### 负向影响与权衡 (Trade-offs & Mitigations)
- **极限超大规模搜索能力受限**: 若文本数据量达到数千万条或需要极复杂的模糊词干分析，PostgreSQL 性能不及分布式专用集群。
  - *缓解措施*: Phase 1 数据体量完全处于 PostgreSQL 最佳性能区间；定义了清晰的升格触发指标。

---

## 7. Required Guards (必须执行的架构守卫)

1. **Guard-01 (公开过滤强制注入)**: 公开检索 DAO/Repository 必须具有代码级静态断言或自动化测试保护，严禁任何未带发布状态过滤的查询执行。
2. **Guard-02 (禁止临床排序)**: 检索排序规则仅允许按相关度 (`similarity`)、年代时间戳 (`dynasty_order` / `publication_year`) 或文献流变层级排序，**绝对禁止按临床疗效评分或主次穴推荐度排序**。
3. **Guard-03 (高亮与片段防越权)**: 检索高亮摘要生成逻辑只能在已被确认授权的内容片段上运行，严禁在预生成阶段泄露未发布段落。

---

## 8. Acceptance Tests (验收测试矩阵)

| 测试用例 ID | 测试目标 | 验证方法 | 预期结果 |
| --- | --- | --- | --- |
| `TEST-ADR02-01` | 中文关键词检索准确性 | 检索《针灸甲乙经》特定穴位名称（如“合谷”）或病证词条 | 毫秒级返回包含精准版本与片段定位的结果列表 |
| `TEST-ADR02-02` | 未发布内容检索隔离性 | 创建草稿状态文献，调用公开检索接口查询其唯一标题 | 返回命中数为 0，零数据泄漏 |
| `TEST-ADR02-03` | 下架撤回即时生效性 | 将已发布文献撤回（WITHDRAW），立即执行公开检索 | 结果即刻消失，命中数为 0 |
| `TEST-ADR02-04` | 负向医学防线拦截 | 模拟输入“胃痛推荐针灸处方”，检查检索结果结构 | 仅返回包含“胃痛”的历史古籍文本引文，无任何“处方推荐”或“主配穴建议”字段 |

---

## 9. Reversal & Escalation Conditions (反转与升格条件)

出现以下任一指标且有真实基准测试证据时，可立项评估引入专用搜索引擎（如 Elasticsearch）：
1. 典籍文本片段总量突破 **500,000 条** 且全文检索 p99 延迟在并发 100 QPS 下持续超过 **200ms**。
2. 明确提出跨语种（如梵文、藏文、西夏文等复杂古文字及多语言对照）的特殊分词与音义多重检索需求。

---

## 10. Affected Work Packages (受影响工作包)

- **P1-05**: 《针灸甲乙经》数字知识体系。
- **P1-08**: 统一策略检索（Unified Search）。
- **P1-11**: 公开门户。
- **P1-12**: 研究工作台。
