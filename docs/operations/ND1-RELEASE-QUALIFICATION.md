# HFM ND-1 Release Qualification — Operations

Status: ND-1 CORRECTION PACKET (B01–B05) implementation record and operator
runbook. Target-infrastructure steps (TLS, reboot, restore drills on a real
target) are marked `ND2_EXECUTION_REQUIRED` and are NOT claimed as completed
by ND-1.

This document is the single operations file for the ND-1 blockers; it does
not duplicate governance archives.

## 1. Effective production environment (B01)

Authoritative runtime inputs (read by `hfm.core.config` / `hfm.phase1.auth`
/ `alembic/env.py`):

| Input | Consumer | Notes |
| --- | --- | --- |
| `HFM_ENV` | system/version, scripts | must be `prod` for production |
| `HFM_DATABASE_URL` | app + Alembic | single authoritative DSN |
| `HFM_TOKEN_SECRET` | token signing | ≥ 32 chars, never the dev default |
| `HFM_MEDIA_ROOT` | media bytes | persistent volume |

The historical `DATABASE_URL`-only template was ambiguous: the runtime never
read it and could silently fall back to the local default database. The
template (`infra/env/prod.env.example`) now declares the real `HFM_*` inputs;
the legacy key remains only so the historical template-shape check passes and
is documented as inert.

Preflight (`scripts/validate-production-env.py`, redacted — values never
printed): rejects missing/template/known-dev DB and token-secret values,
then verifies read-only that the target database is reachable with exactly
one Alembic head and `current == head == 0014`. An unreachable database or
any mismatch is a non-zero failure; `--apply-migrations` can never bypass
verification (the preflight never applies a migration; operators apply
separately and re-run the gate). Launcher: `scripts/deploy-gate.sh
<dev|test|prod> [--env-file FILE] [--apply-migrations]`.

Operator inputs (required values): the real PostgreSQL DSN, the token
secret, and the public origins. ND-1 does not invent host/cert/retention
facts.

## 2. Deterministic release inputs (B02)

Declared platform: linux x86_64 (manylinux2014), CPython 3.12; Node 22 LTS;
pnpm 10.33.2 (root `package.json`). Locked artifacts:

- `infra/requirements-production.lock` — full runtime closure (25 packages)
  with sha256 hashes for the declared platform/ABI (asyncpg pinned 0.30.0,
  the latest release with official linux cp312 wheels; app constraint is
  `>=0.30.0`).
- `infra/requirements-build.lock` — build tooling closure (hatchling/build).
- Root `pnpm-lock.yaml` — frozen frontend install (`pnpm install
  --frozen-lockfile`).

Build: `scripts/build-release.sh --out DIR [--expect-sha SHA]
[--skip-frontend]` builds the backend wheel in an isolated venv from the
build lock (no editable reuse), packages the Alembic tree (without
`__pycache__`), builds the frontend static dist with the frozen pnpm lock,
DOWNLOAD-VERIFIES and packages the complete production runtime closure as a
hash-verified wheelhouse from `requirements-production.lock`, and emits
`manifest.json` (source SHA, tool/lock identifiers, per-artifact sha256
including every runtime wheel). Runtime provisioning from the release bundle
(ND-1 RV-P1-02):

    python3.12 -m venv /opt/hfm/venv
    /opt/hfm/venv/bin/pip install --no-index \
        --find-links /opt/hfm/runtime-wheelhouse \
        -r /opt/hfm/runtime-requirements-production.lock

`build-release.sh --check` validates lock syntax offline.

Regeneration of the Python locks is documented in the lock headers and must
run on the declared platform.

## 3. Existing production initialization (B03)

`scripts/initialize-production.py` is operator-only and establishes the
existing product's minimal production state on an already-migrated database:

- PROD_REQUIRED: exact 5-role matrix (ADR-07, `ensure_roles_seeded`) + one
  first SYSTEM_ADMIN supplied securely (env `HFM_ADMIN_PASSWORD` or TTY
  prompt; never printed; weak/demo passwords rejected).
- PROD_OPTIONAL: none (no invented reference data exists).
- DEV_ONLY / TEST_ONLY: recovery bootstrap fixtures, demo content.
- FORBIDDEN_IN_PRODUCTION: HFB imports, demo credentials, any new RBAC or
  capability.

Repeat execution: an active SYSTEM_ADMIN present → `ALREADY_PRESENT`
(idempotent no-op); an admin user missing the role link → `REPAIRED`; all
writes happen in one transaction (rollback on error → no partial state).
The preflight requires the database to be migrated at 0014 and verifies the
exact role matrix (5 roles, no duplicates). ND-1 RV-P1-03: initialization
NEVER emits DDL and never repairs schema drift — `Base.metadata.create_all`
is not called; a structurally invalid target (missing tables) fails the run
instead of being silently mutated.

## 4. Deploy, persistence and recovery package (B04)

Topology (example configs, unapplied at ND-1):
`Nginx (infra/nginx/hfm.conf.example) → static same-origin /api → private
Uvicorn 127.0.0.1:8000 (infra/systemd/hfm-backend.service.example) → private
PostgreSQL`. Vite is never the production server.

Media boundary (ND-1 RV-P0-01): media bytes live on the persistent volume
(`HFM_MEDIA_ROOT`) but are served ONLY through the application endpoint
`/api/v1/public/media/{asset_id}/bytes`, which rejects absent, draft and
withdrawn assets before resolving the local file. Nginx MUST never alias or
root the raw media volume to a public URL; `production-smoke.sh
--media-alias-check` and `scripts/tests/test_operations_package.py` enforce
that a direct persistent-root alias is forbidden.

Lifecycle: start/stop/restart/reboot recovery = `systemctl` + `Restart=
on-failure` on the stateless backend; the database and media volume are the
only persistent state.

Smoke: `scripts/production-smoke.sh --check-args` (input validation only),
`--media-alias-check FILE` (nginx media-boundary contract, ND-1 RV-P0-01)
and `--api-base URL` (live health + version + migration state + media volume
+ media probes: a direct `/media/<key>` URL must NOT be served 200, a
published asset must be served through `/api/v1/public/media/{asset_id}/bytes`
with operator-supplied asset ids at ND-2).

Backup/restore (PostgreSQL + media) and rollback decisions:

| Term | Meaning | Procedure |
| --- | --- | --- |
| APPLICATION_ROLLBACK | Revert the release artifacts/config only | Re-point the release root / systemd unit to the previous release bundle; state untouched |
| DATABASE_ROLLBACK | Move the database to an earlier revision | NOT a normal rollback: 0014 → 0013 downgrade is not supported as a release path (migration content is additive and not safely reversible). Do not attempt migration downgrade for rollback |
| DATABASE_RESTORE | Recover the database from a backup | Restore the pre-release `pg_dump`/`pg_basebackup` snapshot into the database, then run the post-restore verification (schema version == 0014, data smoke) |

Media restore mirrors the database snapshot (consistent point-in-time pair).
`scripts/backup-restore.sh` remains the operator runbook; its historical
drill used a SQLite fixture and is NOT evidence for the PostgreSQL/media
production contract — real PostgreSQL backup/restore drills are
`ND2_EXECUTION_REQUIRED` on the target with operator-owned retention/RPO/RTO
inputs.

Rollback verification after any restore/rollback: `production-smoke.sh` plus
`validate-production-env.py --verify-migration` (exact `current == 0014`).

## 5. Existing authentication-contract repair (B05)

Product defect in the FRONTEND login parsing only. The backend
`POST /api/v1/auth/login` envelope
`{success,timestamp,message,data:{ok,token,user_id,role}}` is the
authoritative existing API convention and is unchanged. The frontend
`authApi.login` now adapts that envelope into the existing `LoginResponse`
with strict shape validation (nonempty token/user_id, `role` in the frozen
five) and never writes authentication state on a malformed/failed response;
`permissions` stays `[]` (server-only authorization). All login mocks use
the real envelope; a mounted-route backend contract test and the vitest/e2e
login→guard journeys cover the repair. No backend, token, session, RBAC or
permission change was made.

## 6. Test harness hardening (H01 — P2)

Closed by the harness changes in this packet: Playwright/webServer fail
closed when the target port is occupied by a foreign process (never silently
reused) and bind the launched source SHA; the runtime gate scripts prove
ownership (PID/CWD/port) and TARGET_SHA identity (the process environment
must carry the current source SHA) before reuse, and clean up only processes
they launched. See `apps/frontend/playwright.config.ts`,
`apps/frontend/e2e/golden-runtime.spec.ts`,
`infra/scripts/fast-runtime-gate.sh`, `infra/scripts/golden-runtime-gate.sh`.
Static-file serving binds the release `manifest.json` source SHA (ND-2).

## ND2_EXECUTION_REQUIRED checklist (not ND-1 evidence)

- Apply and test the Nginx/systemd example configs on the real target
  (TLS certificates, reboot persistence).
- Execute PostgreSQL + media backup and isolated restore drills with the
  operator's real retention/RPO/RTO values.
- Run the full real-runtime smoke and the E2E suite against the production
  build in the target environment.
- Release the ND-1 corrected candidate only after Codex independent
  re-verification.
