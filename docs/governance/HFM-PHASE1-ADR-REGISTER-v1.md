# HFM Phase 1 ADR Candidate Register v1

Status: NPG-7 ADR CANDIDATES · NO DECISION FROZEN  
Rule: each item requires evidence, alternatives, acceptance impact, and an explicit later decision. No row authorizes implementation.

| ADR-ID | Decision area | Options to evaluate | Current evidence | Constraint from boundary | Status |
| --- | --- | --- | --- | --- | --- |
| ADR-01 | Physical deployment split | Single deployment; separated public/research services; hybrid | Client confirms two logical layers; physical split unknown | Public/research isolation, independent authorization and failure behavior | ADR_REQUIRED |
| ADR-02 | Search implementation | HFM relational/FTS; Elasticsearch; another reviewed index | Search is required; engine is not | Publication/RBAC filters, Chinese relevance, provenance context, operating cost | ADR_REQUIRED |
| ADR-03 | Knowledge relation storage | HFM relational relations; graph database; hybrid projection | A/B/C/D relations are required; graph product is not | One canonical truth, evidence/version/publication-aware relations | IMPLEMENTATION_LOCAL |
| ADR-04 | Object/media storage | Filesystem; object storage; MinIO/OSS; managed service | Media and scans need controlled handling; provider unknown | Rights, isolation, hashes, backup, publication withdrawal | IMPLEMENTATION_LOCAL |
| ADR-05 | Public/research API separation | Separate services; shared service with policy layer; gateway/projection | Two experiences are required; API topology unknown | No ambiguous authorization or research leakage | ADR_REQUIRED |
| ADR-06 | HFB adapter/migration strategy | Batch ETL; contract adapter; staged import service; reference-only | HFB Evidence mapping is dependency-only; no import authorized | Snapshot binding, validation, reconciliation, fail-closed, no runtime dependency | ADR_REQUIRED |
| ADR-07 | Identity/RBAC strategy | HFM-native; adapted HFB concepts; institutional IdP integration; hybrid | HFM RBAC absent; HFB roles are tightly coupled and client roles unknown | Deny-by-default, separation of duties, public anonymity, research ownership | ADR_REQUIRED |

ADR-03 / ADR-04 已由 `docs/audit/HFM-PHASE1-BLOCKING-ADR-RESOLUTION-AUDIT.md`（2026-08-29）裁决为 `IMPLEMENTATION_LOCAL`（local implementation choices；非阻塞、不扩大架构裁决范围）。

These options remain deliberately open. Selecting one is an NPG-7/implementation governance action, not a consequence of HFB existence or Gemini proposal text.
