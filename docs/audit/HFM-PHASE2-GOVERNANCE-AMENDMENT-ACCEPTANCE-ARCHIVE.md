# HFM PHASE 2 — GOVERNANCE AMENDMENT ACCEPTANCE ARCHIVE & FREEZE

## Formal title

HFM PHASE 2
GOVERNANCE AMENDMENT ACCEPTANCE ARCHIVE & FREEZE

## Baseline chain

```
Previous Phase-2 Governance Baseline:
b1a083049ee2caf79bb20143ef14dd340a929ea3

Corrected Frontier-2 Candidate:
d38f871a230ca56713737b7de82f9111e7e73650

Governance Amendment Chain:
d38f871a230ca56713737b7de82f9111e7e73650
→ a54a51ce4df6806cef741e12747297ab907b7f96
→ a5e21812cffbac981bf88da9d1e2a0e826befdc3
→ ddd489436fea55bda87e50cc968fa7db6c426a20
→ 4b7bb151c1f10e5c8e67bb03d17ca97b45ed5d8b
→ f57824810f22bb9fd48ca636cec130caed1b40a1
→ a73314b510e3323682aa90b9ee527fa5fd1f6911

Accepted Governance Amendment Candidate:
a73314b510e3323682aa90b9ee527fa5fd1f6911
```

## Governance Amendment Acceptance Audit

- Audit: Codex Re-Acceptance Audit Round 5
- Final Audit Verdict: `READY_FOR_PHASE2_GOVERNANCE_AMENDMENT_ACCEPTANCE_ARCHIVE`
- P0 = **0**
- P1 = **0**
- P1 Closure: P1-01 CLOSED · P1-02 CLOSED · P1-03 CLOSED · P1-04 CLOSED · P1-05 CLOSED · P1-06 CLOSED · P1-07 CLOSED

## Acceptance evidence

- Tests: **54 PASS / 0 FAIL** (47 supersession + 7 adjudication; exit 0)
- Real verifier: `SUPERSESSION_REGISTER=PASS`, exit 0
- Historical Replays: **3/3 PASS**
- Replacement Executions: **2/2 PASS**
- Authority Bindings: **3** (validated)
- Baseline Bindings: **3** (validated)
- Verifier facts: entries=10 (H=3, P=3, C=1, B=2, A=1), active=7, superseded=3
- Static gates: Root Ruff = PASS · Root Format = PASS · Root Mypy = PASS · Backend Format = PASS · `git diff --check` = PASS
- Frozen drift: Historical = 0 · Scope = 0 · DAG = 0 · ADR = 0 · Frontier-2 = 0 · Migration 0014 = 0

## Accepted governance properties (final)

1. **Exact authority locator binding** — `heading_line == target`; exact/unique locator
   required; prefix, similar-shorter, similar-longer, wrong heading level, and duplicate
   locators rejected.
2. **Authority block binding** — exact document; allowed authority type; authority ID inside
   the exact resolved block; rule/value inside the exact resolved block; wrong clause, token
   elsewhere, and unrelated section rejected.
3. **Portable historical replay** — `git archive`; no git worktree; no current `.git` metadata
   writes; `shell=False`; safe tar extraction; historical cwd/PYTHONPATH isolation; historical
   byte identity verification; fail-closed; cleanup; command-injection rejection.
4. **Assertion-level supersession** — no whole-test exclusion; protected P/B/C/A classes
   fail-closed; every SUPERSEDED assertion resolves to exactly one ACTIVE terminal.
5. **Baseline binding** — identity checked; ancestry checked; three validated baseline bindings.
6. **Strict register schema** — malformed/unknown/duplicate/missing data rejected.
7. **Future compatibility** — valid 0014→0015 synthetic PASS; protected future supersession
   fail-closed.

## Archive semantics

- `a73314b510e3323682aa90b9ee527fa5fd1f6911` is the Accepted Governance Amendment Candidate.
- This archive commit becomes the Phase-2 Governance Baseline.
- The previous baseline `b1a083049ee2caf79bb20143ef14dd340a929ea3` is superseded as the current
  Phase-2 Governance Baseline only by this archive commit.
- Historical baselines remain immutable and retained.
- The archive commit adds governance evidence only and does not alter the accepted candidate.

## Formal status

```
PHASE2_GOVERNANCE_AMENDMENT_ACCEPTANCE_ARCHIVED_AND_FROZEN
```

Boundary: this archive/freeze does NOT imply Frontier-2 reconciled, accepted, archived, or
successor WP authorized. Governance Amendment acceptance and Frontier-2 reconciliation remain
distinct state transitions.
