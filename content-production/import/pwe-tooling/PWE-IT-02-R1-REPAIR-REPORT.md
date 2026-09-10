# PWE-IT-02-R1 — ACCEPTANCE BLOCKER REPAIR REPORT

GENERATED_AT: 2026-09-10
PHASE: PWE_IT-02 Acceptance Blocker Repair (minimal; no importer redesign)
FROZEN: DMIT03_ACCEPTANCE=PASS · DATA_MAPPING_PHASE=CLOSED · DOCUMENT_BASELINE=675 (protected)

## B01 — Runtime enforcement of the formal signed mapping status

Consumed the REAL signature fields (no new semantics invented):
`review/{PERSON,WORK,EDITION}-CONFIRMATION-REVIEW.csv` → `recommendation`
(`CONFIRM_RECOMMENDED` = accepted candidate; `DEFER_RECOMMENDED` = deferred).

Runtime rules now enforced in `load_baseline` (before any DB operation):

- every PERSON/WORK row must carry `CONFIRM_RECOMMENDED`; otherwise `BaselineContractError`;
- every EDITION row must carry `CONFIRM_RECOMMENDED` (non-deferred) or `DEFER_RECOMMENDED` (the 5 deferred);
- **any other value** (`UNCONFIRMED` / `REVIEW_REQUIRED` / `REJECTED` / `UNKNOWN`) → fail closed;
- signed stable-id sets must equal the mapping artifact sets exactly (an unsigned row cannot import);
- presence in CSV + `confidence=HIGH` + resolvable candidate is **no longer sufficient**.

Evidence: hash-independent tamper test — a copied baseline whose review file is edited to
`UNCONFIRMED`/`REVIEW_REQUIRED` **and re-manifested to be self-consistent** is still refused (B01 alone rejects).

```
SIGNED_MAPPING_ENFORCEMENT=PASS
```

## B02 — Frozen mapping baseline identity verification

New controlled manifest `content-production/import/pwe-mapping/MAPPING-BASELINE-MANIFEST.json`
records `relative_path` + `sha256` + `size` for every consumed input and a derived
`mapping_baseline_id`; the id is **pinned in the importer** (`EXPECTED_MAPPING_BASELINE_ID`), so the
importer never auto-recomputes and accepts a new hash.

Controlled inputs (7): `01-entity-bootstrap.csv`, `02-work-canonical-map.csv`, `03-edition-work-map.csv`,
`04-person-identity-map.csv`, `review/PERSON-CONFIRMATION-REVIEW.csv`,
`review/WORK-CONFIRMATION-REVIEW.csv`, `review/EDITION-CONFIRMATION-REVIEW.csv`.

Every run verifies: manifest present → controlled-input set exact (no extra/missing) → per-file sha256+size →
manifest id consistency → pinned id equality. Any deviation → fail closed before DB access.

```
MAPPING_BASELINE_INTEGRITY=PASS
MAPPING_BASELINE_ID=077fd6222eff612978b0aeec93810691f6554f8dbbfe0affa6c4d751ed75594b
```

Tamper tests: content change → REFUSED · status change → REFUSED · missing file → REFUSED · replaced file → REFUSED.

## B03 — Controlled Git baseline

```
PWD=/Users/likeming/Sites/hfm   BRANCH=hfm-canonical
PRE_REPAIR_HEAD=5c7253dfd088c64fc991e951f04d196cb3ae1d74
REPAIR_COMMIT=fff2f39c354fe1b35d8125bf712260bc924df9ce
PARENT=5c7253dfd088c64fc991e951f04d196cb3ae1d74
ANCESTRY=PASS
```

Staged inventory was exactly the 20 authorized artifacts (16 pwe-mapping incl. manifest + 4 pwe-tooling);
`AUTHORIZED_DIFF_ONLY=PASS`. No unrelated file was staged.

```
IMPORTER_TRACKED=YES   TESTS_TRACKED=YES   MAPPING_BASELINE_TRACKED=YES   MANIFEST_TRACKED=YES
```

(Report commit follows immediately after this artifact; final head reported to Codex.)

## Re-verification (measured on this round's code)

```
tooling tests                24 passed   (16 core + 8 B01/B02 tamper & pinned-id tests)
relevant backend tests       18 passed   (test_content_import_schema + test_document_import)

DRY_RUN_ZERO_WRITE=PASS      TRANSACTION_RESULT=DRY_RUN_NO_WRITE; probe rows after dry-run = 0
TEMP_DB_FIRST_APPLY=PASS     COMMITTED; entities=31 persons=17 person_aliases=1 works=14 editions=87
TEMP_DB_RERUN=PASS           created 0 / existing 31,17,14,87 → IDEMPOTENCY=PASS
ROLLBACK=PASS                fail_inject=after_works → ROLLED_BACK; 0/0/0/0 (no partial graph)
PRODUCTION_GUARD=PASS        guard unit tests (fake hfm_prod on sqlite + authorization matrix) refuse;
                             no production dry-run/apply was performed this round
DOCUMENT_BASELINE_PROTECTION=PASS
disposable probe DB cleanup  leftover=0
hfm_prod read-only final     documents=675 persons=0 works=0 editions=0 entities=0
```

Core behavior untouched: transaction model, import order, entity/person/work/edition identity, deferred set,
production guard, and the 17/14/87/5 sets are unchanged.

## Verdict

```text
PWE_IT02_R1_REPAIR=PASS

B01_SIGNED_MAPPING_ENFORCEMENT=PASS
B02_MAPPING_BASELINE_INTEGRITY=PASS
B03_GIT_BASELINE_FREEZE=PASS

MAPPING_BASELINE_ID=077fd6222eff612978b0aeec93810691f6554f8dbbfe0affa6c4d751ed75594b

PERSON_SET=17
WORK_SET=14
EDITION_CONFIRMED_SET=87
EDITION_DEFERRED_SET=5
EXACT_SET_VALIDATION=PASS

IMPORTER_TRACKED=YES
TESTS_TRACKED=YES
MAPPING_BASELINE_TRACKED=YES
MANIFEST_TRACKED=YES

PRE_REPAIR_HEAD=5c7253dfd088c64fc991e951f04d196cb3ae1d74
REPAIR_COMMIT=fff2f39c354fe1b35d8125bf712260bc924df9ce
POST_REPAIR_HEAD=fff2f39c354fe1b35d8125bf712260bc924df9ce (report commit follows; final head to Codex)
ANCESTRY=PASS
AUTHORIZED_DIFF_ONLY=PASS
WORKTREE_CLEAN=YES

SIGNED_STATUS_TAMPER_TEST=PASS
MAPPING_HASH_TAMPER_TEST=PASS

DRY_RUN_ZERO_WRITE=PASS
TEMP_DB_FIRST_APPLY=PASS
TEMP_DB_RERUN=PASS
IDEMPOTENCY=PASS
ROLLBACK=PASS
PRODUCTION_GUARD=PASS

DOCUMENT_BASELINE_PROTECTION=PASS
HFM_PROD_WRITE_EXECUTED=NO

TOOLING_TESTS=24 passed
BACKEND_TESTS=18 passed (relevant)

READY_FOR_CODEX_REACCEPTANCE=YES

PERSON_IMPORT=UNAUTHORIZED
WORK_IMPORT=UNAUTHORIZED
EDITION_IMPORT=UNAUTHORIZED

NEXT_ACTION=CODEX_PWE_IT02_REACCEPTANCE
BLOCKER=
STOP=YES
```
