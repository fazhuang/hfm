# HFM-CONTENT-B03 — INDEPENDENT ACCEPTANCE

```text
BATCH = HFM-CONTENT-B03
CANONICAL_HEAD = 2b372b3ba92443cdf1862cc86d95f0b9b8879f0c
LEDGER_PDF_COUNT = PASS (667 unique rows)
PROFILED_PDF = PASS (667)
ROUTES = PASS (A_TEXT=475, B_OCR=188, C_MIXED=4)
TOTAL_KNOWN_PAGES = PASS (35,808)

DOCUMENT_STATUS = PASS (SUCCESS=544, PARTIAL=123, FAILED=0, EXCEPTION=0)
PAGE_ACCOUNTING = PASS (TEXT=1,475, OCR=431, FAILED=0, BLOCKED=33,902)
PAGE_MAP = PASS (1,906 rows; TEXT=1,475, OCR=431)
SOURCE_TRACEABILITY = PASS (all page rows join ledger and live source SHA256)
OUTPUT_COMPLETENESS = PASS (all mapped output files present)
UNACCOUNTED_ASSETS = 0

QC = PASS (60 documents; 48 PASS, 12 PARTIAL, 0 FAIL)
REVIEW_QUEUE = PASS (1,077; OCR 216 / encrypted 384 / metadata 475 / source 1 / rights 1)
ENCRYPTED_QUEUE = PASS (384)
EXCEPTION_QUEUE = PASS (0)
RAW_SHA256_MISMATCH = 0
SILENT_PAGE_LOSS = NO

HFM_PROD_WRITTEN = NO (read-only check: hfm_prod, Alembic 0014, 33 tables, users=1, persons=0)
PRODUCT_CODE_CHANGED = NO
FULL_CORPUS_TECHNICAL_PROCESSING = PASS
B03_INDEPENDENT_ACCEPTANCE = PASS
CONTENT_READY_FOR_PUBLICATION = NO (review/approval gates remain)
NEXT_ACTION = PRODUCT_OWNER_REVIEW
STOP = MANDATORY
```

## Independent checks

- Rehashed all 667 ledger source files against the live `hfmzl` files: zero mismatches. Canonical Git HEAD remains unchanged.
- Recomputed the ledger: 667 unique assets; 475 `A_TEXT`, 188 `B_OCR`, 4 `C_MIXED`; 35,808 pages. Processing status is 544 `SUCCESS` and 123 `PARTIAL`, with no failed or exception documents.
- Recomputed page accounting: 1,475 TEXT + 431 OCR + 33,902 explicitly blocked/pending pages = 35,808. All 1,906 page-map rows contain `SOURCE_PDF` and `SHA256`, match the ledger/live source, and point to an existing derived output.
- QC sample has 60 rows; review queue has 1,077 rows with the declared category counts. Encrypted review has 384 rows and document exceptions has zero rows. OCR accuracy is not fabricated.
- Read-only database check returned `hfm_prod`, Alembic `0014`, 33 public tables, one system administrator, and zero persons. No customer content or legacy data was imported.

Controlled limitations remain as correctly disclosed: 123 documents are partial, 33,902 scan/mixed pages are queued for full OCR, 384 encrypted documents require review, and publication/import is not authorized.
