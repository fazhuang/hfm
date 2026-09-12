# HFM PERSON / WORK / EDITION 数据映射契约 (PWE-MAPPING-CONTRACT)

**契约编号**：HFM-PWE-MAPPING-CONTRACT-R0  
**制定日期**：2026-09-10  
**适用阶段**：DATA_MAPPING_AND_IMPORT_TOOLING_DESIGN (DMIT-01)  
**治理约束**：只用于映射定义与审查校验，严禁写入生产库，严禁修改既有 schema。

---

## 1. Stable Identity Policy (稳定身份策略)

1. **DOCUMENT 身份不可逆**：
   - 生产库已导入的 675 个 `DOC-HFM-A000xxx` 构成长期不可变资产身份（`LONG_TERM_STABLE_ASSET_IDENTITY`）。
   - 任何未来 mapping、entity bootstrap 或关系构建，严禁变更、重构或废除既有 DOCUMENT stable_id。
2. **确定性生成原则 (Deterministic ID Generation)**：
   - PERSON stable_id 格式：`PERSON-*`（如 `PERSON-HFM-HUANGFUMI`）。
   - WORK stable_id 格式：`WORK-*`（如 `WORK-JIAYI`）。
   - EDITION stable_id 格式：`EDITION-HFM-A000xxx`。
   - ENTITY stable_id 格式：`ENT-PERSON-*` 或 `ENT-WORK-*`。
   - **严禁使用数据库自增主键（auto-increment id）作为跨环境实体身份**。
   - **严禁运行时随机生成 UUID 作为 stable_id**。

---

## 2. Entity Bootstrap Policy (实体底座策略)

1. **Entity 存在前置条件**：
   - 生产数据库中 `persons.entity_id` 是主键且外键指向 `entities.id`（`RESTRICT` 约束）；`works.entity_id` 唯一且外键指向 `entities.id`。
   - 在向 `persons` 和 `works` 表写入任何记录之前，必须先在 `entities` 表中存在对应行。
2. **31 个 Bootstrap 实体范围冻结**：
   - `TOTAL_BOOTSTRAP_ENTITIES = 31`
   - `PERSON_ENTITY_ROWS = 17`（`entity_type = 'person'`）
   - `WORK_ENTITY_ROWS = 14`（`entity_type = 'work'`）
   - `OTHER_ENTITY_ROWS = 0`
3. **映射表消费规范**：
   - `01-entity-bootstrap.csv` 作为唯一指定底座映射来源。
   - 导入执行器必须在单事务内先执行 Entity Bootstrap，确保所有 FK 约束获得满足。

---

## 3. WORK Identity & Type Review Policy (著作身份与类型策略)

1. **WORK 抽象本体边界**：
   - WORK 代表精神与智力创作成果，独立于具体载体与分册。
2. **Work Type 审核标准**：
   - 每部著作必须具备明确的 `WORK_TYPE`。
   - 审核状态分类：
     - `CONFIRMED`：经权威文献学或既有规范确认的类别；
     - `NEEDS_REVIEW`：已有初步推断，但尚需文献专家核准（如古籍 ancient-work 与论说 treatise 的界限，现代编纂 modern-compilation 的认定）；
     - `UNKNOWN`：完全缺乏依据，禁止盲目入库。
   - 导入工具**严禁为了满足约束自行猜测 work_type**。

---

## 4. EDITION → WORK Mapping Policy (版本挂接策略)

1. **外键强制性 (work_id NOT NULL)**：
   - 生产表 `editions.work_id` 是强约束字段，任何拟导入的 EDITION 必须具有明确合法的 `work_id`。
2. **Mapping 置信度阶梯**：
   - `EXPLICIT`：数据源自带结构化 `WORK_ID`（当前基线为 0）；
   - `HIGH`：由文献标题、正文明确包含书名强推断（当前基线为 87 条）；
   - `AMBIGUOUS`：涉及多作品合刊、复合文献（当前基线为 1 条：A000541）；
   - `UNRESOLVED`：仅有数字编号或文件名，无文本依据（当前基线为 4 条：A000529~532）。
3. **推断限制原则**：
   - 严禁将 `HIGH` 置信度自动伪称为 `EXPLICIT`。

---

## 5. Review State Machine & Human Confirmation Policy (审核状态机与人工确认)

```
             ┌────────────────┐
             │ REVIEW_REQUIRED│
             └───────┬────────┘
                     │ (人工审查)
      ┌──────────────┼──────────────┐
      ▼              ▼              ▼
┌───────────┐  ┌───────────┐  ┌───────────┐
│ CONFIRMED │  │ DEFERRED  │  │ REJECTED  │
└─────┬─────┘  └───────────┘  └───────────┘
      │
      ▼
[ 允许生产导入 ]
```

1. **四态定义**：
   - `REVIEW_REQUIRED`：候选映射已生成，等待人工审查；
   - `CONFIRMED`：经人工专家审查并签署确认；
   - `DEFERRED`：证据不足或当前阶段不具备入库条件，延后处理；
   - `REJECTED`：映射错误或数据无效，予以否决。
2. **核心红线：IMPORTER CONSUMPTION RULE**：
   - `IMPORTER_CONSUMES_ONLY_CONFIRMED_ROWS = YES`
   - 导入工具在读取 mapping artifact 时，必须硬性过滤：`WHERE review_status == 'CONFIRMED'`。
   - `REVIEW_REQUIRED` 记录一律拒绝导入；
   - `DEFERRED` 记录一律跳过；
   - `REJECTED` 记录一律丢弃。
   - **禁止任何程序将 HIGH 置信度直接静默视为 CONFIRMED**。

---

## 6. Deferred Record Policy (延后记录策略)

1. **延后对象边界**：
   - 状态为 `DEFERRED` 的 EDITION 暂不进入 `editions` 生产表。
2. **底层资产零冲击**：
   - 延后记录对应的底层 `DOCUMENT` 记录（如 `DOC-HFM-A000529` 等）已在 675 基线中安全存在，其数字化扫描件与文本提取不受任何影响。
3. **后续补录通道**：
   - 延后记录在后续批次完成人工考证后，仅需将其状态更新为 `CONFIRMED` 并补充对应 `work_id`，即可通过正向追加导入入库。

---

## 7. Duplicate & Conflict Policy (重复与冲突策略)

1. **键唯一性检查**：
   - `entity_stable_id` 必须全局唯一；
   - `person_stable_id` 必须全局唯一；
   - `work_stable_id` 必须全局唯一；
   - `edition_stable_id` 必须全局唯一。
2. **冲突即回滚**：
   - 任何批次若出现 stable_id 重复或外键悬挂，必须整批回滚，禁止部分写入。

---

## 8. Evidence Requirements (证据要求)

1. **PERSON:WORK 关系隔离**：
   - 本阶段 `05-person-work-evidence.csv` 仅作为证据留存；
   - `production_relation_authorized = NO`；
   - 严禁在未经学术审查的情况下，将“主编”、“校订”、“辑刊”、“评价者”直接降维塞入单一的 `works.author_entity_id`。
