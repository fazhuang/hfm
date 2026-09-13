# P6 方案 — 4 条数字文件名 DEFERRED 版本补录（A000529–532）

**任务**：HFM-P6-收尾 · 5 条 DEFERRED 版本补录（其中 4 条单作品版本）
**日期**：2026-09-13
**性质**：补录执行方案 + 人工签批单。**本方案不擅自执行**，签批后按 §5 流程落地。
**证据**：见 `P6-DEFERRED-EDITION-EVIDENCE.md`（四条均 OCR 证实为《针灸甲乙经》）。

---

## 1. 范围与结论

| Edition | 归属 Work | 补录动作 |
| :--- | :--- | :--- |
| `EDITION-HFM-A000529` | `WORK-JIAYI` | DEFERRED → CONFIRMED（+work_id） |
| `EDITION-HFM-A000530` | `WORK-JIAYI` | DEFERRED → CONFIRMED（+work_id） |
| `EDITION-HFM-A000531` | `WORK-JIAYI` | DEFERRED → CONFIRMED（+work_id） |
| `EDITION-HFM-A000532` | `WORK-JIAYI` | DEFERRED → CONFIRMED（+work_id） |

`EDITION-HFM-A000541`（合刊四书）**不纳入本方案**，仍维持 DEFERRED，见《P6-COMPOUND-WORK-DESIGN》。

本方案**不新增** Work、**不改** schema、**不动**迁移头（保持 `0015`）。四条都是单作品版本挂接到已有 `WORK-JIAYI`。

---

## 2. 精确改动清单

### 2.1 `03-edition-work-map.csv`（映射表）

对 A000529–532 四行做如下字段变更（列名不变）：

| 字段 | 现值 | 改为 |
| :--- | :--- | :--- |
| `candidate_work_stable_id` | `UNRESOLVED` | `WORK-JIAYI` |
| `candidate_work_title` | `UNRESOLVED` | `针灸甲乙经` |
| `mapping_basis` | `NUMERIC_FILENAME_NO_TEXTUAL_WORK_EVIDENCE` | `COPYRIGHT_PAGE_OCR_TITLE` |
| `mapping_confidence` | `UNRESOLVED` | `HIGH` |
| `review_status` | `DEFERRED` | `REVIEW_REQUIRED`（待签批 → `CONFIRMED`） |
| `evidence` | 「数字文件名…建议延后」 | 填入 §3 的 OCR 题名证据 |

> 注：`review_status` 先置 `REVIEW_REQUIRED`，经人工签批后置 `CONFIRMED`，严禁程序自行静默提升（治理红线）。

### 2.2 `review/EDITION-CONFIRMATION-REVIEW.csv`（签署表）

对 A000529–532 四行：

| 字段 | 现值 | 改为 |
| :--- | :--- | :--- |
| `recommendation` | `DEFER_RECOMMENDED` | `CONFIRM_RECOMMENDED`（**须人工签批**） |
| `current_status` | `DEFERRED` | `CONFIRMED` |
| `mapping_confidence` | `UNRESOLVED` | `HIGH` |
| `ambiguity` | `HIGH_NO_METADATA` | `NONE` |
| `blocking_issue` | `NUMERIC_FILENAME_NO_TEXTUAL_EVIDENCE` | `NONE` |
| `evidence` | 「…维持 DEFER」 | 填入 §3 OCR 题名证据 + 指向证据卷 |

### 2.3 `hfm_import_pwe.py`（导入器常量）

| 常量 | 现值 | 改为 |
| :--- | :--- | :--- |
| `DEFERRED_EDITION_SET` | 5 项 | 仅保留 `EDITION-HFM-A000541`（删 A000529–532） |
| `EXPECTED_EDITION_CONFIRMED` | `87` | `91` |
| `EXPECTED_EDITION_DEFERRED` | `5` | `1` |
| `EXPECTED_MAPPING_BASELINE_ID` | `077f…4b` | 重新生成（见 §4） |

> `EXPECTED_MIGRATION_HEAD` 保持 `0015`；`FROZEN_DOCUMENT_COUNT` 保持 `675`。

### 2.4 基线 manifest

`MAPPING-BASELINE-MANIFEST.json` 的 `mapping_baseline_id` 与 `inputs[].sha256` 随 2.1/2.2 的 CSV 变更失效，须按 §4 重新生成并回填 2.3 的 `EXPECTED_MAPPING_BASELINE_ID`。

---

## 3. 各条 evidence 文案（回填用）

- **A000529**：`OCR 卷端题名「鐵灸甲乙經卷之一」「精帅五藏第一」（PaddleOCR，见 P6 证据卷）`
- **A000530**：`OCR 序页「新校正黄帝鐵灸甲乙經序」+ 宋臣高保衡/孙奇署名 +「皇甫士」（见 P6 证据卷）`
- **A000531**：`OCR 序页「新校正黄帝鐵灸甲乙經序」+「鐵灸甲乙經目錄卷之一」（见 P6 证据卷）`
- **A000532**：`OCR 正文「经穴总述」「【原文】…（卷二，第一上）（出《灵枢》第十）」（见 P6 证据卷）`

---

## 4. 执行流程（签批后）

```bash
# 0) 前置：人工签批 2.2 的 recommendation=CONFIRM_RECOMMENDED + review_status=CONFIRMED
# 1) 改 03-edition-work-map.csv 与 EDITION-CONFIRMATION-REVIEW.csv（按 §2.1/2.2）
# 2) 改 hfm_import_pwe.py 常量（按 §2.3，先不填新 manifest id）
# 3) 重新生成 manifest（作者态，无 DB 访问）：
python content-production/import/pwe-tooling/hfm_import_pwe.py --write-manifest
#    产出新 MAPPING_BASELINE_ID，回填到 hfm_import_pwe.py 的 EXPECTED_MAPPING_BASELINE_ID
# 4) 只读 dry-run（全量校验 + 预测增量，零写入）：
python content-production/import/pwe-tooling/hfm_import_pwe.py \
  --database-url "$(grep HFM_DATABASE_URL ~/.hfm/secrets/prod.env | cut -d= -f2-)" \
  --dry-run
# 5) 正式 apply（hfm_prod 须显式 --allow-hfm-prod + HFM_ENV=prod）：
HFM_ENV=prod python content-production/import/pwe-tooling/hfm_import_pwe.py \
  --database-url "$(grep HFM_DATABASE_URL ~/.hfm/secrets/prod.env | cut -d= -f2-)" \
  --apply --allow-hfm-prod
```

导入器保证：单事务 all-or-nothing、幂等重跑、FK 有序、exact-set 对账、DOCUMENT 基线保护（675 不变）。

---

## 5. 人工签批单

| Edition | 归属 Work | 签批（同意补录） |
| :--- | :--- | :--- |
| `EDITION-HFM-A000529` | `WORK-JIAYI` 针灸甲乙经 | `[ ] 同意` |
| `EDITION-HFM-A000530` | `WORK-JIAYI` 针灸甲乙经 | `[ ] 同意` |
| `EDITION-HFM-A000531` | `WORK-JIAYI` 针灸甲乙经 | `[ ] 同意` |
| `EDITION-HFM-A000532` | `WORK-JIAYI` 针灸甲乙经 | `[ ] 同意` |

签署人 / 日期：__________________ / 2026-09-____
