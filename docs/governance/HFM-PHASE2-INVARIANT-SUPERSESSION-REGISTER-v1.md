# HFM Phase 2 Invariant Supersession Register v1

Status: GOVERNANCE AMENDMENT CANDIDATE · MACHINE-VERIFIABLE
Governance amendment: `docs/governance/HFM-PHASE2-ACCEPTANCE-CONTRACT-v1.md` (§ invariant supersession principles)
Verifier: `scripts/verify-invariant-supersessions.py`
Rule: only CLASS H (historical snapshot) assertions may be superseded; CLASS P (permanent safety) and CLASS B (boundary) assertions are never superseded. Default for every assertion is `ACTIVE`.

## Invariant classes

| CLASS | Name | Purpose | Supersession eligibility | Current-suite applicability |
| --- | --- | --- | --- | --- |
| H | Historical Snapshot Invariant | Locks an acceptance-time snapshot fact (e.g. migration head at acceptance time) | YES — only under this registry contract | Only until validly superseded |
| P | Permanent Safety Invariant | Unconditional safety property (single migration head, clinical REJECTED, credential DO_NOT_MIGRATE, HFB zero-coupling) | NO | Always |
| C | Current-State Invariant | Asserts the current tree state (e.g. current migration head = 0014) | NO | Always (active replacement assertions) |
| B | Boundary Invariant | Unconditional authorization/rights boundary (rights fail-closed, deny-by-default) | NO | Always |
| A | Acceptance-Evidence Assertion | Binds acceptance evidence to an artifact/test | NO | Always |

## Register schema (strict, fail-closed)

Every entry is a `### <ASSERTION_ID>` section containing `KEY: VALUE` lines inside a
code fence. The verifier rejects unknown fields, duplicate fields, malformed records,
unknown CLASS values and unknown STATUS values. Fields marked `(superseded-only)` are
required with real values for superseded Class H entries and must be `N/A` otherwise.

| FIELD | Applies to | Meaning |
| --- | --- | --- |
| ASSERTION_ID | all | unique assertion identifier |
| CLASS | all | H / P / C / B / A |
| STATUS | all | ACTIVE / SUPERSEDED |
| HISTORICAL_TEST | all | test binding the assertion (or N/A for pure invariants) |
| INTRODUCED_AT_BASELINE | all | baseline where the assertion was introduced |
| INTRODUCED_AT_ROLE | all | formal role of that baseline (verifier checks known roles) |
| HISTORICAL_EXPECTATION | all | the literal historical expectation |
| SUPERSEDED_BY_ASSERTION_ID | superseded-only | terminal replacement assertion id |
| AUTHORITY_TYPE | superseded-only | WP_CONTRACT / ADR / ACCEPTED_AMENDMENT |
| AUTHORITY_ID | superseded-only | exact authority id inside the document (e.g. P2-05) |
| AUTHORITY_DOCUMENT | superseded-only | repo-relative governance document |
| EFFECTIVE_FROM | superseded-only | commit where the authorized evolution became effective |
| CURRENT_REPLACEMENT_TEST | superseded-only + Class C | repo-relative pytest node id/path |
| REPLAY_BASELINE | superseded-only | baseline used for historical replay |
| REPLAY_BASELINE_ROLE | superseded-only | formal role of the replay baseline |
| REPLAY_KIND | superseded-only | PYTEST (only allowed kind) |
| REPLAY_TEST | superseded-only | repo-relative pytest node id/path replayed at the baseline |
| RATIONALE | all | reason for the assertion / supersession |

Historical accepted test bytes remain immutable; historical validity is reproduced by the
verifier itself: it creates an isolated temporary worktree at the replay baseline and
executes the structured replay test (pytest only, argv subprocess, no shell).

## Registered assertions

### ASN-P200-MIG-0013-HEAD

```
ASSERTION_ID: ASN-P200-MIG-0013-HEAD
CLASS: H
STATUS: SUPERSEDED
HISTORICAL_TEST: apps/backend/tests/test_phase2_guardrails.py::test_migration_invariant
INTRODUCED_AT_BASELINE: bd0d39e76fe5a8289006664514af9250a7f84f14
INTRODUCED_AT_ROLE: P2_00_ACCEPTANCE_BASELINE
HISTORICAL_EXPECTATION: P2-00 acceptance-time migration literal head == 0013 ("0013" in migration_heads; guardrails.migration_ok expects revisions 0001..0013)
SUPERSEDED_BY_ASSERTION_ID: ASN-P205-MIG-0014-HEAD
AUTHORITY_TYPE: WP_CONTRACT
AUTHORITY_ID: P2-05
AUTHORITY_DOCUMENT: docs/governance/HFM-PHASE2-WORK-PACKAGE-CONTRACT-v1.md
EFFECTIVE_FROM: b53c897cfffd287516ecb1ed230df2f8f83687d9
CURRENT_REPLACEMENT_TEST: apps/backend/tests/test_phase2_media.py::test_p2_current_migration_head_0014
REPLAY_BASELINE: bd0d39e76fe5a8289006664514af9250a7f84f14
REPLAY_BASELINE_ROLE: P2_00_ACCEPTANCE_BASELINE
REPLAY_KIND: PYTEST
REPLAY_TEST: tests/test_phase2_guardrails.py
RATIONALE: P2-05 contract explicitly authorizes schema migration 0014; the migration head advanced from 0013 to 0014; the P2-00-time literal head==0013 snapshot is superseded by the current-state assertion ASN-P205-MIG-0014-HEAD.
```

### ASN-P200-MIG-NO0014

```
ASSERTION_ID: ASN-P200-MIG-NO0014
CLASS: H
STATUS: SUPERSEDED
HISTORICAL_TEST: apps/backend/tests/test_phase2_guardrails.py::test_migration_invariant
INTRODUCED_AT_BASELINE: bd0d39e76fe5a8289006664514af9250a7f84f14
INTRODUCED_AT_ROLE: P2_00_ACCEPTANCE_BASELINE
HISTORICAL_EXPECTATION: P2-00 acceptance-time migration revisions exclude 0014 ("0014" not in migration_revisions)
SUPERSEDED_BY_ASSERTION_ID: ASN-P205-MIG-0014-HEAD
AUTHORITY_TYPE: WP_CONTRACT
AUTHORITY_ID: P2-05
AUTHORITY_DOCUMENT: docs/governance/HFM-PHASE2-WORK-PACKAGE-CONTRACT-v1.md
EFFECTIVE_FROM: b53c897cfffd287516ecb1ed230df2f8f83687d9
CURRENT_REPLACEMENT_TEST: apps/backend/tests/test_phase2_media.py::test_p2_current_migration_head_0014
REPLAY_BASELINE: bd0d39e76fe5a8289006664514af9250a7f84f14
REPLAY_BASELINE_ROLE: P2_00_ACCEPTANCE_BASELINE
REPLAY_KIND: PYTEST
REPLAY_TEST: tests/test_phase2_guardrails.py
RATIONALE: Same authorized evolution as ASN-P200-MIG-0013-HEAD; the literal "no 0014" snapshot is superseded once 0014 is authorized and present.
```

### ASN-P1RW-MIG-0013-HEAD

```
ASSERTION_ID: ASN-P1RW-MIG-0013-HEAD
CLASS: H
STATUS: SUPERSEDED
HISTORICAL_TEST: apps/backend/tests/test_phase1_research_workspace.py::test_migration_0013_upgrade_downgrade_upgrade_single_head
INTRODUCED_AT_BASELINE: c17be40be6f055498fde11c0042e71d3a1056a7c
INTRODUCED_AT_ROLE: PHASE1_COMPLETION_BASELINE
HISTORICAL_EXPECTATION: Phase-1 research workspace single-head assertion: alembic heads == "0013 (head)"
SUPERSEDED_BY_ASSERTION_ID: ASN-P205-MIG-0014-HEAD
AUTHORITY_TYPE: WP_CONTRACT
AUTHORITY_ID: P2-05
AUTHORITY_DOCUMENT: docs/governance/HFM-PHASE2-WORK-PACKAGE-CONTRACT-v1.md
EFFECTIVE_FROM: b53c897cfffd287516ecb1ed230df2f8f83687d9
CURRENT_REPLACEMENT_TEST: apps/backend/tests/test_phase2_media.py::test_p2_current_migration_head_0014
REPLAY_BASELINE: c17be40be6f055498fde11c0042e71d3a1056a7c
REPLAY_BASELINE_ROLE: PHASE1_COMPLETION_BASELINE
REPLAY_KIND: PYTEST
REPLAY_TEST: tests/test_phase1_research_workspace.py::test_migration_0013_upgrade_downgrade_upgrade_single_head
RATIONALE: The literal head=="0013" expectation is a Phase-1 acceptance-time snapshot; the P2-05-authorized migration 0014 advances the single linear head to 0014 while preserving the single-head permanent invariant (ASN-P200-SINGLE-HEAD).
```

### ASN-P205-MIG-0014-HEAD

```
ASSERTION_ID: ASN-P205-MIG-0014-HEAD
CLASS: C
STATUS: ACTIVE
HISTORICAL_TEST: N/A (current-state assertion, not a historical test)
INTRODUCED_AT_BASELINE: b53c897cfffd287516ecb1ed230df2f8f83687d9
INTRODUCED_AT_ROLE: P2_05_MIGRATION_COMMIT
HISTORICAL_EXPECTATION: N/A
SUPERSEDED_BY_ASSERTION_ID: N/A
AUTHORITY_TYPE: N/A
AUTHORITY_ID: N/A
AUTHORITY_DOCUMENT: N/A
EFFECTIVE_FROM: b53c897cfffd287516ecb1ed230df2f8f83687d9
CURRENT_REPLACEMENT_TEST: apps/backend/tests/test_phase2_media.py::test_p2_current_migration_head_0014
REPLAY_BASELINE: N/A
REPLAY_BASELINE_ROLE: N/A
REPLAY_KIND: N/A
REPLAY_TEST: N/A
RATIONALE: Current-state replacement: single linear Alembic head 0014, revisions 0001..0014, chain linear, authorized by P2-05; HFB M0-M7 executed = 0.
```

### ASN-P200-SINGLE-HEAD

```
ASSERTION_ID: ASN-P200-SINGLE-HEAD
CLASS: P
STATUS: ACTIVE
HISTORICAL_TEST: N/A (permanent safety invariant)
INTRODUCED_AT_BASELINE: bd0d39e76fe5a8289006664514af9250a7f84f14
INTRODUCED_AT_ROLE: P2_00_ACCEPTANCE_BASELINE
HISTORICAL_EXPECTATION: exactly one Alembic migration head at all times
SUPERSEDED_BY_ASSERTION_ID: N/A
AUTHORITY_TYPE: N/A
AUTHORITY_ID: N/A
AUTHORITY_DOCUMENT: N/A
EFFECTIVE_FROM: N/A
CURRENT_REPLACEMENT_TEST: N/A
REPLAY_BASELINE: N/A
REPLAY_BASELINE_ROLE: N/A
REPLAY_KIND: N/A
REPLAY_TEST: N/A
RATIONALE: Permanent safety invariant: single migration head must hold for every authorized evolution (0013→0014→0015→...). Never superseded.
```

### ASN-P200-CLINICAL-REJECTED

```
ASSERTION_ID: ASN-P200-CLINICAL-REJECTED
CLASS: P
STATUS: ACTIVE
HISTORICAL_TEST: N/A (permanent safety invariant)
INTRODUCED_AT_BASELINE: bd0d39e76fe5a8289006664514af9250a7f84f14
INTRODUCED_AT_ROLE: P2_00_ACCEPTANCE_BASELINE
HISTORICAL_EXPECTATION: clinical recommendation semantics REJECTED (fail-closed)
SUPERSEDED_BY_ASSERTION_ID: N/A
AUTHORITY_TYPE: N/A
AUTHORITY_ID: N/A
AUTHORITY_DOCUMENT: N/A
EFFECTIVE_FROM: N/A
CURRENT_REPLACEMENT_TEST: N/A
REPLAY_BASELINE: N/A
REPLAY_BASELINE_ROLE: N/A
REPLAY_KIND: N/A
REPLAY_TEST: N/A
RATIONALE: Permanent safety invariant. Never superseded.
```

### ASN-P200-HFB-ZERO-COUPLING

```
ASSERTION_ID: ASN-P200-HFB-ZERO-COUPLING
CLASS: P
STATUS: ACTIVE
HISTORICAL_TEST: N/A (permanent safety invariant)
INTRODUCED_AT_BASELINE: bd0d39e76fe5a8289006664514af9250a7f84f14
INTRODUCED_AT_ROLE: P2_00_ACCEPTANCE_BASELINE
HISTORICAL_EXPECTATION: HFB runtime imports = 0; shared live auth/session/credential store = 0
SUPERSEDED_BY_ASSERTION_ID: N/A
AUTHORITY_TYPE: N/A
AUTHORITY_ID: N/A
AUTHORITY_DOCUMENT: N/A
EFFECTIVE_FROM: N/A
CURRENT_REPLACEMENT_TEST: N/A
REPLAY_BASELINE: N/A
REPLAY_BASELINE_ROLE: N/A
REPLAY_KIND: N/A
REPLAY_TEST: N/A
RATIONALE: Permanent safety invariant (ADR-06). Never superseded.
```

### ASN-P200-CREDENTIAL-NO-MIGRATE

```
ASSERTION_ID: ASN-P200-CREDENTIAL-NO-MIGRATE
CLASS: B
STATUS: ACTIVE
HISTORICAL_TEST: N/A (boundary invariant)
INTRODUCED_AT_BASELINE: bd0d39e76fe5a8289006664514af9250a7f84f14
INTRODUCED_AT_ROLE: P2_00_ACCEPTANCE_BASELINE
HISTORICAL_EXPECTATION: credential/session migration DO_NOT_MIGRATE (MC-12)
SUPERSEDED_BY_ASSERTION_ID: N/A
AUTHORITY_TYPE: N/A
AUTHORITY_ID: N/A
AUTHORITY_DOCUMENT: N/A
EFFECTIVE_FROM: N/A
CURRENT_REPLACEMENT_TEST: N/A
REPLAY_BASELINE: N/A
REPLAY_BASELINE_ROLE: N/A
REPLAY_KIND: N/A
REPLAY_TEST: N/A
RATIONALE: Boundary invariant. Never superseded.
```

### ASN-P205-RIGHTS-FAIL-CLOSED

```
ASSERTION_ID: ASN-P205-RIGHTS-FAIL-CLOSED
CLASS: B
STATUS: ACTIVE
HISTORICAL_TEST: N/A (boundary invariant)
INTRODUCED_AT_BASELINE: b53c897cfffd287516ecb1ed230df2f8f83687d9
INTRODUCED_AT_ROLE: P2_05_MIGRATION_COMMIT
HISTORICAL_EXPECTATION: media publication requires sufficient non-expired rights metadata (fail-closed)
SUPERSEDED_BY_ASSERTION_ID: N/A
AUTHORITY_TYPE: N/A
AUTHORITY_ID: N/A
AUTHORITY_DOCUMENT: N/A
EFFECTIVE_FROM: N/A
CURRENT_REPLACEMENT_TEST: N/A
REPLAY_BASELINE: N/A
REPLAY_BASELINE_ROLE: N/A
REPLAY_KIND: N/A
REPLAY_TEST: N/A
RATIONALE: Boundary invariant (ADR-P2-01 rights fail-closed). Never superseded.
```

### ASN-P210-REUSE-PARSE

```
ASSERTION_ID: ASN-P210-REUSE-PARSE
CLASS: A
STATUS: ACTIVE
HISTORICAL_TEST: N/A (acceptance-evidence assertion)
INTRODUCED_AT_BASELINE: d38f871a230ca56713737b7de82f9111e7e73650
INTRODUCED_AT_ROLE: FRONTIER2_CORRECTED_CANDIDATE
HISTORICAL_EXPECTATION: P2-10 adjudication register machine-parses to 27 classified items
SUPERSEDED_BY_ASSERTION_ID: N/A
AUTHORITY_TYPE: N/A
AUTHORITY_ID: N/A
AUTHORITY_DOCUMENT: N/A
EFFECTIVE_FROM: N/A
CURRENT_REPLACEMENT_TEST: apps/backend/tests/test_phase2_reuse_adjudication.py
REPLAY_BASELINE: N/A
REPLAY_BASELINE_ROLE: N/A
REPLAY_KIND: N/A
REPLAY_TEST: N/A
RATIONALE: Acceptance-evidence assertion binding E2-29 to the parser artifact. Never superseded by schema evolution.
```

## Accounting (machine-validated)

```
DECLARED_TOTAL: 10
DECLARED_CLASS_H: 3
DECLARED_CLASS_P: 3
DECLARED_CLASS_C: 1
DECLARED_CLASS_B: 2
DECLARED_CLASS_A: 1
DECLARED_ACTIVE: 7
DECLARED_SUPERSEDED: 3
```

The verifier derives counts mechanically from the parsed records and requires
`actual rows = declared total`, `category sum = total`, `status sum = total`.
Supersession chain: ASN-P200-MIG-0013-HEAD, ASN-P200-MIG-NO0014, ASN-P1RW-MIG-0013-HEAD
→ ASN-P205-MIG-0014-HEAD (no cycles; each resolves to exactly one ACTIVE terminal).
