# PWE-IT-01 — P/W/E IMPORT TOOLING IMPLEMENTATION REPORT

GENERATED_AT: 2026-09-10
BASELINE_HEAD: 5c7253dfd088c64fc991e951f04d196cb3ae1d74 (hfm-canonical; unchanged by this round)
PHASE: PWE_IMPORT_TOOLING_IMPLEMENTATION

## 0. Deliverables

| Artifact | Path |
| --- | --- |
| Importer tooling | `content-production/import/pwe-tooling/hfm_import_pwe.py` |
| Test suite | `content-production/import/pwe-tooling/tests/test_pwe_import.py` |
| Mapping baseline consumed (read-only) | `content-production/import/pwe-mapping/01-te…04-…csv` |
| This report | `content-production/import/pwe-tooling/PWE-IT-01-IMPLEMENTATION-REPORT.md` |

No product source, schema, migration, or mapping baseline was modified.
Tooling lives in the untracked content-production evidence zone (no commit made this round).

## 1. Mapping contract enforcement (DMIT-03 frozen)

Consumed baseline (single source, no runtime inference):
`01-entity-bootstrap.csv` (31) · `02-work-canonical-map.csv` (14) · `03-edition-work-map.csv` (92) · `04-person-identity-map.csv` (17)

Hard validations implemented (fail-closed → `BaselineContractError`):

- entity rows == 31, split exactly 17 person / 14 work, unique `entity_stable_id`, type ∈ {person, work};
- person ↔ person-entity and work ↔ work-entity bootstrap identity reconciliation;
- work rows == 14, unique `work_stable_id`, non-empty frozen `work_type`;
- edition rows: deferred set must equal the exact DMIT-03 set `{A000541, A000529, A000530, A000531, A000532}`;
  every non-deferred row must be `mapping_confidence == HIGH`; every `candidate_work_stable_id` must exist in the
  14-WORK set; confirmed count must be exactly 87; no deferred row may carry CONFIRMED confidence.
- **No title matching / fuzzy matching / identity guessing / review promotion exists in the code.** The importer
  consumes the preselected candidate WORK id verbatim.

Deterministic identity (no auto-increment, no random UUID as identity):
`entities.id = ENT-PERSON-*/ENT-WORK-*` · `persons.entity_id = entities.id`, `persons.stable_id = PERSON-*` ·
`works.id/stable_id = WORK-*` · `editions.id/stable_id = EDITION-*` · `editions.work_id = candidate WORK id`.

Import order (real FK constraints, no FK disabling / NOT NULL relaxing / schema change):
`entities → persons (+ person_aliases) → works → editions`, all inside ONE transaction.

## 2. Real execution evidence (all numbers measured)

### 2.1 Tooling tests

```
apps/backend/.venv/bin/python -m pytest content-production/import/pwe-tooling/tests/test_pwe_import.py -q
→ 16 passed  (exit 0)
```

Coverage: mapping contract, exact-set (cross-checked against normalized source CSVs, not counts), deferred exclusion,
entity bootstrap, person (+alias)/work/edition import, FK resolution, missing-WORK fail-closed, duplicate stable_id,
identity collision, dry-run zero-write, injected rollback, idempotent rerun, production guard matrix, migration-head
guard, DOCUMENT baseline protection.

### 2.2 Dry-run on real PostgreSQL (disposable)

```
MODE=dry-run  TRANSACTION_RESULT=DRY_RUN_NO_WRITE  RESULT=PASS
ENTITY_CREATED=31  PERSON_CREATED=17  WORK_CREATED=14  EDITION_CREATED=87  EDITION_DEFERRED=5
DOCUMENT_BEFORE=0 DOCUMENT_AFTER=0 DOCUMENT_CHANGED=0
```

(no rows written; subsequent dry-run still predicted 31/17/14/87)

### 2.3 Temporary PostgreSQL — first apply

```
TRANSACTION_RESULT=COMMITTED  RESULT=PASS
ENTITY_CREATED=31 PERSON_CREATED=17 WORK_CREATED=14 EDITION_CREATED=87 EDITION_DEFERRED=5
post-apply DB: entities=31 persons=17 person_aliases=1 works=14 editions=87 documents=0
```

### 2.4 Temporary PostgreSQL — rerun (idempotency)

```
ENTITY_CREATED=0  PERSON_CREATED=0  WORK_CREATED=0  EDITION_CREATED=0
ENTITY_EXISTING=31 PERSON_EXISTING=17 WORK_EXISTING=14 EDITION_EXISTING=87  PERSON_SKIPPED=1(alias)
TRANSACTION_RESULT=COMMITTED  RESULT=PASS     → IDEMPOTENCY=PASS (no duplicate, no identity rewrite)
```

### 2.5 Temporary PostgreSQL — injected failure rollback

```
fail_inject=after_works → TRANSACTION_RESULT=ROLLED_BACK  RESULT=FAIL
post-rollback counts entities/persons/works/editions = 0/0/0/0   → no partial committed graph
```

### 2.6 Production guard (hfm_prod, real read-only)

```
DATABASE_IDENTITY=hfm_prod  DATABASE_TARGET_CLASS=PRODUCTION
TRANSACTION_RESULT=REFUSED  RESULT=FAIL
ERROR=ProductionGuardError: target is hfm_prod; --allow-hfm-prod + HFM_ENV=prod required
hfm_prod after: entities=0 persons=0 works=0 editions=0 documents=675  (unchanged)
```

### 2.7 Relevant backend tests + cleanup

```
pytest apps/backend/tests/test_content_import_schema.py tests/test_document_import.py → 18 passed (exit 0)
disposable probe DBs dropped → leftover=0 ; hfm_prod documents=675 ; git HEAD 5c7253d ; tracked changes=0
```

## 3. Residual (non-functional) notes

- pi-lens static heuristics flag the new tooling with false positives on parameterised/static `conn.execute(text(...))`
  ("SQL injection sink") and `subprocess.run` (S603) — no dynamic SQL/interpolation is used; recorded, not "fixed"
  by weakening the checks. These are tool-layer findings, not runtime defects.
- `05-person-work-evidence.csv` is deliberately NOT consumed (contract §8: relation writing unauthorized).

## Verdict (required block)

```text
PWE_TOOLING_IMPLEMENTED=YES

MAPPING_CONTRACT_ENFORCED=YES
RUNTIME_INFERENCE=FORBIDDEN
DEFERRED_EXCLUSION=PASS

ENTITY_EXPECTED=31
PERSON_EXPECTED=17
WORK_EXPECTED=14
EDITION_EXPECTED=87
EDITION_DEFERRED=5

EXACT_SET_VALIDATION=PASS

DRY_RUN=PASS
DRY_RUN_ZERO_WRITE=PASS

TEMP_DB_FIRST_APPLY=PASS
TEMP_DB_RERUN=PASS
IDEMPOTENCY=PASS
ROLLBACK=PASS

DOCUMENT_BASELINE_PROTECTION=PASS
PRODUCTION_GUARD=PASS

TESTS=16 tooling passed; 18 relevant backend passed
BLOCKERS=pi-lens static heuristic false positives (parameterised text()/subprocess) — non-functional, recorded

PWE_TOOLING_READY_FOR_CODEX_ACCEPTANCE=YES

HFM_PROD_WRITE_EXECUTED=NO

PERSON_IMPORT=UNAUTHORIZED
WORK_IMPORT=UNAUTHORIZED
EDITION_IMPORT=UNAUTHORIZED

NEXT_RECOMMENDED_ACTION=CODEX_PWE_TOOLING_ACCEPTANCE
STOP=YES
```
