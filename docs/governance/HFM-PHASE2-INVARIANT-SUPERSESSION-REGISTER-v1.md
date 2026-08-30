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

Historical accepted test bytes remain immutable; historical validity is reproduced by checking out the bound baseline and re-running the historical replay command.

## Registered assertions

### ASN-P200-MIG-0013-HEAD

```
ASSERTION_ID: ASN-P200-MIG-0013-HEAD
CLASS: H
HISTORICAL_TEST: apps/backend/tests/test_phase2_guardrails.py::test_migration_invariant
INTRODUCED_AT_BASELINE: bd0d39e76fe5a8289006664514af9250a7f84f14
HISTORICAL_EXPECTATION: P2-00 acceptance-time migration literal head == 0013 ("0013" in migration_heads; guardrails.migration_ok expects revisions 0001..0013)
SUPERSEDED_BY_ASSERTION_ID: ASN-P205-MIG-0014-HEAD
SUPERSEDING_AUTHORITY: HFM-PHASE2-WORK-PACKAGE-CONTRACT-v1.md (P2-05 allowed module "alembic/versions/00XX_p2_*")
EFFECTIVE_FROM: b53c897cfffd287516ecb1ed230df2f8f83687d9
CURRENT_REPLACEMENT_TEST: apps/backend/tests/test_phase2_media.py::test_p2_current_migration_head_0014
HISTORICAL_REPLAY_BASELINE: bd0d39e76fe5a8289006664514af9250a7f84f14
HISTORICAL_REPLAY_COMMAND: pytest tests/test_phase2_guardrails.py -q
RATIONALE: P2-05 contract explicitly authorizes schema migration 0014; the migration head advanced from 0013 to 0014; the P2-00-time literal head==0013 snapshot is superseded by the current-state assertion ASN-P205-MIG-0014-HEAD.
STATUS: SUPERSEDED
```

### ASN-P200-MIG-NO0014

```
ASSERTION_ID: ASN-P200-MIG-NO0014
CLASS: H
HISTORICAL_TEST: apps/backend/tests/test_phase2_guardrails.py::test_migration_invariant
INTRODUCED_AT_BASELINE: bd0d39e76fe5a8289006664514af9250a7f84f14
HISTORICAL_EXPECTATION: P2-00 acceptance-time migration revisions exclude 0014 ("0014" not in migration_revisions)
SUPERSEDED_BY_ASSERTION_ID: ASN-P205-MIG-0014-HEAD
SUPERSEDING_AUTHORITY: HFM-PHASE2-WORK-PACKAGE-CONTRACT-v1.md (P2-05 allowed module "alembic/versions/00XX_p2_*")
EFFECTIVE_FROM: b53c897cfffd287516ecb1ed230df2f8f83687d9
CURRENT_REPLACEMENT_TEST: apps/backend/tests/test_phase2_media.py::test_p2_current_migration_head_0014
HISTORICAL_REPLAY_BASELINE: bd0d39e76fe5a8289006664514af9250a7f84f14
HISTORICAL_REPLAY_COMMAND: pytest tests/test_phase2_guardrails.py -q
RATIONALE: Same authorized evolution as ASN-P200-MIG-0013-HEAD; the literal "no 0014" snapshot is superseded once 0014 is authorized and present.
STATUS: SUPERSEDED
```

### ASN-P1RW-MIG-0013-HEAD

```
ASSERTION_ID: ASN-P1RW-MIG-0013-HEAD
CLASS: H
HISTORICAL_TEST: apps/backend/tests/test_phase1_research_workspace.py::test_migration_0013_upgrade_downgrade_upgrade_single_head
INTRODUCED_AT_BASELINE: 0ed47d648efa1478e999439333dc32d36e080831
HISTORICAL_EXPECTATION: Phase-1 research workspace single-head assertion: alembic heads == "0013 (head)"
SUPERSEDED_BY_ASSERTION_ID: ASN-P205-MIG-0014-HEAD
SUPERSEDING_AUTHORITY: HFM-PHASE2-WORK-PACKAGE-CONTRACT-v1.md (P2-05 allowed module "alembic/versions/00XX_p2_*")
EFFECTIVE_FROM: b53c897cfffd287516ecb1ed230df2f8f83687d9
CURRENT_REPLACEMENT_TEST: apps/backend/tests/test_phase2_media.py::test_p2_current_migration_head_0014
HISTORICAL_REPLAY_BASELINE: c17be40be6f055498fde11c0042e71d3a1056a7c
HISTORICAL_REPLAY_COMMAND: pytest tests/test_phase1_research_workspace.py::test_migration_0013_upgrade_downgrade_upgrade_single_head -q
RATIONALE: The literal head=="0013" expectation is a Phase-1 acceptance-time snapshot; the P2-05-authorized migration 0014 advances the single linear head to 0014 while preserving the single-head permanent invariant (ASN-P200-SINGLE-HEAD).
STATUS: SUPERSEDED
```

### ASN-P205-MIG-0014-HEAD

```
ASSERTION_ID: ASN-P205-MIG-0014-HEAD
CLASS: C
HISTORICAL_TEST: N/A (current-state assertion, not a historical test)
INTRODUCED_AT_BASELINE: b53c897cfffd287516ecb1ed230df2f8f83687d9
HISTORICAL_EXPECTATION: N/A
SUPERSEDED_BY_ASSERTION_ID: N/A
SUPERSEDING_AUTHORITY: HFM-PHASE2-WORK-PACKAGE-CONTRACT-v1.md (P2-05)
EFFECTIVE_FROM: b53c897cfffd287516ecb1ed230df2f8f83687d9
CURRENT_REPLACEMENT_TEST: apps/backend/tests/test_phase2_media.py::test_p2_current_migration_head_0014
HISTORICAL_REPLAY_BASELINE: N/A
HISTORICAL_REPLAY_COMMAND: N/A
RATIONALE: Current-state replacement: single linear Alembic head 0014, revisions 0001..0014, chain linear, authorized by P2-05; HFB M0-M7 executed = 0.
STATUS: ACTIVE
```

### ASN-P200-SINGLE-HEAD

```
ASSERTION_ID: ASN-P200-SINGLE-HEAD
CLASS: P
HISTORICAL_TEST: N/A (permanent safety invariant)
INTRODUCED_AT_BASELINE: bd0d39e76fe5a8289006664514af9250a7f84f14
HISTORICAL_EXPECTATION: exactly one Alembic migration head at all times
SUPERSEDED_BY_ASSERTION_ID: N/A
SUPERSEDING_AUTHORITY: N/A
EFFECTIVE_FROM: N/A
CURRENT_REPLACEMENT_TEST: N/A
HISTORICAL_REPLAY_BASELINE: N/A
HISTORICAL_REPLAY_COMMAND: N/A
RATIONALE: Permanent safety invariant: single migration head must hold for every authorized evolution (0013→0014→0015→...). Never superseded.
STATUS: ACTIVE
```

### ASN-P200-CLINICAL-REJECTED

```
ASSERTION_ID: ASN-P200-CLINICAL-REJECTED
CLASS: P
HISTORICAL_TEST: N/A (permanent safety invariant)
INTRODUCED_AT_BASELINE: bd0d39e76fe5a8289006664514af9250a7f84f14
HISTORICAL_EXPECTATION: clinical recommendation semantics REJECTED (fail-closed)
SUPERSEDED_BY_ASSERTION_ID: N/A
SUPERSEDING_AUTHORITY: N/A
EFFECTIVE_FROM: N/A
CURRENT_REPLACEMENT_TEST: N/A
HISTORICAL_REPLAY_BASELINE: N/A
HISTORICAL_REPLAY_COMMAND: N/A
RATIONALE: Permanent safety invariant. Never superseded.
STATUS: ACTIVE
```

### ASN-P200-HFB-ZERO-COUPLING

```
ASSERTION_ID: ASN-P200-HFB-ZERO-COUPLING
CLASS: P
HISTORICAL_TEST: N/A (permanent safety invariant)
INTRODUCED_AT_BASELINE: bd0d39e76fe5a8289006664514af9250a7f84f14
HISTORICAL_EXPECTATION: HFB runtime imports = 0; shared live auth/session/credential store = 0
SUPERSEDED_BY_ASSERTION_ID: N/A
SUPERSEDING_AUTHORITY: N/A
EFFECTIVE_FROM: N/A
CURRENT_REPLACEMENT_TEST: N/A
HISTORICAL_REPLAY_BASELINE: N/A
HISTORICAL_REPLAY_COMMAND: N/A
RATIONALE: Permanent safety invariant (ADR-06). Never superseded.
STATUS: ACTIVE
```

### ASN-P200-CREDENTIAL-NO-MIGRATE

```
ASSERTION_ID: ASN-P200-CREDENTIAL-NO-MIGRATE
CLASS: B
HISTORICAL_TEST: N/A (boundary invariant)
INTRODUCED_AT_BASELINE: bd0d39e76fe5a8289006664514af9250a7f84f14
HISTORICAL_EXPECTATION: credential/session migration DO_NOT_MIGRATE (MC-12)
SUPERSEDED_BY_ASSERTION_ID: N/A
SUPERSEDING_AUTHORITY: N/A
EFFECTIVE_FROM: N/A
CURRENT_REPLACEMENT_TEST: N/A
HISTORICAL_REPLAY_BASELINE: N/A
HISTORICAL_REPLAY_COMMAND: N/A
RATIONALE: Boundary invariant. Never superseded.
STATUS: ACTIVE
```

### ASN-P205-RIGHTS-FAIL-CLOSED

```
ASSERTION_ID: ASN-P205-RIGHTS-FAIL-CLOSED
CLASS: B
HISTORICAL_TEST: N/A (boundary invariant)
INTRODUCED_AT_BASELINE: b53c897cfffd287516ecb1ed230df2f8f83687d9
HISTORICAL_EXPECTATION: media publication requires sufficient non-expired rights metadata (fail-closed)
SUPERSEDED_BY_ASSERTION_ID: N/A
SUPERSEDING_AUTHORITY: N/A
EFFECTIVE_FROM: N/A
CURRENT_REPLACEMENT_TEST: N/A
HISTORICAL_REPLAY_BASELINE: N/A
HISTORICAL_REPLAY_COMMAND: N/A
RATIONALE: Boundary invariant (ADR-P2-01 rights fail-closed). Never superseded.
STATUS: ACTIVE
```

### ASN-P210-REUSE-PARSE

```
ASSERTION_ID: ASN-P210-REUSE-PARSE
CLASS: A
HISTORICAL_TEST: N/A (acceptance-evidence assertion)
INTRODUCED_AT_BASELINE: d38f871a230ca56713737b7de82f9111e7e73650
HISTORICAL_EXPECTATION: P2-10 adjudication register machine-parses to 27 classified items
SUPERSEDED_BY_ASSERTION_ID: N/A
SUPERSEDING_AUTHORITY: N/A
EFFECTIVE_FROM: N/A
CURRENT_REPLACEMENT_TEST: apps/backend/tests/test_phase2_reuse_adjudication.py
HISTORICAL_REPLAY_BASELINE: N/A
HISTORICAL_REPLAY_COMMAND: N/A
RATIONALE: Acceptance-evidence assertion binding E2-29 to the parser artifact. Never superseded by schema evolution.
STATUS: ACTIVE
```

## Accounting

- Entries = 9 (3 superseded Class H, 1 active Class C, 3 active Class P, 2 active Class B, 1 active Class A)
- Superseded = 3; Active = 6; Unclassified = 0
- Supersession chain: ASN-P200-MIG-0013-HEAD → ASN-P205-MIG-0014-HEAD; ASN-P200-MIG-NO0014 → ASN-P205-MIG-0014-HEAD; ASN-P1RW-MIG-0013-HEAD → ASN-P205-MIG-0014-HEAD (no cycles)
