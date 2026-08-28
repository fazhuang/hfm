# HFM Phase 1 DAG v1

Status: NPG-9 GOVERNANCE OUTPUT · ACYCLIC CONTRACT  
Nodes: 14 · Edges: 36 · Cycles: 0 · Unreachable nodes: 0

## Nodes

`P1-00, P1-01, P1-02, P1-03, P1-04, P1-05, P1-06, P1-07, P1-08, P1-09, P1-10, P1-11, P1-12, P1-13`

## Edges

| FROM | TO | Dependency reason | Blocking | Required evidence |
| --- | --- | --- | --- | --- |
| P1-00 | P1-01 | Governance/change control precedes admission contract | YES | governance trace |
| P1-00 | P1-02 | Evidence contract must inherit scope/boundaries | YES | contract review |
| P1-00 | P1-09 | Publication authorization needs governance owner | YES | approval matrix |
| P1-00 | P1-10 | Identity policy needs governed roles | YES | RBAC policy |
| P1-01 | P1-02 | Evidence anchors admitted sources/artifacts | YES | admission schema |
| P1-01 | P1-03 | Person records require admitted sources | YES | source manifest |
| P1-01 | P1-04 | Literature records require admitted content | YES | version manifest |
| P1-01 | P1-05 | C-domain records require content admission | YES | corpus manifest |
| P1-01 | P1-06 | Heritage records require admission/rights | YES | rights manifest |
| P1-01 | P1-08 | Search indexes only admitted content | YES | admission/index trace |
| P1-01 | P1-13 | Reconciliation covers content batches | YES | batch manifest |
| P1-02 | P1-03 | Person claims need source/evidence chain | YES | evidence trace |
| P1-02 | P1-04 | Literature claims need citations | YES | citation trace |
| P1-02 | P1-05 | Historical C retrieval needs versioned evidence | YES | locator/citation trace |
| P1-02 | P1-06 | Heritage lineage needs evidenced relations | YES | relation evidence |
| P1-02 | P1-07 | Reader must expose citation/source context | YES | reader trace |
| P1-02 | P1-12 | Research outputs need provenance | YES | research evidence |
| P1-02 | P1-13 | Audit/reconciliation uses provenance chain | YES | reconciliation report |
| P1-03 | P1-05 | Person/teacher references support C lineage context | NO | cross-domain relation |
| P1-03 | P1-06 | Inheritor/person identity is needed for lineage | YES | identity evidence |
| P1-04 | P1-05 | C-domain knowledge is versioned literature | YES | version lineage |
| P1-04 | P1-07 | Reader addresses literature passages | YES | passage locator |
| P1-05 | P1-07 | C-domain reader needs its historical structures | YES | passage/section trace |
| P1-03 | P1-08 | Person records are searchable | NO | search fixture |
| P1-04 | P1-08 | Literature records are searchable | NO | search fixture |
| P1-05 | P1-08 | C records are searchable | NO | search fixture |
| P1-06 | P1-08 | Heritage records are searchable | NO | search fixture |
| P1-07 | P1-11 | Portal requires approved reader surface | YES | public E2E |
| P1-08 | P1-11 | Portal requires approved search surface | YES | public E2E |
| P1-09 | P1-11 | Portal content must be published | YES | publication trace |
| P1-10 | P1-11 | Public endpoint policy and management controls | YES | authorization trace |
| P1-07 | P1-12 | Research experience uses source reader | YES | research E2E |
| P1-08 | P1-12 | Research experience uses search | YES | research E2E |
| P1-10 | P1-12 | Research experience requires identity/RBAC | YES | auth E2E |
| P1-09 | P1-12 | Research/public state must remain distinct | YES | state isolation trace |
| P1-13 | P1-11 | Public projection needs version/audit state | YES | publication audit |

The 36 edges above are the contractual dependency set. No edge points to Display, HFB UI/Workspace/RBAC reuse, AI, 3D, VR, XR, Virtual Training, or Clinical Recommendation. No edge requires an HFB runtime service.
