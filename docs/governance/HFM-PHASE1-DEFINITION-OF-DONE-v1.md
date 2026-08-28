# HFM Phase 1 Definition of Done v1

Status: NPG-9 GOVERNANCE OUTPUT · NOT IMPLEMENTATION AUTHORIZATION

| DoD-ID | Scope provenance | Exact PASS condition |
| --- | --- | --- |
| DOD-01 | P1-GOV; all IN scope | 14/14 IN items have exactly one WP, DAG position, acceptance, evidence and this DoD mapping. |
| DOD-02 | P1-GOV; DAG | DAG has 14 nodes, 26 declared edges, zero cycles, zero unreachable nodes, and no deferred dependency. |
| DOD-03 | P1-GOV/P1-CONTENT/P1-RBAC | AB-01…AB-16 checks pass; HFM owns canonical truth and no HFB runtime dependency exists. |
| DOD-04 | P1-CONTENT/P1-EVIDENCE/P1-VERSION | Admission, SourceRef/Evidence/Citation, version and rights rejection tests pass with no orphan chain. |
| DOD-05 | P1-A…P1-D | A/B/C/D capabilities each have evidenced domain fixtures, cross-domain references, version and publication state. |
| DOD-06 | P1-READER/P1-SEARCH/P1-PUBLISH/P1-RBAC | Reader/search/publication/RBAC criteria and positive/negative evidence all PASS. |
| DOD-07 | P1-PORTAL/P1-RESEARCH | Public projection and authenticated research state are demonstrably isolated in API and browser traces. |
| DOD-08 | P1-EVIDENCE/P1-VERSION/P1-13 | Every PASS has candidate-bound evidence; hashes, locators, audit and reconciliation artifacts verify. |
| DOD-09 | P1-RBAC/P1-C/P1-PUBLISH | Security negatives pass: no escalation, leakage, clinical recommendation, unapproved publication, orphan, or immutable mutation. |
| DOD-10 | P1-13; NPG-8 | Only authorized preparation M0–M3 evidence may close; M4–M7 remain not executed and Production HFB Import remains NOT PERFORMED. |
| DOD-11 | P1-GOV | No DEFERRED/REJECTED item appears as a positive WP, implementation dependency, or acceptance obligation; no CD-7 or Phase 1 authorization is implied. |
| DOD-12 | all IN scope | Integrated acceptance reproduces all criterion and negative evidence, records PASS/FAIL states, and closes the trace matrix with zero exceptions. |

PLATFORM_DOD is separate from CONTENT_BATCH_DOD. Full future customer content population is not required for platform closure unless explicitly selected as a fixture; rights and publication gates remain enforced for every populated batch.
