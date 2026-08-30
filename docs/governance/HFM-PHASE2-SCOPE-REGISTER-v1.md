# HFM Phase 2 Candidate Scope Register v1

Status: GOVERNANCE CANDIDATE · READY FOR INDEPENDENT AUDIT
Phase-1 Completion Baseline: `c17be40be6f055498fde11c0042e71d3a1056a7c`
Taxonomy: `IN` / `DEPENDENCY_ONLY` / `DEFERRED` / `REJECTED` (frozen Phase-1 taxonomy, unchanged)
Rule: scope verdicts are governance classifications, not implementation authorization.

## Grouped classification

### IN (9)

| SCOPE-ID | Capability | Source requirements | Gap register | Phase-1 capability | Maps to WP |
| --- | --- | --- | --- | --- | --- |
| P2-C1 | Public portal frontend | CR-004/009/021; DR-001 | G2 | P1-11 portal API | P2-01 |
| P2-C2 | Research + admin/publication UI | CR-002/003/009; DR-002 | — | P1-12, P1-09, P1-10 APIs | P2-02 |
| P2-C3 | Reader + search frontend | CR-003/005; Gemini L/M | — | P1-07, P1-08 APIs | P2-03 |
| P2-C4 | Heritage lineage visualization | CR-006; Gemini N | G10 | P1-06 relations API | P2-04 |
| P2-C5 | Media & rights lifecycle | CR-013/015; MC-02 | G4, G13 | content_artifact model | P2-05 |
| P2-C6 | Export / print + disclaimer retention | CR-003/009 | G9 | P1-12 research API | P2-06 |
| P2-C9 | HFB reuse per-item adjudication | CR-022/010; NPG-004 | — | ADR-06, reuse matrix | P2-10 |
| P2-C13 | Deployment / operations / observability | CR-009/021; Tech Baseline | G14 context | ADR-01/02 | P2-07, P2-08 |
| P2-C15 | Admin unified audit view | CR-003 | G12 | P1-13 audit API | P2-09 |

### DEPENDENCY_ONLY (2)

| SCOPE-ID | Capability | Rule | Source |
| --- | --- | --- | --- |
| P2-C8 | HFB migration M0–M3 preparation | Not an implementation completion target; preparation (snapshot verification, mapping review, dry-run design, reconciliation design, authorization readiness) only; M4 production write, M5 execution, M6/M7 closure forbidden without independent authorization | Migration Contract v1 (M0–M7) |
| P2-C14 | Content intake / admission | Not an implementation completion target; intake contract, validation path, fixture-based verification, client asset readiness interface; full customer content population is not a platform-code completion blocker unless governance explicitly selects a fixture | NPG-005; MC-01…MC-11 |

### DEFERRED (4 + carried)

| SCOPE-ID | Capability | Status |
| --- | --- | --- |
| P2-C7 | Teaching surfaces | DEFERRED — requires client course/journey input |
| P2-C10 | AI research assistant | DEFERRED — requires new governance, evidence gate, evaluation set (G8) |
| P2-C11 | Display / exhibition | DEFERRED — requires device/network/ops facts |
| P2-C12 | 3D / VR / XR / virtual training | DEFERRED — CR-018/019/020; safety review required |

Carried Phase-1 deferred (unchanged): P1-AI, P1-DISPLAY, P1-3D, P1-VR, P1-XR, P1-TRAIN, P1-HFB-LIBRARY, P1-HFB-READER, P1-HFB-WORKSPACE, P1-HFB-RBAC. No deferred item auto-enters Phase-2 IN scope.

### REJECTED (1)

| SCOPE-ID | Capability | Status |
| --- | --- | --- |
| P2-CLINICAL | Clinical recommendation / diagnosis / treatment recommendation / prescriptive acupoint recommendation | REJECTED — carried fail-closed from P1-CLINICAL; no new authorization; historical medical content remains limited to historical retrieval, scholarly presentation, and source-grounded research |

## Accounting

- IN = 9
- DEPENDENCY_ONLY = 2
- DEFERRED = 4 (plus 10 carried Phase-1 deferred guards)
- REJECTED = 1
- Unauthorized additions = 0
