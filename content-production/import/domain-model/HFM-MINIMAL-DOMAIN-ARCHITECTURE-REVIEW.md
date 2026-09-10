# HFM PERSON / WORK / EDITION 最小领域架构梳理报告

**阶段**：MINIMAL_DOMAIN_ARCHITECTURE_REVIEW  
**任务编号**：MDAR-01  
**日期**：2026-09-10  
**审查基线**：
- `HFM_PROD_DOCUMENT_IMPORT=ACCEPTED`
- `DOCUMENT_CONTENT_BASELINE=675`
- `DOCUMENT_STABLE_ID_BASELINE=EXACT_IMPORTED_675_SET`
- `CURRENT_MIGRATION_HEAD=0015`
- `GOVERNANCE`: 只做领域分析，禁止代码修改、禁止写库、禁止导入。

---

## 1. 四类对象的领域实体定义与身份边界 (Identity Boundary)

在 HFM 体系中，必须严格区分三种不同层面的身份标识：
1. **DOMAIN_IDENTITY（知识/概念层）**：反映真实历史人物、作品观念、版本源流的本体身份；
2. **DIGITAL_ASSET_IDENTITY（物理/数字资源层）**：反映客户提供的具体原始文件（如 `HFM-A000533.pdf`、`HFM-A000014.pdf`、SHA256 哈希）；
3. **IMPORT_IDENTITY（工程批次与入库层）**：如 `DOC-HFM-A000003`、`EDITION-HFM-A000533` 等带前缀的持久化唯一键。

### 1.1 PERSON (人物)
- **领域概念**：历史或现代人物主体（历史医家、学者、刻书家、非遗传承人、评论者等）。
- **Identity Boundary (什么构成独立人物)**：
  - **唯一性标准**：以客观历史身份/个人为准。历史人物结合朝代、籍贯、字号与传记（如“皇甫谧”）；现代学者结合所属时代与机构/著述（如“钱超尘”）。
  - **别名与异名隔离**：字、号、尊称（如“士安”、“玄晏先生”）属于 `PERSON_ALIAS`，**严禁分立为不同 PERSON 实体**。
  - **当前数据实测**：17 个人物（`PERSON-HFM-HUANGFUMI` 至 `PERSON-WU-MIANXUE`），涵盖皇甫谧（MAIN）、左思/司马炎/李巨来（RELATED）、黄龙祥/钱超尘（SCHOLAR）、李志锋/刘君奇（INHERITOR）、吴勉学（PRINTER）等。
  - **当前层级**：DOMAIN_IDENTITY，底层映射到 `entities.id`（EntityType.person）。

### 1.2 WORK (作品/著作)
- **领域概念**：抽象的智力创作成果（FRBR Work 级别概念，如《针灸甲乙经》、《帝王世纪》、《高士传》）。
- **Identity Boundary (什么构成独立著作)**：
  - **唯一性标准**：作品的思想与内容本体，**独立于具体载体、刊刻版次、分册形式或出版物形态**。
  - **边界判定**：
    - 《针灸甲乙经》是一部独立古籍著作（WORK）。
    - 现代基于该著作的专著、论文集或研究集成（如《皇甫谧研究集成》编纂物，或丛书《医统正脉全书》）在当前 14 个待评估数据中被赋予了 `WORK_ID`，但其属于现代编纂型著作或丛书，需在 `WORK_TYPE` 上清晰区分（`ancient-work` vs `modern-compilation` vs `series` vs `treatise`）。
  - **当前数据实测**：14 个 WORK（`WORK-JIAYI` 至 `WORK-HUANGFUMI-ZHENJIU`）。

### 1.3 EDITION (版本/刊本/整理本)
- **领域概念**：作品的某一特定物质化版本或文本表达形态（FRBR Expression / Manifestation 级别概念，如“明万历吴勉学刻本”、“清乾隆四库全书本”、“黄龙祥1990年新校本”）。
- **Identity Boundary (什么构成独立版本)**：
  - **规范版本身份**：由（所属著作、时代/刊印时间、刻板/出版机构、校勘整理者）共同决定一个独立版本。
  - **现实数据实测（关键发现）**：
    - 当前待评估的 92 条 `jiayi-editions.csv`（`EDITION-HFM-A000529` ~ `EDITION-HFM-A000621`）在数据结构上**与原始资产文件（ASSET_ID）呈 1:1 映射**！
    - 例如：
      - 明万历五车楼藏板在数据中被拆成了 4 条 EDITION 记录（`EDITION-HFM-A000533` ~ `0536`，分别对应 4 个分册 PDF）；
      - 清光绪行素草堂藏板被拆成了 4 条 EDITION 记录（卷一二、卷三四、卷五-七、卷八-十二）；
      - 清乾隆四库全书本被拆成了 9 条 EDITION 记录（卷一、卷二、卷三……）。
    - **结论**：当前数据源中的 92 个“EDITION”实际上是**分册物理文件（PHYSICAL_VOLUME / FILE_MANIFESTATION）**，混淆了“学理版本（Canonical Edition）”与“物理分册（Volume/Part）”。

### 1.4 DOCUMENT (生产已导入 675 条数据)
- **当前 675 条 DOCUMENT 究竟代表什么？**
  - **不是规范抽象著作 (NOT Work)**；
  - **不是学理版本 (NOT Canonical Edition)**；
  - **它的实质是：受治理的数字文献单元/数字资产容器 (DIGITAL_DOCUMENT_ASSET)**。
- **三重身份划分**：
  - **DOMAIN_IDENTITY**：作为数字馆藏/研究文献的“文献项（Document Item）”，包含 672 篇现代化数字文献（PDF）和 3 篇核心规划/历史整理文档（PLANNING_DOC）。
  - **DIGITAL_ASSET_IDENTITY**：与底层物理文件、页码集合（`source_pages`）、SHA256 哈希完全对应。
  - **IMPORT_IDENTITY**：以 `DOC-HFM-A000xxx` 表达的、已被 `0015` 生产库冻结的不可变长期稳定资产标识。

---

## 2. 最小关系链与图谱验证

### 2.1 理论链路 vs 真实数据链路

理想概念链：
```
PERSON ──[created/edited]──> WORK ──[has_edition]──> EDITION ──[manifested_as]──> DOCUMENT
```

**真实数据检验发现**：
1. **675 个 DOCUMENT 并非全部对应古籍 EDITION**：
   - 675 个 DOCUMENT 中，只有 **92 个** DOCUMENT（古籍分册扫描件）对应 `jiayi-editions.csv`；
   - 剩余 **583 个** DOCUMENT（包含 473 篇学术论文、期刊研究、现代文献、3 篇规划文档），在领域上**属于当代研究文献**。它们**直接引用或研究** WORK（如探讨《针灸甲乙经》），或者研究 PERSON（皇甫谧），并不属于古籍的某个“EDITION”。
2. **EDITION ↔ WORK 归属异常**：
   - `jiayi-editions.csv` 中有 9 个 EDITION 并不属于《针灸甲乙经》（`WORK-JIAYI`）：
     - 4 个《帝王世纪》相关（`EDITION-HFM-A000573~576`）；
     - 1 个《高士传》相关（`EDITION-HFM-A000621`）；
     - 4 个数字代号 PDF（`10023266.pdf` 等）。
   - 现有 92 个 EDITION 在 CSV 中**缺少显式 `WORK_ID` 外键列**（仅在标题中含有书名）。

### 2.2 跨对象必要关系检查

| 关系 | 现实必要性 | 说明 |
| :--- | :--- | :--- |
| **PERSON ↔ WORK** | **必须 (核心)** | 表达作者、整理者、注者、校订者（如 皇甫谧-撰《针灸甲乙经》、吴勉学-辑《医统正脉全书》、黄龙祥-校《黄帝针灸甲乙经新校本》）。 |
| **WORK ↔ EDITION** | **必须 (核心)** | 表达作品与其传世/现代版本的归属关系（1 个 WORK 包含多个 EDITION）。 |
| **EDITION ↔ DOCUMENT** | **必须 (核心)** | 表达版本与其数字数字化文献/扫描资产的关联。 |
| **PERSON ↔ EDITION** | **可选/派生** | 版本层面的刻工、出版商、校勘者。可通过关系表或直接挂接在 EDITION 字段。 |
| **WORK ↔ DOCUMENT** | **必须 (对现代文献)** | 583 篇学术论文不经过古籍 EDITION，而是直接作为“针对 WORK 的研究文献（Research Document）”。 |
| **PERSON ↔ DOCUMENT** | **必须 (对现代文献)** | 论文作者（现代学者）与研究皇甫谧文献之间的关联。 |
| **WORK ↔ WORK** | **次要/延后** | 丛书与子目关系（如《医统正脉全书》包含《针灸甲乙经》），可先通过属性或后论表达。 |
| **EDITION ↔ EDITION** | **已存在字段** | `editions.lineage_parent_edition_id`（自引用源流关系）。 |

---

## 3. 关系基数判断 (Cardinality Analysis)

| 关系对 | 最小领域基数 | 生产现实说明 |
| :--- | :---: | :--- |
| **PERSON : WORK** | **N : M** | - 1 人可创多作（皇甫谧撰《甲乙经》、《帝王世纪》、《高士传》等）；<br>- 1 作可有多人（合作、多编者，如《皇甫谧研究集成》由钱超尘与温长路共同主编；校订者与原作者同列）。 |
| **WORK : EDITION** | **1 : N** | - 1 部著作拥有多个版本（《针灸甲乙经》有明万历本、四库本、现代校本等）；<br>- 严格学理上 1 个独立版本只属于 1 个 WORK（合刻本可分解或通过包含表达）。 |
| **EDITION : DOCUMENT** | **1 : N** *(学理)*<br>**1 : 1** *(现实数据)* | - **学理上 1:N**：一个版本（如四库全书本《甲乙经》）在数字化时拆成了 9 个分册 PDF（卷一~卷十二）。<br>- **当前 CSV 现实 1:1**：当前 92 个 EDITION_ID 与 92 个 DOCUMENT 严格 1:1 绑定（每个分册被当成了一个 EDITION）。 |
| **WORK : DOCUMENT** | **1 : N** *(直接关系)* | - 583 篇现代文献（论文、专论）直接探讨某一部或多部著作，形成 1:N 乃至 N:M 的研究挂载关系。 |
| **PERSON : DOCUMENT** | **N : M** | - 论文作者/整理者与文献的关系。 |

---

## 4. 关系就绪级别分类 (R0 ~ R3)

- **R0（下一批导入前必须具备最小生产结构）**：
  1. `WORK` 基础实体及其 `stable_id` 持久化绑定；
  2. `PERSON` 基础实体及其 `stable_id` 持久化绑定；
  3. `EDITION` 明确关联到 `WORK`（`editions.work_id` 外键约束）；
  4. `EDITION` 与 `DOCUMENT` 的最小关联挂接机制（让 92 个古籍 DOCUMENT 能找到归属）；
  5. 严密保护 675 个 `DOCUMENT.stable_id`，禁止重新导入、重建或覆写。
- **R1（应存在，但不阻塞下一批基础导入）**：
  1. `WORK` 与现代 `DOCUMENT` 的直接关联（583 篇论文归属到研究主题/著作）；
  2. `PERSON_WORK` 角色关联（作者、校勘、辑刻、评价的多对多角色链）；
  3. 学理版本（Canonical Edition）与物理分册（Volume Document）的层次收敛（将 9 个四库本分册聚合为 1 个学理版本）。
- **R2（后续领域知识增强）**：
  1. 丛书与子目关系（`WORK ↔ WORK`，如《医统正脉全书》与《针灸甲乙经》）；
  2. 版本源流继承树（`EDITION.lineage_parent_edition_id`）；
  3. 细粒度页码/断句定位与 Evidence 锚定。
- **R3（暂不建设）**：
  1. 复杂多维学术异说知识图谱、全量本体推理机。

---

## 5. 现有 Schema 支持度检查 (`0015` Migration Head)

| 检查项 | 目标关系 | 现有 Schema 状态 | 详细诊断 |
| :--- | :--- | :---: | :--- |
| 1 | `DOCUMENT.stable_id` | **SUPPORTED** | `documents.stable_id` (VARCHAR 120, UNIQUE) 存在，675 基线已入库。 |
| 2 | `PERSON.stable_id` | **SUPPORTED** | `0015` 已为 `persons` 增加 `stable_id` (UNIQUE)。 |
| 3 | `WORK.stable_id` | **SUPPORTED** | `0015` 已为 `works` 增加 `stable_id` (UNIQUE)。 |
| 4 | `EDITION.stable_id` | **SUPPORTED** | `0015` 已为 `editions` 增加 `stable_id` (UNIQUE)。 |
| 5 | `PERSON` 别名支持 | **SUPPORTED** | `0015` 新增 `person_aliases` 表，支持规范人名多别名挂接。 |
| 6 | `WORK` 关联作者 | **PARTIAL** | `works.author_entity_id` 仅为 1:1 单作者外键（指向 `entities.id`），无法支持合作著作（如钱超尘+温长路主编）或非作者角色（校者/辑者）。 |
| 7 | `EDITION` 关联 `WORK` | **SUPPORTED** | `editions.work_id` (FK → `works.id`, NOT NULL) 存在。但当前待导入的 `jiayi-editions.csv` 中**无此列**。 |
| 8 | `EDITION` 关联 `DOCUMENT` | **MISSING** | 现状：`documents` 表无 `edition_id` 外键（仅有可为空的纯文本 `edition` 字符串）；`editions` 表也无 `document_id` 外键或 `asset_id` 物理关联列！两表之间**缺乏数据库级关联外键**。 |
| 9 | `DOCUMENT` 关联 `WORK` | **MISSING** | 583 篇非版本类的现代研究文献在当前 `documents` 表中没有 `work_id` 列，也无关系表支撑。 |

**总体判定**：`CURRENT_SCHEMA_COMPATIBILITY = PARTIAL`

---

## 6. 17 PERSON / 14 WORK / 92 EDITION 与 675 DOCUMENT 现实数据体检

通过对 normalized 目录下数据的严格实测交叉比对，识别出以下关键事实：

1. **DOCUMENT 覆盖度与分布**：
   - 675 个 DOCUMENT 中，92 个完全对应 `jiayi-editions.csv` 中的 `ASSET_ID`；
   - 剩余 583 个 DOCUMENT 中，473 个为学术论文（`papers.csv`），3 个为规划文档，其余为专论资料；
   - **结论**：DOCUMENT 是异质的（既有古籍影印件，也有现代论文），绝不能强行把所有 DOCUMENT 塞入古籍 EDITION 链条。
2. **EDITION 数据存在分册碎片化 (Multi-part Voluming)**：
   - 92 个 EDITION 中，有 25+ 处明显是“分册/卷册”（例如：五车楼刻本 4 个分册、四库全书本 9 个分册、行素草堂本 4 个分册、江左书林印本 4 个分册）。
   - 当前 `jiayi-editions.csv` 将每个 PDF 文件直接命名为一个 `EDITION-HFM-A000xxx`，造成“版本数虚高（92个）”。
3. **EDITION 跨著作混杂**：
   - 虽命名为 `jiayi-editions.csv`，但内含《帝王世纪》（4 本）、《高士传》（1 本）、数字代号文件（4 本），并非全属《针灸甲乙经》。
   - 当前 CSV 中**缺少 `WORK_ID` 外键列**，若直接导入生产 `editions` 表，必因 `work_id NOT NULL` 约束而报错阻断！
4. **PERSON 与 WORK 角色混淆**：
   - `works.csv` 中的 `AUTHOR_ORIGINAL` 存在复合文本，如“黄甫谧(据B01规划文档;待权威核)”、“钱超尘/温长路主编2011”、“吴勉学(明)辑刊”、“皇甫谧(著者归属有学术争议,待核)”。
   - 单一的 `author_entity_id` 无法承载复合主编、辑刻者及学术争议标注。
5. **同名与身份冲突检查**：
   - 17 个 PERSON 的 `PERSON_ID` 唯一，无重名冲突；
   - 14 个 WORK 的 `WORK_ID` 唯一，无重名冲突；
   - 92 个 EDITION 的 `EDITION_ID` 唯一，无重名冲突；
   - 675 个 DOCUMENT 的 `DOCUMENT_ID` 唯一，与生产库已入库集合 **100% 吻合**。
   - **无 stable_id 冲突**。

---

## 7. DOCUMENT stable_id 特别保护原则

- 675 个 DOCUMENT 的 `stable_id` 已在生产库建立唯一索引（`uq_documents_stable_id`），并与原始文件的 SHA256 及 `source_asset_id` 牢牢锁定。
- 领域模型的抽象演进（无论未来如何定义 Work、Canonical Edition、Volume、Paper）**均不得要求重新生成或修改 `DOC-*` 标识**。
- `DOCUMENT` 始终作为最底层的长期稳定物理/数字文献资产承载层。
- **判定结果**：`DOCUMENT_STABLE_ID_PROTECTED = YES`，`DOCUMENT_IDENTITY_CONFLICT = NO`。

---

## 8. 最小目标领域模型 (MINIMAL_TARGET_DOMAIN_MODEL)

```
                    ┌────────────────────────┐
                    │         PERSON         │
                    │ (17 历史人物/现代学者) │
                    └───────────┬────────────┘
                                │
                   person_work_role (R1)
                   [author/editor/commenter]
                                │
                                ▼
                    ┌────────────────────────┐
                    │          WORK          │
                    │    (14 核心著作/丛书)   │
                    └───────┬────────┬───────┘
                            │        │
               has_edition  │        │  studies_work (R1)
                 [1 : N]    │        │  [1 : N]
                            │        │
                            ▼        │
              ┌──────────────────┐   │
              │     EDITION      │   │
              │ (版本/校勘载体)  │   │
              └─────────┬────────┘   │
                        │            │
            manifested_by            │
                [1 : N]              │
                        │            │
                        ▼            ▼
              ┌──────────────────────────────────┐
              │             DOCUMENT             │
              │  (675 生产基线：数字文献/资产)   │
              │  - 92 古籍分册/数字化件          │
              │  - 583 现代研究论文/文档         │
              └──────────────────────────────────┘
```

### 实体与关系规格表

| ENTITY | PRIMARY_IDENTITY | REQUIRED_RELATIONS | OPTIONAL_RELATIONS | RELATION_CARDINALITY | CURRENT_SCHEMA_SUPPORT | IMPORT_BLOCKING |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: |
| **PERSON** | `stable_id` (`PERSON-*`) | (自洽实体，挂接 `entities.id`) | `person_aliases` | 1:N (别名) | **SUPPORTED** | **NO** (需补 `entities` 记录) |
| **WORK** | `stable_id` (`WORK-*`) | `title` | `author_entity_id` | N:1 (主作者) | **SUPPORTED** | **NO** (需处理作者外键) |
| **EDITION** | `stable_id` (`EDITION-*`) | `work_id`, `edition_name` | `lineage_parent_edition_id` | N:1 (归属著作) | **SUPPORTED** (Schema)<br>**MISSING** (CSV 数据无 `work_id`) | **YES (数据列缺失)** |
| **DOCUMENT** | `stable_id` (`DOC-*`) | `title`, `source_asset_id` | `edition_id`, `work_id` | N:1 | **MISSING** (无外键列) | **NO (已入库冻结)** |

---

## 9. 核心问题回答

> **“如果今天把 17 PERSON、14 WORK、92 EDITION 导入生产库，现有领域关系是否足以保证未来继续演进，而不会迫使我们破坏已经冻结的 675 DOCUMENT 生产基线？”**

**答复**：  
**不能直接导入，但 DOCUMENT 生产基线绝对安全。**  
1. **不会破坏 DOCUMENT 基线**：因为 675 条 DOCUMENT 已经在生产库独立存在，且具备独立的自包含属性（`source_asset_id`, `source_pages`, `sha256`）。未来建立与 PERSON/WORK/EDITION 的连接，只需通过**向前迁移（FORWARD_MIGRATION）**新增可为空外键（如 `documents.edition_id` 或关联表），完全无需改动或重建现有 DOCUMENT 的任何数据行与 `stable_id`。
2. **阻断原因在数据与外键缺失，而非破坏基线**：
   - 生产表 `editions.work_id` 是 **NOT NULL** 的，而 `jiayi-editions.csv` 中**完全没有 `work_id` 这一列**！如果今天强制导入，数据库在插入第一条 EDITION 时就会抛出约束违规异常；
   - 生产表 `persons` 的主键 `entity_id` 引用了 `entities.id`（`RESTRICT` 约束），若未预先在 `entities` 表中注册对应的 Person Entity，PERSON 导入也会被外键阻断；
   - 92 个 EDITION 与 92 个古籍 DOCUMENT 之间在数据库层面尚未建立桥梁列。

因此，必须通过后续规范的转换工具与最小 forward migration 来安全桥接，绝对禁止今天盲目灌入。

---

## 10. 最终裁决与前置需求

**最终裁决**：
```
DOMAIN_MODEL_READINESS=READY_WITH_FORWARD_MIGRATION
```

### REQUIRED_SCHEMA_GAPS (最小 Forward Migration 范围，待后续阶段规划)
1. **DOCUMENT ↔ EDITION 连接桥梁**：
   - 在 `documents` 表中增加 `edition_id` (VARCHAR 36, FK → `editions.id`, nullable=True)；或建立 `edition_documents` 关联表；
2. **DOCUMENT ↔ WORK 连接桥梁 (针对 583 篇现代文献)**：
   - 在 `documents` 表中增加 `work_id` (VARCHAR 36, FK → `works.id`, nullable=True)；
3. *(注意：当前阶段禁止实际编写 migration。)*

### REQUIRED_DATA_GAPS (导入包数据修补需求)
1. **`jiayi-editions.csv` 数据补全**：
   - 必须显式补齐 `WORK_ID`（将 83 个甲乙经版本归入 `WORK-JIAYI`，4 个帝王世纪归入 `WORK-DIWANG-SHIJI`，1 个高士传归入 `WORK-GAOSHIZHUAN`）；
2. **PERSON / WORK 的 `entities` 底座数据生成**：
   - 依照 `entities` 表结构，补齐 17 个人物与 14 个著作的 Entity 注册映射。

---

## 11. 治理与审查结论

```yaml
DOCUMENT_IMPORT_PHASE: CLOSED
DOCUMENT_BASELINE: 675
DOCUMENT_STABLE_ID_PROTECTED: YES

PERSON_COUNT: 17
WORK_COUNT: 14
EDITION_COUNT: 92

DOMAIN_MODEL_READINESS: READY_WITH_FORWARD_MIGRATION
CURRENT_SCHEMA_COMPATIBILITY: PARTIAL
DOCUMENT_IDENTITY_CONFLICT: NO

R0_SCHEMA_GAPS: "documents 表缺少指向 editions.id / works.id 的前向关联外键 (或关联关系表)"
R0_DATA_GAPS: "jiayi-editions.csv 缺失 WORK_ID 外键列；persons/works 导入前缺失 entities 表对应实体底座"
HUMAN_DECISIONS_REQUIRED:
  - "确认 EDITION 是保持与 92 个分册物理文件 1:1 映射，还是聚合为规范学理版本 (Canonical Editions) 并下挂 Volume Documents"
  - "确认 583 篇现代研究论文是否直接挂接 WORK (work_id)"
  - "确认 PERSON:WORK 多对多主编/校订者在最小阶段是否先简化为单一作者"

PERSON_IMPORT_READY: NO
WORK_IMPORT_READY: NO
EDITION_IMPORT_READY: NO

NEXT_ACTION: "等待人工审阅本报告，决策学理版本收敛方案及最小 Forward Migration 规划；随后核查 Pi 真实兼容性"
BLOCKER: "editions.work_id NOT NULL 约束与现有 jiayi-editions.csv 缺失 WORK_ID 列冲突"
STOP: YES
```
