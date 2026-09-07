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

Runtime fail-closed (ND-1 B01): the application itself fails at
import/startup when `HFM_ENV=prod` and a real `HFM_DATABASE_URL` /
`HFM_TOKEN_SECRET` is missing or is the development default
(`hfm.core.config._production_fail_closed`, consumed by `hfm.phase1.auth`).
The systemd unit runs the preflight as `ExecStartPre` so an invalid
production configuration can never silently fall back to the localhost
database or the development token secret. Developer/test behavior is
unchanged outside `HFM_ENV=prod`.

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

`build-release.sh --check` validates lock syntax offline and
`--check-runtime` verifies the declared runtimes (CPython 3.12, Node 22 LTS,
pnpm 10.33.2) with actual version + source-SHA output; every real release
build enforces the contract and exits non-zero when a declared runtime is
missing or mismatched (ND-1 B02 — no silent substitution of another
major/minor runtime).

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
and `--api-base URL` (live health + version + migration state + media volume;
media probes: a direct `/media/<key>` URL must NOT be served 200, a
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

### ND1-H01-GOLDEN-PORT-CONTRACT — one frontend-server owner per invocation

The runtime gates use the **Playwright-owned frontend model**: the gate never
pre-starts the frontend Vite. Playwright's webServer is the single frontend
owner (`reuseExistingServer:false` + `--strictPort` + `HFM_TARGET_SHA`
inheritance). Gate contract for every browser invocation:

```text
HFM_E2E_PORT        = GOLDEN_FRONTEND_PORT          (must be free before launch)
HFM_E2E_BASE        = http://localhost:GOLDEN_FRONTEND_PORT
HFM_E2E_TARGET_SHA  = SOURCE_SHA                     (checked by Playwright at load)
CF01_BASE           = http://localhost:GOLDEN_FRONTEND_PORT   (test URL input only; equals HFM_E2E_BASE)
```

`CF01_BASE` remains only a test URL input for `golden-runtime.spec.ts` and is
always set equal to `HFM_E2E_BASE` in gate invocations. While the recorded
Playwright child runs, the gate resolves the listener on
`GOLDEN_FRONTEND_PORT` and verifies PID, CWD under `apps/frontend`, port,
process ownership and `HFM_TARGET_SHA == SOURCE_SHA`; `HARNESS_FRONTEND_TARGET_SHA`
is emitted only after that check passes. If Playwright exits before the
listener is verified the gate fails. On every failure path the gate stops
only the recorded Playwright child and its verified (owned + SHA) child
resources — never a foreign or stale listener.

## ND2_EXECUTION_REQUIRED checklist (not ND-1 evidence)

- Apply and test the Nginx/systemd example configs on the real target
  (TLS certificates, reboot persistence).
- Execute PostgreSQL + media backup and isolated restore drills with the
  operator's real retention/RPO/RTO values.
- Run the full real-runtime smoke and the E2E suite against the production
  build in the target environment.
- Release the ND-1 corrected candidate only after Codex independent
  re-verification.

## Pre-release checklist (machine-executable)

`scripts/pre-release-checklist.sh` records PASS / FAIL / N/A+justification
for every required pre-release item and exits nonzero on any FAIL. Items:
RC SHA (--expect-sha), worktree/artifact identity (clean porcelain +
`git diff --check`), required env/secrets (redacted validator),
PostgreSQL connectivity, target migration revision (current == 0014, one
head), backup/restore point, bootstrap status, persistent media path,
runtime versions (python 3.12 / node 22 / pnpm 10.33.2 contract), reverse
proxy config (media-boundary check), TLS/DNS readiness, auth prerequisite,
and rollback readiness. Operator-declared facts (backup point, TLS/DNS,
bootstrap, auth, rollback) default to N/A with justification until ND-2
executes them on the target.

## Post-deploy smoke checklist (procedure — executed at ND-2)

Evidence per item is produced by the existing mechanical gates; nothing here
runs against a production target during ND-1.

| Check | Evidence command (ND-2, on the target release) |
| --- | --- |
| HOME served 200 + platform heading | golden-runtime.spec HOME |
| PERSON real chain (Browser→/api→PG→render) | golden-runtime.spec PERSON |
| JIAYI served 200 + heading | golden-runtime.spec JIAYI |
| HERITAGE served 200 + heading | golden-runtime.spec HERITAGE |
| SEARCH real results from Golden data | golden-runtime.spec SEARCH |
| RESEARCH_GUARD anonymous → /login | golden-runtime.spec RESEARCH |
| HTTP/HTTPS + API connectivity + PostgreSQL dependency | `scripts/database-dependency-probe.sh` + `scripts/production-smoke.sh --api-base URL` |
| Static assets / media assets (published only, no direct alias) | `production-smoke.sh --media-alias-check` + published-asset probe |
| Valid authentication / invalid authentication (401) | real-browser auth evidence gate |
| Authorization / admin denial (non-admin denied) | real-browser auth evidence gate |
| 404 behavior / 500 behavior | browser journey assertions + `CF01_MONITOR` (no unexpected 4xx/5xx) |
| Browser fatal errors = 0 | `CF01_MONITOR fatal=0` |
| Unexpected network failures = 0 | `CF01_MONITOR requestFailed=0 unexpectedHttp=0` |
| Mobile basic rendering (375) | E2E responsive/viewport suite |

## Rollback trigger matrix

Rollback = APPLICATION_ROLLBACK (release artifacts/config only),
DATABASE_RESTORE (restore pre-release snapshot — migration downgrade is NOT
a rollback path), MEDIA restore in lockstep with the DB snapshot.
`git checkout <old SHA>` alone is never a complete rollback procedure.

| Trigger | Decision | Application rollback | Database handling | Media handling | Verification |
| --- | --- | --- | --- | --- | --- |
| Startup failure (env/import fail-closed, ExecStartPre) | Roll back artifacts; fix env | Point systemd/release root at previous bundle; re-run preflight | None (untouched) | None | `pre-release-checklist.sh` + smoke PASS |
| Migration failure at deploy | Abort; do not run forward | Keep current artifacts | Restore pre-release `pg_dump` snapshot; do NOT downgrade 0014 | Restore matching snapshot | `database-dependency-probe.sh` (revision 0014) |
| Core smoke failure (HOME/PERSON/SEARCH…) | Roll back artifacts | Previous release bundle | None if DB compatible | None | Golden journeys re-run PASS |
| Authentication failure (valid login rejected / invalid accepted) | Roll back artifacts; no auth redesign in rollback | Previous bundle | Restore snapshot if data suspected | None | Real-browser auth evidence PASS |
| Authorization regression (privilege widening/denial broken) | Roll back artifacts | Previous bundle | Restore snapshot if role data suspected | None | RBAC + real-browser admin-denial evidence |
| Persistent 5xx | Roll back artifacts | Previous bundle | Investigate/restore snapshot on data cause | None | Smoke + CF01_MONITOR (unexpectedHttp=0) |
| Data-integrity concern | Stop writes; restore | Previous bundle | Restore pre-release snapshot | Restore matching snapshot | Post-restore smoke + integrity probe |
| Static/media critical failure | Roll back artifacts | Previous bundle | None | Restore media volume from matching backup | Media published/denied probes |

Post-rollback verification is always: `pre-release-checklist.sh` +
`production-smoke.sh` + `database-dependency-probe.sh` + the relevant
golden/auth browser journeys.

## Database dependency probe (post-start, repeatable)

`scripts/database-dependency-probe.sh --api-base URL --db-url DSN` proves a
real database dependency, not just an HTTP process: process must answer
/health (PROBE_PROCESS=UP) and the database must answer a read-only revision
probe at 0014 (PROBE_DATABASE=OK). A process that is up while its database
is unreachable or off-revision is detected as PROBE_RESULT=FAIL.

## Real-browser auth evidence (G7)

`scripts/real-browser-auth-evidence.sh` is the stable, repeatable real-browser
auth path: isolated PostgreSQL → 0014 → first admin (initialize-production,
prod env) → student via the admin API → real backend on :8000 with a valid
prod runtime env → Playwright-owned Vite → real Chromium runs
`apps/frontend/e2e-auth/auth-evidence.spec.ts` (no route fulfillment),
verifying valid login → research, invalid credentials rejected (401),
anonymous guards, and authenticated non-admin denied on an admin endpoint
with the real token. Browser completion evidence is the gate's
`G7_REAL_AUTH_EVIDENCE=PASS` output (with CF01-style pageError=0). The spec
lives under `apps/frontend/e2e-auth/` and is excluded from the standard
88-test suite.
