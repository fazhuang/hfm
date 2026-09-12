# HFM P/W/E R0 数据映射设计与人工裁决报告

**阶段**：DATA_MAPPING_AND_IMPORT_TOOLING_DESIGN  
**任务编号**：DMIT-01  
**日期**：2026-09-10  
**冻结前提**：
- `MDAR03_ACCEPTANCE=PASS`
- `DOCUMENT_BASELINE=675`
- `DOCUMENT_BASELINE_PROTECTED=YES`
- `DOCUMENT_IDENTITY_CONFLICT=NO`
- `CURRENT_SCHEMA_R0_SUFFICIENT=YES`
- `GOVERNANCE`: 只设计和生成 staging/mapping artifact，禁止创建 0016，禁止写库，禁止导入。

---

## 1. 31 个 Entity Bootstrap 真实数据核验

Codex 指出的 `ENTITY_BOOTSTRAP_31_ROWS` 经本次实测完全核实，其精确组成如下：

- **PERSON_ENTITY_ROWS = 17**：
  来自 `content-production/normalized/persons.csv` 中的全部 17 位独立人物（包含皇甫谧、吴勉学、黄龙祥、钱超尘等）。
  映射至 `entity_type = 'person'`，`entity_stable_id` 按确定性规则命名为 `ENT-PERSON-*`。
- **WORK_ENTITY_ROWS = 14**：
  来自 `content-production/normalized/works.csv` 中的全部 14 部独立著作/丛书（包含《针灸甲乙经》、《帝王世纪》、《高士传》等）。
  映射至 `entity_type = 'work'`，`entity_stable_id` 按确定性规则命名为 `ENT-WORK-*`。
- **OTHER_ENTITY_ROWS = 0**：
  无其他混入类型。
- **核验结论**：
  `ENTITY_BOOTSTRAP_TOTAL = 31`，构成 `persons` 与 `works` 生产表外键（`entity_id FK -> entities.id`）的最小闭合底座。

---

## 2. 14 WORK 规范映射与类型审查 (WORK_TYPE_REVIEW)

在 `02-work-canonical-map.csv` 中对全部 14 部著作进行了规范提取。遵循“不得为了完成 mapping 猜测 work_type”的原则：
- **NEEDS_REVIEW (13 部)**：
  - 古典著作 5 部（《针灸甲乙经》、《帝王世纪》、《高士传》、《列女传》、《逸士传》）标记为 `ancient-work`；
  - 论说文 3 部（《玄守论》、《释劝论》、《笃终论》）标记为 `treatise`；
  - 序文 1 部（《三都赋序》）标记为 `preface`（存在学术归属争议）；
  - 丛书 1 部（《医统正脉全书》）标记为 `series`；
  - 现代专著/编纂 3 部（《皇甫谧研究集成》、《皇甫谧遗著集》、《皇甫谧针灸》）标记为 `modern-compilation` / `modern-book`；
  - 上述类型虽有初步推断依据，但按照严格治理规则，均标定为 `NEEDS_REVIEW`，等待文献学专家确认。
- **UNKNOWN (1 部)**：
  - `WORK-XUANYANCHUNQIU`（《玄晏春秋》），在原始数据中标记为 `UNKNOWN`（未见直接来源），依规则保持 `UNKNOWN`，严禁猜测。
- **CONFIRMED (0 部)**：
  - 尚未经人工签字确认，当前基线为 0。

---

## 3. 92 EDITION → WORK 映射与置信度分布

在 `03-edition-work-map.csv` 中对全部 92 条版本记录进行逐行建档：
- **TOTAL = 92**
- **EXPLICIT = 0**：原始 CSV 均无显式 `WORK_ID` 外键列。
- **HIGH (87 条)**：
  - 82 条明确指向《针灸甲乙经》（`WORK-JIAYI`）；
  - 4 条明确指向《帝王世纪》（`WORK-DIWANG-SHIJI`）；
  - 1 条明确指向《高士传》（`WORK-GAOSHIZHUAN`）。
  - *严格执行治理红线：87 条 HIGH 全部标定为 `REVIEW_REQUIRED`，严禁伪称为 EXPLICIT 或直接 CONFIRMED。*
- **AMBIGUOUS (1 条)**：
  - `HFM-A000541`（《针灸甲乙经、伤寒论、金匮要略、温病学》精译），多部经典合刊。
- **UNRESOLVED (4 条)**：
  - `HFM-A000529` ~ `HFM-A000532`（纯数字编号扫描件，无书名文本依据）。

---

## 4. 5 条待裁决记录的人工审查包 (06-human-review-required.md)

已完成详细案卷整理，核心推荐如下：
1. **A000541**：推荐方案 B（`RECOMMENDED_DECISION = DEFER`）。
   - 避免在 R0 阶段强行将四书合刊归属为《甲乙经》单本，亦无需临时扩充复合 Work。
   - 生产库 `DOC-HFM-A000541` 资产安全，不受影响。
2. **A000529 ~ A000532**：全部给出 `RECOMMENDED_DECISION = DEFER`。
   - 坚决杜绝根据数字文件名和批次目录主观臆测。
   - 待离线查验版权页后补录。

---

## 5. PERSON 数据映射与关系解耦

- **PERSON 基础身份**：
  17 位人物在 `04-person-identity-map.csv` 中全部完成结构化提取，身份清晰无重名（`PERSON_MAPPING_TOTAL = 17`）。全部待人工终审（`REVIEW_REQUIRED`）。
- **PERSON:WORK 关系解耦**：
  在 `05-person-work-evidence.csv` 中抽离出 22 条人物-著作证据关系，全部打标为 `production_relation_authorized = NO`。
  严禁将多主编（如钱超尘、温长路）、辑刻者（吴勉学）、校注者（黄龙祥、王军）或评价者（司马炎）盲目降维导入单一作者列。

---

## 6. 部分导入架构安全性分析 (Architectural Feasibility Analysis)

**问题**：若未来 PERSON 17/17、WORK 14/14、EDITION 87/92 获得 CONFIRMED，5 条 EDITION 延后（DEFERRED），是否允许执行部分导入？

**架构裁决**：
```
PARTIAL_EDITION_IMPORT_ARCHITECTURALLY_SAFE = YES
```

**RATIONALE（架构支撑理由）**：
1. **外键单向性与可空性**：
   - 领域依赖方向为 `EDITION -> WORK`（`editions.work_id` 为 NOT NULL 外键，指向 `works.id`）。
   - `works` 表对 `editions` **没有任何外键依赖**。
   - 生产表 `documents` 当前版本**没有针对 `editions` 的外键约束**。
2. **零悬挂与事务完整性**：
   - 只要拟导入的 87 个 EDITION 所引用的 WORK（`WORK-JIAYI`, `WORK-DIWANG-SHIJI`, `WORK-GAOSHIZHUAN`）已在前面步骤全量确认入库，这 87 个 EDITION 即可完全自洽地写入 `editions` 表。
   - 5 条 DEFERRED 的 EDITION 不写入数据库，不会引起任何数据库约束报错，也不会使已导入的 675 个 DOCUMENT 产生任何孤儿记录或数据不一致。
3. **完全向后兼容演进**：
   - 未来人工核实 5 条延后记录后，直接作为新批次追加 `INSERT INTO editions` 即可，完全满足增量向前迁移原则。

---

## 7. 生成的 Staging / Mapping Artifact 清单

所有文件已在目录 `content-production/import/pwe-mapping/` 就绪：
1. `01-entity-bootstrap.csv`：31 个基础 Entity 映射（17 Person + 14 Work）；
2. `02-work-canonical-map.csv`：14 部著作规范映射与类型审核态；
3. `03-edition-work-map.csv`：92 个版本的 Work 挂接、置信度与状态；
4. `04-person-identity-map.csv`：17 个人物身份与别名映射；
5. `05-person-work-evidence.csv`：22 条学术证据记录（严格非生产授权）；
6. `06-human-review-required.md`：5 条待裁决记录的深度分析与裁决表单；
7. `PWE-MAPPING-CONTRACT.md`：严格冻结消费逻辑的数据映射契约；
8. `DMIT-01-REPORT.md`：本治理报告。

---

## 8. 治理与指标汇总

```yaml
ENTITY_BOOTSTRAP_TOTAL: 31
PERSON_ENTITY_ROWS: 17
WORK_ENTITY_ROWS: 14

PERSON_MAPPING_TOTAL: 17
PERSON_MAPPING_CONFIRMED: 0
PERSON_MAPPING_REVIEW_REQUIRED: 17

WORK_MAPPING_TOTAL: 14
WORK_MAPPING_CONFIRMED: 0
WORK_MAPPING_REVIEW_REQUIRED: 14

EDITION_MAPPING_TOTAL: 92
EDITION_MAPPING_CONFIRMED: 0
EDITION_MAPPING_REVIEW_REQUIRED: 88
EDITION_MAPPING_DEFERRED: 4
EDITION_MAPPING_REJECTED: 0

A000541_STATUS: REVIEW_REQUIRED (RECOMMEND_DEFER)
A000529_STATUS: DEFERRED
A000530_STATUS: DEFERRED
A000531_STATUS: DEFERRED
A000532_STATUS: DEFERRED

MAPPING_CONTRACT_COMPLETE: YES
IMPORTER_CONSUMES_ONLY_CONFIRMED_ROWS: YES

PARTIAL_EDITION_IMPORT_ARCHITECTURALLY_SAFE: YES

R0_MAPPING_BLOCKERS: NONE (Artifacts就绪，处于正常审查流)
HUMAN_DECISIONS_REMAINING: 5

NEXT_RECOMMENDED_ACTION: "人工审查 06-human-review-required.md 并签署 5 条特殊裁决，同时对 87 条高置信度版本和 14/17 P/W 进行 CONFIRMED 状态签署"
BLOCKER: NONE
STOP: YES
```
