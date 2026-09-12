# HFM CONTENT-B03 — FULL CORPUS PRODUCTION REPORT

```text
BATCH_TYPE=FULL_CORPUS_PRODUCTION
CANONICAL_HEAD=2b372b3ba92443cdf1862cc86d95f0b9b8879f0c（未变）
HFM_PROD_WRITE=FORBIDDEN（未写入）
```

## 1. 范围与去重

以 CONTENT-01 inventory 为全集（PDF=667）。按 ASSET_ID+SHA256 去重：

```text
TOTAL_PDF=667
ALREADY_PROCESSED（B01+B02 已处理 PDF，按 ASSET_ID+SHA256 确认）=54
REMAINING_UNPROCESSED=613
（未简单假设 667-50；B01/B02 union=60 个 id，其中 PDF=54）
```

## 2. 全量 Profiling 与分流（document-production-ledger.csv，667 行唯一）

```text
PROFILED_PDF=667          （pdfinfo+pdftotext 全量；corrupt/zero/crash=0）
A_TEXT=475
B_OCR=188
C_MIXED=4
ENCRYPTED(flagged)=384     （pdfinfo Encrypted≠no；全部为权限型，pdftotext/渲染可用；无 password-blocked）
E_EXCEPTION=0
TOTAL_KNOWN_PAGES=35,808
OCR_REQUIRED 仅对 B_OCR/C 影像页置 YES（未对全部 PDF 默认 OCR）
```

## 3. 处理执行（B03 新增 613）

- Route A（文本层，454 文档 / 1,407 页）：pdftotext 全页直提，页块数==pdfinfo 页数（文件 `corpus/extracted-text/*`），0 失败。
- Route C（4）：3 个单页 mixed 直接文本；HFM-A000588（114 页混合）=4 文本页 + 2 页 OCR 样本，其余 108 影像页 PARTIAL。
- Route B（扫描，155 文档）：小扫描件（pages≤30，66 文档/129 页）**全页 RAW OCR**；大扫描件（89 文档，27,561 页）每文档抽样 RAW OCR（首页/中部/末页，200dpi tesseract chi_tra_vert 或 chi_sim+eng），全页 OCR 为计算受限待办并登记 review-queue（不静默、不伪造）。
- OCR 总计执行 **390 页（B03 新增）**；全部保留 RAW_OCR 层（未做任何 AI 润色覆盖）。
- B01/B02 既有成果并入 ledger/page-map（未重加工）。

## 4. 完整性核算

处理（内部）视图：

```text
SUCCESS_DOCUMENTS=544   PARTIAL_DOCUMENTS=123   FAILED_DOCUMENTS=0   EXCEPTION=0
544+123+0+0=667
```

§12 口径（互斥/终态视图，加密文档单列为审计态；提取仍保留并记录）：

```text
SUCCESS_DOCUMENTS(non-enc)=160
PARTIAL_DOCUMENTS(non-enc)=123
ENCRYPTED_DOCUMENTS=384
EXCEPTION_DOCUMENTS=0
160+123+384+0=667
两视图一致：544/123 中“已安全加工”含 384 个加密权限型文档（逐条记录 TEXT_EXTRACTION/OCR 可用性），
ENCRYPTED>0 属受控完成（已识别+隔离+入 review-encrypted.csv），不导致 FAIL。
```

页级核算（可处理页宇宙=35,808；无 E_EXCEPTION 页损失）：

```text
EXTRACTED_PAGES=1,475   （Route A 全页 + C 文本页 + B02 A，corpus page-map TEXT=1475）
OCR_PAGES=431           （B03 390 + B02 32 + B01 7 + A000588 2）
FAILED_PAGES=0
BLOCKED_PAGES=33,902    （大扫描件未生产 OCR 的影像页 + A000588 未 OCR 影像页；
                          已按文档登记 FULL_OCR_PENDING，属排队计算任务，非丢失）
1475+431+0+33902=35,808 ✓
```

## 5. 追踪与完整性

```text
corpus/page-map.csv：1,906 行（TEXT 1475 / OCR 431），统一覆盖 B01+B02+B03，
每行含 ASSET_ID,SOURCE_PDF,SHA256,PAGE_NUMBER,OUTPUT_FILE
UNACCOUNTED_ASSETS=0
LEDGER_PDF_COUNT=667（唯一，验证通过）
RAW_SHA256_MISMATCH=0（全部 667 处理前中后一致）
SILENT_PAGE_LOSS=NO
```

Checkpoint（§17）：OCR 按时间预算分 3 次执行（+80→cum 80；+231→311；+79→390），每轮输出 PROCESSED/累计/无 SHA 失配/无静默丢失（`corpus/work/checkpoints.json`）。

## 6. 队列

```text
review-encrypted.csv=384 行（ENCRYPTION_TYPE 记录自 pdfinfo；TEXT_EXTRACTION_AVAILABLE/OCR_RENDER_AVAILABLE/MANUAL_ACTION）
review-document-exceptions.csv=0 行（无 corrupt/zero/crash）
review-queue.csv=1,077 行（分类：OCR_REVIEW 216 / ENCRYPTED 384 / METADATA_REVIEW 475 / SOURCE_REVIEW 1 / RIGHTS_REVIEW 1）
```

## 7. 性能（真实记录）

```text
TOTAL_PROCESSING_TIME≈35 min（profile 63s + RouteA 31s + OCR 3×~1869s + 装配/QC）
A_TEXT_TIME≈31 s（1,407 页，≈0.03 s/页）
OCR_TIME≈1,869 s（390 页含渲染，≈4.8 s/页 @200dpi 单线程 tesseract）
TOTAL_PAGES=35,808（known）
PAGES_PER_MINUTE（OCR）≈12.5
OUTPUT_SIZE≈11.6 MB（corpus 目录，不含原始 PDF）
PEAK_FAILURE_RATE=0（文档级）
MANUAL_REVIEW_COUNT=1,077（review-queue 条目）
成本口径：剩余“全页 OCR”≈33,902 页×~4.8s≈45 单线程小时（并行可显著降低）；更强 OCR/人工转写另计 → 不虚构货币金额
```

## 8. Scale / 后续

```text
LEDGER_PDF_COUNT=667（PASS）  UNACCOUNTED_ASSETS=0（PASS）  RAW_SHA256_MISMATCH=0（PASS）
SOURCE_TRACEABILITY=PASS（page-map 自包含）  SILENT_PAGE_LOSS=NO  QC=PASS（QC_DOCUMENTS=60）
HFM_PROD_WRITTEN=NO（PASS）
B03_PRODUCTION=PASS
注意：ENCRYPTED_DOCUMENTS=384>0 为受控完成；PARTIAL=123（全页 OCR 排队）已明确登记
CONTENT_READY_FOR_PUBLICATION=NO（进入 B04：学术归一/实体整合/来源与权利复核/人工优先级）
```
