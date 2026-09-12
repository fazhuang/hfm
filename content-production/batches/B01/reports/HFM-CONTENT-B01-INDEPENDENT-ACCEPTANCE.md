# HFM-CONTENT-B01 — INDEPENDENT CONTENT ACCEPTANCE

```text
BATCH = HFM-CONTENT-B01
SOURCE_ROOT = /Users/likeming/Sites/hfm/hfmzl
RAW_CUSTOMER_FILES_MODIFIED = NO (no write operation performed)
HFM_PROD_WRITTEN = NO
PRODUCT_BEHAVIOR_CHANGED = NO

B01_ASSET_COUNT = 11
SOURCE_HASH_VERIFICATION = PASS (11/11 after normalizing SOURCE_PATH=hfmzl/<relative>)
PERSON_DOCUMENTS_PROCESSED = 3
PERSON_FACTS_EXTRACTED = 24
PERSON_TIMELINE_CANDIDATES = 14
PERSON_CONFLICTS = YES (3 groups retained unresolved)
JIAYI_SOURCE_SELECTED = 1 set / 5 PDFs
JIAYI_PAGES_PROCESSED = 7
PAGE_MAPPING = PASS (7/7 sample rows)
JIAYI_STRUCTURE = NEEDS_REVIEW (no reliable卷/篇 detection)
OCR_SCALE_DECISION = ITERATE / NOT SUITABLE FOR SCALE
IMAGE_PROCESSING = PASS (one source with separated derivatives)
VIDEO_PROCESSING = ITERATE (2 probes; 35 technical segments; no fabricated descriptions)
VIDEO_TRANSCRIPTS_COMPLETE = NO (correctly marked pending)

SOURCE_TRACEABILITY = BLOCKED_BY_MANIFEST_SCHEMA_ERROR
RIGHTS_BOUNDARY = PASS (all remain customer-confirmation required)
DERIVED_ASSET_SEPARATION = PASS
TEST_DEMO_DATA = 0
CUSTOMER_CONTENT_IMPORTED = 0

CRITICAL_PRODUCT_CODE_DEFECTS = 0
CRITICAL_RAW_ASSET_DEFECTS = 0
DELIVERY_MANIFEST_DEFECTS = 1
B01_INDEPENDENT_ACCEPTANCE = FAIL_PENDING_MANIFEST_CORRECTION
NEXT_ACTION = CORRECT_B01_MANIFEST_COLUMNS_AND_RE-RUN_ACCEPTANCE
```

## Evidence checked

- `BATCH-MANIFEST.csv` contains 11 rows. Each declared SHA-256 matches both the current raw file and `content-production/00-inventory/customer-assets.csv` when the manifest's `hfmzl/` prefix is normalized.
- The manifest header is `BATCH_ID,ASSET_ID,...`, but every row begins `HFM-Axxxxx,B01,...`. Thus the value in `BATCH_ID` is an asset ID and the value in `ASSET_ID` is the batch ID. This is a deterministic column-semantic defect, not a hash mismatch; it breaks consumers that trust the declared schema and prevents unconditional `SOURCE_TRACEABILITY=PASS`.
- `person-facts.csv` has 24 rows and `person-timeline-candidates.csv` has 14 rows. Review/conflict states are retained; no fact is marked VERIFIED.
- `jiayi/page-map.csv` has 7 mapped sample pages and `video-segments.csv` has 35 rows. Both video probe JSON files parse successfully. The transcript status explicitly says ASR unavailable and content not viewed; no unsupported dialogue or scene claims were found in the checked status.
- The image manifest preserves `NEEDS_CUSTOMER_CONFIRMATION`; derivatives are separate from the source. No raw customer file was changed, moved, renamed, deleted, or imported, and no database write was performed.

## Required correction

Rewrite only the manifest header/row column alignment (or regenerate the manifest) so that `BATCH_ID=B01` and `ASSET_ID=HFM-Axxxxx` while preserving every source path and SHA-256. Then rerun the same 11-row hash/path check. No content reprocessing, raw-file operation, database import, or product-code change is warranted.

```text
CUSTOMER_MATERIAL_AUDIT = NOT_STARTED
BATCH_02 = NOT_AUTHORIZED
OCR_BATCH_SCALE = NOT_AUTHORIZED
VIDEO_ASR_OR_TRANSCODE = NOT_AUTHORIZED
STOP = MANDATORY
```
