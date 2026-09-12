# HFM Phase 1 HFB→HFM Migration Contract v1

Status: NPG-8 GOVERNANCE CONTRACT · NO EXECUTION AUTHORIZED  
HFB source snapshot: `03755b57ec0e4c8023d1447619f7d6ead9e44d73`  
Target: HFM canonical domain owned by HFM  
Production HFB Import: `NOT PERFORMED`

## 1. Contract principles

Migration is explicit, versioned, repeatable, reconcilable, fail-closed, auditable, and authorization-gated. HFB is a migration/reuse source, never a permanent HFM runtime dependency. A legacy HFB identifier may be retained only as provenance/mapping metadata; it is never the sole HFM identity.

Customer content delivery is a separate track. Customer ownership does not imply that a file exists in HFB or is publishable. Customer batches follow `Manifest → Admission → Validation → Publication Approval → Production Import`.

## 2. Lifecycle gates M0–M7

| Gate | Name | Required evidence | Allowed state |
| --- | --- | --- | --- |
| M0 | Source Snapshot Verification | Exact HFB commit, tree/manifest, source hashes, license/rights boundary, immutable snapshot record | Preparation allowed; no target writes |
| M1 | Mapping Contract Verification | Versioned source-schema/target-schema mapping, transform rules, ownership and rejection rules reviewed | Preparation allowed; no target writes |
| M2 | Dry-run Replay | Disposable run against the frozen snapshot and mapping version; input/output/rejected manifests; no production DB writes | Preparation only; PASS never means import |
| M3 | Reconciliation | Counts, hashes, duplicates, orphans, mapping failures and rejected records reconcile to PASS/FAIL | Preparation only; FAIL blocks authorization |
| M4 | Production Migration Authorization | Independent signed governance artifact naming snapshot, mapping version, target, operator, scope, rollback and expiry | Required before any production write |
| M5 | Production Import | Authorized, observable, idempotent batch execution with quarantine and rollback capability | **Forbidden until M4 PASS**; current state NOT PERFORMED |
| M6 | Post-import Reconciliation | Independent target/source metrics, hash and lineage checks, rejected/quarantined inventory, public-state check | Required after M5; FAIL blocks release |
| M7 | Migration Freeze | Accepted batch manifest, immutable audit record, rollback window and explicit successor contract | Only after M6 PASS |

M0–M3 may be prepared or executed in an isolated environment. NPG-8 authorizes none of M4–M7 and does not authorize production import.

## 3. Batch identity and idempotency

Every batch must record:

```text
BATCH-ID
SOURCE-SNAPSHOT
MAPPING-CONTRACT-VERSION
INPUT-COUNT
OUTPUT-COUNT
REJECTED-COUNT
DUPLICATE-COUNT
HASH / MANIFEST
RECONCILIATION RESULT: PASS | FAIL
```

The idempotency key is `(SOURCE-SNAPSHOT, MAPPING-CONTRACT-VERSION, source identifier, target canonical identity)`. Replaying the same snapshot and mapping against the same target state produces no duplicate semantic records. A changed snapshot or mapping version creates a new batch and requires explicit conflict/revision handling; it must not silently overwrite reviewed records.

## 4. Common contract fields

Every class in the object register must specify: source system and snapshot; source identifier and schema/version; HFM canonical target; mapping rule and transforms; validation; provenance/evidence/version binding; deduplication and idempotency; conflict and failure behavior; reconciliation; rollback/retry; and authorization gate. The class-specific rules are below.

## 5. Class-specific contracts

### MC-01 HFB Source records — TRANSFORM

- Source: HFB snapshot `03755b57...`; HFB source schema/version recorded in manifest.
- Identifier: HFB source ID plus source hash; target: HFM `Source`.
- Mapping/transform: normalize title, source type, owner, rights and origin; retain HFB ID only as external provenance.
- Validation: required identity, uniqueness, source hash, rights status, and resolvable artifact references.
- Provenance/evidence/version: source manifest and admission evidence; no versionless source may anchor evidence.
- Dedup/idempotency: canonical source identity plus content/metadata hash; duplicate maps to one reviewed source.
- Conflict/failure: quarantine missing rights, identity collision, or invalid hash; no partial public record.
- Reconciliation/rollback/authorization: M3 counts and manifest PASS; batch rollback removes only unreviewed projections; M4 required for production.

### MC-02 Artifacts/files/media — TRANSFORM

- Source: immutable HFB artifact snapshot or later customer batch; target: HFM artifact reference/storage boundary, not merely metadata.
- Identifier: source path/object ID plus byte hash and metadata hash where applicable; mapping contract version required.
- Transform: MIME/type normalization, filename/path mapping, rights and publication state mapping.
- Validation: byte-level hash, metadata hash, MIME/type, size, readability, completeness, duplicate/corruption checks.
- Provenance/evidence/version: artifact must bind to Source/Version and rights record before admission.
- Conflict/failure: corrupt, missing, duplicate, or unauthorized artifacts are rejected/quarantined; metadata alone is never “migrated.”
- Reconciliation/rollback/authorization: accepted/rejected/hash mismatch counts in M3/M6; remove target object and projection through batch rollback; M4 before production.

### MC-03 Evidence — TRANSFORM

- Source: HFB academic evidence model in the frozen snapshot; target: HFM canonical `Evidence`.
- Identifier: HFB evidence ID as external mapping metadata; target identity generated by HFM rules.
- Transform: map evidence level, taint, content hash, statement/anchor and editorial state to HFM fields.
- Validation: valid SourceRef or Passage anchor, content hash, allowed evidence state, and owning assertion context.
- Provenance/evidence/version: evidence must retain source identity and bind to a HFM Version where text is cited.
- Dedup/idempotency: canonical anchor plus content hash and batch key; no duplicate semantic evidence.
- Conflict/failure: orphan/tainted-invalid/unsupported evidence is rejected or quarantined; no silent downgrade.
- Reconciliation/rollback/authorization: orphan and mapping-failure metrics; rollback removes only unaccepted records; M4 required for production.

### MC-04 SourceRef — TRANSFORM

- Source: HFB source-reference fields/services; target: HFM `Source` + structured `SourceRef` semantics.
- Identifier: HFB reference ID and original locator retained as provenance; HFM locator is canonical.
- Transform: convert page/section/paragraph coordinates into HFM locator fields without lossy coercion.
- Validation: source exists, locator is syntactically valid and addressable, and referenced Version/Passage exists where required.
- Provenance/evidence/version: every reference records source snapshot and version binding; unresolved locator fails closed.
- Dedup/idempotency: normalized source/version/locator tuple plus batch key.
- Conflict/failure: ambiguous or cross-version locators quarantine; no guessed page or passage.
- Reconciliation/rollback/authorization: orphan and mapping-failure counts; reversible batch; M4 before production.

### MC-05 Citation — TRANSFORM

- Source: HFB citation persistence/results; target: HFM `Citation` targeting an HFM `Assertion`.
- Identifier: HFB citation ID as external provenance; target identity follows HFM citation contract.
- Transform: map cited assertion, Evidence, SourceRef, Passage and pinned Version; reject polymorphic targets without an HFM assertion.
- Validation: no orphan citation; valid evidence/source chain, target assertion, version reproducibility, and rights state.
- Dedup/idempotency: `(assertion, evidence/source locator, version, batch)` semantic key.
- Conflict/failure: missing target/evidence/version or unsupported target is rejected/quarantined, never auto-attached.
- Reconciliation/rollback/authorization: orphan count must be zero for PASS; rollback unaccepted batch; M4 required for production.

### MC-06 Versions — TRANSFORM

- Source: HFB Version/ClassicalVersion/edition records; target: HFM Work→Edition→Version→Chapter→Passage lineage.
- Identifier: source version ID retained as external mapping; HFM lineage identity is canonical.
- Transform: normalize title, edition, publisher/date, lineage and status; preserve competing versions rather than merge by title.
- Validation: parent lineage, uniqueness, completeness, source hash and rights status.
- Provenance/evidence: version manifest and source references required before dependent evidence/citations.
- Dedup/idempotency: stable edition/version key plus source hash and batch key; changes create revision/conflict review.
- Conflict/failure: lineage ambiguity or hash mismatch quarantines the version and dependent records.
- Reconciliation/rollback/authorization: count accepted versions and dependent orphan checks; batch rollback; M4 required.

### MC-07 Corpus/textual content — TRANSFORM

- Source: HFB corpus/document/chunk/text assets or later customer package; target: HFM Passage and version-bound content.
- Identifier: source document/chunk ID plus byte/content hash; target passage identity is HFM-owned.
- Transform: segment only with a version-specific locator; retain original text/OCR status and editorial status.
- Validation: completeness, encoding, OCR/verification state, locator addressability, rights, and hash.
- Provenance/evidence/version: every passage binds to Version and SourceRef; unverified OCR cannot be presented as verified text.
- Dedup/idempotency: version/locator/content hash key; repeated batch does not duplicate passages.
- Conflict/failure: incomplete, corrupt, unlicensed, or locator-ambiguous text quarantines the whole dependent unit.
- Reconciliation/rollback/authorization: passage/input/hash/rejection metrics; reversible batch; M4 required.

### MC-08 Library metadata — TRANSFORM

- Source: HFB Library metadata and catalog fields; target: HFM Work/Edition/Version plus public/research metadata projection.
- Identifier: HFB document/catalog ID as external provenance; no HFB ID as canonical identity.
- Transform: map labels, collections and discovery metadata to HFM fields; strip HFB route/auth semantics.
- Validation: canonical lineage, rights/publication state, duplicate identity and source manifest.
- Provenance/evidence/version: metadata must point to an admitted source/version; unsupported claims remain non-public.
- Dedup/idempotency: canonical work/edition/version and normalized metadata hash.
- Conflict/failure: duplicate or conflicting catalog claims quarantine for editorial review.
- Reconciliation/rollback/authorization: accepted/rejected/conflict metrics; rollback projections; M4 required for production.

### MC-09 Reader-related structures — REFERENCE_ONLY

HFB reader components and route structures are not canonical data. They may inform a later HFM reader adaptation, but no HFB UI route, API contract, chunk identity, or runtime dependency is migrated. Any passage data still follows MC-07. No production migration gate is satisfied by copying reader code.

### MC-10 Research project/report metadata — TRANSFORM

- Source: HFB workspace/project/report metadata; target: future HFM research project/report entities under HFM identity and RBAC.
- Identifier: HFB project/report ID retained as external provenance; HFM ownership is canonical.
- Transform: map title, notes, citations and report state only where HFM contracts support them; do not import credentials or hidden HFB assumptions.
- Validation: owner mapping, citation/evidence validity, privacy classification, and report provenance.
- Dedup/idempotency: `(HFM owner, project/report external ID, snapshot, mapping version)`.
- Conflict/failure: unknown owner, private-data policy mismatch, or orphan citation quarantines the record.
- Reconciliation/rollback/authorization: privacy and orphan metrics; rollback private batch; M4 required.

### MC-11 Knowledge relations — TRANSFORM

- Source: HFB graph/relation records; target: HFM Entity/Assertion/EventRelation or another explicitly approved canonical relation.
- Identifier: HFB edge ID retained as provenance; HFM subject/object and relation identity are canonical.
- Transform: map relation type, direction, temporal qualifiers and evidence/version/publication state; no implicit graph truth.
- Validation: both endpoints exist, relation type is allowed, evidence/source/version chain is valid, and cross-domain ownership is explicit.
- Dedup/idempotency: canonical ordered endpoints + relation type + evidence/version + batch key.
- Conflict/failure: dangling, contradictory, unsupported, or clinically prescriptive relation quarantines; no inferred edge.
- Reconciliation/rollback/authorization: orphan/conflict/mapping metrics; reversible batch; M4 required.

### MC-12 Identity/RBAC data — DO_NOT_MIGRATE

Users, credentials, password hashes, sessions, tokens, roles, permission assignments, and HFB audit identities are not migrated by default. HFM identity/RBAC is a separate HFM-native or later ADR-approved integration. Any credential or user migration would require a new explicit contract, security review, consent/ownership proof, and independent M4 authorization; NPG-8 provides none.

## 6. Prohibited operations

- No direct HFB foreign-key or runtime API/database dependency in HFM.
- No use of HFB production runtime as a post-migration source of truth.
- No mixed HFB/HFM canonical ownership or silent schema coercion.
- No production import before M4 PASS.
- No interpretation of dry-run PASS as production completion.
- No migration of unknown-rights artifacts into public publication.
- No identity/credential migration under this contract.
