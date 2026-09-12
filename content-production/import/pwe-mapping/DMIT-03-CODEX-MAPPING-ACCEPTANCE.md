# HFM DMIT-03 Codex PWE Mapping Final Acceptance

**阶段**：DATA_MAPPING_AND_IMPORT_TOOLING_DESIGN  
**性质**：独立只读验收与 mapping 输入签署  
**日期**：2026-09-10  
**冻结基线**：DOCUMENTS=`675`；PERSONS/WORKS/EDITIONS production rows=`0/0/0`

## 1. Acceptance Decision

DMIT-03 passes. The reviewed mapping can be frozen as the formal input contract for P/W/E importer implementation, with this exact accepted scope:

- PERSON: all 17 reviewed rows are `CONFIRMED_FOR_IMPORT_TOOLING`;
- WORK: all 14 reviewed rows are `CONFIRMED_FOR_IMPORT_TOOLING`;
- EDITION: exactly 87 reviewed rows are `CONFIRMED_FOR_IMPORT_TOOLING`;
- EDITION: exactly five named rows are `DEFERRED_FOR_IMPORT_TOOLING` and must not be consumed.

This is an engineering-input acceptance only. It is not authorization to import to `hfm_prod`.

The raw review artifacts retain their pre-signature `REVIEW_REQUIRED` values by design; this report is the governance signature that freezes their exact `CONFIRM_RECOMMENDED` sets for **tooling**. An importer must consume the accepted sets below, not reinterpret titles or promote a row at runtime.

## 2. Independent Source and Set Reconciliation

Direct set comparison was performed across the normalized source CSVs, the five mapping artifacts, and the three confirmation review CSVs.

| Scope | Source set | Mapping set | Review set | Result |
| --- | ---: | ---: | ---: | --- |
| Entity bootstrap | 17 PERSON + 14 WORK | 31 rows; 31 unique entity stable IDs | n/a | exact |
| PERSON | 17 unique `PERSON_ID` | 17 identity-map IDs | 17 review IDs / 17 confirm recommendations | exact |
| WORK | 14 unique `WORK_ID` | 14 canonical-map IDs | 14 review IDs / 14 confirm recommendations | exact |
| EDITION | 92 unique `EDITION_ID` | 92 edition-map IDs | 92 review IDs | exact |

No collision was found among 31 entity stable IDs, 17 PERSON stable IDs, 14 WORK stable IDs, and 92 EDITION stable IDs. The 87 confirmation-recommended EDITION rows each have one candidate WORK in the accepted WORK set, non-empty evidence, no stated ambiguity, no stated blocking issue, and no competing candidate. The only candidate WORKs used are `WORK-JIAYI`, `WORK-DIWANG-SHIJI`, and `WORK-GAOSHIZHUAN`.

The 87 rows are accepted because the mapping artifact carries their selected candidate and evidence. Runtime title matching is not an accepted behavior.

## 3. Deferred Edition Boundary

The deferred set is exact:

```text
EDITION-HFM-A000541
EDITION-HFM-A000529
EDITION-HFM-A000530
EDITION-HFM-A000531
EDITION-HFM-A000532
```

`A000541` remains deferred because its four-work compilation cannot truthfully satisfy the R0 single `editions.work_id` meaning. `A000529`–`A000532` remain deferred because their numeric filenames lack sufficient bibliographic evidence. A candidate value in a staging row is not an approved `work_id` for import. Therefore no deferred row has a consumable import mapping.

The accepted decision is `HUMAN_DECISION_FOR_5_DEFERRED=DEFER`: no additional research is required now and these five records do not block the confirmed 87-row EDITION input scope.

## 4. Contract Implementability

The signed mapping contract is implementable without domain reinterpretation when the future importer enforces all of the following:

```text
IMPORTER_CONSUMES_ONLY_CONFIRMED_ROWS=YES
CONFIRMED_ROWS=THE_EXACT_DMIT03_ACCEPTED_SETS
RUNTIME_TITLE_INFERENCE=FORBIDDEN
RUNTIME_IDENTITY_GUESSING=FORBIDDEN
DEFERRED_IMPORT=FORBIDDEN
STABLE_ID_REGENERATION=FORBIDDEN
DOCUMENT_REIMPORT=FORBIDDEN
```

`01-entity-bootstrap.csv` is the only entity-bootstrap source. `02-work-canonical-map.csv`, `04-person-identity-map.csv`, and the signed accepted scope define base records; `03-edition-work-map.csv` supplies preselected WORK mappings only for the accepted 87 EDITION IDs. `05-person-work-evidence.csv` remains evidence-only and is not an authorization to write relationship data.

## 5. Production Boundary

Read-only production verification found `documents=675`, `persons=0`, `works=0`, and `editions=0`. No P/W/E import, publication, or UI propagation occurred during this acceptance.

DMIT03_ACCEPTANCE=PASS

DOCUMENT_BASELINE_PROTECTED=YES

ENTITY_BOOTSTRAP_ACCEPTED=YES

PERSON_CONFIRMED=17
WORK_CONFIRMED=14
EDITION_CONFIRMED=87
EDITION_DEFERRED=5

PERSON_CONFIRMED_SET_EXACT=YES
WORK_CONFIRMED_SET_EXACT=YES
EDITION_CONFIRMED_SET_EXACT=YES
EDITION_DEFERRED_SET_EXACT=YES

IDENTITY_COLLISIONS=0
R0_MAPPING_AMBIGUITIES=0

DEFERRED_ROWS_IMPORTABLE=NO
IMPORTER_MUST_SKIP_DEFERRED=YES

MAPPING_CONTRACT_IMPLEMENTABLE=YES
MAPPING_BASELINE_STATUS=ACCEPTED

DATA_MAPPING_PHASE=CLOSED

NEXT_PHASE=PWE_IMPORT_TOOLING_IMPLEMENTATION
NEXT_EXECUTOR=PI

PERSON_IMPORT=UNAUTHORIZED
WORK_IMPORT=UNAUTHORIZED
EDITION_IMPORT=UNAUTHORIZED
HFM_PROD_WRITE=FORBIDDEN
PUBLICATION=UNAUTHORIZED
UI_CONTENT_PROPAGATION=UNAUTHORIZED

BLOCKER=NONE
STOP=YES
