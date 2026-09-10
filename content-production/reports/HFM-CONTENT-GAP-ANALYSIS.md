# HFM Content Gap Analysis

## Current evidence

```text
CUSTOMER_HAS = 689 raw files; 667 PDF; 9 DOC/DOCX; 4 images; 2 video; 1 archive
CUSTOMER_HAS_BUT_NEEDS_PROCESSING = nearly all substantive files (OCR/text, metadata, entities, relations, media metadata)
CUSTOMER_HAS_BUT_RIGHTS_UNCLEAR = 689 pending customer confirmation
CUSTOMER_DOES_NOT_HAVE = NOT ASSERTED in this inventory-only phase
UNKNOWN = source authority, edition identity, page-level provenance, and publication permissions
```

| Product need | Assessment | Evidence / gap |
|---|---|---|
| Person profile | PARTIAL | Person texts, portrait, videos exist; chronology, verified relations, citations and completeness need extraction/review |
| Jiayi reader | PARTIAL | 612 related assets and editions/papers; complete searchable text, OCR quality, edition/page model and collation not yet established |
| Evidence view | PARTIAL | Many PDF/scan candidates; page/volume anchors, normalized quotations and evidence links not yet structured |
| Heritage | PARTIAL | 52 非遗/传承 assets include teaching, inheritor, qualification and institution evidence; events, people, dates and locations need extraction |

## Explicit gaps

- No claim is made that any individual PDF is complete, authoritative, or publishable before review.
- No reliable page-level citation index, edition graph, or person/event/place graph exists yet in the derived layer.
- No source/rights metadata is confirmed; all records remain review-required.
- No customer material has been written to `hfm_prod`; no missing content is being AI-generated.

## First production batch recommendation

Start with a bounded, reviewable slice: the three Huangfu Mi DOC/DOCX texts plus the portrait and the two Huangfu Mi videos; then select one representative 《针灸甲乙经》 edition PDF and its table-of-contents/pages. Produce source metadata, OCR/text extraction, entity candidates, page anchors, media metadata, and a human review pack. Keep all outputs under `content-production/`; import authorization is a later gate.
