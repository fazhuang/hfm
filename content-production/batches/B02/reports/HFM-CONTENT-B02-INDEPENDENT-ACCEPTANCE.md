# HFM-CONTENT-B02 — INDEPENDENT ACCEPTANCE

```text
BATCH = HFM-CONTENT-B02
CANONICAL_HEAD = 2b372b3ba92443cdf1862cc86d95f0b9b8879f0c
RAW_CUSTOMER_FILES_MODIFIED = NOT OBSERVED
HFM_PROD_WRITTEN = NOT OBSERVED

BATCH_ASSETS = PASS (50 unique manifest rows)
TOTAL_PAGES = PASS (6,027 from pdf-profile)
SOURCE_SHA256 = PASS (50/50 current hfmzl files match manifest)
ROUTE_COUNTS = PASS (A_TEXT=21, B_OCR=29, C=0)
PAGE_MAP_ROWS = PASS (93; TEXT=61, OCR=32)
PAGE_MAP_OUTPUTS = PASS (93/93 output files exist)
REVIEW_QUEUE = PASS (82 rows)
PROCESSING_FAILURE_QUEUE = PASS (10 page-level rows)
RAW_OUTPUT_SEPARATION = PASS (extracted-text vs raw-ocr)

QC_DOCUMENTS = PASS (22)
QC_PAGES = PASS (54)
OCR_ACCURACY = CORRECTLY_NOT_REPORTED
NO_SILENT_PAGE_LOSS = PASS (for declared routes/samples)

REPORT_CONSISTENCY = FAIL (ENCRYPTED count mismatch: actual 15, report says 14)
PAGE_MAP_SELF_CONTAINED_TRACEABILITY = PARTIAL (ASSET_ID/page only; SOURCE_PDF/SHA256 absent from page-map)
SOURCE_TRACEABILITY = PARTIAL (joinable through manifest, not as declared self-contained columns)

B02_INDEPENDENT_ACCEPTANCE = FAIL_PENDING_METADATA_CORRECTION
NEXT_ACTION = CORRECT REPORT COUNT AND PAGE-MAP TRACEABILITY CONTRACT, THEN RE-RUN ACCEPTANCE
```

## Verified facts

- Every B02 manifest source path resolves under `hfmzl` and its SHA-256 matches the current raw file. No raw source was modified by this acceptance.
- `pdf-profile.csv` contains 50 rows and sums to 6,027 pages. Route distribution is 21 `A_TEXT` and 29 `B_OCR`; no corrupted profile was observed. `document-metadata.csv` has 50 rows.
- `page-map.csv` contains 93 rows; all referenced extracted/OCR output files exist. `review-queue.csv` contains 82 rows and `processing-failures.csv` contains 10 rows. The 32 OCR files and 61 extracted-text page blocks are present.
- Entity and structure outputs are discovery-level; QC correctly retains OCR as partial and reports no fabricated accuracy percentage. No database import or customer-content publication was observed.

## Blocking discrepancies

1. `pdf-profile.csv` has 15 rows with `ENCRYPTED=YES` (`HFM-A000013`, `062`, `086`, `111`, `135`, `160`, `184`, `258`, `307`, `331`, `356`, `380`, `405`, `478`, plus one additional row), while the production report states `ENCRYPTED=14`. The report must be corrected to the actual count or the underlying profile corrected with evidence.
2. `page-map.csv` header is `BATCH_ID,ASSET_ID,PAGE_NUMBER,OUTPUT_FILE,PAGE_TEXT_CHARS,LAYER,STATUS`; it contains no `SOURCE_PDF` or `SHA256` fields. The mapping is resolvable by joining `ASSET_ID` to `BATCH-MANIFEST.csv`, but this does not meet the report's stated self-contained `ASSET_ID→SOURCE_PDF→SHA256→page` contract. Either add those immutable trace fields or explicitly revise the contract and evidence.

These are metadata/evidence defects, not raw asset corruption or product-code regressions. The content-processing quality caveats remain as reported: 29 OCR documents are partial, OCR accuracy is not quantified, 10 page-level failures are queued, and all review items remain manual-review required.

```text
CONTENT_REPROCESSED = NO
CUSTOMER_CONTENT_IMPORTED = NO
PRODUCT_CODE_CHANGED = NO
BATCH_03_AUTO_START = FORBIDDEN
STOP = MANDATORY
```
