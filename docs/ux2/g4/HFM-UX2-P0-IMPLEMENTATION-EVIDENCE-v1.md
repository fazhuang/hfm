# HFM-UX2-P0 Implementation Evidence v1

Status: UX2-P0 IMPLEMENTATION CANDIDATE · ready for independent audit
(pre-WP baseline `2a7fc468896f8a19d8129353164a8f463f635426`)

## 1. WP Identity

```text
CURRENT_WP = UX2-P0
WP_NAME   = Shared Presentation Primitives
PRE_WP_BASELINE = 2a7fc468896f8a19d8129353164a8f463f635426
ROLLBACK_TARGET = 2a7fc468896f8a19d8129353164a8f463f635426
```

## 2. Changed-File List

| File | Change | Allowlist class |
| --- | --- | --- |
| `apps/frontend/src/components/primitives/DHObjectLayout.vue` | CREATE — shared DHObjectLayout primitive (Header/Context/Evidence/Relations regions; PRESENT / ABSENT_OPTIONAL / INCOMPLETE_WITH_EVIDENCE_STATE; titleTag N-F-1 contract; text-only relations semantics) | ALLOW_CREATE |
| `apps/frontend/src/components/primitives/BibliographicRecord.vue` | CREATE — shared scholarly record primitive (5 kinds; optional-field degradation; no synthesis; document-level locator only) | ALLOW_CREATE |
| `apps/frontend/src/presentation/stateMapping.ts` | CREATE — deterministic G1-C SOURCE FACT → PRESENTATION STATE → PUBLIC LABEL mapping + N-F-1 `resolveTitleTag` (fail-closed) | ALLOW_CREATE |
| `apps/frontend/src/styles/foundations.css` | MODIFY — extend `.hfm-status` with G1-C presentation states + G1-B surface-role utilities (existing tokens only) | ALLOW_MODIFY |
| `apps/frontend/src/__tests__/ux2_p0_state_mapping.spec.ts` | CREATE — mapping matrix, precedence, labels, titleTag contract (incl. 0 / -1 / 7 / strings / NaN) | ALLOW_CREATE |
| `apps/frontend/src/__tests__/ux2_p0_dhobjectlayout.spec.ts` | CREATE — slot presence, collapse, incomplete visibility, titleTag DOM, relations, negative boundaries | ALLOW_CREATE |
| `apps/frontend/src/__tests__/ux2_p0_bibliographic_record.spec.ts` | CREATE — rendering, degradation, no synthesis, no CitationExport, locator passthrough | ALLOW_CREATE |
| `apps/frontend/src/__tests__/ux2_p0_a11y.spec.ts` | CREATE — axe harness over mounted primitives (component-level rules) | ALLOW_CREATE |
| `apps/frontend/src/__tests__/ux2_p0_token_scan.spec.ts` | CREATE — NB-09 no hard-coded hex in new production files | ALLOW_CREATE |
| `docs/ux2/g4/HFM-UX2-P0-IMPLEMENTATION-EVIDENCE-v1.md` | CREATE — this evidence record (governance path) | governance |

No file outside the G4 §14 UX2-P0 allowlist (+ this governance evidence record) was changed.

## 3. Implementation Rationale

- REUSE: existing `.hfm-status` badge pattern, EmptyState/state conventions, frozen tokens,
  Vue 3 SFC architecture, Vitest + Playwright infra.
- ADAPT: G2 prototype slot-presence semantics, BibliographicRecord field hierarchy, `hfm-status`
  pattern (extended, not replaced).
- MINIMAL NEW: exactly two presentation primitives + one presentation module.
- REJECTED: rewrite, new framework, parallel design system, prototype copy-in
  (production components are Vue SFCs; prototype JS/HTML not ported).

## 4. Data / Domain Impact

- ZERO domain change: no new fields, no synthetic flags (`is_gap`/`is_uncertain`/`is_complete`/`has_resource`);
  presentation predicates remain DERIVED_PRESENTATION_ONLY logic in `stateMapping.ts`.
- ZERO API/schema/database/auth/RBAC change. No route change. No new runtime dependency.
- U-01…U-05 remain UNRESOLVED; CitationExport not implemented (DEFERRED); page-level locator not invented (U-04).

## 5. Test Commands & Results

| Command | Result |
| --- | --- |
| `npx vitest run src/__tests__/ux2_p0_` | 5 files / 58 tests PASS (incl. axe harness: 0 violations) |
| `npx vitest run` (full) | 29 files / 253 tests PASS |
| `npx vue-tsc --noEmit` | PASS (0 errors) |
| `npx eslint "src/components/primitives/**" "src/presentation/**" "src/__tests__/ux2_p0_*"` | 0 errors (auto-fix applied; clean) |
| `npx eslint .` (full) | 0 errors (942 pre-existing warnings; unchanged) |
| `npx vite build` | PASS (170 modules; built in 1.60s) |
| `npx playwright test` (e2e) | 67/67 PASS (no regression on any production surface) |

## 6. Negative-Boundary Results

| Boundary | Result |
| --- | --- |
| no invented historical facts | PASS (primitives render caller-supplied data only; stateMapping predicates are caller-supplied derived logic) |
| no invented relationship | PASS (relations text-only; semantics explicitly labeled; no connector/arrow/lineage markup — tested) |
| no inferred lineage / edition genealogy | PASS (no such behavior exists in P0; no genealogy components added) |
| no clinical content | PASS (no clinical text/logic in any new file) |
| no CitationExport | PASS (tested: no export prop/control; export remains DEFERRED) |
| no page-locator invention | PASS (locator renders exactly the supplied string; no 卷/页 synthesis — tested) |
| no new backend state / schema/API change | PASS (git delta audit: only allowlisted files; §9) |
| no arbitrary hardcoded palette | PASS (token scan test: no hex in new production files; tokens only) |
| N-F-1 truthiness ambiguity | PASS (resolveTitleTag has no truthiness branch; 0 → invalid → fail-closed <p> + dev warning; tested for 0/-1/7/NaN/strings) |

## 7. Responsive Results

Primitives are layout-safe by construction (flex/grid wrap, no fixed widths, tokens-only spacing).
Production surfaces verified by existing e2e at 375/480/768/1024/1440/1920 (viewport spec) —
all PASS. Full UX2 cross-surface responsive acceptance is UX2-P6 scope.

## 8. Accessibility Result

- P0 axe harness (jsdom, component-level rules): **0 violations** on DHObjectLayout and
  BibliographicRecord (ux2_p0_a11y.spec.ts).
- Semantics: heading hierarchy via titleTag contract; `role="status"` on incomplete notes;
  status text + color (never color-only); semantic DOM (article/section/dl/ul); no motion dependence;
  native anchors keyboard-focusable. Full-page axe over authorized surfaces is UX2-P6 scope.

## 9. Worktree Status

```text
git status --short:
 M apps/frontend/src/styles/foundations.css
?? apps/frontend/src/__tests__/ux2_p0_*.spec.ts (×5)
?? apps/frontend/src/components/primitives/ (×2)
?? apps/frontend/src/presentation/stateMapping.ts
?? docs/ux2/g4/HFM-UX2-P0-IMPLEMENTATION-EVIDENCE-v1.md
(pre-existing unrelated untracked dirs docs/research/ hfmzl/ zzcl/ remain unstaged)
```

## 10. Rollback

```text
ROLLBACK_TARGET = 2a7fc468896f8a19d8129353164a8f463f635426
```

The WP is independently reversible: revert = remove the created files and revert
`foundations.css` to baseline; no schema/API/migration operations involved.
No later WP destroys this ability (G4 rollback contract).

## 11. Definition of Done Check

```text
P0-S1 shared primitives implemented      PASS
P0-S2 presentation-state mapping         PASS
P0-S3 N-F-1 semantics exact              PASS (1..6→h1..h6; null/undefined/"none"→<p>;
                                           else incl. 0 → fail-closed <p> + dev warning)
P0-S4 no P1–P5 surface implementation    PASS (no view modified)
P0-S5 all changed files within allowlist PASS (§2)
P0-S6 no API/schema/domain/database change PASS
P0-S7 CitationExport not implemented     PASS
P0-S8 U-01…U-05 remain unresolved        PASS
P0-S9 tests PASS                         PASS (58 P0 + 253 full + 67 e2e)
P0-S10 axe violations = 0                PASS (P0 harness)
P0-S11 responsive primitive checks PASS  PASS (construction + existing viewport e2e)
P0-S12 negative boundaries PASS          PASS (§6)
P0-S13 rollback target valid             PASS (2a7fc468…)
P0-S14 production implementation evidence complete PASS (this record)
```

## 12. Production Delta Audit

```text
git diff --name-only      → apps/frontend/src/styles/foundations.css (only allowlisted modify)
new files                 → primitives ×2, presentation/stateMapping.ts, tests ×5, evidence doc
forbidden areas           → NO delta (router/data/types/services/backend/packages untouched)
```

## 13. Commit

```text
UX2_P0_IMPLEMENTATION_CANDIDATE = <commit SHA recorded at delivery>
PRE_WP_BASELINE = 2a7fc468896f8a19d8129353164a8f463f635426
PRODUCTION_SCOPE = UX2-P0_ONLY
P1-P7_EXECUTION = NOT_STARTED
```
