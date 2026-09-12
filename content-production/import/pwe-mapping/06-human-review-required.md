# HFM 待裁决 EDITION 人工审查包 (Human Decision Package)

**阶段**：DATA_MAPPING_AND_IMPORT_TOOLING_DESIGN  
**任务编号**：DMIT-01  
**状态**：STAGING_ARTIFACT（仅供人工审查裁决，非生产导入授权）  
**总审查项数**：5 项（1 项 AMBIGUOUS，4 项 UNRESOLVED）

---

## 一、概述

在 92 条 EDITION 数据中，经标题与文献线索匹配，87 条与古籍著作（82 篇《针灸甲乙经》、4 篇《帝王世纪》、1 篇《高士传》）具有高置信度（HIGH_CONFIDENCE_INFERENCE）关联。

本人工裁决包专门针对无法通过自动化规则直接确立映射关系的 **5 条特殊记录**：
- **A000541**：四书合刊本，存在多作品归属歧义（AMBIGUOUS）；
- **A000529 ~ A000532**：纯数字编号扫描件，无书名文本线索（UNRESOLVED）。

---

## 二、逐项核查与裁决方案

### 1. ASSET_ID: HFM-A000541 (EDITION-HFM-A000541)

- **CURRENT_METADATA**：
  - `EDITION_ID`: `EDITION-HFM-A000541`
  - `TITLE`: `《针灸甲乙经、伤寒论、金匮要略、温病学》精译.pdf`
  - `EDITION_TYPE`: `UNKNOWN`
  - `PAGES`: 913
  - `DOCUMENT_ID`: `DOC-HFM-A000541` (已导入生产库)
- **AVAILABLE_EVIDENCE**：
  - 标题明确包含四部独立医学经典：《针灸甲乙经》（皇甫谧）、《伤寒论》（张仲景）、《金匮要略》（张仲景）、《温病学》（明清温病学派）；
  - 全书达 913 页，属于现代中医学经典综合精译或合订教材。
- **CANDIDATE_WORKS**：
  - `WORK-JIAYI`（针灸甲乙经）
  - `WORK-COLLECTION`（暂未建：四部经典合集/丛书）
  - 独立现代编译著作（未在 14 WORK 范畴内）
- **OPTION_ANALYSIS**：
  - **方案 A（指定主作品）**：强行将 `work_id` 设为 `WORK-JIAYI`。
    - *风险*：在学术与版本学理上严重失真，将一本包含伤寒、金匮、温病的合刊文献定性为《针灸甲乙经》的单纯刊本，未来如果引入张仲景或伤寒论，会造成版本归属冲突。
  - **方案 B（当前阶段延后，推荐）**：将该 EDITION 标记为 `DEFERRED`，本轮 R0 不导入 `editions` 生产表。保留生产库中的 `DOC-HFM-A000541` 作为基础资产。
    - *收益*：完全符合 R0 最小范围要求，不破坏 14 WORK 和 675 DOCUMENT，不需要临时创建不存在的复合 WORK。
  - **方案 C（建立 compound/collection work）**：在 `works` 中新增《中医经典四书精译》或复合 Work。
    - *风险*：突破了当前经过严密治理冻结的 14 WORK 基线，违反本次审查边界。
- **RECOMMENDED_DECISION**：`DEFER` (方案 B)
- **RECOMMENDATION_CONFIDENCE**：`HIGH`
- **ALTERNATIVE**：若业务必须挂载，可临时挂接 `WORK-JIAYI`，但必须在 `RELATION_NOTE` 中显式注明 `COLLECTION_PRIMARY_JIAYI_ONLY`。
- **RISK_IF_WRONG**：若强行归入《甲乙经》，污染版本谱系；若延后，仅延迟该单一版本的关联，生产库 DOCUMENT 不受影响。
- **HUMAN_DECISION_REQUIRED**：`YES`

---

### 2. ASSET_ID: HFM-A000529 (EDITION-HFM-A000529)

- **CURRENT_METADATA**：
  - `EDITION_ID`: `EDITION-HFM-A000529`
  - `TITLE`: `10023266.pdf`
  - `EDITION_TYPE`: `UNKNOWN`
  - `PAGES`: 243
  - `DOCUMENT_ID`: `DOC-HFM-A000529`
- **AVAILABLE_EVIDENCE**：
  - 仅有数字文件名 `10023266.pdf`（通常为超星/读秀等数字图书馆内部条码/图书控制号）；
  - 提取文本中无明确经书书名证据，缺乏 OCR 目录或书名页考证报告。
- **CANDIDATE_WORKS**：`UNRESOLVED`
- **RECOMMENDED_DECISION**：`DEFER`
- **RECOMMENDATION_CONFIDENCE**：`HIGH`
- **ALTERNATIVE**：安排离线人工查验 `10023266.pdf` 扉页及版权页，获得真实书名后再行归属。
- **RISK_IF_WRONG**：严禁根据数字文件名臆测或因位于 `jiayi` 批次目录下强行赋予 `WORK-JIAYI`，否则会导致不可逆的数据污染。
- **HUMAN_DECISION_REQUIRED**：`YES`

---

### 3. ASSET_ID: HFM-A000530 (EDITION-HFM-A000530)

- **CURRENT_METADATA**：
  - `EDITION_ID`: `EDITION-HFM-A000530`
  - `TITLE`: `10023267.pdf`
  - `EDITION_TYPE`: `UNKNOWN`
  - `PAGES`: 159
  - `DOCUMENT_ID`: `DOC-HFM-A000530`
- **AVAILABLE_EVIDENCE**：
  - 仅有数字文件名 `10023267.pdf`，与 A000529 疑似为同批次数字馆藏序号连续文件（10023266 / 10023267）。
- **CANDIDATE_WORKS**：`UNRESOLVED`
- **RECOMMENDED_DECISION**：`DEFER`
- **RECOMMENDATION_CONFIDENCE**：`HIGH`
- **ALTERNATIVE**：等待离线抽检版权页并补充元数据。
- **RISK_IF_WRONG**：盲目归属将产生虚假版本关联。
- **HUMAN_DECISION_REQUIRED**：`YES`

---

### 4. ASSET_ID: HFM-A000531 (EDITION-HFM-A000531)

- **CURRENT_METADATA**：
  - `EDITION_ID`: `EDITION-HFM-A000531`
  - `TITLE`: `10023268.pdf`
  - `EDITION_TYPE`: `UNKNOWN`
  - `PAGES`: 156
  - `DOCUMENT_ID`: `DOC-HFM-A000531`
- **AVAILABLE_EVIDENCE**：
  - 仅有数字文件名 `10023268.pdf`，连续编号第三册。
- **CANDIDATE_WORKS**：`UNRESOLVED`
- **RECOMMENDED_DECISION**：`DEFER`
- **RECOMMENDATION_CONFIDENCE**：`HIGH`
- **ALTERNATIVE**：等待离线抽检版权页。
- **RISK_IF_WRONG**：盲目归属将产生虚假版本关联。
- **HUMAN_DECISION_REQUIRED**：`YES`

---

### 5. ASSET_ID: HFM-A000532 (EDITION-HFM-A000532)

- **CURRENT_METADATA**：
  - `EDITION_ID`: `EDITION-HFM-A000532`
  - `TITLE`: `10023609.pdf`
  - `EDITION_TYPE`: `UNKNOWN`
  - `PAGES`: 354
  - `DOCUMENT_ID`: `DOC-HFM-A000532`
- **AVAILABLE_EVIDENCE**：
  - 仅有数字文件名 `10023609.pdf`。
- **CANDIDATE_WORKS**：`UNRESOLVED`
- **RECOMMENDED_DECISION**：`DEFER`
- **RECOMMENDATION_CONFIDENCE**：`HIGH`
- **ALTERNATIVE**：等待离线抽检版权页。
- **RISK_IF_WRONG**：盲目归属将产生虚假版本关联。
- **HUMAN_DECISION_REQUIRED**：`YES`

---

## 三、人工裁决登记汇总表 (Staging Decision Form)

| 资产标识 | 原始文件名 | 候选著作 | 推荐裁决 | 审查状态 | 人工签署 (Sign-off) | 最终决定 (Final Decision) |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| `HFM-A000541` | 《针灸甲乙经、伤寒论、金匮要略、温病学》精译.pdf | `WORK-JIAYI` / 复合 | **DEFER** | `REVIEW_REQUIRED` | `[ 待签署 ]` | `[ 待人工选择 A/B/C ]` |
| `HFM-A000529` | 10023266.pdf | 无 | **DEFER** | `DEFERRED` | `[ 待签署 ]` | `[ 待核实版权页 ]` |
| `HFM-A000530` | 10023267.pdf | 无 | **DEFER** | `DEFERRED` | `[ 待签署 ]` | `[ 待核实版权页 ]` |
| `HFM-A000531` | 10023268.pdf | 无 | **DEFER** | `DEFERRED` | `[ 待签署 ]` | `[ 待核实版权页 ]` |
| `HFM-A000532` | 10023609.pdf | 无 | **DEFER** | `DEFERRED` | `[ 待签署 ]` | `[ 待核实版权页 ]` |
