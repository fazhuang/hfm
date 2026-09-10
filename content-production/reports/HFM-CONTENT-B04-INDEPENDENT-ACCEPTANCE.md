# HFM CONTENT-B04 — INDEPENDENT ACCEPTANCE

## Verdict

```text
B04_INDEPENDENT_ACCEPTANCE=FAIL_PENDING_CSV_SCHEMA_CORRECTION
WORKSPACE=/Users/likeming/Sites/hfm
BRANCH=hfm-canonical
HEAD=2b372b3ba92443cdf1862cc86d95f0b9b8879f0c
PRODUCT_CODE_CHANGED=NO
HFM_PROD_WRITTEN=NO
RAW_CUSTOMER_FILES_MODIFIED=NO
```

The reported object counts and the source-page traceability chain are substantially reproducible, but the normalized deliverable is not currently machine-safe as a CSV contract. This blocks independent acceptance until serialization/alignment is corrected and rechecked. No content reprocessing is required by the evidence currently available.

## Scope and verified results

```text
NORMALIZED_CSV_FILE_COUNT=18
REPORTED_CSV_FILE_COUNT=17
OBJECT_COUNTS=PASS
SOURCE_PAGE_LINKS=1819/1819 TRACEABLE
RAW_ASSET_INTEGRITY=PASS (B03/B04 evidence; no raw writes observed)
HFM_PROD_WRITTEN=NO
```

Verified row counts:

```text
documents=675
persons=17
person-facts=24
person-timeline=14
person-relations=5
works=14
jiayi-editions=92
jiayi-source-pages=1819
jiayi-structure=0
evidence=24
papers=473
research-topics=5
heritage-objects=68
heritage-events=10
knowledge-object-candidates=26
review-priority=127
citations-candidates=0
```

The report's review-priority totals are consistent: R0=4, R1=17, R2=0, R3=106.

## Blocking findings

### 1. `jiayi-editions.csv` is structurally malformed

Header width is 8, while all 92 data rows have width 7 (`bad_widths=92`). The first row demonstrates a semantic shift: the value in the `ASSET_ID` position is a source filename, `PAGES` is blank, and the terminal `REVIEW_STATUS` field is absent. Consequently the 92 edition objects cannot be safely consumed by a standard CSV reader without repairing column alignment.

```text
JIAYI_EDITIONS_SCHEMA=FAIL
JIAYI_EDITIONS_BAD_WIDTH_ROWS=92
```

### 2. `person-facts.csv` contains malformed rows

The declared width is 11. Two of 24 rows contain 12 fields because comma-bearing values are not quoted; this shifts confidence/review/conflict columns for those rows.

```text
PERSON_FACTS_SCHEMA=FAIL
PERSON_FACTS_BAD_WIDTH_ROWS=2
```

### 3. `person-timeline.csv` contains malformed rows

The declared width is 10. Two of 14 rows contain 12 fields because comma-bearing period/person values are not quoted; this shifts subsequent fields.

```text
PERSON_TIMELINE_SCHEMA=FAIL
PERSON_TIMELINE_BAD_WIDTH_ROWS=2
```

These are serialization/schema defects, not evidence of raw-file corruption. They nevertheless prevent reliable object-level normalization, stable IDs/fields, and downstream import preparation for the affected records.

## Non-blocking verified evidence

```text
JIAYI_SOURCE_PAGE_TRACEABILITY=PASS (1819/1819; ASSET_ID→SOURCE_PDF→SHA256→PAGE→OUTPUT)
DOCUMENTS_AND_EVIDENCE_ROW_WIDTHS=PASS
PERSONS_RELATIONS_WORKS_PAPERS_HERITAGE_ROW_WIDTHS=PASS
JIAYI_STRUCTURE_UNITS=0 (explicitly unresolved; no fabricated structure)
SOURCE_TRACEABILITY=PASS for page-link layer; PARTIAL overall while malformed normalized rows remain
RAW_ASSET_INTEGRITY=PASS
RIGHTS_ORIGIN_NOT_ESCALATED=PASS (no evidence of automatic rights/public-domain conversion)
```

The declared partial readiness and review queues remain appropriate: this batch is reviewable candidates, not import-ready production content.

## Required correction and re-acceptance

Correct only CSV serialization/header alignment for the affected files (including quoting of comma-bearing fields and the `jiayi-editions.csv` field mapping), then rerun independent width, semantic-column, row-count, and traceability checks. Do not rewrite source assets, reprocess OCR, import content, or write `hfm_prod` for this correction.

```text
NEXT_ACTION=CORRECT_CSV_QUOTING_AND_COLUMN_ALIGNMENT_THEN_RERUN_ACCEPTANCE
HFM_PROD_IMPORT=FORBIDDEN
B05_AUTO_START=FORBIDDEN
CUSTOMER_CONTENT_PUBLICATION=FORBIDDEN
```

## Hard stop

```text
RAW_CUSTOMER_FILES_MODIFIED=NO
HFM_PROD_WRITTEN=NO
PRODUCT_CODE_CHANGED=NO
CONTENT_REPROCESSED=NO
STOP=MANDATORY
```
