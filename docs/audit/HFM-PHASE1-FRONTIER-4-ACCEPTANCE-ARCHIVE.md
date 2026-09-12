# HFM Phase 1 Frontier-4 Reacceptance Archive

## Candidate chain

- Frontier-3 acceptance baseline: `8e769791bd30493b66ce4a1ea7b75aea80fe3d9`
- Original Frontier-4 candidate: `abf1d57b89806abac0b18a472a39ab7e2f4a38af`
- Original verdict: `FRONTIER_4_REJECTED`
- Correction candidate: `728cd6c985585baecca69a478bc27af8383d5f85`
- Both baseline and original candidate are ancestors of the correction candidate.

## Correction closure

The correction changes exactly two files from the rejected candidate:

1. `apps/backend/alembic/versions/0012_p1_frontier4.py`
2. `docs/audit/HFM-PHASE1-FRONTIER4-P1-05-P1-06-IMPLEMENTATION.md`

Diffstat: `74 insertions(+), 14 deletions`; the migration portion is formatting-only.
AST-normalized comparison of the pre/post migration is identical, therefore
`MIGRATION_SEMANTIC_DELTA = 0`.

RC-1 is CLOSED: `ruff check` and `ruff format --check` both pass; 151 files
are formatter-clean. RC-2 is CLOSED: the evidence preserves the original
rejection, the original failed format check, the correction successor, the
semantic proof, and the post-correction commands/results.

## Acceptance

- P1-05: `ACCEPTED` — 11 focused tests pass; canonical C-domain identity,
  historical/versioned passage linkage, evidence-bound relations, publication
  projection, withdrawal, search and clinical-safety negatives verified.
- P1-06: `ACCEPTED` — 10 focused tests pass; canonical heritage identity,
  official-name/evidence lineage, P1-03 person integration, publication /
  withdrawal, public/research separation and authorization negatives verified.

Quality results:

- Relevant regression: 61 PASS (as recorded in candidate evidence).
- Migration gates: 20 PASS (`tests/test_migrations.py`).
- Full pytest: PASS, 346 passed / 0 failed / 1 warning.
- Ruff check: PASS.
- Ruff format check: PASS.
- mypy: PASS, 138 source files.

## Scope and safety

- Unauthorized scope additions: 0.
- P1-07, P1-11, P1-12 implementation: 0.
- Display, AI, 3D, VR, XR, Virtual Training: 0.
- Clinical recommendation behavior: 0.
- HFB runtime dependencies added: 0.
- Production HFB Import: `NOT PERFORMED / NOT AUTHORIZED`.
- CD-7: `NONEXISTENT`.

## Migration

Migration `0012` is the single head and has `down_revision = 0011`.
Repository migration tests establish the chain, upgrade, downgrade and
reversal gates. No production migration or import was performed.

## Next DAG frontier

PASS state now includes P1-00, P1-01, P1-02, P1-03, P1-04, P1-05, P1-06,
P1-08, P1-09, P1-10 and P1-13. The authoritative DAG yields:

`NEXT_EXECUTABLE_FRONTIER = [P1-07]`

P1-07 blocking predecessors: P1-02 PASS, P1-04 PASS, P1-05 PASS.

P1-11 remains blocked by P1-07. P1-12 remains blocked by P1-07. No next
frontier implementation is started or authorized by this archive.

## Verdict

`FRONTIER_4_ACCEPTED_READY_FOR_NEXT_FRONTIER`
