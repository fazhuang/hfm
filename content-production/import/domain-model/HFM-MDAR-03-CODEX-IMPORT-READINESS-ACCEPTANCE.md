# HFM MDAR-03 Codex Import Readiness Acceptance

**阶段**：MINIMAL_DOMAIN_ARCHITECTURE_REVIEW  
**性质**：独立只读验收  
**日期**：2026-09-10  
**验收基线**：`5c7253dfd088c64fc991e951f04d196cb3ae1d74`，`hfm_prod`，Alembic `0015`

## 1. 结论

MDAR-03 通过：当前缺口已被准确界定。`0015` schema 足以承载下一阶段的 PERSON、WORK 与 EDITION 基础对象导入；本轮没有发现需要先行创建 R0 migration 的真实 schema blocker。下一阶段必须是数据映射与导入 tooling 设计，不是导入授权。

675 DOCUMENT 基线保持独立、不可重导、不可重建 stable ID。对其建立更丰富关系属于后续 R1/R2 演进，不是当前 P/W/E 基础导入的前置条件。

## 2. 独立核查范围与方法

已直接复核：

- `HFM-MINIMAL-DOMAIN-ARCHITECTURE-REVIEW.md` 与 `HFM-MDAR-02-REALITY-COMPATIBILITY-AUDIT.md`；
- `persons`、`works`、`editions`、`documents`、`entities`、`person_aliases` 的 ORM、迁移与实际 PostgreSQL 元数据；
- 只读 `hfm_prod`：`alembic_version=0015`，`entities=0`、`persons=0`、`works=0`、`editions=0`、`documents=675`；
- `normalized/persons.csv`（17，identity 唯一）、`works.csv`（14，identity 唯一）、`jiayi-editions.csv`（92，identity 唯一）；
- 当前 B05 0015 contract 与 `content-production/import` tooling。

当前唯一可定位的导入工具是 DOCUMENTS 的 `hfm_import_documents.py`（另有旧 guarded runner）。未发现 PERSON、WORK 或 EDITION 的 import entrypoint、dry-run、batch audit 或实体 bootstrap 路径。

## 3. Schema Gate

实际数据库与 ORM 均确认：

| 事实 | 独立结论 |
| --- | --- |
| `persons.entity_id` | 非空、主键，FK 至 `entities.id`，`RESTRICT`；必须先有 entity，但不需要新 schema。 |
| `works.entity_id` / `author_entity_id` | 均可空 FK；基础 WORK 导入可不压缩有争议的多角色作者关系。 |
| `editions.work_id` | 非空 FK 至 `works.id`，`CASCADE`；符合当前最小模型，必须以已确认 WORK 映射填入。 |
| stable IDs | PERSON/WORK/EDITION 都有 nullable unique `stable_id`；可用于安全重跑/冲突检测的实现基础已存在。 |
| `person_aliases` | 已存在，FK 至 person，适合与 PERSON importer 的 entity→person→alias 链路一并处理。 |
| DOCUMENT 关系 | `documents` 没有 `work_id`/`edition_id`。这不阻止 P/W/E 基础对象导入，且不应要求修改已冻结的 675 行。 |

`editions.work_id NOT NULL` 是正确的 R0 完整性约束：应补足数据映射，而不是放宽约束。当前没有 document→work 或 document→edition FK 也不构成 R0 blocker；92 个资产层对应和 583 个独立现代文献都不需要在本轮写成领域 FK。`person_work_role` 的 N:M、角色语义与争议保留应在 R1 设计，不能被压缩为当前的单一 `author_entity_id`。

**Schema verdict**

```text
R0_SCHEMA_GAP_CONFIRMED=NONE
FORWARD_MIGRATION_REQUIRED_BEFORE_DATA_REPAIR=NO
DOCUMENT_RELATION_SCHEMA_R0_REQUIRED=NO
PERSON_WORK_ROLE_SCHEMA_R0_REQUIRED=NO
IMMEDIATE_FORWARD_MIGRATION=NOT_REQUIRED
```

## 4. Data Gate — 92 EDITION 与 WORK 归属

`jiayi-editions.csv` 有 92 条，表头没有 `WORK_ID`；其 `RELATION_BASIS` 为空、`RELATION_NOTE` 为 `UNKNOWN`。因此标题命中不能升级为已经确认的生产事实。

| 分类 | 数量 | 验收判断 |
| --- | ---: | --- |
| EDITION_TOTAL | 92 | 已核对 |
| EDITION_EXPLICIT_WORK_ID | 0 | 无直接 source FK |
| EDITION_DETERMINISTIC_WORK_MAPPING | 0 | 无可直接写库的显式映射 |
| HIGH_CONFIDENCE_INFERENCE | 87 | 标题唯一命中：甲乙经 82、帝王世纪 4、高士传 1；仍须被正式映射产物确认，不能以标题直接写为事实。 |
| EDITION_AMBIGUOUS | 1 | `A000541` 为《针灸甲乙经、伤寒论、金匮要略、温病学》合刊。 |
| EDITION_UNRESOLVED | 4 | `A000529`–`A000532` 仅有数字文件名，缺少著录证据。 |

重点对象的源数据均没有 `WORK_ID`：

- `A000541`：多书合刊，需要决定单一主 WORK、合刊/丛书处理，或将其延后；
- `A000529`、`A000530`、`A000531`、`A000532`：`10023266.pdf`、`10023267.pdf`、`10023268.pdf`、`10023609.pdf`，无可用著录证据。

因 `editions.work_id` 是非空 FK，92 个可写 `work_id` 值必须作为下一阶段可审计 mapping artifact 产生；不得把 87 条高置信标题推断直接当作已确认生产关系。

## 5. Human Decision Gate

```text
HUMAN_DECISION_A000541=REQUIRED
HUMAN_DECISION_A000529_532=REQUIRED
PERSON_ROLE_DECISION_BLOCKS_PERSON_IMPORT=NO
EDITION_1_TO_1_POLICY_ACCEPTABLE=YES_FOR_R0_AS_ASSET_LEVEL_FILE_MANIFESTATION
```

PERSON 的基础对象导入不依赖先裁决所有 PERSON↔WORK 角色：现有 `author_entity_id` 可为空，不能承担多作者、主编、辑刻、校订或争议。R0 应保留原始角色文本与证据，不把不确定关系写成单作者事实；完整的 `person_work_role` 由 R1 处理。

92 条保持 1:1 资产单元可以作为 R0 的导入策略，但不得宣称它们已经是最终 canonical edition 模型。后续 canonical edition/volume 聚合仍是 R2 演进。

## 6. Import Tooling Gate

| 能力 | 事实 | 结论 |
| --- | --- | --- |
| PERSON_IMPORTER_EXISTS | 未发现 | TOOLING_MISSING |
| WORK_IMPORTER_EXISTS | 未发现 | TOOLING_MISSING |
| EDITION_IMPORTER_EXISTS | 未发现 | TOOLING_MISSING |
| ENTITY_BOOTSTRAP_SUPPORTED | 未发现创建 `entities` 后再写 PERSON/WORK 的路径 | TOOLING_MISSING |
| IDEMPOTENCY_SUPPORTED | DOCUMENTS 工具存在；P/W/E 无实现 | TOOLING_MISSING for P/W/E |
| DRY_RUN_SUPPORTED | DOCUMENTS 有既有证明；P/W/E 无实现 | TOOLING_MISSING for P/W/E |
| TRANSACTION_ROLLBACK_SUPPORTED | DOCUMENTS 有既有证明；P/W/E 无实现 | TOOLING_MISSING for P/W/E |
| AUDIT_REPORT_SUPPORTED | DOCUMENTS 有既有证明；P/W/E 无实现 | TOOLING_MISSING for P/W/E |

不能以“可临时写脚本”代替可验收 importer。后续设计至少须定义 entity bootstrap 顺序、输入 manifest、映射审阅状态、唯一/重复策略、单事务/失败回滚、dry-run 和机器可读 reconciliation。

## 7. Ready State 与唯一下一阶段

```text
PERSON_IMPORT_READY=NO
WORK_IMPORT_READY=NO
EDITION_IMPORT_READY=NO

R0_DATA_GAPS=ENTITY_BOOTSTRAP_31_ROWS;EDITION_WORK_ID_92_VALUES
R0_TOOLING_GAPS=NO_PWE_IMPORT_TOOLING
R0_HUMAN_DECISIONS=A000541;A000529_A000532;ROLE_TEXT_PRESERVATION;WORK_TYPE_REVIEW

NEXT_PHASE=DATA_MAPPING_AND_IMPORT_TOOLING_DESIGN
NEXT_AUTHORIZED_ACTION=DESIGN_AND_REVIEW_PWE_MAPPING_AND_IMPORT_TOOLING_WITHOUT_HFM_PROD_WRITES
```

选择 PATH_A。PATH_B 不适用，因为不存在必须先行修复的 R0 schema gap；PATH_C 不适用，因为最小模型足以表达基础对象并保留 R1/R2 关系演进；PATH_D 不适用，因为三个 importer 都尚未 ready。

## 8. Frozen Boundaries

```text
DOCUMENT_BASELINE_PROTECTED=YES
DOCUMENT_IDENTITY_CONFLICT=NO
DOCUMENT_REIMPORT=FORBIDDEN
DOCUMENT_STABLE_ID_REBUILD=FORBIDDEN

PERSON_IMPORT=UNAUTHORIZED
WORK_IMPORT=UNAUTHORIZED
EDITION_IMPORT=UNAUTHORIZED
PUBLICATION=UNAUTHORIZED
UI_CONTENT_PROPAGATION=UNAUTHORIZED
```

本验收未修改代码、CSV、migration、importer 或 `hfm_prod`，也未执行 P/W/E import、publication 或 UI propagation。

MDAR03_ACCEPTANCE=PASS

DOCUMENT_BASELINE_PROTECTED=YES
DOCUMENT_IDENTITY_CONFLICT=NO

DOMAIN_MODEL_MINIMUM_SUFFICIENT=YES
CURRENT_SCHEMA_R0_SUFFICIENT=YES

R0_SCHEMA_GAPS=NONE
R0_DATA_GAPS=ENTITY_BOOTSTRAP_31_ROWS;EDITION_WORK_ID_92_VALUES
R0_TOOLING_GAPS=NO_PWE_IMPORT_TOOLING
R0_HUMAN_DECISIONS=A000541;A000529_A000532;ROLE_TEXT_PRESERVATION;WORK_TYPE_REVIEW

IMMEDIATE_FORWARD_MIGRATION=NOT_REQUIRED

PERSON_IMPORT_READY=NO
WORK_IMPORT_READY=NO
EDITION_IMPORT_READY=NO

NEXT_PHASE=DATA_MAPPING_AND_IMPORT_TOOLING_DESIGN
NEXT_AUTHORIZED_ACTION=DESIGN_AND_REVIEW_PWE_MAPPING_AND_IMPORT_TOOLING_WITHOUT_HFM_PROD_WRITES

PERSON_IMPORT=UNAUTHORIZED
WORK_IMPORT=UNAUTHORIZED
EDITION_IMPORT=UNAUTHORIZED
PUBLICATION=UNAUTHORIZED
UI_CONTENT_PROPAGATION=UNAUTHORIZED

BLOCKER=EDITION_WORK_ID_DATA_GAP;PERSON_ENTITY_BOOTSTRAP_GAP;NO_PWE_IMPORT_TOOLING
STOP=YES
