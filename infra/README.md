# HFM Infra (P2-07 deployment / operations foundation)

Status: P2-07 implementation · ADR-P2-02 ACCEPTED · no production execution

## Environment contracts (P2-07-AC-01)

- `infra/env/dev.env.example`, `infra/env/test.env.example`,
  `infra/env/prod.env.example` — the dev/test/prod configuration matrix.
  Placeholders only; real values are injected at deploy time, never committed.
- `scripts/check-env.sh` — verifies required keys per environment and that
  production never cross-overlaps dev/test values.

## Secret boundary (P2-07-AC-02)

- `scripts/check-secrets.sh` — scans all tracked files for committed secrets
  (`*.env.example` placeholder contracts exempt). Any finding fails the check.

## Database migration gate (P2-07-AC-03)

- `scripts/deploy-gate.sh <dev|test|prod> [--apply-migrations]` — the release
  gate: environment separation must pass, exactly one Alembic head must
  exist, and pending migrations block the release unless explicitly applied.
  Production deploy ≠ production HFB import (ADR-P2-02).

## Backup / restore runbook (P2-07-AC-04)

- `scripts/backup-restore.sh` — backup (test/prod) and restore drill (test
  env with `--verify`). Production restore is an operator-gated manual
  runbook; the foundation validates the procedure on the test environment.

## Boundaries

- No real production deployment is performed by this foundation.
- No production HFB import; M0–M7 HFB migration lifecycle NOT EXECUTED.
- No credentials are committed; no vendor-specific irreversible coupling.
