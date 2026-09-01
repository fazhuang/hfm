# HFM-UX2 Presentation State Matrix v1

Status: UX2-G1 NORMATIVE ARTIFACT · Binds to frozen UI baseline `ae55abc…`
Layer discipline: `SOURCE FACT → PRESENTATION STATE → PUBLIC LABEL`; layers never merge.

## 0. Mapping Contract

The mapping is:

```text
DETERMINISTIC
TOTAL_FOR_SUPPORTED_INPUTS
PRIORITY_DEFINED
FAIL_CLOSED
```

Not injective. Inputs below use ACTUAL authoritative fields of the frozen
baseline. Where a needed field cannot be confirmed, it is recorded as
`SOURCE_FIELD_UNRESOLVED` (an audit finding, not an implementation assumption).
No synthetic flags (`is_gap`, `is_uncertain`, `is_complete`, `has_resource`)
are required; evidence predicates that are not literal fields are marked
`DERIVED_PRESENTATION_ONLY`.

## 1. Authoritative Input Fields (existing)

| Field / constant | Layer | Notes |
| --- | --- | --- |
| `ContentStatus` (`AVAILABLE`/`METADATA_ONLY`/`DATA_GAP`) | SOURCE FACT | types/content.ts |
| `ReadingAvailability` (`FULL_TEXT`/`EXCERPT`/`METADATA_ONLY`) | SOURCE FACT | types/reader.ts |
| `publication_status` (`published`) | SOURCE FACT | public projection |
| `evidence_ids` presence | SOURCE FACT | person assertions |
| citation availability (`citationCount`) | SOURCE FACT | reader `houlun` = 12 |
| `LINEAGE_STRUCTURING = PARTIAL` | SOURCE FACT | heritageView.ts |
| `JIAYI_EDITION_RELATIONS = DATA-GAP` | SOURCE FACT | jiayiView.ts |
| `AUDITED_PAPER_TOTAL = 515` / `SEARCHABLE_PAPER_TOTAL = 5` | SOURCE FACT | searchIndex.ts |
| edition records (19 × status `METADATA_ONLY`) | SOURCE FACT | jiayiView.ts |
| verified-text predicates (e.g., 散佚/争议 statements in 其传/后论) | DERIVED_PRESENTATION_ONLY | extracted from verified text, not a stored flag |

## 2. Normative State Matrix

| # | Authoritative Input Condition | Derived Evidence Predicate | Conflict Priority | Presentation State | Public Label | Allowed UI Surfaces | Fallback Behavior | Verification Method |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `ContentStatus=AVAILABLE` ∧ `ReadingAvailability=FULL_TEXT` | resource readable | 5 | `RESOURCE_READY` | 数字资源可阅 / 全文已整理 | Portal · Reader · Archive · Search · Research | none (fully rendered) | existing reader tests (`houlun`/`qichuan` FULL_TEXT=2) |
| 2 | `ContentStatus=AVAILABLE` ∧ `ReadingAvailability=EXCERPT` | excerpt only | 5 | `RESOURCE_READY`(excerpt) | 存目 | Portal · Reader · Archive | render excerpt; never imply full text | G1-D NB-07 (excerpt ≠ full) |
| 3 | `ContentStatus=METADATA_ONLY` ∧ metadata fields present | bibliographic record only | 4 | `METADATA_ONLY` | 仅题录 / 存目 | Portal · Archive · Search · Research · Reader (status page) | metadata grid; no blank body | ui07 reader METADATA_ONLY state; ui06 archive statuses |
| 4 | `ContentStatus=DATA_GAP` ∧ no metadata ∧ no explicit loss | platform has no structured data | 3 | `UNSTRUCTURED_OR_INCOMPLETE` | 资料整理中 / 当前资料不完整 | Portal · Archive · Research | inline status note; never an empty shell; never “系统出错” | G1-D NB-08; ui06 empty/status states |
| 5 | classical full text absent from corpus ∧ collation description present | full text not in corpus (not asserted lost) | 4 | `METADATA_ONLY` | 仅题录（原典全文未收录） | Yan · Reader · Search | show collation description; full-text status explicit | ui07 四论 METADATA_ONLY entries |
| 6 | verified text explicitly records 佚/散佚 (e.g., 逸士传/列女传 辑佚 note) | loss explicitly documented | 6 | `HISTORICAL_ABSENCE` | 文献阙佚 | Yan · Archive · Reader | render the loss note; never a generic empty state | G1-D NB-07; yan collection supplement text |
| 7 | verified text explicitly asserts scholarly controversy | controversy documented (e.g., 生卒年 建安/正始 之议 in 其传 考据) | 7 | `SCHOLARLY_UNCERTAIN` | 尚有争议 / 待考 | Person · Reader · Research | render controversy note alongside verified anchor; no certainty claim | G1-D NB-07; 其传 现代学术考据 text |
| 8 | `LINEAGE_STRUCTURING=PARTIAL` (intermediate generations) | lineage incompletely structured | 3 | `UNSTRUCTURED_OR_INCOMPLETE` | 谱系整理中 | Heritage | gap marker + PARTIAL note; never draw implied chain | ui09 heritage PARTIAL tests; NB-04 |
| 9 | `JIAYI_EDITION_RELATIONS=DATA-GAP` | version relations not structured | 3 | `UNSTRUCTURED_OR_INCOMPLETE` | 版本关系整理中 | Jiayi | PNG asset stays RESOURCE_READY; structured edges never drawn | ui08 DATA-GAP caption; NB-03 |
| 10 | edition record exists ∧ digitized resource absent | bibliographic record only | 4 | `METADATA_ONLY` | 存目 | Jiayi · Works · Archive | edition metadata grid; no fake “阅读” CTA | ui08 edition collection; NB-08 |
| 11 | `SEARCHABLE_PAPER_TOTAL=5` (of 515 audited) | 5 structured records | 4 (searchable) / 3 (rest) | `RESOURCE_READY` (5) · `UNSTRUCTURED_OR_INCOMPLETE` (rest) | 仅题录（可检索） / 论文题录整理中 | Search · Research | never claims 515 searchable; audited total shown separately | ui10/ui03 515/5 invariant tests; NB-07 |
| 12 | `ContentStatus=AVAILABLE` ∧ `evidence_ids` present | evidence-linked | 5 | `RESOURCE_READY` | 数字资源可阅（带证据） | Person · Research | evidence badges render | ui04 evidence badge test |
| 13 | heritage person `generationTitle=第六代名医` | confirmed identity | 5 | `RESOURCE_READY` | 第六代名医 | Heritage · Home · Search · Person | confirmed anchor renders normally | ui09/ui03 generation invariants |

## 3. Conflict Precedence (semantic truthfulness first)

Precedence is numeric; higher wins.

```text
7  SCHOLARLY_UNCERTAIN      — documented controversy outranks availability.
6  HISTORICAL_ABSENCE       — documented loss outranks unavailability.
5  RESOURCE_READY           — available resource (no controversy/loss).
4  METADATA_ONLY            — bibliographic record only.
3  UNSTRUCTURED_OR_INCOMPLETE — platform incompleteness (fail-closed default).
```

Audited conflict classes:

| Conflict | Resolution |
| --- | --- |
| resource available + scholarly uncertainty | `SCHOLARLY_UNCERTAIN` wins (truth over availability). |
| resource unavailable + historical loss | `HISTORICAL_ABSENCE` wins (loss is asserted). |
| metadata available + incomplete structuring | `METADATA_ONLY` wins (never presented ready). |
| historical absence vs platform incompleteness | explicit-loss predicate → `HISTORICAL_ABSENCE`; otherwise → `UNSTRUCTURED_OR_INCOMPLETE`. Loss is NEVER inferred from data absence. |

Fail-closed: any unparseable input combination maps to `UNSTRUCTURED_OR_INCOMPLETE`
(当前资料不完整), never to `RESOURCE_READY`.

## 4. No Synthetic Flags

The matrix uses only existing fields and `DERIVED_PRESENTATION_ONLY` predicates
derived from verified text. No `is_gap`/`is_uncertain`/`is_complete`/
`has_resource` fields are introduced (AC-07).

## 5. SOURCE_FIELD_UNRESOLVED Findings (audit items, not assumptions)

| # | Item | Needed for | Status |
| --- | --- | --- | --- |
| U-01 | Dedicated scholarly-controversy field (person date disputes) | `SCHOLARLY_UNCERTAIN` | UNRESOLVED — predicate currently `DERIVED_PRESENTATION_ONLY` from verified 其传 text |
| U-02 | Explicit loss-recorded flag | `HISTORICAL_ABSENCE` | UNRESOLVED — predicate currently `DERIVED_PRESENTATION_ONLY` from verified text |
| U-03 | Edition holding/source institution field | BibliographicRecord hierarchy | UNRESOLVED — editions carry imprint; holding institution not a field |
| U-04 | Citation page/volume-level locator fields | CitationLocator depth | UNRESOLVED — locator renders at document/section level only |
| U-05 | Per-edition digitized-resource flag | distinguishing 存目 vs 数字资源可阅 per edition | UNRESOLVED — all 19 editions currently `METADATA_ONLY` |

None of U-01..U-05 blocks G1 acceptance; all are recorded as audit findings for
G2 prototype scoping and must not become implementation assumptions.
