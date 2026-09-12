# HFM Phase 1 Content Batch Definition of Done Template v1

This template is a content-population gate, not a platform DoD and not a production authorization.

| Step | Required record | PASS condition |
| --- | --- | --- |
| Manifest | BATCH-ID, source snapshot, mapping version, inventory and hashes | Every input is enumerated and immutable |
| Admission | Source/artifact ownership and intake decision | Unknown/untrusted inputs are rejected or quarantined |
| Validation | MIME, byte/hash, schema, completeness, locator and OCR status | All required checks pass; failures are enumerated |
| Rights | Rights holder, publication/teaching/download/modification permissions | Public use is explicitly allowed; UNKNOWN is not publishable |
| Normalization | Canonical identity, Work/Edition/Version/Passage and relation mapping | No silent coercion; conflicts are resolved or quarantined |
| Evidence | SourceRef, Evidence, Citation, version and provenance chain | No orphan chain; evidence is addressable and reproducible |
| Approval | Editorial/reviewer decision and separation of duties | Approval is recorded before publication |
| Import | Authorized target batch execution | M4 authorization exists; idempotent write and quarantine are observable |
| Reconciliation | Source/accepted/rejected/target/duplicate/orphan/hash/mapping metrics | Result is `PASS`; no warning-only integrity closure |
| Publication | Approved projection, withdrawal and rollback state | Only approved content is public; withdrawal is effective and audited |

Customer assets CA-01…CA-05 remain import dependencies; CA-06/07/10 remain publication-rights dependencies. A partial or absent content batch does not erase or redefine platform capability scope.
