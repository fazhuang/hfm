# HFM-B05-SG-R2 — AUTHORITATIVE COMMIT MANIFEST FINAL

```text
WORKSPACE=/Users/likeming/Sites/hfm
BRANCH=hfm-canonical
HEAD=2b372b3ba92443cdf1862cc86d95f0b9b8879f0c
SCOPE=COMMIT_FILESET_AUTHORITY_ONLY
```

## Binding decisions

```text
core/test_data_policy.py=COMMIT_A
test_test_data_policy.py=COMMIT_A
test_migration_0008_boolean_default.py=EXCLUDE_OTHER_WORKFLOW
ALL_PREVIOUSLY_CLASSIFIED_IMPLEMENTATION_FILES=INCLUDE
```

## Machine manifests

```text
COMMIT_A_FILELIST=/tmp/HFM-B05-SG-R2-COMMIT-A-FINAL.files
COMMIT_A_FILES=30
COMMIT_B_FILELIST=/tmp/HFM-B05-SG-R2-COMMIT-B-FINAL.files
COMMIT_B_FILES=2
EXCLUDE_FILELIST=/tmp/HFM-B05-SG-R2-EXCLUDE-FINAL.files
EXCLUDE_ENTRIES=9
```

`EXCLUDE` directory roots cover every current descendant of `.playwright-cli/`, `content-production/`, and `video-production/`; all other current changed paths appear individually in exactly one manifest.

## Commit A authority

Every A path is either the 0015 content-import/current-head implementation itself or a required 0015 schema, model, guardrail, runtime/ops expectation, or corresponding test.

```text
A_REQUIRES_0015=YES_OR_A_REQUIRED_FOR_0015_TEST_OR_GUARDRAIL=YES
A_FILES_COMPLETE=YES
A_FILES_MINIMAL=YES
A_CONTAINS_FRONTEND_AUTH_WORKFLOW=NO
A_CONTAINS_CUSTOMER_CONTENT=NO
A_CONTAINS_VIDEO=NO
A_CONTAINS_UV_LOCK=NO
A_CONTAINS_0008_HISTORICAL_TEST_CHANGE=NO
```

## Commit B authority

The two B paths are the only `GOVERNANCE_HASH_BINDING_ONLY` files. The current `2b372b3...` binding is an allowed pre-A placeholder and does not affect A manifest readiness.

```text
B_ONLY_GOVERNANCE_HASH_BINDING=YES
COMMIT_B_EXECUTABLE_PRODUCT_CHANGE=0
COMMIT_B_SCHEMA_CHANGE=0
```

## Set-integrity result

```text
CURRENT_CHANGED_RECORDS=4046
CURRENT_DIRECT_NONROOT_PATHS=38
ROOT_COVERED_RECORDS=4008
CURRENT_CHANGED_FILES=A_UNION_B_UNION_EXCLUDE=YES
A_INTERSECT_B=EMPTY
A_INTERSECT_EXCLUDE=EMPTY
B_INTERSECT_EXCLUDE=EMPTY
UNCLASSIFIED_FILES=0
```

## Final decision

```text
DB_RUNTIME_RECHECK=PENDING
AUTHORITATIVE_COMMIT_MANIFEST=PASS
COMMIT_A_READY_TO_STAGE=YES
COMMIT_B_DESIGN_READY=YES
NEXT_ACTION=PI_STAGE_EXACT_COMMIT_A_FINAL_MANIFEST
NO_GIT_ADD=YES
NO_COMMIT=YES
NO_DATABASE_WRITE=YES
STOP=MANDATORY
```
