# HFM Phase 2 ADR-P2-02 — Deployment / Operations Topology

Status: ADR CANDIDATE · READY FOR INDEPENDENT AUDIT · NOT BINDING UNTIL PHASE-2 GOVERNANCE ACCEPTANCE
Phase-1 Completion Baseline: `c17be40be6f055498fde11c0042e71d3a1056a7c`
Authority: CR-009/021 (two-layer architecture); ADR-01 (single modular deployment with strict logical/security public-research separation); Technology Baseline (observability UNKNOWN/TO BE DECIDED; conditional infra).

## Decision candidates

### Candidate A (recommended): single deployment, strict logical/security separation, namespaced services

- **Public service topology**: `/api/v1/public/*` surface behind a reverse proxy/gateway; anonymous-first, read-only.
- **Research service topology**: `/api/v1/research/*` + `/api/v1/admin/*` surfaces; authenticated, role-controlled; independent authorization and failure behavior (per ADR-01).
- **Database**: PostgreSQL (single instance; logical/security separation via ADR-05 namespaces + RBAC); physical split remains a future decision (ADR-01 notes "physical split unknown").
- **Object storage**: per ADR-P2-01 (S3-compatible) when media scope enters.
- **Reverse proxy / gateway**: single gateway routing to public/research namespaces with strict network isolation rules; no security-boundary merge for deployment convenience.
- **Environment separation**: dev / test / prod distinct with config matrix; no shared secrets.
- **Secret management**: env-injected secrets at deploy time; no committed secrets; dedicated secret store only when justified.
- **Logging / metrics / tracing**: structured logging baseline (P2-08); metrics/tracing conditional on evidence (no Prometheus/Grafana/OTel default).
- **Health checks**: health/ready probes for gateway and API; release gate checks health before cutover.
- **Backup / restore**: scheduled backups; verified restore drill on test env.
- **Release process / rollback**: migration-gate-before-deploy; rollback procedure (projection + reversible migrations); release = deploy, never import.
- **CI/CD boundary**: CI runs lint/type/test/build; deploy and production import are two distinct authorized actions; deploy authorization ≠ import authorization.

### Candidate B (rejected): merged public/research surface for deployment convenience

- Violates ADR-01/05 security separation; rejected.

### Candidate C (deferred): physical service split / multi-service topology

- Revisit when load/ops evidence justifies; not a Phase-2 prerequisite.

## Non-negotiables

- Public / Research strong separation remains mandatory (ADR-01/05).
- Production HFB import is a separate authorization from production deploy (DOD-P2-13; M4 gate).
- Production import remains NOT PERFORMED; M4–M7 not executed.

## Impact

- **Architecture**: deployment foundation (P2-07) + observability/release gates (P2-08).
- **Migration**: no migration execution; release gate includes database migration step.
- **Security**: secret boundary, env separation, RBAC at gateway.
- **Operations**: backup/restore, rollback, health verification, release gates.
