# HFM CONTENT-B02 — QC REPORT

```text
BATCH=HFM-CONTENT-B02 (CONTROLLED_SCALE)
BATCH_TOTAL=50 PDFs
TOTAL_PAGES=6,027
```

## 1. QC 集（>=10 文档 / >=30 页）

| 覆盖类型 | 文档 | 页 | 验证方式 | 判定 |
| --- | --- | --- | --- | --- |
| clean digital PDF / 学术论文（Route A） | 21 | 61（全量逐页） | pdfinfo 页数 == 抽取页块（21/21）；逐页非空映射；page-map 完整 | QC_PASS |
| 期刊论文复杂排版（Route A 内两栏论文） | 见上（正文两栏样本 6 篇 / 22 页） | 22 | 页级文本连续、无跨页丢失；抽取确定性复测一致 | QC_PASS |
| old-book scan（版本影印，Route B） | 4 | 20（抽样：首页+25/50/75%+末页） | tesseract chi_tra_vert RAW OCR；**无 ground truth，不做字符级精度** | QC_PARTIAL |
| heritage 扫描件（证书/证明，Route B） | 12 | 12（首页全量） | tesseract chi_sim+eng RAW OCR | QC_PARTIAL（打印件好、手写/照片页差） |
| low-quality/手写页 | 见 heritage（A000627 等） | 3 | OCR 空输出或 <80 字 | QC_FAIL（页级，见失败队列） |
| mixed PDF | 0 | — | 本批 50 个文档按整文特征分类无 MIXED（无 10≤pp<150 且有文本层者）；逐页路由在 B02 无触发 | N/A（如实记录） |

QC 统计：`QC_DOCUMENTS=22`（6 RouteA 复核 + 16 OCR），`QC_PAGES=54`（22+32）。

## 2. 观测问题（不虚构精度）

```text
MISSING_TEXT=0（Route A 全部页映射成功，无静默丢页）
WRONG_CHARACTERS=OCR 木刻/证书页存在（无 ground truth，不量化；见 raw-ocr 原文可人工复核）
WRONG_READING_ORDER=旧书竖排 psm6 跨栏串读个别页（B01 同源现象）
HEADER_FOOTER_NOISE=论文页存在页眉/页码噪声（未去除，保留 RAW 层）
PAGE_MAPPING_ERROR=0（修正后 Route A 21/21；OCR 页 32/32 记录到 page-map）
LAYOUT_FAILURE=旧书影印竖排为主（tesseract 局限，见 B01 QC）
UNREADABLE_REGION=3 页（OCR 输出 <80 字或空：A000627 p1、A000671 p1、A000676 p1 等，已在 processing-failures.csv 登记）
```

## 3. 结论

```text
QC_PASS=PASS（Route A 文本层直提与页级映射）
QC_PARTIAL=PASS-with-notes（OCR 路由全部如实标注；raw-ocr 层保留）
QC_FAIL=页级 3 项（登记失败队列，非文档级丢失）
OCR_ACCURACY=未报告百分比（无 ground truth，禁止虚构）
```
