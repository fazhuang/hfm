# HFM-CONTENT-B05-SG — BLOCKING SCHEMA GAP DECISION AUDIT

```text
CURRENT_SCHEMA=0014 / 33 tables
CURRENT_WORKSPACE=/Users/likeming/Sites/hfm
CURRENT_HEAD=2b372b3ba92443cdf1862cc86d95f0b9b8879f0c
SCHEMA_CHANGED=NO
MIGRATION_CREATED=NO
HFM_PROD_WRITTEN=NO
B05_REMAINS_BLOCKED=YES
```

## First-principles result

The five rows marked blocking in the B05 gap register are not all genuine schema absences. Existing `sources.source_key`, `content_artifacts.content_hash/source_id`, `source_refs.locator`, `evidences.source_ref_id/source_passage_id/content_hash`, the assertion–evidence many-to-many table, and `citations.quote_text/passage_id` already provide substantial identity and provenance capability. The B05 map is stricter than the current model in those areas.

```text
BLOCKING_SCHEMA_GAPS_REPORTED=5
REAL_SCHEMA_GAPS=3 (SG-01, SG-02, SG-04)
FALSE_SCHEMA_GAPS_OR_MAPPING_GAPS=2 (SG-03, SG-05)
CORE_BLOCKING_GAPS=SG-01, SG-02, SG-04
NON_CORE_GAPS=SG-03, SG-05 as schema changes (the capabilities are core, but existing tables can represent them)
GAPS_RESOLVABLE_WITH_EXISTING_SCHEMA=SG-03, SG-05
GAPS_REQUIRING_SCHEMA_CHANGE=SG-01, SG-02, SG-04
```

## Gap decisions

### SG-01 — Document object / normalized title-author representation

```text
GAP_ID=SG-01
CONTENT_OBJECT=DOCUMENT (675)
SOURCE_CSV=documents.csv
SOURCE_FIELDS=DOCUMENT_ID,title_normalized,author_original,rights/source metadata
CURRENT_DATABASE_TABLE=sources,content_artifacts (no documents table)
CURRENT_DATABASE_CAPABILITY=sources.title/source_key/rights fields; content_artifacts hash/admission/source binding
WHY_CURRENT_SCHEMA_CANNOT_REPRESENT=No first-class document identity with separate normalized title and original author fields; forcing this into source/artifact loses document semantics and dual title/author provenance.
PRODUCT_SURFACE_AFFECTED=SEARCH,RESEARCH,JIAYI_READER, EVIDENCE_VIEW
USER_VISIBLE_IMPACT=No reliable document listing, normalized search result, or document-to-source display.
CAN_IMPORT_WITHOUT_SCHEMA_CHANGE=NO
DATA_LOSS_RISK=HIGH
SEMANTIC_DISTORTION_RISK=HIGH
SCHEMA_CHANGE_REQUIRED=YES
MINIMUM_CHANGE=New documents table: id UUIDv7 PK, stable_id varchar(100) UNIQUE NOT NULL, source_id FK sources.id NOT NULL, title_normalized varchar(500) NOT NULL, title_original varchar(500), author_original varchar(500), document_type varchar(80), review_status varchar(40), created_at/updated_at; indexes on stable_id/title_normalized/source_id.
```

Option A (no schema) is unsafe; Option B (the table above) is the minimum correct change; Option C (full bibliographic/paper model) is deferred. Recommendation: Option B.

### SG-02 — Persistent content stable IDs

```text
GAP_ID=SG-02
CONTENT_OBJECT=ALL B04 content objects
SOURCE_CSV=all normalized object CSVs
SOURCE_FIELDS=DOCUMENT_ID/PERSON_ID/WORK_ID/EDITION_ID/EVIDENCE_ID/etc.
CURRENT_DATABASE_TABLE=all BaseModel tables; sources.source_key is the only explicit external key
CURRENT_DATABASE_CAPABILITY=Most rows have UUIDv7 id PKs; persons/events/works share entity IDs; Source has unique source_key.
WHY_CURRENT_SCHEMA_CANNOT_REPRESENT=External HFM-* IDs are not the model's UUIDv7 PK contract, and no uniform external stable-id lookup exists across content types. An import manifest alone cannot provide database-level idempotency or object reverse lookup.
PRODUCT_SURFACE_AFFECTED=ALL (especially SEARCH, RESEARCH, JIAYI_READER, EVIDENCE_VIEW)
USER_VISIBLE_IMPACT=Re-import can duplicate objects or lose deterministic links to source records.
CAN_IMPORT_WITHOUT_SCHEMA_CHANGE=NO (unless Product Owner explicitly changes the contract to treat UUID PKs/source_key as the canonical IDs)
DATA_LOSS_RISK=HIGH
SEMANTIC_DISTORTION_RISK=HIGH
SCHEMA_CHANGE_REQUIRED=YES
MINIMUM_CHANGE=Add stable_id varchar(100) UNIQUE NOT NULL to each imported content table (or one approved content_identity table keyed by object_type/object_id/stable_id); preserve UUID PKs and add indexes. Do not overwrite existing IDs.
```

Option A can work only after a formal identity-contract decision, not by implicit mapping. Option B is the minimum extension; Option C is unnecessary. Recommendation: Option B, preferably one coherent identity table if the team wants to avoid repeating columns and can enforce FK/type integrity.

### SG-03 — Source-page → asset → SHA provenance chain

```text
GAP_ID=SG-03
CONTENT_OBJECT=ALL content with source references
SOURCE_CSV=jiayi-source-pages.csv, evidence.csv, person-facts.csv, person-timeline.csv
SOURCE_FIELDS=ASSET_ID,SOURCE_PDF,SHA256,PAGE,SOURCE_LOCATION,OUTPUT
CURRENT_DATABASE_TABLE=sources,content_artifacts,source_refs,evidences,citations
CURRENT_DATABASE_CAPABILITY=source_key/source_uri/rights; content_hash/source_id; source_refs.locator JSON; evidence source_ref/source_passage/content_hash; citations evidence/passage/quote.
WHY_CURRENT_SCHEMA_CANNOT_REPRESENT=The current B05 mapping does not define how ASSET_ID/SHA/page rows map into these existing anchors. This is a missing import mapping contract, not proof that provenance columns/tables are absent.
PRODUCT_SURFACE_AFFECTED=EVIDENCE_VIEW, JIAYI_READER, RESEARCH
USER_VISIBLE_IMPACT=Without a mapping, page-level citations cannot be rendered or audited; with the existing chain mapped correctly, no new schema is required.
CAN_IMPORT_WITHOUT_SCHEMA_CHANGE=YES, after a reviewed mapping
IF_YES_HOW=Create/resolve Source by source_key=ASSET_ID (or a documented asset key), ContentArtifact by immutable content_hash, SourceRef with locator={source_pdf,page,output,layer}, then bind Evidence/Citation through FKs; preserve alternate outputs as provenance records.
DATA_LOSS_RISK=LOW if mapping is complete; HIGH if flattened
SEMANTIC_DISTORTION_RISK=LOW with structured locator; HIGH if stored in description strings
SCHEMA_CHANGE_REQUIRED=NO (mapping/adapter required)
MINIMUM_CHANGE=No DB delta; publish an import adapter and locator field contract.
```

Option A is recommended. Option B is only needed if the Product Owner requires queryable first-class asset/output columns beyond the existing JSON locator and hash.

### SG-04 — Person aliases / source_forms

```text
GAP_ID=SG-04
CONTENT_OBJECT=PERSON (17; aliases affect entity resolution across documents)
SOURCE_CSV=persons.csv (aliases/source_forms)
SOURCE_FIELDS=aliases,source_forms,variant names
CURRENT_DATABASE_TABLE=entities,persons
CURRENT_DATABASE_CAPABILITY=entities.name/name_zh; persons name_pinyin/courtesy_name/pseudonym/dynasty; no repeatable alias collection.
WHY_CURRENT_SCHEMA_CANNOT_REPRESENT=Multiple source-specific variants cannot be represented without overwriting or concatenating values into a single field.
PRODUCT_SURFACE_AFFECTED=PERSON_PROFILE, SEARCH, RESEARCH
USER_VISIBLE_IMPACT=Search/entity resolution misses historical names and source spellings; provenance of each variant is lost.
CAN_IMPORT_WITHOUT_SCHEMA_CHANGE=NO
DATA_LOSS_RISK=HIGH
SEMANTIC_DISTORTION_RISK=HIGH
SCHEMA_CHANGE_REQUIRED=YES
MINIMUM_CHANGE=New person_aliases table: id UUIDv7 PK, person_entity_id FK entities.id NOT NULL, alias_text varchar(300) NOT NULL, alias_type varchar(60), source_ref_id FK source_refs.id NULL, review_status varchar(40) NOT NULL, UNIQUE(person_entity_id,alias_text,alias_type), index(alias_text).
```

Option A (comma-joined persons field) is rejected. Option B is the minimum correct relation; Option C (full authority/ontology service) is deferred. Recommendation: Option B.

### SG-05 — Fact evidence page/quote and multi-source binding

```text
GAP_ID=SG-05
CONTENT_OBJECT=FACT/CLAIM (24)
SOURCE_CSV=person-facts.csv, evidence.csv
SOURCE_FIELDS=SOURCE_PAGE,QUOTE_OR_CONTEXT,conflict/multi-source references
CURRENT_DATABASE_TABLE=assertions,assertion_evidences, evidences, source_refs, citations
CURRENT_DATABASE_CAPABILITY=Assertion has value/object/confidence/editorial state; assertion_evidences is many-to-many; Evidence anchors source_ref/source_passage and hash; SourceRef.locator is structured JSON; Citation has quote_text and passage/evidence FKs.
WHY_CURRENT_SCHEMA_CANNOT_REPRESENT=The B05 map omitted the existing assertion/evidence/citation path. Page and quote can be represented via SourceRef.locator and Citation.quote_text; multi-source facts via assertion_evidences.
PRODUCT_SURFACE_AFFECTED=EVIDENCE_VIEW, PERSON_PROFILE, RESEARCH
USER_VISIBLE_IMPACT=Only if the adapter fails: claims would appear uncited. Correct mapping preserves page/quote and conflicting assertions.
CAN_IMPORT_WITHOUT_SCHEMA_CHANGE=YES, after mapping
IF_YES_HOW=Assertion per fact; Evidence per source anchor; SourceRef.locator for page; Citation.quote_text for quoted context; link all evidence through assertion_evidences; keep conflict groups in review metadata until a separately authorized conflict model exists.
DATA_LOSS_RISK=LOW with this mapping; HIGH if quote/page is concatenated into assertion.value
SEMANTIC_DISTORTION_RISK=LOW with structured anchors
SCHEMA_CHANGE_REQUIRED=NO for current 24-row seed
MINIMUM_CHANGE=Import adapter contract; optional later conflict_group table/column is non-blocking.
```

Option A is recommended for B05. Option B (evidence extension) is optional only if locator JSON/queryability is insufficient after a prototype. Option C is deferred.

## Consolidation and migration proposal

```text
CONSOLIDATE=YES
CONSOLIDATION=SG-03 + SG-05 share the existing Source→SourceRef→Evidence/Citation provenance abstraction; do not create duplicate provenance tables.
PROPOSED_NEW_TABLES=documents, person_aliases (and optionally one generic content_identity table if chosen instead of repeated stable_id columns)
PROPOSED_CHANGED_TABLES=none required for SG-03/SG-05; stable_id columns or identity table for SG-02
PROPOSED_NEW_COLUMNS=documents fields; stable_id contract; no ad-hoc description fields
PROPOSED_MIGRATION=0015 (one coherent content-schema migration for SG-01/SG-02/SG-04; SG-03/SG-05 are adapter-only)
BREAKING_API_CHANGE=NO by default (additive tables/fields; existing response contracts remain compatible)
FRONTEND_CHANGE_REQUIRED=YES only when exposing newly imported document/alias/evidence data; not required to preserve existing routes
EXISTING_DATA_MIGRATION_REQUIRED=YES for backfill of stable IDs only if existing rows receive the new columns; preserve system_admin and all existing rows
SYSTEM_ADMIN_PRESERVATION=YES
SOURCE_TRACEABILITY_PRESERVATION=YES (SourceRef.locator/content_hash/alternate-output policy retained)
```

## Recommendation

```text
RECOMMENDATION=B = MINIMAL_SCHEMA_CHANGE_RECOMMENDED
MINIMUM_SCHEMA_CHANGE_SET=documents table + person_aliases table + explicit stable-id persistence (columns or one integrity-enforced identity table); reuse existing provenance/evidence/citation tables for SG-03/SG-05
RECOMMENDED_NEXT_ACTION=PRODUCT_OWNER_DECISION on stable-id representation and authorize one 0015 content-schema migration; separately approve the SG-03/SG-05 import adapter contract
B05_REMAINS_BLOCKED=YES
```

No schema, ORM, API, migration, import, or database change was performed in this audit.

```text
SCHEMA_CHANGED=NO
MIGRATION_CREATED=NO
PRODUCT_CODE_CHANGED=NO
HFM_PROD_WRITTEN=NO
CONTENT_IMPORTED=NO
NEXT_ACTION=PRODUCT_OWNER_SCHEMA_DECISION
STOP=MANDATORY
```
