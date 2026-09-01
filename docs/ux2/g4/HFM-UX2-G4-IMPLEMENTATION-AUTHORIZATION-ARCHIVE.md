# HFM-UX2 G4 Implementation Authorization Archive

Status: UX2-G4 IMPLEMENTATION_AUTHORIZED_AND_ARCHIVED · Immutable
implementation-authorization baseline
Pre-UX2 Production UI Baseline (frozen, untouched):
`ae55abc606c419f27259fc80bb8bee258d595ce9`

## 1. Archive Identity

```text
UX2_G0_G3_ACCEPTANCE_ARCHIVE_BASELINE=
e8593ffc7eec98584b3d69207a9bcd95e1698f8d

UX2_G4_IMPLEMENTATION_AUTHORIZATION_BASELINE=
<this commit> (SHA recorded in the archive delivery report / final state)

G4_INDEPENDENT_VERDICT=
UX2_G4_IMPLEMENTATION_AUTHORIZED

P0_FINDINGS=
0

P1_FINDINGS=
0

G4_AC=
17/17 PASS

PRODUCTION_DELTA_AT_AUTHORIZATION=
ZERO

AUTHORIZED_CANDIDATES=
12

CitationExport=
DEFERRED

Later Scholarship=
DEFERRED

G4-O-1=
CLOSED_DOCUMENTATION_ONLY
```

## 2. Scope of the Archive

This commit contains ONLY the accepted G4 authorization artifacts
(`docs/ux2/g4/**`) required to bind the implementation authorization. It is a
governance baseline, not a production implementation commit.

```text
docs/ux2/g4/**   — G4 authorization package + authorization archive + manifest
```

Forbidden in this commit: `apps/**` · `packages/**` · `backend/**` ·
`infra/**` · `scripts/**` · `prototype/**`.

## 3. Authorized Implementation State

```text
PRODUCTION_IMPLEMENTATION=
AUTHORIZED_ONLY_WITHIN_ACCEPTED_WP_DAG_AND_FILE_ALLOWLIST
```

Authorized candidates (12):

```text
C-01 DHObjectLayout         C-02 BibliographicRecord
C-03 Person surface         C-04 Jiayi surface
C-05 Heritage surface       C-06 Scholarly Discovery
C-07 Homepage Exhibition Narrative
C-08 Presentation-state mapping
C-09 Semantic token roles   C-10 Responsive semantics
C-11 Accessibility requirements
C-12 CitationLocator
```

F-5 determinations:

```text
Life Events = AUTHORIZE · Historical Assessments = AUTHORIZE
Archival Media = AUTHORIZE · Later Scholarship = DEFER
```

CitationLocator granularity:

```text
DOCUMENT_LEVEL_EXISTING_GRANULARITY_ONLY
```

No page-level invention (U-04 stays UNRESOLVED).

## 4. Preserved Deferred / Unresolved Items

```text
CitationExport       = DEFERRED
F-5 Later Scholarship = DEFERRED
U-01 = UNRESOLVED · U-02 = UNRESOLVED · U-03 = UNRESOLVED
U-04 = UNRESOLVED · U-05 = UNRESOLVED
```

No archive step promotes them; no domain/API/schema field is introduced for
them.

## 5. N-F-1 Production Contract (frozen)

```text
titleTag = 1..6                    → semantic h1..h6
titleTag = null | undefined | "none" → non-heading <p>
anything else including 0          → invalid → fail-closed <p> + development warning

0 = NOT_A_VALID_PRODUCTION_TITLETAG_VALUE
```

No domain/API/schema field may be introduced for this behavior.

## 6. G4-O-1 Closure (documentation-only)

`G4-O-1 = CLOSED_DOCUMENTATION_ONLY`. `components/search/BibliographyEntry.vue`
now has one deterministic allowlist rule in the implementation contract:
`ALLOW_MODIFY_ONLY_IN_UX2-P4`; outside UX2-P4: `FORBIDDEN_TO_MODIFY`. Scope and
allowlist were not widened.

## 7. G4 Authorization Manifest

Full inventory with SHA-256:
`docs/ux2/g4/HFM-UX2-G4-IMPLEMENTATION-AUTHORIZATION-MANIFEST.md` (committed
alongside this record).

## 8. Integrity & Freeze

```text
MANIFEST_FILE_COUNT = ARCHIVED_G4_FILE_COUNT
SHA256_MATCH = 100% (recomputed at freeze)
MISSING = 0 · EXTRA = 0
PRODUCTION_IMPLEMENTATION_DELTA = ZERO (parent unchanged)
```

## 9. Parent Relationship (proven at archive time)

```text
HEAD^ = e8593ffc7eec98584b3d69207a9bcd95e1698f8d
```

The authorization archive's parent is the G0–G3 acceptance archive baseline,
proving the freeze added governance only — production implementation was not
modified.

## 10. Next Execution Frontier

```text
NEXT_EXECUTION_FRONTIER = UX2-P0 (Shared Presentation Primitives)
```

UX2-P0 is a SEPARATE operation. Do NOT start P1–P7; do NOT combine work
packages; do NOT implement UX2-P0 in the same operation as this archive.
