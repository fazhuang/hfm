# HFM Phase 2 Acceptance Contract v1

Status: GOVERNANCE CANDIDATE · READY FOR INDEPENDENT AUDIT
Completion states: `NOT_STARTED | IN_PROGRESS | BLOCKED | PASS | FAIL` (frozen Phase-1 semantics)
Every AC is machine-verifiable where possible, binary PASS/FAIL, bound to a concrete artifact/test/behavior, and includes a negative-boundary test. No subjective criteria ("UI looks good", "works correctly", "reasonable performance", "user-friendly").

| WP | AC-ID | Acceptance criterion | Negative criterion | Required test/evidence |
| --- | --- | --- | --- | --- |
| P2-00 | P2-00-AC-01 | Scope taxonomy parses with exactly one classification per scope item (machine check) | no duplicate/absent classification | audit + script |
| P2-00 | P2-00-AC-02 | Negative-boundary guardrail tests pass on Phase-2 modules (no clinical/AI/3D/VR/XR/display markers) | no deferred/rejected leakage | guardrail test run |
| P2-00 | P2-00-AC-03 | Fixture-based acceptance policy is documented and applied to ≥1 WP AC | no content-population dependency blocks platform AC | contract review |
| P2-01 | P2-01-AC-01 | Anonymous user traverses public routes without auth challenge (E2E) | no login wall on public surface | E2E test |
| P2-01 | P2-01-AC-02 | Public surface renders only published projection; withdrawn items absent (fixture E2E) | no withdrawn/draft/private content visible | E2E + fixture |
| P2-01 | P2-01-AC-03 | No research/admin route reachable anonymously (route-guard test) | anonymous access to research/admin denied | route-guard test |
| P2-01 | P2-01-AC-04 | Accessibility assertions (axe) pass on home/portal routes | no a11y-blocking violation | axe assertion |
| P2-01 | P2-01-AC-05 | Responsive breakpoint matrix renders without layout regression | no breakpoint failure | viewport matrix test |
| P2-02 | P2-02-AC-01 | Unauthenticated user is redirected to login on research/admin routes | no anonymous research/admin access | auth-flow test |
| P2-02 | P2-02-AC-02 | Role-based route/permission matrix enforced in UI (deny-by-default) | no privilege escalation path | role matrix test |
| P2-02 | P2-02-AC-03 | Admin publish/withdraw actions append an audit entry | no unlogged privileged mutation | audit assertion |
| P2-02 | P2-02-AC-04 | Token revocation produces 401 handling and logout | no stale-token bypass | revocation test |
| P2-03 | P2-03-AC-01 | Reader resolves the same locator to the same passage/version (reproducibility E2E) | no non-reproducible locator | locator E2E |
| P2-03 | P2-03-AC-02 | Public reader hides draft/private/withdrawn passages | no unauthorized draft display | negative E2E |
| P2-03 | P2-03-AC-03 | Search results respect role scoping (anonymous = published only) | no research leakage in anonymous results | role-scoped search test |
| P2-03 | P2-03-AC-04 | Reader/search UI exposes no clinical recommendation surface (forbidden-term negative test) | no diagnosis/treatment/prescription/ranking output | negative test |
| P2-04 | P2-04-AC-01 | Visualization renders evidence-backed relations from P1-06 API (fixture) | no relation without evidence binding | API render test |
| P2-04 | P2-04-AC-02 | Unverified/private nodes are not displayed publicly | no unauthorized node display | negative render test |
| P2-04 | P2-04-AC-03 | Empty genealogy state renders gracefully (fixture) | no crash/blank state | empty-state test |
| P2-05 | P2-05-AC-01 | Media without sufficient rights metadata cannot publish (fail-closed) | no publication without rights | fail-closed test |
| P2-05 | P2-05-AC-02 | Original asset vs public derivative separation enforced (byte-hash binding) | no derivative/original confusion | hash test |
| P2-05 | P2-05-AC-03 | Withdrawal removes the public derivative from the public projection | no stale public media | withdrawal test |
| P2-05 | P2-05-AC-04 | Redaction/watermark applied deterministically (fixture) | no unredacted derivative | fixture test |
| P2-06 | P2-06-AC-01 | Export output preserves the disclaimer (fixture assertion) | no export without disclaimer | export assertion |
| P2-06 | P2-06-AC-02 | Export of withdrawn content is blocked | no withdrawn-content export | negative export test |
| P2-06 | P2-06-AC-03 | PDF export (if enabled) is deterministic on fixture | no nondeterministic output | PDF fixture test |
| P2-07 | P2-07-AC-01 | Environment separation verified by config matrix (dev/test/prod) | no cross-env leakage | config matrix check |
| P2-07 | P2-07-AC-02 | Secret scan finds no committed secrets | no secret in tree | secret scan |
| P2-07 | P2-07-AC-03 | Database migration gate runs before deploy in the release script | no unmigrated deploy | CI script test |
| P2-07 | P2-07-AC-04 | Backup/restore verified on the test environment | no untested restore | restore drill |
| P2-08 | P2-08-AC-01 | Health/ready endpoints respond correctly | no false-healthy state | health probe test |
| P2-08 | P2-08-AC-02 | Release-gate command (lint+type+test+build) passes in CI | no skipped/weakened gate | CI gate run |
| P2-08 | P2-08-AC-03 | Structured logs emitted on request lifecycle | no silent request loss | log assertion |
| P2-09 | P2-09-AC-01 | Admin can browse audit entries (role-gated) | non-admin denied | RBAC test |
| P2-09 | P2-09-AC-02 | Audit view is read-only (no mutation endpoints) | no mutation path | read-only test |
| P2-09 | P2-09-AC-03 | Reconciliation PASS/FAIL states displayed correctly | no state misdisplay | display test |
| P2-10 | P2-10-AC-01 | Every HFB reuse candidate has exactly one verdict (machine check) | no un-adjudicated candidate | script check |
| P2-10 | P2-10-AC-02 | No verdict implies HFB runtime dependency (zero-coupling) | no HFB runtime import | coupling scan |
| P2-10 | P2-10-AC-03 | Register references frozen NPG-004/reuse-matrix evidence | no unsupported verdict | evidence trace |

## Accounting

- AC total = 39 (P2-00:3, P2-01:5, P2-02:4, P2-03:4, P2-04:3, P2-05:4, P2-06:3, P2-07:4, P2-08:3, P2-09:3, P2-10:3)
- WP without AC = 0
- Missing AC = 0
