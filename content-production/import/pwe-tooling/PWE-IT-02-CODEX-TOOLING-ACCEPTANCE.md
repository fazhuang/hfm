# HFM PWE IT 02 Codex Tooling Acceptance

**阶段**：PWE_IMPORT_TOOLING_IMPLEMENTATION  
**性质**：独立验收，未实施修复  
**日期**：2026-09-10

## 1. Decision

PWE-IT-02 does not pass. The temporary PostgreSQL execution behavior is sound in the tested current state, but the importer does not actually enforce the signed DMIT-03 mapping contract at runtime. In addition, neither implementation nor mapping artifacts form a Git-tracked baseline.

Accordingly, this tooling must not proceed to `PRODUCTION_DRY_RUN_AND_RECONCILIATION`.

## 2. Repository Reality

The current repository identity is `hfm-canonical` at `5c7253dfd088c64fc991e951f04d196cb3ae1d74`, under `/Users/likeming/Sites/hfm`. The worktree has no staged or unstaged tracked diff, but is dirty with a large pre-existing untracked collection.

The importer, its tests, its implementation report, the PWE mapping artifacts, the DMIT-03 acceptance, and this report are all untracked. There are also unrelated untracked backend/frontend/content artifacts. This is not an error in the tested code path, but it prevents a controlled, commit-bound release baseline.

## 3. Independently Verified Execution Evidence

An independent disposable PostgreSQL audit used two freshly migrated `0015` databases. No canonical production write was performed.

| Probe | Result |
| --- | --- |
| Dry run | `DRY_RUN_NO_WRITE`; predicted `31/17/14/87`, deferred `5`; `documents 0→0`. |
| First apply | committed `entities=31`, `persons=17`, `works=14`, `editions=87`, `documents=0`. |
| Rerun | created `0/0/0/0`; existing `31/17/14/87`. |
| Failure injection after works | `ROLLED_BACK`; post-failure `entities/persons/works/editions=0/0/0/0`. |
| Unauthorised hfm_prod apply | `REFUSED` before write; final canonical counts `entities/persons/works/editions/documents=0/0/0/0/675`. |

The FK order is real and compatible with the schema: `entities → persons → works → editions`; `persons.entity_id` is FK-restricted and `editions.work_id` is non-null FK-backed. No FK disabling, NOT NULL relaxation, schema mutation, migration, DOCUMENT mutation, publication, or UI propagation occurred.

## 4. Mapping Contract Defects

The following are functional blockers, independently found by direct code review:

1. **Confirmed-status enforcement is absent.** `load_baseline()` consumes only files 01–04. It does not consume the DMIT-03 signed acceptance or any confirmation-review CSV. The 87 rows are accepted solely because their `mapping_confidence == "HIGH"`; their raw mapping `review_status` values remain `REVIEW_REQUIRED`. This makes HIGH confidence a runtime substitute for signed confirmation, contrary to `IMPORTER_CONSUMES_ONLY_CONFIRMED_ROWS` and the no-promotion rule.
2. **The frozen mapping is not cryptographically or set-wise pinned by the importer.** Hashes are calculated and reported but never compared with a known accepted baseline. A changed edition candidate pointing to another existing WORK, while retaining the expected row count/HIGH confidence/deferred set, would be consumed.
3. **Existing entity collisions are incompletely checked.** `_apply_entities()` treats an existing `entity_stable_id` as idempotent without confirming its `entity_type` or canonical name. A wrong pre-existing entity can therefore be reused before PERSON/WORK creation.

The deferred set itself is correctly hardcoded and excluded: `A000541`, `A000529`, `A000530`, `A000531`, `A000532` cannot enter the current edition insertion loop. This does not cure the signed-confirmation and baseline-pinning defects.

## 5. Static Security Review

No security blocker was found in the stated pi-lens warnings:

- `text()` calls in the importer contain static SQL only; no dynamic interpolation reaches SQL.
- `subprocess.run` occurs in the test migration fixture, uses an argument list with `shell=False`, and has no user-controlled command construction.
- The importer contains no shell invocation, `os.system`, arbitrary command execution, or title/path-derived SQL.

These findings do not offset the mapping-contract defects above.

## 6. Test Evidence

Independent runs:

```text
content-production/import/pwe-tooling/tests/test_pwe_import.py: 16 passed
apps/backend/tests/test_content_import_schema.py + test_document_import.py: 18 passed
```

The tests do not cover a wrong pre-existing Entity type/name, an altered accepted edition candidate, or a rejected/review-required mapping row being denied by the importer; these omissions are consistent with the blockers above.

PWE_IT02_ACCEPTANCE=FAIL

FUNCTIONAL_ACCEPTANCE=FAIL
BASELINE_ACCEPTANCE=FAIL

REPOSITORY_IDENTITY=PASS
WORKTREE_STATE=DIRTY_UNTRACKED_PREEXISTING_AND_CANDIDATE_FILES
IMPLEMENTATION_TRACKED=NO
MAPPING_BASELINE_TRACKED=NO
UNRELATED_CHANGES=YES

MAPPING_CONTRACT_ENFORCED=FAIL
EXACT_SET_VALIDATION=FAIL
DEFERRED_EXCLUSION=PASS

DRY_RUN_ZERO_WRITE=PASS

TEMP_DB_FIRST_APPLY=PASS
TEMP_DB_RERUN=PASS
IDEMPOTENCY=PASS
RERUN_EXACT_SET=PASS

ATOMICITY=PASS
ROLLBACK=PASS

PRODUCTION_GUARD=PASS
HFM_PROD_WRITE_EXECUTED=NO

DOCUMENT_WRITE_PATH=ABSENT
DOCUMENT_BASELINE_PROTECTION=PASS

TOOLING_TESTS=16 passed
BACKEND_TESTS=18 passed
SECURITY_BLOCKERS=NONE

PWE_TOOLING_BASELINE_STATUS=UNFROZEN
NEXT_PHASE=BLOCKED
NEXT_ACTION=REPAIR_MAPPING_CONTRACT_ENFORCEMENT_THEN_FREEZE_PWE_TOOLING_BASELINE

PERSON_IMPORT=UNAUTHORIZED
WORK_IMPORT=UNAUTHORIZED
EDITION_IMPORT=UNAUTHORIZED
PUBLICATION=UNAUTHORIZED
UI_CONTENT_PROPAGATION=UNAUTHORIZED

BLOCKER=CONFIRMED_MAPPING_STATUS_NOT_ENFORCED;FROZEN_MAPPING_BASELINE_NOT_PINNED;ENTITY_COLLISION_VALIDATION_INCOMPLETE;UNTRACKED_IMPLEMENTATION_AND_MAPPING
STOP=YES
