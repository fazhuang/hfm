# HFM Phase 2 Governance Manifest v1

Status: GOVERNANCE CANDIDATE · READY FOR INDEPENDENT AUDIT · NOT FROZEN
Phase-1 Completion Baseline: `c17be40be6f055498fde11c0042e71d3a1056a7c`
Binding: none of the Phase-2 governance artifacts below binds until the independent audit passes and Phase-2 Governance Acceptance → Archive → Freeze completes.

## Artifacts

| Artifact | Path | Status |
| --- | --- | --- |
| Phase-2 Scope Register | `docs/governance/HFM-PHASE2-SCOPE-REGISTER-v1.md` | CANDIDATE |
| Phase-2 Work Package Contract | `docs/governance/HFM-PHASE2-WORK-PACKAGE-CONTRACT-v1.md` | CANDIDATE |
| Phase-2 DAG | `docs/governance/HFM-PHASE2-DAG-v1.md` | CANDIDATE |
| Phase-2 Acceptance Contract | `docs/governance/HFM-PHASE2-ACCEPTANCE-CONTRACT-v1.md` | CANDIDATE |
| Phase-2 Evidence Contract | `docs/governance/HFM-PHASE2-EVIDENCE-CONTRACT-v1.md` | CANDIDATE |
| Phase-2 Definition of Done | `docs/governance/HFM-PHASE2-DEFINITION-OF-DONE-v1.md` | CANDIDATE |
| ADR-P2-01 Media/Object Storage | `docs/governance/adr/HFM-PHASE2-ADR-01-MEDIA-OBJECT-STORAGE.md` | CANDIDATE |
| ADR-P2-02 Deployment/Operations | `docs/governance/adr/HFM-PHASE2-ADR-02-DEPLOYMENT-OPERATIONS.md` | CANDIDATE |
| Phase-2 Customer Dependency Register | `docs/governance/HFM-PHASE2-CUSTOMER-DEPENDENCY-REGISTER-v1.md` | CANDIDATE |
| Phase-2 Governance Manifest | `docs/governance/HFM-PHASE2-GOVERNANCE-MANIFEST-v1.md` | CANDIDATE |

## Governance counts (design)

- IN scope = 9; DEPENDENCY_ONLY = 2; DEFERRED = 4 (+10 carried Phase-1 guards); REJECTED = 1
- WP = 11 (P2-00 … P2-10)
- DAG nodes = 11; edges = 12; blocking = 10; non-blocking = 2; cycles = 0; unreachable = 0
- AC = 39; Evidence = 32 (E2-00 … E2-31); DoD = 14 (DOD-P2-01 … DOD-P2-14)
- ADR candidates = 2 (media, deployment)
- Customer dependencies = 16

## Binding rule

- Phase-2 IN scope binds only after `PHASE2_GOVERNANCE_ACCEPTED` (independent audit) and `PHASE_2_GOVERNANCE_ARCHIVED_AND_FROZEN`.
- No Phase-2 implementation, migration, UI, or production import is authorized by this manifest.
- Phase-1 frozen governance, implementation, and history remain immutable.
