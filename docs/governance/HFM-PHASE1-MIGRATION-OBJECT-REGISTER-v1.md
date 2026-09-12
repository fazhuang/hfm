# HFM Phase 1 Migration Object Register v1

| Object ID | Object class | Classification | HFM canonical target | Source snapshot | Required gate | Key rejection condition |
| --- | --- | --- | --- | --- | --- | --- |
| MC-01 | HFB Source records | TRANSFORM | HFM Source | `03755b57...` | M0–M4 | Missing identity, rights, hash, or artifact binding |
| MC-02 | Artifacts/files/media | TRANSFORM | HFM artifact boundary + Source/Version reference | HFB snapshot or customer batch | M0–M4 | Metadata-only, corrupt, duplicate, hash/MIME/rights failure |
| MC-03 | Evidence | TRANSFORM | HFM Evidence | `03755b57...` | M0–M4 | Orphan, invalid anchor, unsupported state, hash failure |
| MC-04 | SourceRef | TRANSFORM | HFM Source + SourceRef semantics | `03755b57...` | M0–M4 | Ambiguous/unaddressable locator or missing source/version |
| MC-05 | Citation | TRANSFORM | HFM Citation→Assertion | `03755b57...` | M0–M4 | Orphan target/evidence/source chain/version |
| MC-06 | Versions | TRANSFORM | HFM Work→Edition→Version→Chapter→Passage | `03755b57...` | M0–M4 | Ambiguous lineage, incomplete version, hash/rights failure |
| MC-07 | Corpus/textual content | TRANSFORM | HFM version-bound Passage/content | HFB snapshot or customer batch | M0–M4 | Incomplete/OCR-unverified/unauthorized/locator failure |
| MC-08 | Library metadata | TRANSFORM | HFM catalog/publication projections | `03755b57...` | M0–M4 | Duplicate/conflicting identity or unsupported public claim |
| MC-09 | Reader-related structures | REFERENCE_ONLY | None; later HFM reader contract | `03755b57...` | No migration gate | HFB routes/API/chunk IDs treated as canonical |
| MC-10 | Research project/report metadata | TRANSFORM | HFM-owned research project/report | `03755b57...` | M0–M4 | Unknown owner, privacy mismatch, orphan citation |
| MC-11 | Knowledge relations | TRANSFORM | HFM Entity/Assertion/EventRelation | `03755b57...` | M0–M4 | Dangling/unsupported/contradictory/clinical-prescriptive relation |
| MC-12 | Identity/RBAC: users, credentials, hashes, sessions, roles, assignments, audit identities | DO_NOT_MIGRATE | None under NPG-8 | `03755b57...` | Separate future authorization | Credential, ownership, consent, or HFM role mapping absent |

Detailed source identifiers, schema/version, transforms, validation, provenance/evidence/version binding, deduplication, idempotency, conflicts, failure, reconciliation, rollback/retry, and authorization rules are defined in [HFM-PHASE1-MIGRATION-CONTRACT-v1.md](/Users/likeming/Sites/hfm/docs/governance/HFM-PHASE1-MIGRATION-CONTRACT-v1.md).

## Batch manifest minimum

No object row is considered migrated without a batch manifest containing `BATCH-ID`, exact `SOURCE-SNAPSHOT`, `MAPPING-CONTRACT-VERSION`, input/output/rejected/duplicate counts, source/target hashes, and a `PASS` reconciliation result.
