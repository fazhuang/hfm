# HFM CONTENT-B04-R1 — INDEPENDENT ACCEPTANCE

```text
WORKSPACE=/Users/likeming/Sites/hfm
BRANCH=hfm-canonical
HEAD=2b372b3ba92443cdf1862cc86d95f0b9b8879f0c
TRACKED_WORKTREE=CLEAN
CSV_FILE_COUNT=18
```

## Independent parser results

All 18 normalized CSV files were parsed with Python's RFC4180-compatible CSV parser.

```text
HEADER_PARSE=PASS (18/18)
ROW_PARSE=PASS (18/18)
COLUMN_ALIGNMENT=PASS (18/18)
UTF8_PARSE=PASS (18/18)
DUPLICATE_HEADER_CHECK=PASS (18/18)
MALFORMED_QUOTE_CHECK=PASS (18/18)
EMPTY_ID_CHECK=PASS (18/18)
```

Row counts match the correction report with zero drift, including documents=675, persons=17, person-facts=24, person-timeline=14, person-relations=5, works=14, jiayi-editions=92, jiayi-structure=0, jiayi-source-pages=1819, evidence=24, papers=473, research-topics=5, heritage-objects=68, heritage-events=10, knowledge-object-candidates=26, product-content-map=6, review-priority=127, and citations-candidates=0.

Stable IDs are non-empty and unique for checked object sets: editions 92/92, facts 24/24, timeline 14/14, documents 675/675, persons 17/17. Required source/reference fields are populated in the checked facts, timeline, evidence, and Jiayi page-link records. `jiayi-source-pages.csv` contains 1819 parseable records with required asset, source-PDF, SHA, and page fields.

## Boundary checks

```text
RAW_ASSET_INTEGRITY=PASS (no raw customer-file writes observed)
JIAYI_SOURCE_PAGES_UNCHANGED=PASS (1819 records; correction scope is CSV serialization)
HFM_PROD_WRITTEN=NO (no database write command executed in this acceptance)
PRODUCT_CODE_CHANGED=NO
CONTENT_REPROCESSED=NO
```

The local PostgreSQL socket was not available for a live read during this check; therefore database non-write status is based on the declared correction boundary and this run's command activity, not a fresh DB query.

## Acceptance

```text
CSV_SCHEMA_CORRECTION=PASS
OBJECT_ROW_COUNT_DRIFT=0
STABLE_ID_DRIFT=0 (within corrected deliverable; edition IDs now deterministically populated)
SOURCE_REFERENCE_DRIFT=0 (per correction evidence; current required-reference scan passes)
AUTHORIZED_SCOPE_ONLY=PASS
B04_R1_INDEPENDENT_ACCEPTANCE=PASS
```

This acceptance covers serialization, quoting, column alignment, row counts, IDs, and source-reference integrity only. The normalized content remains reviewable candidates and is not import-ready.

```text
HFM_PROD_IMPORT=FORBIDDEN
B05_AUTO_START=FORBIDDEN
CONTENT_REPROCESSING=FORBIDDEN
NEXT_ACTION=PRODUCT_OWNER_REVIEW
STOP=MANDATORY
```
