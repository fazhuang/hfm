# HFM 待裁决 EDITION 最终人工确认签批单 (HUMAN-DECISION-SHEET)

**阶段**：DATA_MAPPING_AND_IMPORT_TOOLING_DESIGN  
**任务编号**：DMIT-02  
**日期**：2026-09-10  
**审查原则**：严禁依据推测强行确认，证据不足一律 DEFER，不影响生产已冻结的 675 DOCUMENT 资产。

---

## 一、特殊待裁决记录审议详情

### 1. ASSET_ID: HFM-A000541 (EDITION-HFM-A000541)

- **当前元数据**：
  - `EDITION_ID`: `EDITION-HFM-A000541`
  - `TITLE`: `《针灸甲乙经、伤寒论、金匮要略、温病学》精译.pdf`
  - `PAGES`: 913
  - `DOCUMENT_ID`: `DOC-HFM-A000541` (已在 675 基线中安全持久化)
- **事实与证据复核**：
  - 该书汇集汉代张仲景《伤寒论》《金匮要略》、魏晋皇甫谧《针灸甲乙经》以及明清《温病学》四部独立中医学经典；
  - 属于典型的现代综合性中医四大经典合编/合刊；
  - 当前 R0 数据库模型 `editions.work_id` 为单一非空外键（1:N），无法支持多作品合刊表达。
- **裁决建议**：
  - **RECOMMENDATION**: `DEFER_RECOMMENDED`
  - **建议审查状态**: 维持 `DEFERRED`（不进入本次 R0 `editions` 表导入集）。
  - **架构与学理理由**：强行挂靠单一 `WORK-JIAYI` 会造成学术失真与版本源流污染；延后处理该版本不破坏任何已有外键，675 DOCUMENT 资产保持完整。
- **签批栏**：
  - [ ] 同意建议：维持 DEFER，延后至多对多合刊关系支持后再行处理（推荐）
  - [ ] 方案调整：以《针灸甲乙经》为主作品强制挂靠（注明合刊附录）
  - **签署人 / 日期**：__________________ / 2026-09-____

---

### 2. ASSET_ID: HFM-A000529 (EDITION-HFM-A000529)

- **当前元数据**：
  - `EDITION_ID`: `EDITION-HFM-A000529`
  - `TITLE`: `10023266.pdf`
  - `PAGES`: 243
  - `DOCUMENT_ID`: `DOC-HFM-A000529` (已在 675 基线中安全持久化)
- **事实与证据复核**：
  - 文件名为纯数字图书馆条码编号 `10023266.pdf`；
  - 虽放置于 `jiayi` 收集目录中，但当前缺乏文本 OCR 提取报告及版权页扫描考证，无直接书名与版本题跋证据；
  - 严守“不得根据数字文件名猜测”的治理红线。
- **裁决建议**：
  - **RECOMMENDATION**: `DEFER_RECOMMENDED`
  - **建议审查状态**: 维持 `DEFERRED`。
  - **理由**：证据不足，坚决不猜测。待线下复核版权页后补充录入。
- **签批栏**：
  - [ ] 同意建议：维持 DEFER，等待离线版权页核验
  - **签署人 / 日期**：__________________ / 2026-09-____

---

### 3. ASSET_ID: HFM-A000530 (EDITION-HFM-A000530)

- **当前元数据**：
  - `EDITION_ID`: `EDITION-HFM-A000530`
  - `TITLE`: `10023267.pdf`
  - `PAGES`: 159
  - `DOCUMENT_ID`: `DOC-HFM-A000530`
- **裁决建议**：
  - **RECOMMENDATION**: `DEFER_RECOMMENDED`
  - **建议审查状态**: 维持 `DEFERRED`。
- **签批栏**：
  - [ ] 同意建议：维持 DEFER，等待离线版权页核验
  - **签署人 / 日期**：__________________ / 2026-09-____

---

### 4. ASSET_ID: HFM-A000531 (EDITION-HFM-A000531)

- **当前元数据**：
  - `EDITION_ID`: `EDITION-HFM-A000531`
  - `TITLE`: `10023268.pdf`
  - `PAGES`: 156
  - `DOCUMENT_ID`: `DOC-HFM-A000531`
- **裁决建议**：
  - **RECOMMENDATION**: `DEFER_RECOMMENDED`
  - **建议审查状态**: 维持 `DEFERRED`。
- **签批栏**：
  - [ ] 同意建议：维持 DEFER，等待离线版权页核验
  - **签署人 / 日期**：__________________ / 2026-09-____

---

### 5. ASSET_ID: HFM-A000532 (EDITION-HFM-A000532)

- **当前元数据**：
  - `EDITION_ID`: `EDITION-HFM-A000532`
  - `TITLE`: `10023609.pdf`
  - `PAGES`: 354
  - `DOCUMENT_ID`: `DOC-HFM-A000532`
- **裁决建议**：
  - **RECOMMENDATION**: `DEFER_RECOMMENDED`
  - **建议审查状态**: 维持 `DEFERRED`。
- **签批栏**：
  - [ ] 同意建议：维持 DEFER，等待离线版权页核验
  - **签署人 / 日期**：__________________ / 2026-09-____

---

## 二、人工签批汇总表

| 记录标识 (Stable ID) | 原始标题 (Title) | 歧义度 (Ambiguity) | 复核建议 (Recommendation) | 建议最终状态 (Target Status) | 治理签署 (Approval Sign-off) |
| :--- | :--- | :---: | :---: | :---: | :---: |
| `EDITION-HFM-A000541` | 《针灸甲乙经、伤寒论、金匮要略、温病学》精译.pdf | HIGH (合刊四书) | **DEFER_RECOMMENDED** | `DEFERRED` | `[ 待签批 ]` |
| `EDITION-HFM-A000529` | 10023266.pdf | HIGH (纯数字文件名) | **DEFER_RECOMMENDED** | `DEFERRED` | `[ 待签批 ]` |
| `EDITION-HFM-A000530` | 10023267.pdf | HIGH (纯数字文件名) | **DEFER_RECOMMENDED** | `DEFERRED` | `[ 待签批 ]` |
| `EDITION-HFM-A000531` | 10023268.pdf | HIGH (纯数字文件名) | **DEFER_RECOMMENDED** | `DEFERRED` | `[ 待签批 ]` |
| `EDITION-HFM-A000532` | 10023609.pdf | HIGH (纯数字文件名) | **DEFER_RECOMMENDED** | `DEFERRED` | `[ 待签批 ]` |
