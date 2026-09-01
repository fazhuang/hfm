# HFM-UX2 G3 Risk & Deferred Items Register v1

Status: UX2-G3 NORMATIVE ARTIFACT · Package-ready for independent audit
Frozen UI Baseline: `ae55abc606c419f27259fc80bb8bee258d595ce9`
Binding: G1-C §5 `SOURCE_FIELD_UNRESOLVED` findings (U-01…U-05) + G2
corrective pass F-5 + Claude independent-audit observation N-F-1.

Rule: **deferred/unresolved items are NOT G4 implementation assumptions.**
Each entry below states what it is needed for, its current status, and its
explicit non-assumption disposition.

## 1. Deferred Items Register — U-01…U-05 (source fields)

| # | Item | Needed for | Current status | G4 disposition |
| --- | --- | --- | --- | --- |
| U-01 | Dedicated scholarly-controversy field (person date disputes 建安/正始) | `SCHOLARLY_UNCERTAIN` state | UNRESOLVED — predicate `DERIVED_PRESENTATION_ONLY` from verified 其传 text; P1 renders the controversy note | NOT an implementation assumption; G4 renders from verified text predicate, does not add a domain field |
| U-02 | Explicit loss-recorded flag (逸士传/列女传 辑佚) | `HISTORICAL_ABSENCE` state | UNRESOLVED — predicate `DERIVED_PRESENTATION_ONLY` from verified text | NOT an implementation assumption; loss never inferred from data absence |
| U-03 | Edition holding/source institution field | BibliographicRecord hierarchy | UNRESOLVED — editions carry imprint; holding institution not a field; P2 slot collapses | NOT an implementation assumption; slot stays ABSENT_OPTIONAL |
| U-04 | Citation page/volume-level locator fields | CitationLocator depth | UNRESOLVED — locator renders at document/section level only; P4 page-level collapsed | NOT an implementation assumption; CitationLocator renders existing fields only |
| U-05 | Per-edition digitized-resource flag | distinguishing 存目 vs 数字资源可阅 per edition | UNRESOLVED — all 19 editions `METADATA_ONLY`; P2 renders 存目 uniformly | NOT an implementation assumption; no fake digitized state, no forced flag |

## 2. G2 Legacy — F-5 Deferred Person Coverage

Status: `DEFERRED_COVERAGE` · `NON_BLOCKING` · `NO_G2_SCOPE_EXPANSION`
(recorded in `HFM-UX2-G2-CORRECTIVE-PASS-v1.md` §5; carried into G3 formally).

The P1 Person prototype does not cover:

```text
Life Events
Historical Assessments
Later Scholarship
Archival Media
```

These are `DEFERRED_COVERAGE` — explicitly registered coverage gaps, NOT
"遗漏待补" (omissions to be patched). Whether they enter production scope is a
G4/G5 decision. G3 makes no coverage promise and no implementation plan for
them.

## 3. N-F-1 Register — titleTag:0 Latent Edge Case

| Field | Value |
| --- | --- |
| Source | Claude Independent Audit observation (post-corrective-pass) |
| ID | N-F-1 |
| Finding | `renderDHObjectLayout` header slot accepts presentation-only `titleTag` ('h1'..'h6' / 1..6 / 'p' / 0 / 'none'). The renderer's enforcement check uses truthiness (`slot.titleTag`), so `titleTag: 0` (documented as non-heading `<p>`) is treated as "no titleTag" and the re-tag is skipped, leaving the surface-built tag in place — a truthiness ambiguity between the documented contract and the enforcement condition. |
| Current usage | No prototype page uses `titleTag: 0` (surfaces use `2` and `3`). |
| Severity | `P2` |
| Blocking | `NO` (`BLOCKING=NO`) |
| G3 action | Recorded only. **No prototype modification in G3.** |
| G4 precondition | IF G4 plans to formally reuse the `titleTag` API, the truthiness ambiguity MUST be eliminated before implementation (e.g., explicit `titleTag !== undefined && titleTag !== null` guard, or drop `0` from the documented vocabulary). Until then the contract documentation and enforcement must agree. |
| Verification pointer | `prototype/ux2/assets/js/ux2.js` — `renderDHObjectLayout` header-slot enforcement block; `dhObjectTitle` factory fallback. |

## 4. Negative Authorization Matrix (persistent UX2 contract boundary)

These prohibitions are NOT prototype limitations — they are continuously valid
UX2 contract boundaries. They bind any future G4 authorization:

| # | Prohibited | Governing rule |
| --- | --- | --- |
| N-01 | NEW DOMAIN MODEL | G1-A §10 / AC-12 |
| N-02 | GRAPH DATABASE REQUIREMENT | G1-A §1.1 NO_GRAPH_REQUIREMENT |
| N-03 | AI GENERATED HISTORICAL CONTENT | G1-A §1.3 / NB-01 |
| N-04 | AI HISTORICAL PORTRAIT | G1-A §1.3 / G2 P1 optional portrait collapse |
| N-05 | INFERRED EDITION GENEALOGY | G1-A §1.6 / NB-03 (JIAYI_EDITION_RELATIONS DATA-GAP) |
| N-06 | INFERRED HERITAGE LINEAGE | G1-A §4.3 / NB-04 (LINEAGE_STRUCTURING PARTIAL) |
| N-07 | CLINICAL RECOMMENDATION | NB-05 |
| N-08 | THERAPEUTIC CLAIM | NB-05 |
| N-09 | UNVERIFIED MARKETING COPY | G1-A §9 homepage boundary |
| N-10 | HFB RUNTIME DEPENDENCY | G2 isolation guarantee NO_HFB_RUNTIME_DEPENDENCY |
| N-11 | NEW LARGE UI FRAMEWORK | G1-B §0 NO_LARGE_UI_LIBRARY |
| N-12 | ARBITRARY DESIGN TOKEN | G1-B §3 new-token justification |
| N-13 | NEWS-PORTAL HOMEPAGE | G1-A §9 homepage grammar |
| N-14 | HONOR-WALL DOMINANT HERITAGE PAGE | G1-A §4 / G2 F-4 recognition secondary metadata |

## 5. Risk Register

| # | Risk | Likelihood | Impact | Trigger | Blocking Status | Mitigation |
| --- | --- | --- | --- | --- | --- | --- |
| R-01 | Prototype code auto-promoted to production (equivalence fallacy) | Low | High | G4 copies `prototype/ux2` files verbatim into `apps/` or treats them as production source | NO | Production Mapping §3 (scope matrix): DESIGN_REQUIREMENT / IMPLEMENTATION_REFERENCE_ONLY / PROTOTYPE_ONLY; G3-AC-04 |
| R-02 | `titleTag` contract/enforcement mismatch resurfaces in G4 (N-F-1) | Medium | Medium | G4 reuses the `titleTag` API without first resolving the truthiness ambiguity (N-F-1 G4 precondition unmet) | NO | G4 precondition in §3 above; add contract test at implementation time |
| R-03 | Fixture drift between prototype and frozen data sources | Medium | Medium | Frozen data source values change without ledger/manifest update, or PT-NB suite not re-run after a fixture change | NO | Data-binding ledger closure; production reads authoritative sources; PT-NB re-run per change |
| R-04 | U-05 default (all editions 存目) masks a real digitized resource | Low | Medium | A production edition gains a digitized resource while U-05 remains UNRESOLVED and rendering guesses status | NO | U-05 stays UNRESOLVED; G4 renders only what the authoritative field states; no forced flag |
| R-05 | Facet semantic ambiguity regresses (档案 inventory-count vs search-index count) | Low | Low | G4 implements the archive facet from `ARCHIVE_RECORDS.length` instead of search-index type counts | NO | F-3 semantic recorded in fixture provenance + ledger; G4 implements search-index type counts |
| R-06 | Deferred person coverage (F-5) mistaken for planned scope | Medium | Low | F-5 items (Life Events / Historical Assessments / Later Scholarship / Archival Media) appear in a G4 backlog without a scope decision | NO | §2 DEFERRED_COVERAGE register; no G4 plan |
| R-07 | New palette/token introduced during implementation | Low | High | A new hex or `--hfm-*` token is introduced without G1-B justification | NO | G1-B scan rule (NB-09); new-token justification rule |
| R-08 | Clinical or honor-wall content creeps into heritage/home surfaces | Low | High | PT-NB-05 or honor-wall checks fail on a heritage/home surface in G4 | NO | PT-NB-05 zero-tolerance; negative matrix N-07/N-08/N-14 |

## 6. Exit State

```text
DEFERRED_REGISTER_COMPLETE = TRUE (U-01…U-05, F-5, N-F-1)
NEGATIVE_AUTHORIZATION_MATRIX = COMPLETE (N-01…N-14)
UX2_G4 = NOT_AUTHORIZED
PRODUCTION_IMPLEMENTATION = LOCKED
```

## 7. G3 Audit Closure — G3-F-1

```text
G3-F-1 = CLOSED_DOCUMENTATION_ONLY
```

Claude G3 audit finding G3-F-1 (SEVERITY=P2): the risk register schema lacked
explicit `Trigger` and `Blocking Status` columns. Closed in this revision by
adding both columns to the R-01…R-08 table above. `Blocking Status = NO` for
all entries, consistent with the accepted G3 audit (no blocking risks). No
substantive risk decision (likelihood / impact / mitigation) was changed.
N-F-1 (titleTag:0) remains OPEN as an accepted known observation — see §3.
