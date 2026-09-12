# HFM Customer Material Inventory

```text
ROOT = /Users/likeming/Sites/hfm/hfmzl
TOTAL_FILES = 689
TOTAL_SIZE_BYTES = 6,673,295,130
PDF = 667
DOC_DOCX = 9
XLS_XLSX = 0
PPT_PPTX = 0
IMAGE = 4
VIDEO = 2
AUDIO = 0
TEXT = 0
ARCHIVE = 1
OTHER = 6
CLASSIFIED_FILES = 689 (provisional path/content-signature classification)
UNCLASSIFIED_FILES = 0 (all remain SOURCE_STATUS=NEEDS_REVIEW)
EXACT_DUPLICATE_GROUPS = 2
HIGH_VALUE_P0 = 0
HIGH_VALUE_P1 = 682
RIGHTS_CLEAR = 0
RIGHTS_UNCLEAR = 689
PERSON_RELEVANT_ASSETS = 76
JIAYI_RELEVANT_ASSETS = 612
HERITAGE_RELEVANT_ASSETS = 52
RESEARCH_RELEVANT_ASSETS = 665
OCR_REQUIRED = 667
VIDEO_PROCESSING_REQUIRED = 2
AUDIO_TRANSCRIPTION_REQUIRED = 2
```

The machine inventory is complete and recursive. Every row has a stable `ASSET_ID`, relative path, type, byte size, SHA-256, source directory, provisional category, surface candidates, and review flags. The authoritative machine files are `00-inventory/customer-assets.csv`, `00-inventory/duplicate-groups.csv`, `01-classification/content-classification.csv`, `02-metadata/content-object-map.csv`, and `07-review/rights-review.csv`.

Classification uses directory/name signals plus MIME/extension; it is a production planning classification, not OCR or scholarly fact verification. PDFs dominate the corpus (667), with a large 《针灸甲乙经》 branch, 52 non-heritage evidence assets, 24 Huangfu Mi-related assets, and one housekeeping/unknown item. No raw file was modified, moved, renamed, deleted, or imported.

## High-value findings

- 皇甫谧人物：three DOC/DOCX texts, two MPG videos, one portrait, and related material indicate a viable source package for a person profile, chronology extraction, and media review; completeness and source authority remain to be reviewed.
- 《针灸甲乙经》：612 assets, including editions/影印 material and a large paper/PDF collection, are sufficient for a staged reader/evidence pipeline after OCR/text extraction, edition and page metadata, and human review.
- Evidence/heritage: 52 assets under 非遗佐证/传承 paths include inheritor, teaching, qualification, media, technical-result, and institutional evidence candidates; event/person/place extraction is required.
- Exact duplicate groups are recorded only; no duplicate deletion is authorized.

## Source and rights posture

All 689 assets are marked `SOURCE_STATUS=NEEDS_REVIEW`, `RIGHTS_STATUS=NEEDS_CUSTOMER_CONFIRMATION`, and `PUBLIC_USE_STATUS=UNRESOLVED` until file/page-level review records author, institution, publication, date, identifier, attribution, and restrictions. This is a workflow flag, not a legal adjudication or development blocker.
