# HFM-B05-SG-R2 — AUTHORITATIVE COMMIT MANIFEST AUDIT

```text
WORKSPACE=/Users/likeming/Sites/hfm
BRANCH=hfm-canonical
HEAD=2b372b3ba92443cdf1862cc86d95f0b9b8879f0c
INDEX=EMPTY
TRACKED_WORKTREE=27_MODIFIED
UNTRACKED_TOP_LEVEL_ENTRIES=14 (several are directory trees)
FILE_MODIFICATION_BY_AUDIT=NO
GIT_ADD=NO
COMMIT=NO
DATABASE_WRITE=NO
```

## Current inventory and classification

### COMMIT_A_FILES

The following files are directly required for the 0015 implementation/current-head transition, its guardrails, or tests that assert that transition:

```text
apps/backend/alembic/versions/0015_content_import_support.py
apps/backend/src/hfm/core/test_data_policy.py
apps/backend/src/hfm/models/document.py
apps/backend/src/hfm/models/edition.py
apps/backend/src/hfm/models/evidence.py
apps/backend/src/hfm/models/person.py
apps/backend/src/hfm/models/work.py
apps/backend/src/hfm/phase2/guardrails.py
apps/backend/tests/conftest.py
apps/backend/tests/test_content_import_schema.py
apps/backend/tests/test_phase1_research_workspace.py
apps/backend/tests/test_phase2_guardrails.py
apps/backend/tests/test_phase2_media.py
apps/backend/tests/test_phase2_supersession.py
apps/backend/tests/test_test_data_policy.py
docs/operations/ND1-RELEASE-QUALIFICATION.md
infra/scripts/test-release-gate-precheck.sh
scripts/database-dependency-probe.sh
scripts/deploy-gate.sh
scripts/initialize-production.py
scripts/pre-release-checklist.sh
scripts/production-smoke.sh
scripts/real-browser-auth-evidence.sh
scripts/tests/test_harness_ownership.py
scripts/tests/test_initialize_production.py
scripts/tests/test_operations_package.py
scripts/tests/test_ops_release_artifacts.py
scripts/tests/test_production_db_allowlist.py
scripts/tests/test_validate_production_env.py
scripts/validate-production-env.py
```

Necessity grouping (each listed A file is covered):

| Group | Files | Proof |
|---|---|---|
| schema/ORM | migration 0015; `models/document.py`, `person.py`, `edition.py`, `evidence.py`, `work.py` | creates documents/person aliases and stable-id fields required by SG-01/02/04 |
| guardrail/test isolation | `core/test_data_policy.py`, `tests/test_test_data_policy.py`, `phase2/guardrails.py` | fail-closed current-head and customer-test DB protections |
| migration/current-head tests | `tests/conftest.py`, `test_content_import_schema.py`, `test_phase1_research_workspace.py`, `test_phase2_guardrails.py`, `test_phase2_media.py`, `test_phase2_supersession.py` | imports new model and asserts 0015 single-head lineage |
| runtime/ops | `docs/operations/ND1-RELEASE-QUALIFICATION.md`, `infra/scripts/test-release-gate-precheck.sh`, `scripts/database-dependency-probe.sh`, `deploy-gate.sh`, `initialize-production.py`, `pre-release-checklist.sh`, `production-smoke.sh`, `real-browser-auth-evidence.sh`, `validate-production-env.py` | replaces hard-coded current-head 0014 with 0015 in required runtime/release paths |
| corresponding tests | `scripts/tests/test_harness_ownership.py`, `test_initialize_production.py`, `test_operations_package.py`, `test_ops_release_artifacts.py`, `test_production_db_allowlist.py`, `test_validate_production_env.py` | preserves those 0015 runtime/qualification invariants |

`A_SCOPE=IMPLEMENTATION_AND_REQUIRED_CURRENT_HEAD_TESTS_ONLY`; no customer data or import output is included.

### COMMIT_B_FILES

```text
docs/governance/HFM-PHASE2-INVARIANT-SUPERSESSION-REGISTER-v1.md
scripts/verify-invariant-supersessions.py
```

Both are governance/hash-attestation files. They contain the supersession role and baseline binding, but currently bind `ASN-SG-MIG-0015-HEAD` to the pre-commit workspace hash `2b372b3...`, not to an actual future Commit A hash. Therefore they are the correct B candidates, but B cannot be finalized until Commit A is created and these two files are updated to that exact hash.

```text
B_REQUIRES_ACTUAL_COMMIT_A_HASH=YES
B_EXECUTABLE_PRODUCT_DIFF=0
B_SCHEMA_DIFF=0
B_RUNTIME_BEHAVIOR_CHANGE=0
```

### EXCLUDED_FILES

```text
apps/backend/tests/test_api_permission_status.py — unrelated auth HTTP regression; auth workflow owner
apps/backend/tests/test_migration_0008_boolean_default.py — explicitly 0008/0014 regression, untracked stale test; legacy migration-test workflow
apps/backend/uv.lock — no dependency declaration change in this transition; dependency lock workflow
apps/frontend/src/__tests__/auth_flow_store.spec.ts — unrelated frontend auth store coverage; WR00/auth workflow
.playwright-cli/ — browser scratch/evidence artifacts; browser QA workflow
content-production/ — customer-derived inventories, batches, normalized objects and B05 reports; content workflow, not product commit A/B
video-production/ — media production artifacts; video workflow
design-qa.md — design QA artifact; design workflow
docs/design/HFM-DESIGN-RESOURCE-UTILIZATION-PLAN.md — design planning artifact; design workflow
```

Directory entries above exclude all descendants; no individual content or media file is admitted to A/B.

## A/B readiness and database check

```text
A_FILES_COMPLETE=YES (for the identified implementation scope)
A_FILES_MINIMAL=YES (no frontend/auth/content/video artifacts)
A_CONTAINS_OTHER_WORKFLOW=NO
A_CONTAINS_SECRET=NO
A_CONTAINS_LOCAL_DB=NO
A_CONTAINS_CUSTOMER_RAW_ASSET=NO
B_FILES_COMPLETE=YES (candidate governance files identified)
B_FILES_MINIMAL=YES
B_ONLY_GOVERNANCE_HASH_BINDING=YES
```

The required live read of PostgreSQL could not be completed in this sandbox: the local PostgreSQL socket returned `Operation not permitted`, and Docker socket access was unavailable. Consequently the supplied `HFM_PROD=0015 / 35 tables / documents=0 / person_aliases=0` remains unverified here.

```text
HFM_PROD_IDENTITY=UNVERIFIED_LIVE
SYSTEM_ADMIN_PRESERVATION=REQUIRED_BY_DESIGN
PREVIOUS_BASELINE=2b372b3... / historical 0014
PARENT_BASELINE=0014
INTRODUCED_AT_BASELINE=actual Commit A (not yet available)
EFFECTIVE_FROM=actual Commit A (not yet available)
BASELINE_ROLES[B05_SG_R2_MIGRATION_COMMIT]=actual Commit A (current file still pre-commit hash)
```

## Final decision

```text
UNRESOLVED_FILES=0
COMMIT_MANIFEST_RECOVERY=FAIL
COMMIT_A_READY_TO_STAGE=NO (live DB identity not independently verified; A hash not yet created)
COMMIT_B_DESIGN_READY=NO (governance files await actual Commit A hash)
NEXT_ACTION=PRODUCT_OWNER_REVIEW_OF_MANIFEST; VERIFY HFM_PROD 0015 READ-ONLY; STAGE A ONLY AFTER AUTHORIZATION; THEN BIND B TO ACTUAL A HASH
```

No files were staged, committed, reset, restored, migrated, or written to the database.

```text
NO_FILES_MODIFIED_BY_AUDIT=YES
NO_FILES_STAGED=YES
NO_COMMIT_CREATED=YES
NO_DATABASE_WRITE=YES
STOP=MANDATORY
```
