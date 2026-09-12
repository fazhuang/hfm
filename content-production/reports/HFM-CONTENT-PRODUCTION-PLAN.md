# HFM Content Production Plan

## Governance

```text
hfmzl = RAW / IMMUTABLE / READ ONLY
content-production = DERIVED / WORKING
hfm_prod = APPROVED PRODUCTION DATA ONLY
NO_UNREVIEWED_PRODUCTION_IMPORT = YES
```

## Priority and processing matrix

| Priority | Scope | Required work |
|---|---|---|
| P0 | None yet | No asset is directly production-ready until source, rights, identity and review gates pass |
| P1 | Huangfu Mi package; representative Jiayi editions/papers; heritage evidence | OCR/text extraction, metadata, entity/relation candidates, image/video metadata, transcription where applicable, human review |
| P2 | Remaining Jiayi papers/editions and supporting institutional material | Batch extraction and prioritization after P1 quality baseline |
| P3 | Housekeeping/archives, exact duplicates, low-value derivatives | Preserve and index; no deletion |
| PX | Any source/rights/identity conflict | Hold for customer/editorial decision |

## Work packages

1. `00-inventory`: completed recursive file inventory and SHA-256 manifest.
2. `01-classification`: completed provisional category/surface matrix.
3. `02-metadata`: completed candidate object map; next add author, institution, date, publication, identifier and page/location fields.
4. `03-text-extraction`: OCR/extract only approved P1 samples; preserve raw-to-derived links and tool/version metadata.
5. `04-entities` / `05-relations`: propose PERSON, WORK, BOOK_EDITION, EVENT, PLACE, INSTITUTION, INHERITOR and evidence links; never auto-promote inference to fact.
6. `06-media`: probe image/video/audio technical metadata and create separate derived derivatives; do not overwrite raw.
7. `07-review`: source, rights, authenticity, attribution and editorial review queues.
8. `08-approved` / `09-import-packages`: only after explicit approval; database import is a separate authorized task.

## Required flags per asset

`OCR_REQUIRED`, `TEXT_EXTRACTION_REQUIRED`, `METADATA_EXTRACTION_REQUIRED`, `MANUAL_REVIEW_REQUIRED`, `ENTITY_EXTRACTION_REQUIRED`, `RELATION_EXTRACTION_REQUIRED`, `IMAGE_PROCESSING_REQUIRED`, `VIDEO_PROCESSING_REQUIRED`, `TRANSCRIPTION_REQUIRED` should be added during Batch 01 review. Current inventory intentionally does not run OCR, transcription, media conversion, or database writes.

## Traceability contract

Every derived record must retain `ASSET_ID`, raw relative path, source page/location, extractor and version, processing timestamp, confidence, reviewer, and status. Keep `SOURCE_FACT`, `EXTRACTED_FACT`, `NORMALIZED_METADATA`, `EDITORIAL_COPY`, and `AI_INFERENCE` separate; AI inference is never verified fact.

## Acceptance gate for Batch 01

Batch 01 may proceed only after Product Owner review of the inventory and explicit authorization. Acceptance requires raw hashes unchanged, page-level provenance captured, rights/source status recorded, no unreviewed imports, and a reviewable derived package.
