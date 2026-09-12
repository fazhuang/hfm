# HFM Phase 1 Acceptance Contract v1

Status: NPG-9 GOVERNANCE OUTPUT · EVIDENCE REQUIRED  
Completion states: `NOT_STARTED | IN_PROGRESS | BLOCKED | PASS | FAIL`

| WP-ID | Inputs | Outputs | Preconditions | Acceptance criteria | Negative criteria | Required tests/evidence | Completion state |
| --- | --- | --- | --- | --- | --- | --- | --- |
| P1-00 | NPG-6/7/8 | traceable governance contract | frozen inputs | every IN scope maps once to WP/DAG/criterion/DoD | no unauthorized WP or scope expansion | audit + manifest | NOT_STARTED |
| P1-01 | source/artifact/content rules | admission contract | P1-00 | invalid provenance/rights is rejected; admitted content has source/version state | no metadata-only admission | API/DB/negative tests | NOT_STARTED |
| P1-02 | HFM canonical models; HFB mapping dependency | evidence chain | P1-01 | SourceRef→Evidence→Citation chain resolves to HFM targets | no orphan citation/evidence/source | DB/API/trace | NOT_STARTED |
| P1-03 | CA-01 and admitted entities | A capability | P1-01/02 | person/event records expose evidence and publication state | no unsupported biography claim | API/E2E/evidence | NOT_STARTED |
| P1-04 | CA-02/03 | B capability | P1-01/02 | work/edition/version/passages preserve lineage and rights | no version collapse or unlicensed publication | DB/reader trace | NOT_STARTED |
| P1-05 | CA-03/04/05 | C capability | P1-01/02/04 | historical disease/point/meridian/technique retrieval returns source/version/citation | no diagnosis, treatment, ranking or prescription | search/API/negative tests | NOT_STARTED |
| P1-06 | CA-06/07 and lineage evidence | D capability | P1-01/02/03 | lineage relations carry official-name, evidence and publication state | no unverified heritage/inheritor claim | API/rights/E2E | NOT_STARTED |
| P1-07 | admitted versioned text | reader | P1-02/04/05 | passage locator reproducibly opens source context and citation | no reader access to unauthorized draft | E2E/locator trace | NOT_STARTED |
| P1-08 | admitted A/B/C/D index inputs | search | P1-01/02/domain WPs | public filters published; research filters authorized; result retains source context | no research leakage or uncited hit | API/E2E/index trace | NOT_STARTED |
| P1-09 | content and RBAC contracts | publication workflow | P1-00/01/02/10 | review→approve→publish→withdraw→rollback states are observable | no publish without approval; withdrawal cannot erase audit | API/DB/E2E/audit | NOT_STARTED |
| P1-10 | client role policy; HFM identity boundary | identity/RBAC | P1-00 | deny-by-default roles and separation of duties are enforced | no privilege escalation or public auth bypass | auth/API/E2E/security | NOT_STARTED |
| P1-11 | reader/search/publication/RBAC | portal | dependencies PASS | anonymous users see approved projection only | no research/private/unpublished response | browser/API/HAR | NOT_STARTED |
| P1-12 | reader/search/RBAC/evidence | research experience | dependencies PASS | authenticated workflow preserves ownership and richer evidence access | no cross-user/tenant access or public exposure | browser/API/DB | NOT_STARTED |
| P1-13 | version/provenance/migration prep | audit/reconciliation | P1-01/02 | immutable lineage, batch metrics, and reconciliation PASS are recorded | no silent failure, mutation, or WARN-only integrity completion | DB/hash/reconciliation | NOT_STARTED |

No criterion is satisfied by subjective claims such as “beautiful” or “complete”; each requires the evidence contract.
