# PWE-IT-02-R1 — Codex Independent Re-Acceptance

Date: 2026-09-10  
Scope: read-only acceptance of the candidate baseline. No repository implementation,
mapping, schema, migration, hfm_prod dry-run, production apply, or publication action
was performed.

## Candidate identity and baseline governance

`HEAD` is `92f206c85ddbc4a6403c2c323de063aa665ecde3` on `hfm-canonical`.
Its parent is `fff2f39c354fe1b35d8125bf712260bc924df9ce`; the latter's parent is
`5c7253dfd088c64fc991e951f04d196cb3ae1d74`. The fixed-point diff contains
exactly 21 authorized PWE mapping/tooling/report paths: 20 implementation and
mapping artifacts in the repair commit plus this tracked R1 repair report.

All required importer, tests, frozen mapping, review/signature CSVs, manifest,
DMIT-03 acceptance, PWE-IT-01 report, PWE-IT-02 report, and R1 repair report
are tracked. However, before this acceptance report was created the repository
had 0 staged paths, 0 unstaged tracked paths, and **4018 untracked paths**.
Therefore this is not a clean candidate worktree. This report is an additional
untracked audit artifact and does not rebaseline that condition.

## B01 — signed mapping state

The importer consumes all three formal review CSVs and validates their
`recommendation` fields before database connection. It requires the exact signed
sets: 17 PERSON and 14 WORK `CONFIRM_RECOMMENDED`, 87 non-deferred EDITION
`CONFIRM_RECOMMENDED`, and the exact five deferred EDITION
`DEFER_RECOMMENDED` values.

I performed an independent causal test in a temporary mapping copy: changed a
PERSON recommendation to `UNCONFIRMED`, regenerated a self-consistent manifest,
and set the test process's expected ID to that regenerated manifest ID. The
importer refused before database access with
`BaselineContractError: ... illegal/unsigned recommendation 'UNCONFIRMED'`.

Result: B01 is closed.

## B02 — immutable mapping baseline

`MAPPING-BASELINE-MANIFEST.json` controls exactly seven consumed inputs by
relative path, SHA-256, and size. The importer verifies the exact input set,
per-file values, manifest self-consistency, and its pinned baseline identity
before database connection. Independently computed and verified ID:

`077fd6222eff612978b0aeec93810691f6554f8dbbfe0affa6c4d751ed75594b`

Independent selected tests for content tamper, mapping-status tamper, and
missing controlled input passed (3 passed); the full tooling suite passed (24
passed). Each is refused through `load_baseline` before database connection.

Result: B02 is closed.

## Functional evidence

Relevant backend tests passed (18 tests; command exited 0 with no failure/error
output). A temporary PostgreSQL 16 target migrated to 0015 was used, then
deleted. It produced:

| Check | Independent result |
| --- | --- |
| dry-run | 31 entities, 17 persons, 14 works, 87 editions predicted; 5 deferred; zero writes |
| first apply | committed 31 / 17 / 14 / 87 |
| rerun | created 0; existing 31 / 17 / 14 / 87 |
| exact sets | entities, persons, works, editions each exactly matched frozen mapping; no deferred edition inserted |
| injected failure after works | `ROLLED_BACK`; post-check entities/persons/works/editions all 0 |

The production guard unit behavior remains fail-closed and requires the
production target plus `HFM_ENV=prod` and explicit authorization. No hfm_prod
command was run. Read-only hfm_prod verification after temporary testing showed
documents=675 and entities/persons/works/editions=0. The tool has no DOCUMENT
write path.

No SQL injection, shell invocation, arbitrary command execution, or path-
traversal security blocker was found. There are non-security lint/hygiene
findings (line length/async blocking write and preserved CRLF diagnostics in
frozen mapping artifacts); they do not alter this R1 safety verdict and are not
used to rebaseline the candidate.

## Decision

B01 and B02 are functionally closed. B03 remains open solely because the
candidate repository worktree is not clean. Thus functional acceptance passes,
but commit-bound baseline acceptance and the aggregate R1 gate fail. No
production dry-run or apply is authorized.

```text
PWE_IT02_R1_ACCEPTANCE=FAIL

B01_STATUS=CLOSED
B02_STATUS=CLOSED
B03_STATUS=OPEN

FUNCTIONAL_ACCEPTANCE=PASS
BASELINE_ACCEPTANCE=FAIL

REPOSITORY_IDENTITY=PASS
CANDIDATE_HEAD=92f206c85ddbc4a6403c2c323de063aa665ecde3
WORKTREE_CLEAN=NO
AUTHORIZED_DIFF_ONLY=PASS

SIGNED_MAPPING_STATE_ENFORCED=PASS
UNSIGNED_MAPPING_FAIL_CLOSED=PASS

EXPECTED_MAPPING_BASELINE_ID=077fd6222eff612978b0aeec93810691f6554f8dbbfe0affa6c4d751ed75594b
ACTUAL_MAPPING_BASELINE_ID=077fd6222eff612978b0aeec93810691f6554f8dbbfe0affa6c4d751ed75594b
MAPPING_BASELINE_ID_MATCH=PASS
MAPPING_BASELINE_INTEGRITY=PASS

IMPLEMENTATION_TRACKED=YES
MAPPING_BASELINE_TRACKED=YES
MANIFEST_TRACKED=YES

EXACT_SET_VALIDATION=PASS

ENTITY_EXPECTED=31
PERSON_EXPECTED=17
WORK_EXPECTED=14
EDITION_EXPECTED=87
EDITION_DEFERRED=5

DRY_RUN_ZERO_WRITE=PASS
TEMP_DB_FIRST_APPLY=PASS
TEMP_DB_RERUN=PASS
IDEMPOTENCY=PASS
ROLLBACK=PASS

PRODUCTION_GUARD=PASS
DOCUMENT_BASELINE_PROTECTION=PASS
HFM_PROD_WRITE_EXECUTED=NO

TOOLING_TESTS=24 passed
BACKEND_TESTS=18 passed, exit 0, no FAILED/ERROR output
SECURITY_BLOCKERS=NONE

PWE_TOOLING_BASELINE_STATUS=REJECTED
PWE_TOOLING_BASELINE=92f206c85ddbc4a6403c2c323de063aa665ecde3

NEXT_PHASE=BLOCKED
NEXT_ACTION=RESOLVE_WORKTREE_GOVERNANCE_BLOCKER_WITH_A_CLEAN_COMMIT_BOUND_CANDIDATE

PERSON_IMPORT=UNAUTHORIZED
WORK_IMPORT=UNAUTHORIZED
EDITION_IMPORT=UNAUTHORIZED
PRODUCTION_APPLY=UNAUTHORIZED
PUBLICATION=UNAUTHORIZED
UI_CONTENT_PROPAGATION=UNAUTHORIZED

BLOCKER=WORKTREE_NOT_CLEAN:4018_PREEXISTING_UNTRACKED_PATHS_AT_ACCEPTANCE_START
STOP=YES
```
