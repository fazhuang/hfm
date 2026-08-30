# HFM Phase 2 Fixture-Based Acceptance Policy v1

Status: P2-00 IMPLEMENTATION-GENERATED GOVERNANCE ARTIFACT · BINDS TO THE FROZEN PHASE-2 CONTRACTS  
Scope: `docs/governance/HFM-PHASE2-*` (allowed module per frozen P2-00 contract, in-scope deliverable "fixture-based acceptance policy")  
Authority: HFM-PHASE2-ACCEPTANCE-CONTRACT-v1.md, P2-00-AC-03; frozen contract text takes precedence over this policy.

## 1. Policy statement

Synthetic or controlled fixtures may satisfy engineering acceptance criteria
where the frozen Phase-2 Acceptance Contract explicitly permits it — that is,
where the criterion text itself marks fixture usage (e.g. "(fixture)",
"(fixture E2E)", "(fixture assertion)"). The contract-verifier machine-checks
this by selecting every frozen AC whose criterion cell contains the token
`fixture` and asserting at least one exists (P2-00-AC-03).

## 2. Mandatory distinctions (frozen, non-negotiable)

- fixture acceptance ≠ customer content acceptance
- fixture acceptance ≠ production content readiness
- fixture acceptance never replaces customer-provided content, rights,
  authorizations, or production data

## 3. Fixture-permitted ACs (machine-derived from the frozen contract)

The frozen Acceptance Contract marks the following ACs as fixture-permitted
(machine-derived by the P2-00 verifier from the criterion text; any change to
this list must come from a governance amendment to the frozen contract, never
from this policy):

- P2-00-AC-03 — fixture-based acceptance policy (this policy)
- P2-01-AC-02 — public projection fixture E2E
- P2-04-AC-01 — visualization API render fixture
- P2-04-AC-03 — empty-genealogy fixture
- P2-05-AC-04 — redaction/watermark fixture
- P2-06-AC-01 — export disclaimer fixture assertion
- P2-06-AC-03 — PDF fixture determinism

## 4. Rules

1. No AC without an explicit `fixture` token in the frozen criterion may be
   satisfied by fixture alone.
2. No fixture may fabricate customer content, rights, or authorizations.
3. Fixture PASS recorded as engineering acceptance only; production content
   readiness is governed by the Customer Dependency Register and NPG-005.
4. The verifier (`apps/backend/src/hfm/phase2/`) validates this policy
   mechanically; policy text alone is never acceptance evidence.
