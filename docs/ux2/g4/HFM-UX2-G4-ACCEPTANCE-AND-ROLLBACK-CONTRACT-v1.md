# HFM-UX2 G4 Acceptance & Rollback Contract v1

Status: UX2-G4 NORMATIVE ARTIFACT · Package-ready for independent review
Binding: Production Implementation Contract v1 + Work Package DAG v1.

## 1. Responsive Acceptance Contract

Production acceptance tests at minimum viewport widths: `375 · 768 · 1440 ·
1920` across all authorized surfaces (P1–P5). Required for every surface:

```text
NO_HORIZONTAL_OVERFLOW              (document scrollWidth ≤ clientWidth)
SEMANTIC_ORDER_PRESERVED            (DOM/render order unchanged by reflow)
EVIDENCE_ACCESS_PRESERVED           (source/status/citation affordances reachable)
HERITAGE_CONTEXT_SEPARATION_PRESERVED (historical vs contemporary never merged)
RELATION_SEMANTICS_PRESERVED        (EXPLICIT_RELATION/ASSOCIATED_CONTEXT/
                                      CO_PRESENTED_ONLY labels intact)
```

Verification tooling: Playwright e2e (`apps/frontend/e2e/ux2-*.spec.ts`),
reusing the existing project matrix approach (375/768/1024/1440/1920 + 200%
zoom where already covered).

## 2. Accessibility Acceptance Contract

Required on every authorized production surface:

```text
axe violations = 0                      (axe-core, project standard)
heading hierarchy correct               (no level skips; titleTag contract)
keyboard accessibility                  (all interactions reachable)
focus visibility                        (visible :focus-visible ring)
status not color-only                   (text label + token color)
semantic structure                      (landmarks, headings, lists, dl)
reduced motion where applicable         (prefers-reduced-motion guard)
```

No new project-wide accessibility standard is introduced (G1-A §8).

## 3. Test Contract

For each production WP (P0–P6):

```text
unit tests            — Vitest, src/__tests__/ux2_*.spec.ts
component tests       — Vitest + @vue/test-utils (project setup)
route/render tests    — existing per-surface suites (ui03…ui12 style) extended
negative-boundary tests — NB-01…NB-12 assertions per surface
responsive checks     — Playwright e2e matrix (375/768/1440/1920)
accessibility checks  — axe + heading/keyboard/focus/reduced-motion assertions
```

Reuse existing project test infrastructure (Vitest + Playwright). No new test
framework solely for UX2. Existing suites (`ui02_shell` … `ui13_polish`,
`p2_*`) must remain green (regression gate).

## 4. Rollback Contract

Every WP is independently reversible:

```text
PRE_WP_BASELINE         — the accepted commit before the WP starts
                          (production baseline ae55abc… → G0–G3 archive
                          e8593ff… → each prior WP acceptance baseline)
IMPLEMENTATION_CANDIDATE — the WP's change set on its branch/worktree
ACCEPTANCE_BASELINE     — the accepted post-WP state (only after independent
                          acceptance of the WP)
ROLLBACK_TARGET         — PRE_WP_BASELINE for an unaccepted candidate
```

Rules:

- No later WP may destroy the ability to return to the previous accepted
  baseline (no destructive migrations, no irreversible edits to data/types).
- Each WP's changes are confined to its allowed files (§14 allowlist), so
  revert = restore the WP's file set.
- WPs P6/P7 are verification-only and need no rollback path beyond reverting
  their test files.
- Rollback does not require schema/API/migration operations (none exist in
  scope).

## 5. Acceptance Evidence Contract

Every WP must produce machine-verifiable evidence. Visual screenshots alone
are insufficient. At minimum:

```text
changed-file list          — git diff --name-status per WP
production diff            — git diff -- apps packages (must stay bounded to
                             allowlisted files; final delta ZERO at handover)
test results               — Vitest + Playwright output
negative-boundary results  — NB-01…NB-12 assertion outputs
responsive results         — 375/768/1440/1920 matrix output
accessibility results      — axe output (0 violations) + heading/keyboard/focus
data provenance samples    — for every new UI string: source object + field
baseline parent            — git rev-parse HEAD^ identity
worktree status            — git status --short (no unexpected files)
```

## 6. G4 Acceptance Criteria (self-check)

| ID | Criterion | Verification | Self-check |
| --- | --- | --- | --- |
| G4-AC-01 | authoritative archive baseline correctly bound | contract binds `e8593ff…` + `ae55abc…` | PASS |
| G4-AC-02 | production targets mapped to real repository paths | surface mapping §1 — all paths inspected from `apps/frontend` | PASS |
| G4-AC-03 | authorization scope finite | 12 candidates, each with finite change boundary | PASS |
| G4-AC-04 | file allowlist finite and fail-closed | contract §14; NOT_EXPLICITLY_ALLOWED = FORBIDDEN | PASS |
| G4-AC-05 | no backend/domain/schema/API expansion | invariant NO/NO/NO; architecture boundaries §9 | PASS |
| G4-AC-06 | prototype not auto-promoted | contract §8 DO_NOT_PORT; allowlist excludes prototype copy-in | PASS |
| G4-AC-07 | unresolved data remains unresolved | U-01…U-05 carry-forward, no schema invention | PASS |
| G4-AC-08 | CitationExport remains deferred | contract §3 | PASS |
| G4-AC-09 | N-F-1 production semantics resolved contractually | contract §5 (1..6 / null·none / fail-closed; 0 invalid) | PASS |
| G4-AC-10 | historical/relation boundaries preserved | contract §10 + NB-02/03/04 | PASS |
| G4-AC-11 | clinical boundary preserved | contract §11 CLINICAL=REJECTED, violation → P0 | PASS |
| G4-AC-12 | token contract deterministic | contract §13; tokens.css READ_ONLY; no new palette/hex | PASS |
| G4-AC-13 | responsive/accessibility acceptance deterministic | this contract §1/§2 | PASS |
| G4-AC-14 | WP DAG finite and rollback-safe | DAG v1 §3 (8 WPs, per-WP reversible) | PASS |
| G4-AC-15 | acceptance evidence contract machine-verifiable | this contract §5 | PASS |
| G4-AC-16 | production remains unchanged during G4 preparation | verified: HEAD `e8593ff…` (archive), `git diff -- apps packages` = 0 | PASS |
| G4-AC-17 | package sufficient for independent implementation-authorization decision | five artifacts + evidence chain complete | PASS |

```text
G4-AC-01…17 = ALL PASS
```

## 7. Exit State

```text
RESPONSIVE_CONTRACT = DETERMINISTIC · ACCESSIBILITY_CONTRACT = DETERMINISTIC
TEST_CONTRACT = EXISTING_INFRA_ONLY · ROLLBACK_CONTRACT = PER_WP_REVERSIBLE
EVIDENCE_CONTRACT = MACHINE_VERIFIABLE
UX2_G4 = PACKAGE_READY / PENDING_INDEPENDENT_REVIEW
```
