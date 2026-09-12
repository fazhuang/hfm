# HFM PROD DOCUMENT IMPORT — FROZEN STATE RECORD

RECORDED_AT: 2026-09-10 (post CONTROLLED_HFM_PROD_DOCUMENT_IMPORT acceptance)

## Frozen conclusions (authoritative)

HFM_PROD_DOCUMENT_IMPORT=ACCEPTED

DOCUMENT_CONTENT_BASELINE=675
DOCUMENT_STABLE_ID_BASELINE=EXACT_IMPORTED_675_SET
DOCUMENT_STABLE_ID_POLICY=LONG_TERM_STABLE_ASSET_IDENTITY
CURRENT_DOCUMENT_SCHEMA=EVOLVABLE_NOT_FINAL_DOMAIN_MODEL
FUTURE_SCHEMA_CHANGE_POLICY=FORWARD_MIGRATION_ONLY
DOCUMENT_DOMAIN_MODEL_FINALIZED=NO

DOCUMENT_IMPORT_PHASE=CLOSED

PERSON_IMPORT=UNAUTHORIZED
WORK_IMPORT=UNAUTHORIZED
EDITION_IMPORT=UNAUTHORIZED
PUBLICATION=UNAUTHORIZED
UI_CONTENT_PROPAGATION=UNAUTHORIZED

STOP=NO
BLOCKER=NONE

## Environment / baseline cross-reference

- AUTHORIZED_BASELINE (git HEAD) = 5c7253dfd088c64fc991e951f04d196cb3ae1d74 (hfm-canonical)
- Importer commit: 5c7253d… (content-production/import/B05/tools/hfm_import_documents.py)
- Input package: content-production/import/B05/package/documents.csv
  (SHA256=27bccdd6cf9bb610de694bc88ae83bea8db532ba8146226e6ebcf56c98048da7, 675 rows, 675 unique DOCUMENT_ID)
- hfm_prod: PostgreSQL 16.14, alembic 0015 (single head), documents=675, stable_id set == imported 675 set,
  dup groups=0, null stable_id=0, null title=0; persons/works/editions=0.
- Re-read confirmation: HEAD=5c7253dfd088c64fc991e951f04d196cb3ae1d74; tracked dirty=0.

## Semantics (frozen)

- Real customer content is now present in hfm_prod (LOCAL_PRODUCTION_EQUIVALENT runtime), DOCUMENTS only.
- Do NOT regenerate stable_id to resolve future domain-model changes.
- Future schema evolution: FORWARD_MIGRATION_ONLY; future PERSON/WORK/EDITION must link to the existing
  imported DOCUMENT identities.
- This record does NOT finalize the DOCUMENT domain model and does NOT authorize any other object type,
  publication, or UI propagation.
