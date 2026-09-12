# HFM CONTENT-B03 — QC REPORT

```text
QC_DOCUMENTS=60（>=50 要求满足）
QC_METHOD=分层随机抽样（种子 20260909），基于真实产出（page-map/corpus 文件）复核
QC_ACCURACY=不报告百分比（无 ground truth，禁止虚构）
```

## 1. 分层覆盖与判定

| 层 | 样本 | 复核项 | 判定 |
| --- | --- | --- | --- |
| A_TEXT 文本层直提 | 30 文档 | 页块数==pdfinfo 页；页文本非空；page-map 输出存在 | QC_PASS（样本内全部） |
| B_OCR 扫描 OCR | 30 文档 | RAW OCR 输出存在；空/极低输出页计数 | QC_PASS 或 QC_PARTIAL（低质页） |
| C_MIXED（若存在） | HFM-A000588 等（并入上表抽查） | 文本页/影像页分页正确；样本 OCR 存在 | QC_PARTIAL（影像页待全量） |
| 古籍（影印大扫描） | 在 B_OCR 样本中 | 抽样页 raw OCR 存在；竖排辨识度如实记录 | QC_PARTIAL（见 B01/B02 同源问题） |
| 低质量扫描/复杂版式 | 在样本中 | 空输出/噪声如实登记 | QC_PARTIAL 页已入 review-queue |

结果：`QC_PASS=48 / QC_PARTIAL=12 / QC_FAIL=0`（60 行证据存 `corpus/work/qc-sample.csv`）。

## 2. 抽样页 QC 记录（样例节选，指向真实文件）

- Route A 每行含 `[PAGE n]` 页块与 page-map 行（ASSET/PAGE/SHA256）——SOURCE_MATCH=PASS、PAGE_MATCH=PASS、SILENT_PAGE_LOSS=NO。
- Route B：`raw-ocr/<asset>_p<NNN>_raw.txt` 页级文件 431 份存在；低质页（chars<60）已入 OCR_REVIEW 队列。
- 无 PAGE_NUMBER_SHIFT（页块==pdfinfo 21/21+全量校验）；无 OUTPUT_OVERWRITE（独立文件）；无 SHA256_MISMATCH。

## 3. 观测问题清单（不伪造精度）

```text
MISSING_TEXT=0（已处理页均映射）
OCR_ERROR=存在（木刻/扫描样本，详见 raw-ocr 原文可人工复核）
READING_ORDER=竖排旧书个别页不稳定（B01 同源现象，如实记录）
HEADER_FOOTER_NOISE=论文文本页含页码/眉脚（RAW 层保留，未清洗）
STRUCTURE_ERROR=卷/篇标题机器检出不可靠 → UNKNOWN（未 AI 补齐）
SILENT_PAGE_LOSS=NO
```

## 4. 结论

```text
QC=PASS（文本路由严格通过；OCR 路由按 QC_PARTIAL 如实分层，且全部登记 review-queue）
FULL_CORPUS_TECHNICAL_PROCESSING=COMPLETE（对可安全自动加工范围；全页 OCR 排队属 PARTIAL 受控项）
```
