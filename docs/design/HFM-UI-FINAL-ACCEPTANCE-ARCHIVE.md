# HFM UI OPTIMIZATION — FINAL ACCEPTANCE ARCHIVE & FREEZE

Status: FORMAL UI ACCEPTANCE ARCHIVE · FROZEN
Date: 2026-09-01

## Formal identity

```
Original Pre-UI Candidate Base:      094713bd06c56ef67499724925cb8a2219e1b4c8
Accepted UI Implementation Candidate:329b983f660b79a67f600af78ec6655408292d53
Formal UI Optimization Completion Baseline: this commit (acceptance archive/freeze commit)

Accepted implementation bytes are represented by the Candidate commit
`329b983f…`; this archive commit contains no runtime implementation change.
```

Phase-2 (untouched, unchanged, still canonical):

```
Phase-2 Governance Baseline:          7fa7c4f60244daa6999e377d08502bde522c56b2
Frontier-3 Acceptance Baseline:       cd8176dac880f4229a2979aca51b6d5e8d638036
Formal Phase-2 Completion Baseline:   50572a4eba453c3eafa396e48e632a6ac49db73e
```

`parent(UI_IMPLEMENTATION_CANDIDATE) = 094713bd…`; this archive commit's
parent is the Candidate; the Candidate's accepted implementation bytes are
represented by that commit. The Formal Phase-2 Completion Baseline remains
uniquely `50572a4…` — the UI Optimization is an independent post-Phase-2 UI
workstream and does not supersede or replace it.

## Included UI WP Set

`[UI-01, UI-02, UI-03, UI-04, UI-06, UI-07, UI-08, UI-09, UI-10, UI-11, UI-12, UI-13, UI-14]`

(UI-05 Timeline is an absorbed dependency component; UI-12 covers the
Cross-Surface Audit + P1/P2 correction.)

## Scope Closure

PASS

## Issue counts

```
P0: 0
P1: 0
P2: 3 NON-BLOCKING
```

P2 non-blocking findings:

1. Historical ESLint warnings (0 errors; warnings pre-date this workstream).
2. jsdom Canvas warning — axe tooling observation, no business change made.
3. lens-guard `session_mismatch` blocks `git diff --check` in some harness
   invocations; equivalent whitespace scans pass (0 trailing whitespace /
   0 tab indentation across all staged/committed additions).

## Final Tests (clean-room, re-run from the committed Candidate tree)

| Gate | Result |
| --- | --- |
| typecheck | PASS |
| lint | PASS (0 errors) |
| format:check | PASS |
| vitest | 195/195 PASS (24 files) |
| build | PASS |
| e2e | 67/67 PASS |
| git diff --check (committed tree) | PASS |

## Final Invariants

```
PUBLIC_PRIMARY_NAV_COUNT       = 5
CANONICAL_PERSON_ROUTE         = /persons/person-huangfu-mi
AUDITED_PAPER_TOTAL            = 515
SEARCHABLE_PAPER_TOTAL         = 5
EDITION_TOTAL                  = 19
FULL_TEXT_DOCUMENT_TOTAL       = 2 (后论 · 其传)
SEARCH_INDEX_COUNT             = 1
JIAYI_LINEAGE_STATUS           = DATA-GAP
HERITAGE_LINEAGE_STATUS        = PARTIAL
LIU_JUNQI_GENERATION           = 第六代名医
RBAC_REGRESSION                = PASS
PHASE2_CONTRACT_REGRESSION     = PASS
FAKE_ANCIENT_TEXT_CREATED      = NO
FAKE_METADATA_CREATED          = NO
UNVERIFIED_HERITAGE_LINEAGE    = NO
INTERNAL_SOURCE_PATH_EXPOSED   = NO (rendered surface; data-layer provenance only)
SENSITIVE_DATA_EXPOSED         = NO
COPYRIGHT_BLOCKERS_REINTRODUCED = NO
CLINICAL_MEDICAL_CONTENT       = NO
```

## Customer Source Assets Changed

NO (`hfmzl/`, `zzcl/` remain untracked customer corpus, byte-unchanged)

## Governance Changed

NO

## Formal Phase-2 Baseline Touched

NO

## Excluded / Deferred (unchanged from UI-14 freeze candidate)

- AI / RAG / semantic search
- 3D / WebGL / VR / XR
- annotation persistence backend
- notebook / collaboration / user collections
- full-text migration engineering
- complete 515-paper structuring (stays PARTIAL)
- Jiayi inferred structured lineage (stays DATA-GAP)
- first–fifth heritage lineage reconstruction (stays PARTIAL)
- the four unavailable ancient full texts (stay METADATA_ONLY / DATA_GAP)
- Exhibition / large-screen standalone app

## Final Verdict

`HFM_UI_OPTIMIZATION_ACCEPTED_FOR_ARCHIVE_AND_FREEZE`
