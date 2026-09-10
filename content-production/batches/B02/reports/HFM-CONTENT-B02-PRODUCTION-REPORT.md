# HFM CONTENT-B02 — PRODUCTION REPORT（CONTROLLED_SCALE）

## 1. 方法

```text
SOURCE PDF → DOCUMENT PROFILING → TEXT-LAYER DETECTION → ROUTE A/B/C
→ PAGE-LEVEL TEXT / RAW_OCR → METADATA → STRUCTURE(discovery) → TRACEABILITY
→ QC → REVIEW QUEUE
NO "667 PDFs → OCR everything"
OCR_REQUIRED 仅对影像型 PDF 置 YES（29/50），其余不默认 OCR
```

## 2. 选择（50/667，含困难样本）

`BATCH-MANIFEST.csv`（与 B01 schema 一致，BATCH_ID=B02，SHA256 逐一重验）：

- 论文 21（数字文本层 PDF，含 4 篇皇甫谧主题）
- 甲乙经论著/现代整理 11
- 古籍版本/影印 6（老书扫描：甲乙经全册、五车楼、医统正脉、行素草堂等）
- 非遗/传承佐证 12（扫描证书/证明）

技术覆盖：digital text、academic paper、old-book scan、low-quality scan、复杂排版（论文两栏）。
B02 内未出现 doc 级 mixed（10≤pp<150 且文本>0 的样本），如实标注 `MIXED=0`，不做 C 路由硬凑。

## 3. Profiling 结果（pdf-profile.csv，50 行）

```text
ROUTE A（可靠文本层，直提）  = 21（全部学术论文，pp 1400–2200/页）
ROUTE B（影像/扫描，OCR）    = 29（6 版古籍 + 11 论著扫描 + 12 非遗证书）
ROUTE C（mixed）             = 0
ENCRYPTED=15（均为 print:y，可提取）
CORRUPTED/FAILED profile     = 0
TOTAL_PAGES = 6,027
```

## 4. 处理输出

- `extracted-text/`：21 篇 Route A 全文逐页直提（`[PAGE n]` 块），61 页，page-blocks==pdfinfo 21/21
- `raw-ocr/`：32 页 RAW OCR（16 文档抽样：非遗 12 全首页 + 版本影印 4×5 页）
- `page-map.csv`：93 行（61 文本页 + 32 OCR 页），每行自带 `ASSET_ID → SOURCE_PDF → SHA256 → PAGE_NUMBER → 输出文件`（自包含可追踪，不依赖 join manifest）
- `structure/structure-discovery.csv`（21 行 Route A：首行候选标题、摘要/关键词标记，AUTO_EXTRACTED）
- `entities/entity-discovery.csv`（21 行 Route A：PERSON/WORK/ACUPOINT/MERIDIAN/DISEASE/TREATMENT 提及计数，DISCOVERY_ONLY，非知识图谱事实）
- `document-metadata.csv`（50 行，机器抽取默认 AUTO_EXTRACTED；AUTHOR/PUBLICATION 无法确定者=UNKNOWN，不猜）
- `review/review-queue.csv`（82 行）`review/processing-failures.csv`（10 页级 OCR 异常登记，无静默丢页）

## 5. 分层与纠错边界

```text
RAW_EXTRACTED_TEXT / RAW_OCR 独立落盘；AUTO_CORRECTION != VERIFIED_TRANSCRIPTION
本批未做“AI 润色覆盖原层”；无任何 corrected 层冒充原文
```

## 6. 失败与成功核算

```text
SUCCESS_DOCUMENTS=21（Route A 全页直提完成）
PARTIAL_DOCUMENTS=29（Route B：影像型文档已完成 profiling+代表页 RAW OCR；全页 OCR 属规模阶段，明确登记不静默）
FAILED_DOCUMENTS=0（无文档级处理失败）
21+29+0=50=BATCH_TOTAL
页级 OCR 异常 10 条（含 3 页空/极低输出）→ processing-failures.csv（RETRY_STATUS=RETRY_ADVANCED_OCR，MANUAL_REVIEW_REQUIRED=YES）
```

## 7. 性能与规模化（performance.json）

```text
TOTAL_DOCUMENTS=50   TOTAL_PAGES=6,027
DIRECT_EXTRACTION=21（实测 ≈0.03 s/页，22 页基准）
OCR=29（抽样 32 页实测 389.6s → ≈12.2 s/页，300dpi 单线程 tesseract）
PROCESSING_DURATION≈本批实测（profiling + 直提 + OCR 抽样）
AVERAGE_SECONDS_PER_PAGE≈12.2（OCR）/≈0.03（直提）
FAILURE_COUNT=0（文档级）/10（页级 OCR 质量异常）
MANUAL_REVIEW_COUNT=82（review-queue 全部条目）
OUTPUT_SIZE≈（B02 目录体积，含抽样渲染与 OCR）
ESTIMATED_REMAINING_PDF_COUNT=617（667−50）
ESTIMATED_FULL_SCALE_PROCESSING_COST≈仅计算资源/时间口径：若影像型占比按本批 58%（29/50）外推
  ≈617×120 页/份(样本均值)=~74,000 页；其中 OCR 路由页≈43,000 页×~12s≈143 小时单线程
  （或并行~6 核 ≈24h），直提页≈31,000 页×0.03s 可忽略；
  存储/人工复核/GPU/高级 OCR(PaddleOCR) 成本未计入 → 货币金额不虚构
```

## 8. Scale Gate

```text
SOURCE_TRACEABILITY=PASS（page-map 93 行自包含：每行含 SOURCE_PDF 与 SHA256，指向原文件/原页，SHA256 与 live 源文件一致）
PAGE_MAPPING=PASS（Route A 21/21 页块==pdfinfo；OCR 页 32/32 记录）
RAW_ASSET_INTEGRITY=PASS（50/50 SHA256 前后一致）
NO_SILENT_PAGE_LOSS=PASS（Route A 全页；Route B 抽样页全登记，未登记页=规模阶段待办并写入 review-queue）
QC_ACCEPTABLE=PASS（QC_PASS 文本路由；OCR 路由 QC_PARTIAL 已如实记录、无伪造精度）
BATCH_DOCUMENT_PIPELINE=PASS（文本直提链达标）
READY_FOR_BATCH_03_SCALE=YES（需满足条件：规模阶段 OCR 使用更强引擎/并行并保留 raw-ocr 层；
  每页映射与失败队列机制保持；人工复核 82 项先于内容使用）
```

## 9. 边界

```text
PRODUCT_CODE_CHANGE=NO（未改产品代码/未加依赖；脚本为独立内容生产脚本）
CANONICAL_HEAD_UNCHANGED=YES（2b372b3）
HFM_PROD_WRITE=FORBIDDEN → 未写入
RIGHTS/SOURCE 状态未自动改变（全部保持 NEEDS_REVIEW / NEEDS_CUSTOMER_CONFIRMATION）
RAW_ROOT 只读；处理结束 50/50 SHA256 重验一致（SOURCE_SHA256_BEFORE=SOURCE_SHA256_AFTER）
```

交付物目录：见 `content-production/batches/B02/`（BATCH-MANIFEST/pdf-profile/document-metadata/page-map/
extracted-text/raw-ocr/structure/entities/review/reports）。
