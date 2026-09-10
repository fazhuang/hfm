# HFM CONTENT-B04-R1 — CSV SCHEMA CORRECTION

```text
BATCH=HFM-CONTENT-B04-R1（CSV_SCHEMA_CORRECTION_ONLY）
CONTENT_REPROCESSING=FORBIDDEN（未发生）
OCR_RERUN=FORBIDDEN
ENTITY_REEXTRACTION=FORBIDDEN
NORMALIZATION_RERUN=FORBIDDEN
OBJECT_COUNT_CHANGE=FORBIDDEN（未发生）
SEMANTIC_CONTENT_CHANGE=FORBIDDEN（未发生：仅 serialization/quoting/alignment）
HFM_PROD_WRITE=FORBIDDEN（未写入）
```

## 1. 修正内容

全部 18 个 CSV 用标准 `csv.writer`（RFC4180 等价的 quoting/转义，UTF-8）重新序列化；未使用手工字符串拼接。

1. `jiayi-editions.csv`（92 行全部列数错误）：原生成行缺少前导 `EDITION_ID` 列。修正：在每行前补确定性稳定 ID `EDITION-<ASSET_ID>`（与 §19 `EDITION-*` 稳定 ID 方案一致），其余单元格内容不变 → 8 列对齐、92 行不变。
2. `person-facts.csv`（2 行内嵌逗号）：`HFM-B01-PF-001`（行尾多余空字段）与 `HFM-B01-PF-006`（OBJECT 字段含未转义 ASCII 逗号）→ 以标准 quoting 重写；内嵌 ASCII 引号标记在该两行改为全角引号（内容词义不变，规避引号嵌套歧义）。
3. `person-timeline.csv`（2 行内嵌逗号）：`HFM-B01-PT-003`、`HFM-B01-PT-007` 的 DATE/RELATED_PERSON 字段含未转义 ASCII 逗号 → 标准 quoting 重写。

其它 15 个 CSV 经机器解析确认无异常，仍统一经标准 writer 重序列化以保持一致（未改内容/计数）。

## 2. 验收数据

```text
FILES_CORRECTED=3（jiayi-editions.csv / person-facts.csv / person-timeline.csv；另 15 个经规范化重写内容不变）
TOTAL_B04_CSV=18

JIAYI_EDITIONS_ROWS=92
JIAYI_EDITIONS_MALFORMED_BEFORE=92
JIAYI_EDITIONS_MALFORMED_AFTER=0

PERSON_FACTS_MALFORMED_BEFORE=2
PERSON_FACTS_MALFORMED_AFTER=0

PERSON_TIMELINE_MALFORMED_BEFORE=2
PERSON_TIMELINE_MALFORMED_AFTER=0

CSV_SCHEMA_PASS=18
CSV_SCHEMA_FAIL=0

OBJECT_ROW_COUNT_DRIFT=0
  documents=675 persons=17 person-facts=24 person-timeline=14 person-relations=5 works=14
  jiayi-editions=92 jiayi-structure=0 jiayi-source-pages=1819 evidence=24 papers=473
  research-topics=5 heritage-objects=68 heritage-events=10 knowledge=26 product-map=6
  review-priority=127 citations-candidates=0（header only）——修正前后一致
STABLE_ID_DRIFT=0（facts/timeline/其它 ID 未变；jiayi-editions 补前导 EDITION-<ASSET_ID> 系补齐缺失列，
  原缺列故无法“保持不变”，已如实说明，不影响既有稳定 ID 语义）
SOURCE_REFERENCE_DRIFT=0

JIAYI_SOURCE_PAGES_UNCHANGED=PASS（1819/1819，文件未重写）
```

## 3. 机器解析全量扫描（18/18）

```text
FILE_EXISTS=PASS(18)   HEADER_PARSE=PASS(18)   ROW_PARSE=PASS(18)
COLUMN_ALIGNMENT=PASS(18)   UTF8_PARSE=PASS(18)   EMPTY_ID_CHECK=PASS(18)
DUPLICATE_HEADER_CHECK=PASS(18)   MALFORMED_QUOTE_CHECK=PASS(18)
CSV_SCHEMA_PASS=18   CSV_SCHEMA_FAIL=0
```

## 4. 边界

```text
RAW_ASSET_INTEGRITY=PASS（未改动 hfmzl）
HFM_PROD_WRITTEN=NO
ALEMBIC=0014   TABLES=33
PRODUCT_CODE_CHANGED=NO   CANONICAL_BRANCH=hfm-canonical
HEAD_BEFORE=2b372b3ba92443cdf1862cc86d95f0b9b8879f0c
HEAD_AFTER=2b372b3ba92443cdf1862cc86d95f0b9b8879f0c（内容层未入产品提交，无 tracked 改动）
TRACKED_WORKTREE=CLEAN（仅 content-production/ untracked 内容工件）
```

## 5. 报告计数更正

```text
CSV_FILE_COUNT=17 → 18（normalized 目录实际 18 个 CSV，含 citations-candidates.csv）
（已并入 HFM-CONTENT-B04-NORMALIZATION.md R1 更正节）
```
