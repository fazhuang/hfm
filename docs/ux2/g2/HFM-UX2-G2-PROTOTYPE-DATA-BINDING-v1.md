# HFM-UX2 G2 Prototype Data Binding Ledger v1

Status: UX2-G2 NORMATIVE ARTIFACT · Binds to frozen baseline `ae55abc…`
Rule: every visible prototype fact must trace to an authoritative source.
Status vocabulary: `EXISTING | DERIVED_PRESENTATION_ONLY | OPTIONAL_COLLAPSED | SOURCE_FIELD_UNRESOLVED`.
Anything outside these four classes is REMOVE_FROM_PROTOTYPE.

## P-G2-01 Huangfu Mi Person Archive

| Surface | UI Field | Source Object/File/API | Existing Field | Transformation | Status |
| --- | --- | --- | --- | --- | --- |
| Header | 姓名 | `src/config/corePerson.ts` | `CORE_PERSON_NAME` | direct | EXISTING |
| Header | 生卒年 215—282 | `corePerson.ts` | `CORE_PERSON_DATES` | direct | EXISTING |
| Header | 多维身份 | `corePerson.ts` | `CORE_PERSON_IDENTITIES` | direct | EXISTING |
| Header | 权威定义 | `corePerson.ts` | `CORE_PERSON_DEFINITION` | direct | EXISTING |
| Context | 作品/史料整理 | `workCollection.ts` / `readerDocuments.ts` | titles/hrefs | curated | EXISTING |
| Evidence | 《晋书》引文 12 条 | `readerDocuments.ts` (houlun) | citation objects | count/type | EXISTING |
| Evidence | 其传/后论文稿 | `archiveInventory.ts` | sourceName | display name | EXISTING |
| Relations | 甲乙经/其言/非遗 | `corePerson.ts` works / `heritageView.ts` | hrefs | curated | EXISTING |
| Optional | 肖像 | — | — | — | OPTIONAL_COLLAPSED (no approved derivative; no AI portrait) |
| Optional | 馆藏机构 | — | — | — | SOURCE_FIELD_UNRESOLVED (U-03) → OPTIONAL_COLLAPSED |
| Incomplete | 四论全文未收录 | `readerDocuments.ts` (READER_METADATA_ONLY) | readingStatus | METADATA_ONLY label | EXISTING |
| Incomplete | 生卒年争议 | `readerDocuments.ts` (qichuan 现代学术考据段) | verified text | SCHOLARLY_UNCERTAIN note | DERIVED_PRESENTATION_ONLY |

## P-G2-02 Jiayi Work / Edition

| Surface | UI Field | Source | Existing Field | Transformation | Status |
| --- | --- | --- | --- | --- | --- |
| Work Header | 书名/撰/时期/类型 | `jiayiView.ts` / `workCollection.ts` | title/attribution/period | direct | EXISTING |
| Invariants | 19 / 2 / DATA-GAP | `contentInventory.ts` / `readerDocuments.ts` / `jiayiView.ts` | counts + status | direct | EXISTING |
| Edition ×19 | 题名/时期/刊刻/类型 | `jiayiView.ts` (`JIAYI_ANCIENT_EDITIONS`+`JIAYI_MODERN_EDITIONS`) | title/period/imprint/editionType | direct | EXISTING |
| Edition state | 存目 | `jiayiView.ts` edition.status (METADATA_ONLY) | status | label mapping | EXISTING |
| Edition digitization | 逐版本数字化 | — | — | — | SOURCE_FIELD_UNRESOLVED (U-05); rendered METADATA_ONLY, no fake digitized state |
| Full text | 后论/其传 | `readerDocuments.ts` | readingStatus FULL_TEXT | direct | EXISTING |
| DATA-GAP | 版本关系整理中 | `jiayiView.ts` (JIAYI_EDITION_RELATIONS) | comment/status | label + note | DERIVED_PRESENTATION_ONLY (no stored flag) |
| Lineage image | 版本脉络图 | `jiayiView.ts` (JIAYI_LINEAGE_IMAGE_*) | asset | presentation asset only; no edges | EXISTING (asset) / no inferred edges |

## P-G2-03 Heritage Living Archive

| Surface | UI Field | Source | Existing Field | Transformation | Status |
| --- | --- | --- | --- | --- | --- |
| Project | 项目/分类/传承人 | `heritageView.ts` (HERITAGE_PROJECT) | name/classification/inheritors | direct | EXISTING |
| Person | 第六代名医/身份/职务 | `heritageView.ts` (HERITAGE_PERSON) | generationTitle/role/institution | direct | EXISTING |
| Historical | 皇甫谧 源头 | `heritageView.ts` (HERITAGE_LINEAGE) | person/evidence | direct | EXISTING |
| Historical | 中间代 PARTIAL | `heritageView.ts` | LINEAGE_STRUCTURING | PARTIAL note | EXISTING |
| Contemporary | 师承 2023-09-26 | `heritageView.ts` (HERITAGE_APPRENTICESHIPS) | title/date/location | direct | EXISTING |
| Contemporary | 技术成果 2007 | `heritageView.ts` (HERITAGE_TECHNICAL) | title/year/award | direct | EXISTING |
| Contemporary | 媒体报道 2025-04-25 | `heritageView.ts` (HERITAGE_MEDIA) | title/outlet/date | direct | EXISTING |
| Contemporary | 工作室 ×2 | `heritageView.ts` (HERITAGE_STUDIOS) | name/institution | direct | EXISTING |
| Recognition | 8 条记录（8/8 覆盖） | `heritageView.ts` (HERITAGE_RECOGNITIONS) | title/category | curated display (no honor-wall). Full 8/8 coverage presented as 4 grouped strings: r-fy / r-gs-mzy+r-pl-mzy+r-pl-my+r-kt-gj / r-gs-xjj+r-gs-rc / r-yz-2016 (G2 F-4) | EXISTING |
| Context separation | historical vs contemporary | `heritageView.ts` | grouped arrays | two semantic contexts | DERIVED_PRESENTATION_ONLY (layout category, not domain) |

## P-G2-04 Scholarly Discovery

| Surface | UI Field | Source | Existing Field | Transformation | Status |
| --- | --- | --- | --- | --- | --- |
| Invariants | 515 / 5 | `searchIndex.ts` | AUDITED_PAPER_TOTAL / SEARCHABLE_PAPER_TOTAL | direct | EXISTING |
| Facets | 人物/作品/版本/档案/论文题录/文本 | `searchIndex.ts` SEARCH_INDEX type counts | type counts | deterministic taxonomy (no UI re-classification). Facet semantic = search-index type count (G2 F-3): 人物 2 / 作品 8 / 版本 19 / 论文题录 5 / 文本 6 match SEARCH_INDEX person/work/edition/paper/text counts; 档案 = archive-type index entries = 16 (heritage-project 1 + HERITAGE_APPRENTICESHIPS 1 + HERITAGE_STUDIOS 2 + HERITAGE_MEDIA 4 + ARCHIVE_RECORDS 8), NOT the ARCHIVE_RECORDS.length (8) inventory-object count | EXISTING |
| Result | 甲乙经 work | `workCollection.ts` | title/attribution/period | BibliographicRecord | EXISTING |
| Result | 医统正脉 edition | `jiayiView.ts` | title/imprint/period | BibliographicRecord | EXISTING |
| Result | 论文题录 | `jiayiView.ts` (JIAYI_PAPER_PREVIEW) | title | METADATA_ONLY 仅题录 | EXISTING |
| CitationLocator | 后论《晋书》引文 | `readerDocuments.ts` (houlun p2) | text/attribution/source | document-level locator | EXISTING |
| Citation page/volume | 页码级定位 | — | — | — | SOURCE_FIELD_UNRESOLVED (U-04) → collapsed |

## P-G2-05 Homepage Exhibition Narrative

| Surface | UI Field | Source | Existing Field | Transformation | Status |
| --- | --- | --- | --- | --- | --- |
| Hero | 平台名/副题/日期/定义 | `homeProjection.ts` (HOME_HERO) | title/subtitle/dates/definition | direct (approved copy only) | EXISTING |
| Hero | 双主入口 + 次级检索 | `homeProjection.ts` | primary/secondary hrefs | direct | EXISTING |
| Narrative | 01–05 顺序 | `homeProjection.ts` (HOME_* features) | headings/ledes/hrefs | curated order | EXISTING |
| Research | 从资料到研究（弱入口） | `homeProjection.ts` (HOME_RESEARCH_STEPS) | labels | direct | EXISTING |

## Ledger Closure

Every visible prototype string above traces to `EXISTING` frozen-baseline data or
to an explicitly marked `DERIVED_PRESENTATION_ONLY` presentation predicate.
`SOURCE_FIELD_UNRESOLVED` items (U-03, U-04, U-05) collapse or render a
meaningful incomplete state; none are synthesized. No invented museum, page,
digitization, or loss flags exist in the prototype.
