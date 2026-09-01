# HFM-UX2 G4 Authorization Decision Package v1

Status: UX2-G4 NORMATIVE ARTIFACT · Package-ready for independent review
Binding: Production Implementation Contract v1 · Surface Mapping v1 ·
Work Package DAG v1 · Acceptance & Rollback Contract v1.

## 1. Authoritative Archive Baseline

```text
PRE_UX2_PRODUCTION_UI_BASELINE   = ae55abc606c419f27259fc80bb8bee258d595ce9
UX2_G0_G3_ACCEPTANCE_ARCHIVE_BASELINE = e8593ffc7eec98584b3d69207a9bcd95e1698f8d
PRODUCTION_IMPLEMENTATION = LOCKED
```

## 2. Authorization Candidate Matrix

| Candidate | Recommendation | Dependencies | Risk | Evidence | Decision Basis |
| --- | --- | --- | --- | --- | --- |
| 01 DHObjectLayout | AUTHORIZE | — | Low (create-only; N-F-1 contract fixes ambiguity) | G1-A §1, G2 P1/index, G3 item 1 | proven reusable primitive; presentation-only; no data/API change |
| 02 BibliographicRecord | AUTHORIZE | P0 | Low (create-only; degrade rules) | G1-A §2, G2 P2/P4, G3 item 2 | proven 5 kinds; field degradation normative |
| 03 Person surface | AUTHORIZE | P0 | Medium (view refactor) | G1-A §1/§6, G1-C, G2 P1, F-5 | production view exists; delta bounded; F-5 items data-backed |
| 04 Jiayi surface | AUTHORIZE | P0 | Low | G1-A §2, G2 P2, G3 item 4 | 19 editions + DATA-GAP already data-backed |
| 05 Heritage surface | AUTHORIZE | P0 | Low | G1-A §4, G2 P3, G3 item 5 | two-context separation already data-backed |
| 06 Scholarly Discovery | AUTHORIZE | P0 | Low | G1-A §2/§3, G2 P4, G3 item 6 | facets already search-index semantic (F-3); locator document-level |
| 07 Homepage narrative | AUTHORIZE | P0,P1,P2,P3,P4 | Low | G1-A §9, G2 P5, G3 item 7 | frozen narrative already implemented |
| 08 Presentation-state mapping | AUTHORIZE | — | Medium (vocabulary extension) | G1-C, G3 item 8 | deterministic mapping; no synthetic flags |
| 09 Semantic token roles | AUTHORIZE | — | Low | G1-B, G3 item 9 | existing tokens; roles applied only |
| 10 Responsive semantics | AUTHORIZE | P1–P5 | Low | G1-A §7, G2, G3 item 10 | acceptance matrix deterministic |
| 11 Accessibility requirements | AUTHORIZE | P1–P5 | Medium (heading contract) | G1-A §8, G2 F-1, G3 item 11 | axe 0 + heading-order testable |
| 12 CitationLocator | AUTHORIZE | P1,P2,P4 | Low | G1-A §3.1, G2 P4, G3 item 12 | reuse existing CitationBlock; U-04 collapsed |
| CitationExport | DEFER | — | — | G3 item, capability gate | no data change; no new formats |
| F-5 Later Scholarship | DEFER | — | — | no authoritative person-scholarship projection | data not confirmed |

## 3. Deferred / Blocked Items

```text
DEFERRED:
  CitationExport                        (capability-gated; unchanged since G3)
  F-5 Later Scholarship                 (no confirmed person-scholarship data)
  U-01…U-05                             (UNRESOLVED / NO_IMPLEMENTATION_ASSUMPTION)

BLOCKED: none
EXCLUDED: negative authorization N-01…N-14 (contract boundary; never in scope)

N-F-1 = P2 / NON_BLOCKING / resolved contractually for production (1..6 → heading;
        null·undefined·'none' → non-heading; anything else incl. 0 → fail-closed)
```

## 4. N-F-1 Resolution Contract (summary)

Production `titleTag`: `1..6 → h1..h6` · `null | undefined | 'none' →
non-heading <p>` · any other value (including `0`) → fail-closed non-heading
`<p>` + deterministic dev warning. `0` is invalid in production; no falsy
ambiguity. Contract decision only — no production code changed.

## 5. Architecture Boundary Verification

```text
NO_DATABASE_CHANGE · NO_SCHEMA_CHANGE · NO_DOMAIN_MODEL_CHANGE
NO_API_CONTRACT_CHANGE · NO_AUTH_CHANGE · NO_RBAC_CHANGE
NO_GRAPH_DATABASE · NO_HFB_RUNTIME_DEPENDENCY · NO_NEW_LARGE_UI_FRAMEWORK
ROUTE_CHANGE_REQUIRED = NO · API_CHANGE_REQUIRED = NO · SCHEMA_CHANGE_REQUIRED = NO
```

## 6. Content / Clinical Boundary Verification

```text
NO_HISTORICAL_FABRICATION · NO_RELATION_INFERENCE · NO_EDITION_GENEALOGY_INFERENCE
NO_HERITAGE_LINEAGE_INFERENCE · NO_UNVERIFIED_PUBLIC_COPY
CLINICAL = REJECTED (violation → P0)
```

## 7. Production Delta Verification (G4 preparation)

```text
git rev-parse HEAD          → e8593ffc7eec98584b3d69207a9bcd95e1698f8d
git diff -- apps packages   → EMPTY (0 lines)
git status --short          → untracked only: docs/research/ hfmzl/ zzcl/
                              (docs/ux2 + prototype/ux2 committed in archive)
PRODUCTION_IMPLEMENTATION_DELTA = ZERO
```

G4 preparation changed governance documentation only (`docs/ux2/g4/**`).

## 8. Final Pi Verdict

```text
UX2_G4_AUTHORIZATION_PACKAGE_READY_FOR_INDEPENDENT_REVIEW
```

Pi does NOT authorize implementation. Authorization authority belongs to the
independent review.

## 9. Hard Stop

```text
NO_PRODUCTION_UI_MODIFICATION
NO_WP_EXECUTION
NO_PROTOTYPE_MERGE
NO_ROUTE_REPLACEMENT
NO_SELF_AUTHORIZATION
```

## 10. Terminal State

```text
UX2-G4 = PACKAGE_READY / PENDING_INDEPENDENT_REVIEW
PRODUCTION_IMPLEMENTATION = LOCKED
```
