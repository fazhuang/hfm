# HFM-UX2-P1 Implementation Evidence v1

Status: UX2-P1 IMPLEMENTATION CANDIDATE · ready for independent audit
(pre-WP baseline `2b315795e43faf92e03cd3db2c74b18c47c0927e`)

## 1. WP Identity

```text
WP = UX2-P1 · Person Archive
PRE_WP_BASELINE = 2b315795e43faf92e03cd3db2c74b18c47c0927e
DEPENDENCIES = UX2-P0 SATISFIED (frozen acceptance baseline 2b315795 includes P0)
```

## 2. Implementation Scope (from frozen WP DAG + G4 contract candidate 03)

```text
IN_SCOPE:
  PersonDetailView adopts DHObjectLayout (context/evidence/relations regions;
  header ABSENT_OPTIONAL — the hero owns the object title at H1)
  G1-C presentation states: RESOURCE_READY (identities/definition; 其传/后论
  FULL_TEXT), SCHOLARLY_UNCERTAIN (生卒年 note, DERIVED from verified 其传
  考据), METADATA_ONLY (四论原典全文未收录), ABSENT_OPTIONAL (portrait/holding)
  F-5: Life Events (existing 生平 timeline verified) · Historical Assessments
  (后论 real content from readerDocuments houlun) · Archival Media (existing
  影像资料 verified)
  heading hierarchy correct (single H1; no skips)

OUT_OF_SCOPE:
  F-5 Later Scholarship (DEFERRED — not added) · new fields ·
  data/types/router/services/api modifications · UX2-P0 primitive changes ·
  UX2-P2/P3/P4/P5/P6/P7
```

Note on contract wording: the WP DAG listed `METADATA_ONLY (其传/后论 文稿)`.
Per source precedence (production data contracts rank above WP shorthand),
`readerDocuments.ts` marks 其传/后论 `FULL_TEXT`/`AVAILABLE`, so G1-C row 1
applies → they render `RESOURCE_READY 全文已整理`. The `METADATA_ONLY` state is
still demonstrated on the page via the 四论 原典全文未收录 incomplete note.
P0-1 (`role="status"`) is untouched — the frozen DHObjectLayout primitive's
behavior is used as accepted.

## 3. Changed Paths

| Path | Change |
| --- | --- |
| `apps/frontend/src/views/persons/PersonDetailView.vue` | MODIFY — DHObjectLayout block (语境·证据·关联); G1-C states; 其传/后论 real reader content (F-5) |
| `apps/frontend/src/__tests__/ux2_p1_person.spec.ts` | CREATE — 14 tests (regions/states, F-5, heading, negative boundaries, axe) |
| `apps/frontend/e2e/ux2-p1-person.spec.ts` | CREATE — real-browser person surface proof (states, 后论/其传, single h1, 375px overflow) |
| `docs/ux2/g4/HFM-UX2-P1-IMPLEMENTATION-EVIDENCE-v1.md` | CREATE — this record |

## 4. Acceptance Criteria (frozen WP DAG DoD)

| Criterion | Result |
| --- | --- |
| person page renders DHObjectLayout regions + states | PASS — context/evidence INCOMPLETE_WITH_EVIDENCE_STATE, relations PRESENT, header ABSENT_OPTIONAL (collapsed) |
| heading order correct | PASS — single H1; DHObjectLayout header non-rendered; no level skips (tested) |
| F-5 authorized sections from real data | PASS — Life Events (timeline), Historical Assessments (houlun FULL_TEXT), Archival Media (movies) |
| G1-C states | PASS — RESOURCE_READY / SCHOLARLY_UNCERTAIN / METADATA_ONLY / ABSENT_OPTIONAL |
| Later Scholarship NOT added | PASS — tested absent |
| suite green | PASS (below) |

## 5. Test / Quality Results

```text
TARGETED_TESTS      = 14/14 PASS (ux2_p1_person.spec.ts)
P0_REGRESSION_TESTS = 58/58 PASS (ux2_p0_* — P0_REGRESSION = NONE)
FULL_VITEST         = 267/267 PASS (30 files)
VUE_TSC             = PASS (0 errors)
ESLINT              = 0 errors (modified view carries pre-existing style warnings,
                      consistent with repo baseline of 942 warnings; gate is errors)
VITE_BUILD          = PASS
PLAYWRIGHT          = 68/68 PASS (67 existing + 1 new UX2-P1)
AXE                 = 0 (P1 page axe test; P0 harness 0)
```

## 6. Negative Boundaries

```text
NB-01 no historical fabrication         PASS (render existing data only)
NB-02 no relation inference             PASS (relations text-only; EXPLICIT_RELATION/
                                          ASSOCIATED_CONTEXT labels; no svg/connector)
NB-05 clinical                          PASS (no clinical content)
NB-06 no citation synthesis             PASS (no 第X卷/页/章; locator text only)
NB-07 missing ≠ historical absence      PASS (fail-closed via G1-C mapping)
F-5 Later Scholarship deferred          PASS (not rendered)
```

## 7. Data / Domain Impact

ZERO domain change — readerDocuments/archiveInventory/corePerson read-only;
`resolvePresentationState`/`presentationLabel` (P0) consumed presentation-only.
No API/schema/route/auth change. U-01…U-05 unchanged (UNRESOLVED).
CitationExport untouched (DEFERRED).

## 8. Worktree Status

```text
 M apps/frontend/src/views/persons/PersonDetailView.vue
?? apps/frontend/src/__tests__/ux2_p1_person.spec.ts
?? apps/frontend/e2e/ux2-p1-person.spec.ts
?? docs/ux2/g4/HFM-UX2-P1-IMPLEMENTATION-EVIDENCE-v1.md
(pre-existing excluded untracked dirs docs/research/ hfmzl/ zzcl/ remain)
```

## 9. Rollback

```text
ROLLBACK_TARGET = 2b315795e43faf92e03cd3db2c74b18c47c0927e (PRE_WP_BASELINE)
```

View-only change; route unchanged; revert = restore PersonDetailView + drop test/evidence files.

## 10. Commit

```text
UX2_P1_IMPLEMENTATION_CANDIDATE = <commit SHA recorded at delivery>
CANDIDATE_PARENT = 2b315795e43faf92e03cd3db2c74b18c47c0927e
OUT_OF_SCOPE_CONFIRMED = YES
```
