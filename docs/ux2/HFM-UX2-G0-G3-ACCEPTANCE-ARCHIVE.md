# HFM-UX2 G0–G3 Acceptance Archive

Status: UX2-G0…G3 ACCEPTED_AND_ARCHIVED · Immutable governance archive baseline
Semantic distinction (this archive does NOT redefine the pre-UX2 production baseline):

```text
PRE_UX2_PRODUCTION_UI_BASELINE
=
ae55abc606c419f27259fc80bb8bee258d595ce9

UX2_G0_G3_ACCEPTANCE_ARCHIVE_BASELINE
=
<this commit> (SHA recorded in the archive delivery report / final state)
```

## 1. Archive Identity

```text
Project:
HFM Digital Humanities Experience 2.0

Pre-UX2 Production UI Baseline:
ae55abc606c419f27259fc80bb8bee258d595ce9

UX2-G0:
ACCEPTED

UX2-G1:
ACCEPTED

UX2-G2:
ACCEPTED

UX2-G3:
ACCEPTED

G2 Final Independent Verdict:
UX2_G2_ACCEPTED

G3 Final Independent Verdict:
UX2_G3_ACCEPTED

UX2-G4:
NOT_YET_AUTHORIZED

Production Implementation:
LOCKED
```

## 2. Scope of the Archive

The archive commit contains ONLY the accepted UX2 G0–G3 governance and
prototype evidence required for the acceptance chain:

```text
docs/ux2/**        — G1 contracts + G2/G3 governance + acceptance archive
prototype/ux2/**   — G2 prototype evidence (isolated; never promoted to production)
```

Excluded (not UX2 accepted artifacts; never staged):

```text
hfmzl/**      EXCLUDE
zzcl/**       EXCLUDE
docs/research/** EXCLUDE
apps/**       ZERO_DELTA (frozen production untouched)
packages/**   ZERO_DELTA
```

Full inventory with SHA-256: `HFM-UX2-G0-G3-ACCEPTANCE-ARCHIVE-MANIFEST-v1` →
`docs/ux2/HFM-UX2-G0-G3-ACCEPTANCE-ARCHIVE-MANIFEST.md` (committed alongside).

## 3. Archived Governance State

```text
U-01…U-05 = UNRESOLVED / NO_IMPLEMENTATION_ASSUMPTION
CitationExport = DEFERRED
F-5 = DEFERRED_COVERAGE
N-F-1 = P2 / NON_BLOCKING / G4_PRECONDITION_IF_REUSED
G3-F-1 = CLOSED_DOCUMENTATION_ONLY
```

N-F-1 (titleTag:0 truthiness ambiguity) is archived as an accepted known
observation; it remains OPEN — it must be resolved before any G4 reuse of the
`titleTag` API. G3-F-1 was closed in this archive by a documentation-only
schema correction (Trigger + Blocking Status columns added to the R-01…R-08
risk register); no substantive risk decision changed.

## 4. Evidence Chain (G0 → G3)

| Gate | Artifacts | Verdict |
| --- | --- | --- |
| G0 | frozen UI baseline `ae55abc…` preserved | ACCEPTED |
| G1 | PRESENTATION-CONTRACT · DESIGN-TOKEN-MAPPING-SPEC · PRESENTATION-STATE-MATRIX · NEGATIVE-BOUNDARY-VERIFICATION-MATRIX | ACCEPTED |
| G2 | prototype evidence (`prototype/ux2/**`) + PLAN · DATA-BINDING · ACCEPTANCE-MATRIX · AUDIT-REPORT · CORRECTIVE-PASS | ACCEPTED (`UX2_G2_ACCEPTED`) |
| G3 | DESIGN-ACCEPTANCE-PACKAGE · IMPLEMENTATION-SCOPE-MATRIX · RISK-AND-DEFERRED-ITEMS · AUTHORIZATION-READINESS-REPORT | ACCEPTED (`UX2_G3_ACCEPTED`) |

## 5. Integrity & Freeze

```text
FROZEN_PRE_UX2_UI_BASELINE = ae55abc606c419f27259fc80bb8bee258d595ce9
PRODUCTION_IMPLEMENTATION_DELTA = ZERO
SHA256_MATCH = 100% (see manifest; re-verified at freeze)
MANIFEST_FILE_COUNT = ARCHIVED_FILE_COUNT
MISSING = 0
EXTRA = 0
```

The archive commit is `UX2_G0_G3_ACCEPTANCE_ARCHIVE`. It is NOT a production
implementation baseline, NOT a G4 implementation candidate, NOT a prototype
production merge.

## 6. Parent Relationship (proven at archive time)

```text
HEAD^ = ae55abc606c419f27259fc80bb8bee258d595ce9
```

The archive commit's parent is the frozen pre-UX2 production UI baseline,
proving the archive adds governance/prototype evidence only — production
implementation was not modified.

## 7. Next Operation

```text
NEXT_GATE = UX2-G4_IMPLEMENTATION_AUTHORIZATION_REVIEW
UX2-G4 = NOT_YET_AUTHORIZED
```

The next operation requires a separate UX2-G4 Implementation Authorization
Review using this archive baseline as its authoritative governance input.
