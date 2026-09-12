# HFM PHASE 2 — FRONTIER-3 ACCEPTANCE ARCHIVE & FREEZE

## Formal title

HFM PHASE 2
FRONTIER-3 ACCEPTANCE ARCHIVE & FREEZE

## Baseline binding

```
Governance Baseline:
7fa7c4f60244daa6999e377d08502bde522c56b2

Frontier-2 Acceptance Baseline:
e2d9440f4e4d34e5a0a599d3191bfbb27fd9333e

Rejected Frontier-3 Candidate:
b0979e2258b3ec2d58d9d67a149965f11b37b213

Accepted Corrected Frontier-3 Candidate:
88435bcf09ad8136bcd3026ccc003a92d72f1e76
```

## Acceptance chronology

1. Original implementation candidate `b0979e2258b3ec2d58d9d67a149965f11b37b213`
   (five atomic per-WP commits + formatting fix above the Frontier-2 Acceptance Baseline).
2. Initial Codex acceptance rejection: `PHASE2_FRONTIER3_ACCEPTANCE_REJECTED` (P0=1, P1=2, P2=2).
3. Blocking findings closed in the correction round.
4. Correction commit `88435bcf09ad8136bcd3026ccc003a92d72f1e76` (single minimal commit,
   parent exactly the rejected candidate).
5. Corrected-candidate re-audit: `PHASE2_FRONTIER3_ACCEPTANCE_CORRECTION_REQUIRED`
   (P0=0, P1=1) — only P1-02 remained open.
6. Independent Docker-container Browser E2E evidence closure (P1-02 CLOSED).
7. Final acceptance re-audit: `READY_FOR_PHASE2_FRONTIER3_ACCEPTANCE_ARCHIVE` (P0=0, P1=0).

Final independent verdict: `READY_FOR_PHASE2_FRONTIER3_ACCEPTANCE_ARCHIVE`
Findings at acceptance: P0 = 0, P1 = 0.

## Rejected-candidate record (history preserved, not rewritten)

The original candidate was NOT accepted directly.

```
Original/rejected candidate:
b0979e2258b3ec2d58d9d67a149965f11b37b213

Initial acceptance verdict:
PHASE2_FRONTIER3_ACCEPTANCE_REJECTED
```

Blocking findings:

- P0-01: release-gate governed deselection was not fail-closed because canonical
  governance verification was not required before deselection.
- P1-01: Frontier-3 mandatory Evidence IDs lacked candidate-bound execution evidence.
- P1-02: Browser E2E 10/10 was not independently established in the Codex sandbox.

Correction commit: `88435bcf09ad8136bcd3026ccc003a92d72f1e76`

Final closure: P0-01 CLOSED · P1-01 CLOSED · P1-02 CLOSED

## Accepted Frontier-3 scope

```
FRONTIER_3_WP_SET=[P2-03, P2-04, P2-06, P2-08, P2-09]

P2-03 = ACCEPTED   (Reader/Search, deps: P2-01)
P2-04 = ACCEPTED   (Heritage visualization, deps: P2-03 non-blocking)
P2-06 = ACCEPTED   (Export/Print, deps: P2-02)
P2-08 = ACCEPTED   (Observability/gates, deps: P2-07 + ADR-P2-02)
P2-09 = ACCEPTED   (Admin audit view, deps: P2-02)
```

Each WP binds to the Accepted Corrected Frontier-3 Candidate
`88435bcf09ad8136bcd3026ccc003a92d72f1e76`.

## Release-gate acceptance record (P2-08 / P0-01 closure)

Accepted final release semantics — fail-closed governance chain:

```
canonical governance verifier
→ exit 0
→ SUPERSESSION_REGISTER=PASS
→ register-derived authorization checks
→ exact governed deselection
→ current-applicable pytest
```

Accepted governed deselections (exact node IDs, formally SUPERSEDED Class H):

- `tests/test_phase1_research_workspace.py::test_migration_0013_upgrade_downgrade_upgrade_single_head`
- `tests/test_phase2_guardrails.py::test_frozen_boundary_states`
- `tests/test_phase2_guardrails.py::test_migration_invariant`

Recorded facts:

- All three are formally SUPERSEDED Class H assertions (register entries
  ASN-P1RW-MIG-0013-HEAD, ASN-P200-MIG-0013-HEAD, ASN-P200-MIG-NO0014).
- Valid ACTIVE terminal replacements exist (e.g. ASN-P205-MIG-0014-HEAD →
  `test_p2_current_migration_head_0014`), executed in the current-applicable suite.
- No ACTIVE assertion is deselected (deselections are disjoint from all ACTIVE
  `CURRENT_REPLACEMENT_TEST` values).
- Adversarial cases A–J (verifier failure, verifier unavailable, malformed register,
  assertion no longer superseded, unauthorized deselection, active-replacement
  deselection, invalid authority binding, invalid baseline binding, missing node
  mapping, injected unregistered deselection) all FAIL CLOSED; valid state PASS.
- Actual release gate run: `GOVERNANCE_PRECHECK=PASS` then `RELEASE_GATE=PASS`.
- Precheck implementation: `infra/scripts/verify-governance-precheck.sh`;
  adversarial suite: `infra/scripts/test-release-gate-precheck.sh`.

## Frontier-3 implementation evidence (P1-01 closure)

Formal evidence artifact: `docs/audit/HFM-PHASE2-FRONTIER3-IMPLEMENTATION-EVIDENCE.md`

Accepted mandatory Evidence IDs — 15/15 valid:

```
P2-03: E2-08 PASS · E2-09 PASS · E2-10 PASS
P2-04: E2-11 PASS · E2-12 PASS · E2-13 PASS
P2-06: E2-17 PASS · E2-18 PASS · E2-19 PASS
P2-08: E2-23 PASS · E2-24 PASS · E2-25 PASS
P2-09: E2-26 PASS · E2-27 PASS · E2-28 PASS
```

- Every Evidence ID binds Evidence ID / WP ID / AC ID / candidate SHA /
  governance baseline SHA / Frontier-2 acceptance baseline SHA / implementation
  artifact / authoritative test command / actual machine result / execution
  timestamp / PASS outcome.
- Candidate binding: the corrected candidate `88435bcf…` (self-referential
  "this commit" convention; SHA recorded post-commit). Evidence was re-executed
  this round — no carried-over results.

## Independent Browser E2E record (P1-02 closure)

- Accepted candidate: `88435bcf09ad8136bcd3026ccc003a92d72f1e76`.
- Independent execution channel: clean Docker container (isolated filesystem and
  network namespace; localhost binding unrestricted).
- Primary authoritative command: `cd apps/frontend && pnpm e2e`.
- Result: 10 tests · 10 passed · 0 failed · 0 skipped · 0 retries · exit 0.
- Committed suite: `public.spec.ts` = 6, `viewport.spec.ts` = 4; total = 10.
- Recorded: candidate checkout exact (`CONTAINER_HEAD == expected`), tracked diff
  clean, Playwright config byte-identical to the candidate commit, real Chromium
  (headless) used, Vite dev server bound port 5199 and served the suite, no
  grep/skip/only/retry weakening, machine-generated JUnit (`tests="10" failures="0"`)
  / HTML report / `.last-run.json` (`{"status":"passed","failedTests":[]}`) artifacts
  validated with recorded SHA-256.
- The earlier Codex `listen EPERM` on port 5199 was an auditor sandbox limitation,
  not a candidate defect.
- Historical execution references (not permanent archive assets): container
  `576e4999fe4f…`, snapshot image `hfm-p1e2e-snapshot`, artifacts under the round's
  temporary execution directory with recorded SHA-256 hashes.

## Final acceptance evidence

- Governance: `SUPERSESSION_REGISTER=PASS` — entries=10 (A=1, B=2, C=1, H=3, P=3),
  ACTIVE=7, SUPERSEDED=3; historical replays 3/3 PASS; replacement tests 2/2 PASS;
  authority bindings 3; baseline bindings 3. Governance tests 54/54 PASS
  (47 supersession + 7 adjudication). Verifier and register unchanged.
- WP Acceptance: P2-03 PASS · P2-04 PASS · P2-06 PASS · P2-08 PASS · P2-09 PASS.
- Backend current-applicable: 515 collected, 3 governed superseded, 512 current
  applicable, 512 passed, 0 failed, 0 errors, 0 skipped, 0 xfailed.
- Historical replay: 3/3 PASS (separate from current-applicable pytest).
- Migration: 20/20 PASS.
- Frontend Vitest: 79/79 PASS.
- Browser E2E: 10/10 PASS.
- P2-03: 10/10 PASS · P2-04: 8/8 PASS · P2-06: 4 backend + 7 frontend PASS ·
  P2-08: 5 observability tests + health + release gate + governance precheck PASS ·
  P2-09: 7/7 PASS.
- Static/build: Backend Ruff PASS, Backend Format PASS, Backend Mypy PASS (12 files),
  Frontend ESLint PASS under formal threshold (0 errors; warnings below blocking
  threshold), Frontend Typecheck PASS, Frontend Build PASS, `git diff --check` PASS,
  correction shell syntax PASS (`bash -n` on release-gate, precheck, adversarial scripts).

## Migration record

```
Previous head: 0014
Current head:  0014
Single Alembic head: PASS
Migration 0014: UNCHANGED
Migration tests: 20/20 PASS
```

No Frontier-3 migration; the P2-05-authorized migration 0014 remains the single head.

## Security / boundaries

Environment separation PASS · Secret boundary PASS · Synthetic scanner PASS ·
RBAC deny-by-default PASS · Rights filtering PASS · HFB runtime zero-coupling PASS ·
Clinical boundary PASS · No real secrets detected.

## P2 observations (non-blocking, recorded only)

- Historical root/tooling hygiene findings outside canonical Frontier-3 gate scope
  (`scripts/core_completion/dry_run.py` RUF100/import-not-found;
  `scripts/check-reuse-adjudication.py` root-config format) — byte-identical to the
  Frontier-2 baseline, not remediated.
- Frontend lint warnings below blocking threshold (pre-existing).
- Historical 0013 Class H assertions superseded by governance (register-valid,
  replays PASS) — by design of the supersession mechanism.
- Artifact/JUnit timestamp metadata discrepancy with no result inconsistency
  (junit capture timestamp differs from the primary run; both runs 10/10 exit 0).

None remediated in this archive commit; none promoted.

## Frozen protection

Zero unauthorized drift verified across: Governance Baseline artifacts, Frontier-2
Acceptance Baseline and archives, P2-00/P2-01/P2-02/P2-05/P2-07/P2-10 accepted
artifacts, Scope Register, DAG, ADR-P2-01/P2-02, Migration 0014, Supersession
register, Governance verifier, and the Frontier-3 accepted implementation candidate
(`88435bcf…` byte identity). The archive operation changes only:
`docs/audit/HFM-PHASE2-FRONTIER3-ACCEPTANCE-ARCHIVE.md`.

## Cumulative accepted Phase-2 WP state

```
ACCEPTED_PHASE2_WP_SET=[
  P2-00,
  P2-01,
  P2-02,
  P2-03,
  P2-04,
  P2-05,
  P2-06,
  P2-07,
  P2-08,
  P2-09,
  P2-10
]
```

This is an acceptance-state record only; NEXT_FRONTIER is not computed in this round.

## Formal status

```
PHASE2_FRONTIER3_ACCEPTANCE_ARCHIVED_AND_FROZEN
```

- The accepted corrected candidate `88435bcf…` remains the Accepted Corrected
  Frontier-3 Candidate.
- This archive commit becomes the Formal Phase-2 Frontier-3 Acceptance Baseline.
- The Formal Phase-2 Governance Baseline remains `7fa7c4f…` — a distinct formal
  object, not replaced by the Frontier-3 Acceptance Baseline.
