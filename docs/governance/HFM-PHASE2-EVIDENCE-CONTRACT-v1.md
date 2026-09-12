# HFM Phase 2 Evidence Contract v1

Status: GOVERNANCE CANDIDATE · READY FOR INDEPENDENT AUDIT
Every criterion in the Acceptance Contract is bound to at least one evidence row. Evidence is candidate-bound, machine-verifiable, and includes automated tests, integration/E2E tests, DOM/accessibility assertions, route/API contract tests, and build output. Screenshots are never the sole evidence.

| EVIDENCE-ID | WP | AC | Required artifact | Verification method | Pass condition |
| --- | --- | --- | --- | --- | --- |
| E2-00 | P2-00 | P2-00-AC-01 | scope matrix parse script + output | machine parse of Scope Register | 15 scope rows, exactly one classification each |
| E2-01 | P2-00 | P2-00-AC-02/03 | guardrail test suite + run log; fixture-based acceptance policy review | run `pytest tests/test_phase2_guardrails*`; review fixture policy application | zero forbidden markers in Phase-2 modules; fixture policy applied to ≥1 AC |
| E2-02 | P2-01 | P2-01-AC-01 | anonymous E2E test | run E2E against public routes | all public routes 200 without auth |
| E2-03 | P2-01 | P2-01-AC-02 | published-projection fixture E2E | run fixture E2E | withdrawn/draft absent from DOM |
| E2-04 | P2-01 | P2-01-AC-03/04/05 | route-guard + axe + viewport tests | run test suites | anonymous denial, axe clean, breakpoints pass |
| E2-05 | P2-02 | P2-02-AC-01 | auth-flow test | run auth E2E | redirect on unauthenticated research/admin route |
| E2-06 | P2-02 | P2-02-AC-02 | role matrix test | run role-matrix suite | every forbidden role-action denied |
| E2-07 | P2-02 | P2-02-AC-03/04 | audit assertion + revocation test | run suites | audit entry appended; revocation honored |
| E2-08 | P2-03 | P2-03-AC-01 | locator reproducibility E2E | run locator E2E twice | identical passage/version on reopen |
| E2-09 | P2-03 | P2-03-AC-02 | draft/withdrawn negative E2E | run negative E2E | hidden from public reader |
| E2-10 | P2-03 | P2-03-AC-03/04 | role-scoped search + forbidden-term test | run suites | anonymous=published only; no clinical output |
| E2-11 | P2-04 | P2-04-AC-01 | P1-06 API render fixture test | run render test | evidence-backed relations rendered |
| E2-12 | P2-04 | P2-04-AC-02 | unverified-node negative test | run negative render test | unverified/private nodes absent |
| E2-13 | P2-04 | P2-04-AC-03 | empty-genealogy fixture test | run empty-state test | graceful empty state |
| E2-14 | P2-05 | P2-05-AC-01 | rights fail-closed test | run media test suite | publish denied without rights metadata |
| E2-15 | P2-05 | P2-05-AC-02/04 | hash binding + redaction/watermark fixture test | run media test suite | original/derivative separated; deterministic derivative |
| E2-16 | P2-05 | P2-05-AC-03 | withdrawal projection test | run withdrawal test | public derivative removed from projection |
| E2-17 | P2-06 | P2-06-AC-01 | export disclaimer fixture assertion | run export test | disclaimer present in every export |
| E2-18 | P2-06 | P2-06-AC-02 | withdrawn-export negative test | run negative export test | export blocked |
| E2-19 | P2-06 | P2-06-AC-03 | PDF fixture determinism test | run PDF test | byte-stable output on fixture |
| E2-20 | P2-07 | P2-07-AC-01 | environment config matrix check | run config check | dev/test/prod distinct and isolated |
| E2-21 | P2-07 | P2-07-AC-02/03 | secret scan + migration-gate script test | run scan + CI script | no secrets; migration before deploy |
| E2-22 | P2-07 | P2-07-AC-04 | backup/restore drill log | run restore drill on test env | restore verified |
| E2-23 | P2-08 | P2-08-AC-01 | health/ready probe test | run probe test | correct status responses |
| E2-24 | P2-08 | P2-08-AC-02 | release-gate CI run | run gate command in CI | lint+type+test+build all PASS |
| E2-25 | P2-08 | P2-08-AC-03 | structured-log assertion | run log test | request lifecycle logged |
| E2-26 | P2-09 | P2-09-AC-01 | role-gated audit browse test | run RBAC test | admin browses; non-admin denied |
| E2-27 | P2-09 | P2-09-AC-02 | read-only enforcement test | run mutation-denial test | no mutation endpoint exposed |
| E2-28 | P2-09 | P2-09-AC-03 | reconciliation display test | run display test | PASS/FAIL rendered correctly |
| E2-29 | P2-10 | P2-10-AC-01 | adjudication register parse script | machine parse of register | exactly one verdict per candidate |
| E2-30 | P2-10 | P2-10-AC-02 | coupling scan | run HFB-import scan on Phase-2 modules | zero HFB runtime imports |
| E2-31 | P2-10 | P2-10-AC-03 | evidence trace | cross-reference register rows | every verdict cites NPG-004/reuse-matrix evidence |

## Accounting

- Evidence total = 32 (E2-00 … E2-31; grouped rows bind all 39 ACs)
- WP without evidence = 0
- Missing evidence = 0
- Orphan evidence = 0
