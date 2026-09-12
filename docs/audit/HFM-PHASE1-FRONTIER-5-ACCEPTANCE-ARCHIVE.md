# HFM Phase 1 Frontier-5 Acceptance Archive

## Candidate and scope

- Frontier-4 acceptance baseline: `311e24c610dd7c7325cada51b23cfc3c4ed1bcea`
- Frontier-5 candidate: `1339835976d9d13807c9c9c52a45a697a14bf9ad`
- Authorized work package: P1-07 (versioned source reader)
- Ancestry: PASS

P1-07 implements the frozen reader contract: a specific version/passage
locator reproducibly resolves to quotation, source context, citation/evidence
context, rights and publication state; unauthorized drafts fail closed.

## Candidate delta

The tracked candidate delta is exactly five files (`+1123`):

- `apps/backend/src/hfm/api/v1/phase1.py` — reader API wiring
- `apps/backend/src/hfm/core/locator.py` — structured locator parsing/serialization
- `apps/backend/src/hfm/phase1/reader.py` — versioned reader projection
- `apps/backend/tests/test_phase1_reader.py` — P1-07 tests
- `docs/audit/HFM-PHASE1-FRONTIER5-P1-07-IMPLEMENTATION.md` — implementation evidence

No schema migration, predecessor contract rewrite, deferred feature, or
downstream P1-11/P1-12 implementation was introduced.

## Acceptance results

- Locator reproducibility: PASS; exact passage/version ancestry is validated,
  malformed and mismatched locators fail closed, and canonical locators are
  deterministically regenerated.
- Citation/Evidence integration: PASS; reader reuses canonical Source,
  SourceRef, Evidence, Citation, Version and Publication records.
- Public/research boundary: PASS; public resolution requires published
  authorization, while research resolution requires authentication.
- Draft/withdrawal behavior: PASS; drafts, private material and withdrawn
  versions are inaccessible from the public reader.
- C-domain safety: PASS; no diagnosis, treatment, prescription, ranking,
  recommendation, or relation-traversal surface exists.
- P1-07 focused tests: 13 PASS.
- Full pytest: 359 PASS / 0 FAIL (candidate evidence; independent run exited 0).
- Ruff check: PASS.
- Ruff format check: PASS (153 files).
- mypy: PASS (140 source files).
- Migration gates: 20 PASS; Alembic head remains 0012.

## Boundaries and evidence

- Evidence inconsistencies: 0.
- Scope violations: 0.
- HFB runtime dependencies added: 0.
- Production HFB Import: `NOT PERFORMED / NOT AUTHORIZED`.
- CD-7: `NONEXISTENT`.
- Clinical recommendation behavior: 0.

The implementation evidence does not predeclare formal acceptance; acceptance
is recorded here by the independent auditor after verification.

## Known unrelated untracked artifact

`docs/research/2026-08-30-presentation-video-tools.md` exists as an
untracked, unstaged file, is not part of the candidate and is not referenced
by P1-07 evidence. The frozen acceptance contract does not require an empty
untracked namespace, so it is a non-blocking unrelated artifact and remains
untouched.

- `TRACKED_WORKTREE_CLEAN = PASS`
- `KNOWN_UNTRACKED_ARTIFACT_PRESENT = YES`

## Next executable frontier

With P1-07 PASS, the authoritative DAG makes both remaining WPs executable:

`NEXT_EXECUTABLE_FRONTIER = [P1-11, P1-12]`

- P1-11 blocking predecessors: P1-07 PASS, P1-08 PASS, P1-09 PASS, P1-10 PASS,
  P1-13 PASS.
- P1-12 blocking predecessors: P1-02 PASS, P1-07 PASS, P1-08 PASS, P1-09 PASS,
  P1-10 PASS.

No implementation of either WP is started by this archive.

## Verdict

`FRONTIER_5_ACCEPTED_READY_FOR_NEXT_FRONTIER`
