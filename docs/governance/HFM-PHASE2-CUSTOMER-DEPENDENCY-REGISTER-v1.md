# HFM Phase 2 Customer Dependency Register v1

Status: GOVERNANCE CANDIDATE · READY FOR INDEPENDENT AUDIT
Source: NPG-005 §4 (client material request list) + NPG-001 §4 (open client decisions). This register is a governance artifact, not a code work package. Full customer content population is never a platform-code completion blocker unless a specific fixture is selected by governance.

| DEP-ID | Dependency | Marker | Affected Phase-2 scope |
| --- | --- | --- | --- |
| CD-01 | Master asset register (owner, contact, format, count, storage location, hash, digitization state, intended use) | REQUIRED_FOR_CONTENT_POPULATION | P2-C14, P2-C5 |
| CD-02 | 《针灸甲乙经》version/file list (complete/OCRed/structured/collated status) | REQUIRED_FOR_CONTENT_POPULATION | P2-C14, P2-C3 |
| CD-03 | 皇甫谧史料 catalogue with page/volume locators per biography event/quotation | REQUIRED_FOR_CONTENT_POPULATION | P2-C14, P2-C4 |
| CD-04 | 皇甫谧 works list with extant/lost/full-text status and rights | REQUIRED_FOR_CONTENT_POPULATION | P2-C14, P2-C3 |
| CD-05 | 128-chapter and 349-acupoint structured datasets (if claimed) with reconciliation evidence | REQUIRED_FOR_CONTENT_POPULATION | P2-C14 (conditional) |
| CD-06 | Meridian/disease/technique datasets (historical semantics only; expert review responsibility) | REQUIRED_FOR_CONTENT_POPULATION | P2-C14 (conditional) |
| CD-07 | Official heritage certificate/notice (item name, level, number, holder/protection unit, display conditions) | REQUIRED_FOR_CONTENT_POPULATION | P2-C5, P2-C4 |
| CD-08 | Inheritor register, genealogy relationships, supporting evidence, completeness statement, per-person publication authorization | REQUIRED_FOR_CONTENT_POPULATION | P2-C5, P2-C4 |
| CD-09 | Campus photo originals, captions, photographer copyright, portrait/underage consent, allowed channels, expiry, withdrawal contact | REQUIRED_FOR_CONTENT_POPULATION | P2-C5 |
| CD-10 | Certificate/photo public derivatives, redaction/watermark rules, authorized content approver per institution | REQUIRED_FOR_PRODUCTION | P2-C5, P2-C7 |
| CD-11 | Visitor/research/student journeys and acceptance metrics | REQUIRED_FOR_FIXTURE | P2-C1, P2-C2, P2-C4 |
| CD-12 | Success metrics / acceptance targets | REQUIRED_FOR_FIXTURE | P2-14 DoD |
| CD-13 | Joint-governance ownership and final approvers | REQUIRED_FOR_PRODUCTION | P2-07, governance |
| CD-14 | Public editorial workflow, withdrawal policy, research-to-public handoff | REQUIRED_FOR_FIXTURE | P2-C2 |
| CD-15 | Per-asset HFB reuse verdicts (client/governance input to P2-C9) | OPTIONAL | P2-10 |
| CD-16 | Display device facts (if exhibition is pursued) | OPTIONAL | P2-C11 (deferred) |

## Accounting

- DEP total = 16
- REQUIRED_FOR_CODE = 0 (no code WP is blocked by customer material)
- REQUIRED_FOR_FIXTURE = 3 (CD-11, CD-12, CD-14)
- REQUIRED_FOR_CONTENT_POPULATION = 9 (CD-01…CD-09)
- REQUIRED_FOR_PRODUCTION = 2 (CD-10, CD-13)
- OPTIONAL = 2 (CD-15, CD-16)
