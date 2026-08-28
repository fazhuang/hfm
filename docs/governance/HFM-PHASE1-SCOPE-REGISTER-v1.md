# HFM Phase 1 Candidate Scope Register v1

Status: NPG-6 SCOPE ARBITRATION OUTPUT · READ-ONLY GOVERNANCE  
Branch: `governance/next-phase-authorization`  
Parent baseline: `0167b1702dac13993a5206f63752eafcc8e5387e`  
Rule: `IN` / `DEPENDENCY_ONLY` / `DEFERRED` / `REJECTED` are candidate scope verdicts, not implementation authorization.

| SCOPE-ID | Capability | Requirement Authority | Requirement Source | Business Value | Existing HFM Support | HFB Reuse Candidate | Reuse Disposition | Content Dependency | Risk | Verdict | Reason | Acceptance Implication |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P1-GOV | Phase 1 governance contract | L1/L2 | CR-009/010; NPG-000/BOUNDARY | Controls two-layer scope and evidence | Canonical governance docs only | N/A | REFERENCE_ONLY | None | Governance drift | IN | Required control plane for later architecture arbitration | Contract, decision log, and status boundaries must be tested |
| P1-CONTENT | Content admission/source/provenance/evidence | L2 | CR-003/005/009; NPG-005 | Trustworthy scholarly content intake | Evidence/SourceRef/Citation data layer; no admission UI | HFB-025 | ADAPT | CA-01…CA-07, CA-10 | Rights, provenance, medical boundary | IN | Platform capability is required even while packages are absent | Reject unproven or unauthorized content at admission |
| P1-A | 皇甫谧人物档案 | L1/L2 | CR-003/005; NPG-001 | Cultural discovery and research | Entity/Person/Event primitives only | HFB-003 | ADAPT | CA-01; CA-06/07 for public claims | Historical evidence, likeness/privacy | IN | Domain surface serves explicit cultural goal; records remain content batches | Event-level source evidence and publication status required |
| P1-B | 文献与思想体系 | L1/L2 | CR-003/005 | Teaching and research corpus | Work/Edition/Version/Chapter/Passage foundation | HFB-004/HFB-014 | ADAPT / REFERENCE_ONLY | CA-02/03 | Copyright, edition identity | IN | Explicit research goal and known literature assets justify capability | Versioned text, rights, and locator acceptance |
| P1-C | 《针灸甲乙经》数字知识体系 | L1/L2 | CR-003/005; NPG-002 boundary | Core scholarly knowledge domain | Canonical text lineage and provenance primitives | HFB-014/HFB-015 | REFERENCE_ONLY | CA-03/04/05 | Medical semantic drift, incomplete data | IN | Platform/data model/search/reader is required; production datasets are deferred | Historical retrieval only; citation/version chain mandatory |
| P1-D | 非遗传承体系 | L1/L2 | CR-003/005/006/007 | Preserve and display transmission lineage | Entity/Event/EventRelation primitives only | HFB-018/HFB-025 | REFERENCE_ONLY / ADAPT | CA-06/07 | Official-name, evidence, privacy, rights | IN | Explicit transmission goal; public claims await evidence and authorization | Provenance, official naming, withdrawal, and rights gates |
| P1-PORTAL | Public Internet Portal | L1/L2 | CR-004/009 | Visitor-first public access | Frontend is skeleton only | HFB-001/HFB-003 | ADAPT | Published snapshots and rights-cleared content | Public/research leakage | IN | Two-layer direction and visitor priority require a public surface | Anonymous read, publication snapshot, withdrawal behavior |
| P1-RESEARCH | Internal Research Experience | L1/L2 | CR-002/003/009 | Institutional teaching/research work | No workspace/UI; canonical data foundation | HFB-006/HFB-016 | ADAPT | Research corpus and user-owned work | Identity, tenancy, privacy | IN | School and research-center users require internal workflows | Authenticated ownership, audit, recovery tests |
| P1-READER | Text/source reader | L2 | CR-003/005; NPG-002-L | Locate and study source text | Passage model only; no reader/API | HFB-005 | ADAPT | CA-02/03/04/05 | OCR trust, rights, locator accuracy | IN | Necessary scholarly interaction, independent of final reader technology | Same-source locator, quotation, citation, rights display |
| P1-SEARCH | Cross-domain unified search | L2 | CR-003/009; NPG-002-M | Discover cultural and research material | Search absent | HFB-007 | ADAPT | Indexed admitted content | Relevance, authorization, medical wording | IN | Discoverability is derived from aggregation/research goals | Metadata/full-text scope and evidence-preserving result tests |
| P1-PUBLISH | Review/publication/withdrawal workflow | L2 | CR-005/006/007/009; boundary B-06 | Safe public release | No workflow/admin; provenance fields only | HFB-025/HFB-026 | ADAPT / REFERENCE_ONLY | CA-06/07/10 and all public rights | Unauthorized publication, stale snapshots | IN | Public portal requires an explicit publication boundary | Approve, reject, withdraw, rollback, observable state |
| P1-RBAC | Management/research permissions | L2 | CR-002/009/010 | Separate visitor, researcher, operator authority | RBAC/auth absent | HFB-008/HFB-009/HFB-027 | ADAPT | Role and approval matrix from client | Security, separation of duties | IN | Dual-layer architecture cannot be safely operated without identity/roles | Deny-by-default and real UI/API authorization evidence |
| P1-DISPLAY | Large-screen/touch display mode | L3 / conditional L2 | NPG-002-E/F; visitor priority only | On-site exhibition adaptation | Absent | HFB-001/HFB-002 | ADAPT | Device-specific media and rights | Hardware, accessibility, operations | DEFERRED | Display medium is not independently confirmed; arbitrate after device facts | Separate responsive/display acceptance; no 3D assumption |
| P1-EVIDENCE | Citation/Evidence/SourceRef chain | L2 | CR-003/005; frozen contracts | Academic trust and reproducibility | Evidence, SourceRef, Citation implemented at data layer | HFB-010/HFB-011/HFB-012 | MIGRATE | Source files, locators, rights | Broken lineage or unsupported claims | IN | Required by research and provenance goals; HFM model is authority | Write-time anchors, version pinning, citation rendering |
| P1-VERSION | Versioning/provenance/audit trail | L2 | CR-005/009; frozen contracts | Distinguish editions and preserve history | Work→Edition→Version→Passage and constraints implemented | HFB-014/HFB-015 | REFERENCE_ONLY | Version manifests and hashes | False equivalence, rights drift | IN | Required to represent customer versions and scholarly changes | Immutable history, source hash, withdrawal/revision evidence |
| P1-HFB-LIBRARY | Reuse HFB Library | L3 / unresolved reuse | CR-010; NPG-004 HFB-004 | Reduce UX effort if compatible | No HFM Library | HFB-004 | ADAPT | HFM-admitted content | Legacy model/route coupling | DEFERRED | Reuse is optional and not a customer requirement | Reassess after NPG-7 boundary and data contract |
| P1-HFB-READER | Reuse HFB Reader | L3 / unresolved reuse | CR-010; NPG-004 HFB-005 | Accelerate reader interaction | No HFM Reader | HFB-005 | ADAPT | Rights-cleared passages/OCR | HFB locator and corpus coupling | DEFERRED | Reader is IN; copying HFB implementation is not required | Prototype only after HFM reader contract |
| P1-HFB-WORKSPACE | Reuse HFB Workspace | L3 / unresolved reuse | CR-010; NPG-004 HFB-006 | Research workflow leverage | No HFM Workspace | HFB-006 | ADAPT | Research identity/data | Very high workflow coupling | DEFERRED | Research experience is IN; HFB implementation remains optional | Ownership and tenancy mapping first |
| P1-HFB-RBAC | Reuse HFB RBAC | L3 / unresolved reuse | CR-010; NPG-004 HFB-009 | Security pattern leverage | RBAC absent | HFB-009 | ADAPT | Client role/approval matrix | Role mismatch, security risk | DEFERRED | HFM must define authority before selecting code | Independent deny/allow acceptance required |
| P1-HFB-EVIDENCE | Reuse HFB Evidence/SourceRef | L3 / L2 capability | CR-010; NPG-004 HFB-010/011 | Provenance implementation leverage | HFM canonical chain already exists | HFB-010/011/012 | MIGRATE | Validated sources and rights | Schema/semantic mismatch | DEPENDENCY_ONLY | Data mapping may support P1-CONTENT/EVIDENCE; whole-schema reuse is rejected | Contract mapping and rejection tests, no row copy |
| P1-AI | AI research assistant | L3 | NPG-002; CR-010 unresolved | Optional research assistance | AI absent | HFB-019/HFB-020 | REFERENCE_ONLY | Admitted corpus and evaluation set | Unsupported claims, privacy, cost, medical drift | DEFERRED | No L1/L2 requirement; evidence-safe research AI can be reconsidered later | Separate evaluation and refusal boundary |
| P1-3D | 3D Huangfu Mi | L1 deferred | CR-008 | Future engagement | Absent | HFB-028 only static media | REJECT | 3D assets/rights | Scope, likeness, cost | DEFERRED | Explicitly outside current acceptance | No 3D acceptance criteria in Phase 1 |
| P1-VR | 720/VR exhibition hall | L1 deferred / L3 | CR-008; NPG-002-C | Future exhibition | Absent | HFB-028 media only | REJECT | Panorama/device/site rights | Hardware, safety, content | DEFERRED | Explicitly future; not a platform prerequisite | Separate future decision and site evidence |
| P1-XR | WebXR | L3 | NPG-002-D | Technical option only | Absent | None | REJECT | None | Browser/device support | DEFERRED | No confirmed requirement; cannot bind stack | No WebXR dependency or test in Phase 1 |
| P1-TRAIN | Virtual acupuncture training | L1 deferred | CR-008 | Future teaching simulation | Absent | HFB-019 not equivalent | REJECT | Clinical/teaching content and safety governance | Medical and liability risk | DEFERRED | Explicitly outside current acceptance | Requires separate authorization and safety review |
| P1-CLINICAL | Clinical acupuncture recommendation/treatment suggestion | Not authorized; conflicts with boundary | NPG-002/P/medical boundary; B-07 | None in current product | Absent | HFB-019 does not authorize it | REJECT | N/A | Clinical, legal, patient-safety risk | REJECTED | Historical retrieval must not become diagnosis or treatment advice | Acceptance must assert absence of recommendation semantics |

## Grouped result

### IN

P1-GOV, P1-CONTENT, P1-A, P1-B, P1-C, P1-D, P1-PORTAL, P1-RESEARCH, P1-READER, P1-SEARCH, P1-PUBLISH, P1-RBAC, P1-EVIDENCE, P1-VERSION.

### DEPENDENCY_ONLY

P1-HFB-EVIDENCE.

### DEFERRED

P1-DISPLAY, P1-HFB-LIBRARY, P1-HFB-READER, P1-HFB-WORKSPACE, P1-HFB-RBAC, P1-AI, P1-3D, P1-VR, P1-XR, P1-TRAIN.

### REJECTED

P1-CLINICAL.

All HFB dispositions above are candidate-only and do not freeze reuse. No content package is implied to be received or publishable by an `IN` platform verdict.
