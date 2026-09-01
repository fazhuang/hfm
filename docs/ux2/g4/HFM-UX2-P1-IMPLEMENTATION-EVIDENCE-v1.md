# HFM-UX2-P1 Implementation Evidence v1 (Fourth Corrective · V5)

Status: UX2-P1 GOVERNANCE_BLOCKED · scope restored · F-5 contract satisfiability
escalated (rejected V1 `7f603d3…`, V2 `af337eb…`, V3 `c5fb206…`,
V4 `87a316d…`)

## 1. WP Identity

```text
WP = UX2-P1 · Person Archive
PRE_WP_BASELINE = 2b315795e43faf92e03cd3db2c74b18c47c0927e
REJECTED_V1 = 7f603d385e258e62afab7dca6eba5210ed8a2d68
REJECTED_V2 = af337ebc00f210ce1ef331503e8a95ae25b701dd
REJECTED_V3 = c5fb2064c5b67b61eea9fa43dc5cc8dd706bd5ee
REJECTED_V4 = 87a316d5240174fcda91cc24a40e65954f2a61bb
CORRECTIVE_BASIS = rejected V4 (linear successor; no amend/squash)
```

## 2. This Corrective Pass — Scope Restoration & F-5 Contract Satisfiability

Two audit blockers were addressed:

| Blocker | Disposition |
| --- | --- |
| P0-03 FORBIDDEN_PRODUCTION_DATA_ARCHITECTURE | CLOSED — V4 production data architecture fully reverted (§3) |
| P1-01 F5_REAL_MEDIA_RUNTIME_CHAIN | BLOCKED_BY_FROZEN_CONTRACT — F-5 is UNSATISFIABLE within the frozen P1 allowlist (§4–§7) |

## 3. P0-03 Closure — Forbidden V4 Production Delta Reverted

The V4 corrective introduced production data architecture outside the frozen
P1 allowlist. All of it is removed:

```text
REVERTED:
  apps/frontend/src/data/archiveInventory.ts  → ARCHIVE_MEDIA_RECORDS block removed
                                                (restored to pre-V4 state)
  apps/frontend/src/data/mediaProjection.ts   → deleted (projectPublicMedia removed)
```

```text
FORBIDDEN_V4_PRODUCTION_DELTA = ZERO
P0-03 = CLOSED
```

Pre-existing, unrelated data (`a-movies` aggregate, `INVENTORY_MOVIES`) and
valid earlier P1 fixes (P0-01/P0-02/P1-02 + PersonDetailView corrections) are
preserved. Real customer media files (`hfmzl/皇甫谧/皇甫谧电影/`) are NOT
deleted and their bytes are NOT modified.

## 4. F-5 Contract Satisfiability Determination

### Frozen P1 allowlist (exact, from governance)

```text
UX2_P1_ALLOWED_PRODUCTION_PATHS =
  MODIFY: apps/frontend/src/views/persons/PersonDetailView.vue
  CREATE: apps/frontend/src/__tests__/ux2_p1_*.spec.ts
          apps/frontend/e2e/ux2-p1-*.spec.ts
  (source: HFM-UX2-G4-WORK-PACKAGE-DAG-v1.md UX2-P1 row)

UX2_P1_FORBIDDEN_PATHS =
  data/** modification · types/** · router/** · services/** (services/api.ts)
  backend/** · packages/** · migrations/** · schema/** · server/**
  new media registry · new media projection · new storage/import architecture
  (source: WORK-PACKAGE-DAG UX2-P1 "Production Files Forbidden" +
           PRODUCTION-IMPLEMENTATION-CONTRACT-v1 §14 READ_ONLY/FORBIDDEN)
```

### F-5 authoritative requirement

```text
F5_AUTHORITATIVE_REQUIREMENT =
  F-5 "Archival Media" AUTHORIZE (G4 Implementation Authorization Archive §6)
  requires the person page's 影像资料 to render the real customer movies
  through the production chain.

F5_REQUIRED_DATA_STATE =
  real per-media source records that the production public media endpoint can
  return (backend media_assets rows for the two movies, or an equivalent
  admitted projection).

F5_REQUIRED_RUNTIME_PROOF =
  /api/v1/public/media (or canonical equivalent) → fetchPublicMedia('movie')
  → PersonDetailView → rendered metadata, with fields traceable to the real
  per-media source.
```

### Actual production runtime state (observed)

```text
REAL_MEDIA_FILES_EXIST = YES
  hfmzl/皇甫谧/皇甫谧电影/皇甫谧一.mpg (1,009,262,592 B)
  hfmzl/皇甫谧/皇甫谧电影/《针灸鼻祖皇甫谧》第1集 大器晚成.mpg (718,133,252 B)

EXISTING_BACKEND_MEDIAASSET_RECORDS_FOR_THE_TWO_MOVIES = NO
  media_assets schema exists (alembic 0014) but has NO rows; no seed/import data

EXISTING_PUBLIC_API_RETURNS_THE_TWO_MOVIES = NO
  /api/v1/public/media → MediaService.public_projection() over empty table

EXISTING_RUNTIME_fetchPublicMedia_RETURNS_THE_TWO_MOVIES = NO
  (same — endpoint returns nothing for the two movies)

P1_ALLOWLIST_PERMITS_CREATING_MISSING_RECORDS = NO
  data/** is READ_ONLY / FORBIDDEN; backend/migrations FORBIDDEN

P1_ALLOWLIST_PERMITS_CHANGING_API_PROJECTION = NO
  services/api.ts FORBIDDEN; backend FORBIDDEN
```

### Decision

```text
CASE = B (production chain does not exist and cannot legally be created inside P1)

F5_WITHIN_FROZEN_P1_SCOPE = UNSATISFIABLE
ROOT_CAUSE = CONTRACT_CAPABILITY_MISMATCH
```

Explanation: F-5 requires a real `source → governed per-media record →
production API → runtime → render` chain. The real source files exist, but the
governed per-media records (backend media_assets rows) and the API projection
capability do not exist in the frozen production state, and the frozen P1
allowlist prohibits creating/modifying them (data/**, services/**, backend/**).
A frontend registry/projection substitute was attempted in V4 and was itself
rejected as P0-03 FORBIDDEN_PRODUCTION_DATA_ARCHITECTURE. Therefore F-5 cannot
be satisfied within the frozen P1 scope. No fake PASS, no new fixture, no new
frontend registry, no backend change were made in this pass.

## 5. Governance Blocker Evidence (P1-authorized evidence path)

```text
F5_CONTRACT_SATISFIABILITY = FAIL
BLOCKER_ID = UX2-P1-F5-CONTRACT-CAPABILITY-MISMATCH
MISSING_CAPABILITY =
  governed per-media source records (backend media_assets rows for the two
  movies) and/or the production public media projection/API capability that
  returns them — none exists in the frozen production state.

F5_REQUIRES =
  real source → governed per-media record → production API → runtime
  (fetchPublicMedia('movie')) → PersonDetailView render, with field-level
  provenance (id/name/mime_type/byte_size/license_basis/object_key).

P1_ALLOWLIST_FORBIDS =
  apps/frontend/src/data/** (modification — READ_ONLY)
  apps/frontend/src/services/** (api.ts modification — FORBIDDEN)
  backend/** · migrations/** · schema/** (FORBIDDEN)
  new media registry / projection / storage-import architecture (FORBIDDEN)

EXISTING_RUNTIME_STATE =
  real files exist (hfmzl/皇甫谧/皇甫谧电影/, 2 × .mpg, bytes verified);
  media_assets table empty; /api/v1/public/media returns no movie records;
  fetchPublicMedia('movie') returns none; a-movies aggregate + INVENTORY_MOVIES
  describe the collection at inventory granularity only.

REQUIRED_GOVERNANCE_DECISION = ONE_OF (NOT chosen here; frozen governance NOT amended):
  A. amend UX2-P1 allowlist to authorize the minimal real media
     admission/projection work;
  B. reclassify real media admission/projection into a prerequisite WP and
     make P1 depend on it;
  C. amend F-5 acceptance semantics to match the actual existing P1 capability.
```

This is a governance escalation. The F-5 media runtime chain is not an ordinary
code defect; it requires a governance decision on which capability layer may be
authorized.

## 6. Test / Quality Results (independently reproduced)

```text
TARGETED_TESTS      = 14/14 PASS (ux2_p1_person.spec.ts — media-proof tests
                      removed; valid P0-02 / reader / heading / axe tests kept)
P0_REGRESSION_TESTS = 58/58 PASS (ux2_p0_* — P0_REGRESSION = NONE)
FULL_VITEST         = 267/267 PASS (30 files)
VUE_TSC             = PASS (0 errors)
ESLINT              = 0_ERRORS_965_WARNINGS (actual reproduction; repo-wide
                      pre-existing style-warning baseline; gate is errors)
VITE_BUILD          = PASS
PLAYWRIGHT          = 72/72 PASS (67 existing + 5 UX2-P1)
BROWSER_AXE         = 0 (real browser, full rule set)
P0_PRIMITIVE_DELTA  = ZERO
READER_QICHUAN_NAVIGATION = PASS · READER_HOULUN_NAVIGATION = PASS
KEYBOARD = PASS · FOCUS = PASS · RESPONSIVE_375/1280/1920 = PASS
```

## 7. Preserved Guarantees

```text
P0-01 = CLOSED · P0-02 = CLOSED · P1-02 = CLOSED · P2-02 = CLOSED
PROVENANCE = PASS · ACCESSIBILITY = PASS · RESPONSIVE = PASS
P0_REGRESSION = NONE · P0_PRIMITIVE_IMPLEMENTATION_DELTA = ZERO
P0-1 = OPEN_P2_NON_BLOCKING_REVERIFY_AT_P6 (role="status" untouched)
P2-01 = OPEN_DOCUMENTATION_ONLY_CLOSE_AT_ACCEPTANCE_ARCHIVE
```

## 8. Worktree Status

```text
git status --short → CLEAN (local .git/info/exclude isolates pre-existing
unrelated untracked material)
```

## 9. Rollback

```text
ROLLBACK_TARGET = 2b315795e43faf92e03cd3db2c74b18c47c0927e (PRE_WP_BASELINE)
```

## 10. Commit

```text
UX2_P1_CORRECTED_CANDIDATE_V5 = <commit SHA recorded at delivery>
CANDIDATE_PARENT = 87a316d5240174fcda91cc24a40e65954f2a61bb (rejected V4)
FORBIDDEN_PRODUCTION_PATH_DELTA = ZERO
OUT_OF_SCOPE_CONFIRMED = YES (UX2-P2..P7 delta ZERO; P0 primitive delta ZERO)
```
