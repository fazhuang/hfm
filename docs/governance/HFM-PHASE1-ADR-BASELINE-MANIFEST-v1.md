# HFM Phase 1 ADR Baseline Manifest v1

Status: ACCEPTED ADR BASELINE · GOVERNANCE ONLY  
Phase 1 Governance Baseline: `29c5b856f221a12bac9de13e1a5043c5d05208e2`  
Blocking ADR Resolution Audit: `docs/audit/HFM-PHASE1-BLOCKING-ADR-RESOLUTION-AUDIT.md`

| Path | SHA-256 | Decision status | Affected WP | Binding status |
| --- | --- | --- | --- | --- |
| `docs/governance/adr/HFM-PHASE1-ADR-01-DEPLOYMENT-TOPOLOGY.md` | `b1951acdfdf91bd7d7bced5913c0f5ffb298f6fedef52b42f276bbf67db2cff9` | ACCEPTED | P1-11, P1-12 | FROZEN ADR |
| `docs/governance/adr/HFM-PHASE1-ADR-02-SEARCH.md` | `1ceca090ce6bea252265e0de10ff31db9d9356434ca50821449cbe99d58e87eb` | ACCEPTED | P1-05, P1-08, P1-11, P1-12 | FROZEN ADR |
| `docs/governance/adr/HFM-PHASE1-ADR-05-PUBLIC-RESEARCH-API.md` | `db5ded2c9a7a546115177c6c2e66f9a4c802f5b00d270217d93431be73e7731c` | ACCEPTED | P1-09, P1-10, P1-11, P1-12 | FROZEN ADR |
| `docs/governance/adr/HFM-PHASE1-ADR-06-HFB-MIGRATION-ADAPTER.md` | `84447bf0117f46757abe059cb5047f3301216e0b9aaaf81d57ca9524da216b69` | ACCEPTED | P1-01, P1-02, P1-13 | FROZEN ADR |
| `docs/governance/adr/HFM-PHASE1-ADR-07-IDENTITY-RBAC.md` | `634cc04ba10b51185eaa628a1f977427e168f732096644dad666319a37c8f985` | ACCEPTED | P1-00, P1-09, P1-10, P1-11, P1-12 | FROZEN ADR |
| `docs/audit/HFM-PHASE1-BLOCKING-ADR-RESOLUTION-AUDIT.md` | `fa0f767d270a1eb6d5f52f98813a9f707b5a5cd54ce5fbcfdea0e71815f2ccc1` | PASS / 0 new P0 | ADR-01/02/05/06/07 | AUDIT BINDING |
| `docs/governance/HFM-PHASE1-GOVERNANCE-AUTHORIZATION-v1.md` | `17ab800b0c1eff168d6c5dae5208d583beed35eaa7fc7244d146f004b15bf3b8` | GOVERNANCE AUTHORIZATION | All approved scope | AUTHORIZATION INPUT |

Decisions preserved: ADR-01 single modular deployment with logical/security separation; ADR-02 PostgreSQL native search with `pg_trgm`/GIN and no Elasticsearch requirement; ADR-05 `/api/v1/public/*`, `/api/v1/research/*`, `/api/v1/admin/*` with independent response schemas and repository/service filtering; ADR-06 offline adapter with no HFB runtime dependency and M0–M7 gates; ADR-07 HFM-native identity/RBAC, no HFB credential migration, default deny.

The manifest itself is excluded from its hash list to avoid self-reference; its committed Git blob is verified post-commit.
