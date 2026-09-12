# HFM CONTENT-B05-R1 — INDEPENDENT RE-ACCEPTANCE

```text
WORKSPACE=/Users/likeming/Sites/hfm
BRANCH=hfm-canonical
HEAD=2b372b3ba92443cdf1862cc86d95f0b9b8879f0c
TRACKED_WORKTREE=CLEAN
SCHEMA_SNAPSHOT=PASS (33 tables)
PRE_IMPORT_COUNTS_SNAPSHOT=PASS (hfm_prod, alembic 0014, system_admin=1)
PACKAGE_GENERATED_ARTIFACTS=PASS (no __pycache__/pyc)
```

## Verified corrections

```text
CSV_MAP_ROWS=18
TRANSFORM_REQUIRED=10
REFERENCE_ONLY=3
NOT_SUPPORTED_BY_CURRENT_SCHEMA=3
NOT_READY=2
SCHEMA_GAPS=10
BLOCKING_SCHEMA_GAPS=5
IMPORTABLE_OBJECTS=0
VALIDATION_ROWS=18
SCHEMA/UTF8/ROW_VALIDATION=PASS (18/18; empty files explicitly HEADER_ONLY)
DRY_RUN_1=PASS (reported)
DRY_RUN_2=PASS (reported)
IDEMPOTENCY=PASS (reported)
ROLLBACK=PASS (reported)
UNEXPLAINED_DELTA=0
```

The restored JSON snapshots parse correctly: `database-schema-map.json` contains 33 table entries, and `pre-import-row-counts.json` identifies `hfm_prod`, Alembic 0014, 33 count entries, and one system admin. The import contract count now agrees with the machine-readable CSV map.

## Remaining blocker: duplicate policy contradiction

`validation-report.csv` now labels the page-link check `PASS_WITH_POLICY`, but its policy says the import dedupe key is `(ASSET_ID,PAGE_NUMBER)` while simultaneously treating two records with that exact key as distinct outputs:

```text
ASSET_ID=HFM-A000542
PAGE=1
OUTPUT_FILE=content-production/batches/B02/raw-ocr/HFM-A000542_p001_raw.txt
OUTPUT_FILE=content-production/batches/B01/jiayi/raw-ocr/A000542_p001_raw.txt
```

Both records point to the same source PDF/page, so `(ASSET_ID,PAGE_NUMBER)` is not unique for the delivered data. A deterministic import identity must either include the output/layer/batch identity, or explicitly model these as one content object with multiple derived outputs. Until that key is made consistent with the stated “distinct output files” rule, stable-ID/provenance verification is not fully complete.

This is a contract/evidence issue only; the package remains empty by design and no production data was imported.

## Verdict

```text
SCHEMA_SNAPSHOT_EVIDENCE=PASS
MAPPING_COUNT_CONSISTENCY=PASS
PACKAGE_SCOPE=PASS
ZERO_ROW_DRY_RUN_EVIDENCE=PASS_AS_REPORTED
PRODUCTION_WRITE_BY_ACCEPTANCE=NO
PRODUCT_CODE_CHANGED=NO
STABLE_ID_AND_DUPLICATE_POLICY=FAIL_PENDING_CORRECTION
B05_INDEPENDENT_ACCEPTANCE=FAIL_PENDING_DUPLICATE_POLICY_CORRECTION
NEXT_ACTION=DEFINE_MACHINE_READABLE_IDENTITY_FOR_CROSS-BATCH_PAGE_OUTPUTS; RERUN VALIDATION/DRY-RUN ACCEPTANCE
HFM_PROD_IMPORT=FORBIDDEN
SCHEMA_CHANGE=FORBIDDEN
STOP=MANDATORY
```
