# HFM Phase 1 Work Package Inventory v1

Status: NPG-9 GOVERNANCE OUTPUT · NO IMPLEMENTATION AUTHORIZATION  
Source of truth: NPG-6 `IN` scope only. Deferred/rejected items are negative guards, not work packages.

| WP-ID | Scope ID | Accountable output | Preconditions | Completion state |
| --- | --- | --- | --- | --- |
| P1-00 | P1-GOV | Governance contract, scope traceability and change control | NPG-6 scope; NPG-7 boundaries | NOT_STARTED |
| P1-01 | P1-CONTENT | Canonical content admission and content-core contracts | P1-00; architecture boundaries | NOT_STARTED |
| P1-02 | P1-EVIDENCE | Source/SourceRef/Evidence/Citation/provenance contract | P1-00; P1-01 | NOT_STARTED |
| P1-03 | P1-A | Person/biography/event capability | P1-01; P1-02 | NOT_STARTED |
| P1-04 | P1-B | Literature/work/edition/version content capability | P1-01; P1-02 | NOT_STARTED |
| P1-05 | P1-C | Historical *Zhen Jiu Jia Yi Jing* knowledge capability | P1-01; P1-02; P1-04 | NOT_STARTED |
| P1-06 | P1-D | Heritage/inheritance capability | P1-01; P1-02; P1-03 | NOT_STARTED |
| P1-07 | P1-READER | Versioned source reader | P1-02; P1-04; P1-05 | NOT_STARTED |
| P1-08 | P1-SEARCH | Unified policy-aware search | P1-01; P1-02; P1-03…P1-06 | NOT_STARTED |
| P1-09 | P1-PUBLISH | Review/publication/withdrawal workflow | P1-00; P1-01; P1-02; P1-10 | NOT_STARTED |
| P1-10 | P1-RBAC | Identity and deny-by-default RBAC | P1-00 | NOT_STARTED |
| P1-11 | P1-PORTAL | Public approved-content portal | P1-07; P1-08; P1-09; P1-10 | NOT_STARTED |
| P1-12 | P1-RESEARCH | Authenticated research experience | P1-02; P1-07; P1-08; P1-10 | NOT_STARTED |
| P1-13 | P1-VERSION | Versioning, audit and reconciliation closure | P1-01; P1-02; migration contract | NOT_STARTED |

Every `IN` scope item appears exactly once above. P1-02 is the implementation expression of dependency-only HFB Evidence/SourceRef/Citation mapping; it is not an HFB product feature. No deferred or rejected capability is a positive work package.
