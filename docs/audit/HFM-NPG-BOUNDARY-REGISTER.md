# HFM NPG Product Boundary Register

Date: 2026-08-29
Applies to NPG-0…NPG-5 fact audit and any proposed NPG-6 scope arbitration.

| ID | Boundary | Left side means | Right side means | Current status | Evidence / enforcement |
| --- | --- | --- | --- | --- | --- |
| B-01 | Phase 0.4 dry-run ≠ Production HFB Import | Disposable transformation/reconciliation proof against a frozen source | Persistent records loaded into an authorized production HFM database | ENFORCED AS DISTINCT | Completion artifact: production DB touched false; records imported 0; persistent state NONE |
| B-02 | CD-7 NONEXISTENT | Frozen DAG ends at CD-6; CORE-COMPLETION is a non-CD work package | A new domain batch/schema/API authorization | NONEXISTENT / NOT AUTHORIZED | Amendment and completion archive; no CD-7 file, migration, or commit found |
| B-03 | Phase 1 NOT AUTHORIZED | Documents may name future deliverables/placeholders | Permission to implement, migrate, freeze scope, create DAG/DoD, or deploy | NOT AUTHORIZED | Baseline archive and client prohibition; no post-baseline commit found |
| B-04 | 3D / VR / XR / Virtual Training DEFERRED | Long-term experience ideas | Current mandatory acceptance or stack requirement | DEFERRED | Client-confirmed boundary §III.7 |
| B-05 | Public Portal ≠ Research Backend | Visitor-first, approved public content, anonymous/read-only consumption | Authenticated research production, notes, evidence review, admin and internal data | REQUIRED SEPARATION | Client-confirmed two-layer direction; exact physical topology unresolved |
| B-06 | Research Capability ≠ Public Content | A tool/model can create, inspect, or store research-state material | A rights-cleared, editorially approved, withdrawable public representation | ENFORCED AS DISTINCT | HFM frozen Assertion editorial state explicitly is not publication state; publication model absent |
| B-07 | Digital Humanities Search ≠ Clinical Decision Support | Locate and cite historical sources, terms, passages, relationships, and interpretations | Diagnose, recommend treatment/acupoints, rank interventions, or imply efficacy for a user | CLINICAL SIDE REJECTED IN CURRENT SCOPE | Client positioning and NPG-2 medical boundary; disease→main/auxiliary acupoint recommendation rejected |
| B-08 | Source Evidence ≠ Editorial Interpretation | Addressable source material and evidence supporting a claim | Curated narrative, significance, summary, preferred assertion, or display copy | REQUIRED SEPARATION | HFM SourceRef→Evidence→Assertion/Citation model; HFB exhibition prose is not accepted as source evidence |
| B-09 | Official Organization Name ≠ Informal Display Alias | `灵台县皇甫谧中医针灸传承创新示范中心` | `皇甫谧针灸非遗传承中心` or another short business expression | OFFICIAL NAME FIXED; ALIAS NON-CANONICAL | Client §III.6; repository had no contrary official proof |
| B-10 | HFB Capability Exists ≠ HFM Must Reuse It | Code/data/test/doc asset is present at HFB `03755b57` | Final selection, migration authority, or HFM architecture decision | REUSE DECISIONS UNRESOLVED | Client §III.9; NPG-4 contains candidate values only |
| B-11 | Gemini Design ≠ Customer Requirement | AI-authored feature, schedule, or technology suggestion | L1 client-confirmed need | ENFORCED BY AUTHORITY REGISTER | NPG-1 L1/L2/L3 matrix; original Gemini artifact not found |
| B-12 | Technical Option ≠ Frozen Architecture Decision | A plausible technology such as ES/Neo4j/MinIO/WebSocket/ECharts/D3 | Authorized, accepted, and frozen system choice with acceptance evidence | UNRESOLVED | HFM baseline calls several options conditional/future; Phase 1 architecture not authorized |

## Operational rule

Any later scope card must cite the relevant boundary ID and must not silently collapse the two sides. A boundary may change only through an explicit client/governance decision; this audit does not change one.
