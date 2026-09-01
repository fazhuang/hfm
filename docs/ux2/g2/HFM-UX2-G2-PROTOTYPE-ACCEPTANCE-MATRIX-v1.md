# HFM-UX2 G2 Prototype Acceptance Matrix v1

Status: UX2-G2 NORMATIVE ARTIFACT · Results finalized in the audit report.
Each criterion is machine- or inspection-verifiable against `prototype/ux2/`
and the frozen baseline.

> ⚠ CORRECTIVE OVERLAY (UX2-G2 corrective pass) — the Claude Independent Audit
> found one criterion initially failing: G2-AC-12 (heading-order defect, F-1
> P1 BLOCKING). The corrective pass resolved F-1…F-5; full correction record:
> `HFM-UX2-G2-CORRECTIVE-PASS-v1.md`. G2-AC-12 re-adjudicated PASS after
> re-verification (axe clean on all six pages). Original rows below are
> preserved unchanged as the pre-audit state of record.

| ID | Criterion | Verification | Result |
| --- | --- | --- | --- |
| G2-AC-01 | All 5 representative surfaces exist | 5 HTML pages + primitive hub in `prototype/ux2/` | (audit report) |
| G2-AC-02 | Both core primitives demonstrably reusable | DHObjectLayout renders 3 slot states; BibliographicRecord renders 5 kinds | (audit report) |
| G2-AC-03 | All visible facts trace to authoritative data | Data Binding Ledger closure; no unbound string | (audit report) |
| G2-AC-04 | Five unresolved source-field classes remain unresolved | U-01…U-05 dispositions: collapse or incomplete state, no synthesis | (audit report) |
| G2-AC-05 | No domain/API/DB expansion | `git diff -- apps packages` empty; no schema text | (audit report) |
| G2-AC-06 | No unsupported relation inference | PT-NB-02/03/04 pass; no connector implying lineage | (audit report) |
| G2-AC-07 | Heritage historical/contemporary contexts separated | P3 renders two semantic bands, not one timeline | (audit report) |
| G2-AC-08 | Clinical boundary zero-tolerance | PT-NB-05 pass; no clinical guidance text | (audit report) |
| G2-AC-09 | Presentation-state behavior conforms to G1-C | RESOURCE_READY/METADATA_ONLY/SCHOLARLY_UNCERTAIN/DATA_GAP labels map per G1-C | (audit report) |
| G2-AC-10 | Token use conforms to G1-B | hex scan ⊆ frozen tokens.css values; no new palette | (audit report) |
| G2-AC-11 | Responsive semantics PASS | 375/768/1280/1920 no horizontal scroll; meaning preserved | (audit report) |
| G2-AC-12 | Accessibility checks PASS | axe-clean; keyboard; focus; color-independent status; reduced motion | (audit report) |
| G2-AC-13 | G1-D negative matrix PASS | PT-NB-01…12 all pass | (audit report) |
| G2-AC-14 | Frozen production implementation unchanged | `git status` production delta empty; baseline SHA intact | (audit report) |
| G2-AC-15 | Prototype sufficient to decide future production authorization | All five surfaces + both primitives demonstrated with real data | (audit report) |

## Corrective Pass Result (UX2-G2 · see HFM-UX2-G2-CORRECTIVE-PASS-v1.md)

| ID | Criterion | Corrective result |
| --- | --- | --- |
| G2-AC-12 | Accessibility checks PASS | **PASS (re-verified)** — F-1 fixed: object title level now declared per surface via `renderDHObjectLayout` `titleTag` (presentation-only); axe 0 violations on ALL six pages (was 1 heading-order violation on p01); PT-NB-01…12 PASS; responsive 0 overflow; token 35/35 ZERO drift; production delta ZERO |

```text
F-1 CORRECTED · F-2 CORRECTED · F-3 CLARIFIED · F-4 CORRECTED · F-5 DEFERRED_NON_BLOCKING
UX2_G2_CORRECTED_CANDIDATE_READY_FOR_REAUDIT · PENDING_REAUDIT
```
