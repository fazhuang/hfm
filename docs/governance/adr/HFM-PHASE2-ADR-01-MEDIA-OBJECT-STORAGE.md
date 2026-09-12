# HFM Phase 2 ADR-P2-01 — Media / Object Storage

Status: ADR CANDIDATE · READY FOR INDEPENDENT AUDIT · NOT BINDING UNTIL PHASE-2 GOVERNANCE ACCEPTANCE
Phase-1 Completion Baseline: `c17be40be6f055498fde11c0042e71d3a1056a7c`
Authority: CR-013/015 (media asset families); G4/G13 gap register; MC-02 (artifact contract); Technology Baseline (object storage JUSTIFIED_WITH_CONDITIONS — condition: G4 media need proves it).

## Decision candidates

### Candidate A (recommended): HFM-native media with S3-compatible object storage + PostgreSQL metadata

- **Media asset storage model**: binaries in an object store behind an S3-compatible abstraction; metadata (identity, rights, hashes, publication state, lineage) in HFM PostgreSQL.
- **Binary vs metadata boundary**: clear — bytes live in object storage, everything queryable lives in the relational model; no binary blobs in the relational DB (no evidence supports blob-in-DB for this workload).
- **Rights metadata**: rights holder, license/use basis, restriction, expiry, publication permission — required fields on every media record; fail-closed publication when insufficient.
- **Public derivative**: generated derivative (redacted/watermarked/resized) is a distinct object with its own hash; original asset is never served publicly.
- **Original asset**: stored privately; never in the public projection.
- **Redaction / watermarking**: deterministic transformation at ingestion; derivative hash binds the transformation.
- **Withdrawal**: projection-state change removes the public derivative from public visibility; original retained per retention policy.
- **Hash binding**: byte-hash on every object; original/derivative linkage via hash + version lineage.
- **Versioning**: media versions as immutable objects with lineage to source/version records.
- **Retention**: retention policy per rights record; expiry enforced; withdrawal contact retained.

### Candidate B (rejected): binaries embedded in relational database

- Requires justification evidence none exists for this workload; rejected.

### Candidate C (deferred option): fully managed object storage vendor decision

- Implementation abstraction is S3-compatible; concrete vendor/region decision is a deployment concern (ADR-P2-02), not a media-model concern.

## Non-negotiables

- No file presence implies public display rights (fail-closed).
- No HFB media model inheritance (Reuse Matrix: Media = DEPRECATE + Build).
- HFM runtime zero-coupling to HFB remains mandatory.

## Impact

- **Architecture**: new media domain module (P2-05); public/research display integration point (non-blocking).
- **Migration**: MC-02 artifact mapping applies to future content batches; no migration executed.
- **Security**: rights + redaction + watermark enforced at ingestion; object-store access controlled.
- **Content**: depends on client assets and rights (Customer Dependency Register).
