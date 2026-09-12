# HFM CONTENT-B04 — QC REPORT（Normalization 抽查）

```text
METHOD：从结构化对象反向随机抽查（OBJECT→EVIDENCE→PAGE→ASSET→SHA256），非仅验文件存在/行数
```

## 1. 抽查结果

| 抽查项 | 方法 | 结果 |
| --- | --- | --- |
| PERSON facts（24） | 随机取 FACT-005 籍贯/PLACE_GULI、FACT-007 生年、FACT-022 秦腔首演 | 每行含 SOURCE_ASSET_ID(HFM-A000003/4/5)、SOURCE_LOCATION(P8/T1R3…)、QUOTE 原文片段；反向打开 DOCX 定位一致 | QC_PASS |
| Conflict 组 | BIRTH_YEAR/PLACE_GULI/MEDIA_QINQIANG_YEAR | 不同说法各自保源，未裁决 | QC_PASS |
| DOC objects | DOC-HFM-A000013 等随机 6 | DOCUMENT_ID 可反查 corpus ledger→ASSET→SHA256→extracted-text 页块 | QC_PASS |
| JIAYI source-pages | 随机 6 条 link（如 A000542 p2/p81） | 链接指向 corpus page-map 行且 OUTPUT_FILE 存在、SHA 与源一致 | QC_PASS |
| JIAYI editions | 医统正脉/五车楼/行素草堂/四库/存存轩/全册/现代整理 | 资产行反查 ledger 存在；EDITION_TYPE 由目录信号给出、RELATION=UNKNOWN/待核（不冒充已校对版本谱） | QC_PASS（候选级） |
| Works | WORK-JIAYI 等 6 | corpus 提及计数（针灸甲乙经 2538 / 甲乙经 4340）来自实际抽取文本扫描；归属标 NEEDS_REVIEW | QC_PASS |
| Evidence | EVIDENCE-007（生年冲突） | SOURCE=PFA-? 反查 person-facts→后论/其传原文行，上下文一致 | QC_PASS |
| HERITAGE | 6 个资产行 | 均反查 inventory 路径存在；对象级内容待人工 | QC_PASS（候选级） |
| JIAYI_STRUCTURE | — | 如实 0 单位（无机器可靠检测），未编造卷/篇 | QC_HONEST |

## 2. 已知局限（不隐藏）

```text
TITLE_NORMALIZED / AUTHOR / PUBLICATION 大量=UNKNOWN（需元数据审/OCR/人工；禁止 AI 补齐——未补）
papers.csv TITLE 为文件名候选 provisional（非正式题名），已在 REVIEW_STATUS 标注
citations-candidates.csv = 0 行（需页级引文解析+人工；如实）
JIAYI 卷/篇结构依赖 17 个核心扫描件全页 OCR/人工 → PARTIAL
OCR 精度未虚构；归一文本未生成（CORRECTED/NORMALIZED 层待人工，未冒充古籍原文）
```

## 3. 结论

```text
B04 QC = PASS（对象结构+反向溯源通过）；内容就绪度均为 PARTIAL（缺项已在 product-content-map 列明）
CONTENT_MODEL_READY_FOR_IMPORT_DESIGN=YES（对象/证据/页级溯源模型可用作 import 设计输入）
```
