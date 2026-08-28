# HFM Phase 1 Evidence Contract v1

Every acceptance criterion has at least one evidence row below. A criterion is `PASS` only when its artifact exists, is candidate-bound, and meets the stated pass condition.

| EVIDENCE-ID | WP-ID | Criterion | Evidence type | Required artifact | Verification method | Pass condition |
| --- | --- | --- | --- | --- | --- | --- |
| E-00 | P1-00 | Scope trace complete | AUDIT/MANIFEST | scope→WP→DAG→DoD matrix | count and cross-reference | 14/14 mapped, no orphan |
| E-01 | P1-01 | Admission fail-closed | API/DB/TEST | admission fixtures and rejection log | replay invalid cases | all invalid cases rejected |
| E-02 | P1-02 | Evidence chain resolves | DB/API/TRACE | chain fixture/report | follow SourceRef→Evidence→Citation | zero orphan links |
| E-03 | P1-03 | Person evidence/public state | API/E2E | A-domain fixture and evidence trace | inspect response and source | every public claim evidenced |
| E-04 | P1-04 | Literature lineage | DB/HASH/TRACE | Work→Edition→Version manifest | compare lineage and hashes | no lineage loss |
| E-05 | P1-05 | Historical C retrieval | API/E2E/NEGATIVE | search/reader fixture | query terms and forbidden prompts | source retrieval works; clinical output absent |
| E-06 | P1-06 | Heritage lineage rights | API/AUDIT | D relation and rights manifest | inspect evidence/public state | only evidenced/authorized claims public |
| E-07 | P1-07 | Reader reproducibility | E2E/TRACE | locator screenshot/trace and citation | reopen same locator | same version/passage resolves |
| E-08 | P1-08 | Search policy filtering | API/E2E/HAR | public/research search traces | compare role-scoped results | no unauthorized result |
| E-09 | P1-09 | Publication lifecycle | API/DB/E2E/AUDIT | review/approval/withdrawal log | execute state transitions | approval required; withdrawal observable |
| E-10 | P1-10 | RBAC deny-by-default | API/E2E/SECURITY | role matrix and negative traces | unauthorized calls/UI actions | all forbidden actions denied |
| E-11 | P1-11 | Public projection isolation | E2E/HAR | anonymous portal trace | inspect network/response | only approved content returned |
| E-12 | P1-12 | Research ownership isolation | E2E/API/DB | authenticated two-user trace | cross-user access attempt | private state isolated |
| E-13 | P1-13 | Reconciliation/audit | RECONCILIATION/HASH/DB | batch manifest and report | recompute counts/hashes | PASS with zero prohibited orphans |

## Required negative evidence

The integrated evidence set must also demonstrate: no HFB runtime dependency; no production import without M4; no CD-7; no clinical recommendation; no unpublished research exposure; no orphan Citation/Evidence/Source; no silent migration failure; no deferred-module leakage; no privilege escalation; no publication without approval; and no prohibited immutable-record mutation.
