#!/usr/bin/env bash
# HFM CLEAN FORWARD CF-01 — FULL_GOLDEN_GATE (ND-1 H01 hardened)
#
# Proves the real runtime chain without any mock / route fulfillment:
#   fresh disposable PostgreSQL
#     → alembic upgrade head
#     → deterministic bootstrap_recovery.py
#     → FastAPI backend (:8000, real /api)
#     → Vite dev with real /api proxy (:5199 → :8000)
#     → real Chromium journeys (HOME/PERSON/JIAYI/HERITAGE/SEARCH/RESEARCH_GUARD)
#     → build + typecheck
#
# ND-1 H01 (test-harness hardening): every server started here is recorded by
# its actual listener PID and cleaned up only after its working directory is
# proven to be THIS repository. A foreign process occupying the target port
# FAILS THE GATE (never reused, never killed). No broad pkill is used.
#
# Not for daily use (costly); milestone / CF acceptance runs this.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
FAIL=0
step() { echo "\n==> $*"; }

GOLDEN_DB="${GOLDEN_DB:-hfm_cf01}"
GOLDEN_PGUSER="${GOLDEN_PGUSER:-hfb}"
GOLDEN_PGPASS="${GOLDEN_PGPASS:-change-me}"
GOLDEN_PGHOST="${GOLDEN_PGHOST:-127.0.0.1}"
GOLDEN_PGPORT="${GOLDEN_PGPORT:-5432}"
# Deterministic APP password for the dedicated role (never from a real secret).
GOLDEN_APP_PW="${GOLDEN_APP_PW:-cf01-golden-pw}"
GOLDEN_DB_URL="postgresql+asyncpg://hfm_app:${GOLDEN_APP_PW}@${GOLDEN_PGHOST}:${GOLDEN_PGPORT}/${GOLDEN_DB}"
GOLDEN_BACKEND_PORT="${GOLDEN_BACKEND_PORT:-8000}"
GOLDEN_FRONTEND_PORT="${GOLDEN_FRONTEND_PORT:-5199}"

rec() { echo "$1=$2"; }
# Recorded listener PIDs owned by this run (killed on cleanup only after an
# ownership re-check). Empty until each server reports healthy.
BE_PID=""
FE_PID=""

# ------------------------------------------------------------------ ownership
listener_pid() { lsof -nP -iTCP:"$1" -sTCP:LISTEN -t 2>/dev/null | head -1; }
pid_cwd() { lsof -a -p "$1" -d cwd -Fn 2>/dev/null | sed -n 's/^n//p' | head -1; }

# owned_listener PORT DIRPREFIX — echoes the listener PID when its cwd is
# under DIRPREFIX (this repository's own process); empty otherwise.
owned_listener() {
  local pid cwd
  pid="$(listener_pid "$1")" || true
  [[ -z "$pid" ]] && return 0
  cwd="$(pid_cwd "$pid")" || true
  case "$cwd" in
    "$2"*) echo "$pid" ;;
  esac
}

# fail_on_foreign PORT KIND — a live listener on PORT whose cwd is NOT this
# repository is a hard gate failure (never reused, never killed).
fail_on_foreign() {
  local pid cwd
  pid="$(listener_pid "$1")" || true
  [[ -z "$pid" ]] && return 0
  cwd="$(pid_cwd "$pid")" || true
  case "$cwd" in
    "$ROOT"*) return 0 ;;   # owned (this repo) leftover — cleanup handles it
  esac
  echo "HARNESS_FOREIGN_OWNER=FAIL kind=$2 port=$1 pid=$pid cwd=${cwd:-<unknown>}"
  FAIL=1
}

kill_owned_listener() {
  # PID CWD_DIRPREFIX — kill only when the process is proven owned.
  local pid="$1" prefix="$2" cwd
  [[ -n "$pid" ]] || return 0
  cwd="$(pid_cwd "$pid")" || true
  case "$cwd" in
    "$prefix"*) kill "$pid" 2>/dev/null || true ;;
    *) echo "HARNESS_SKIP_FOREIGN_KILL pid=$pid (not owned; left intact)" ;;
  esac
}

cleanup() {
  echo "==> cleanup"
  # Only recorded, ownership-re-verified PIDs are terminated. Foreign
  # processes are always left intact (never a broad pkill).
  kill_owned_listener "${BE_PID:-}" "$ROOT/apps/backend"
  kill_owned_listener "${FE_PID:-}" "$ROOT/apps/frontend"
  PGPASSWORD="$GOLDEN_PGPASS" dropdb -h "$GOLDEN_PGHOST" -U "$GOLDEN_PGUSER" -f --if-exists "$GOLDEN_DB" 2>/dev/null || true
}
trap cleanup EXIT

# H01: refuse to run when a foreign process already owns a target port.
fail_on_foreign "$GOLDEN_BACKEND_PORT" backend
fail_on_foreign "$GOLDEN_FRONTEND_PORT" frontend
if [ "$FAIL" -ne 0 ]; then
  echo "FULL_GOLDEN_GATE=FAIL (foreign process on a target port; free the port and re-run)"
  exit 1
fi

step "fresh disposable PostgreSQL ($GOLDEN_DB)"
# Dedicated role + isolated db, owned by app role (like the runtime contract).
PGPASSWORD="$GOLDEN_PGPASS" psql -h "$GOLDEN_PGHOST" -U "$GOLDEN_PGUSER" -d postgres -v ON_ERROR_STOP=1 <<SQL
DO \$\$ BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname='hfm_app') THEN
    CREATE ROLE hfm_app LOGIN PASSWORD '${GOLDEN_APP_PW}';
  END IF;
END \$\$;
SQL
PGPASSWORD="$GOLDEN_PGPASS" dropdb -h "$GOLDEN_PGHOST" -U "$GOLDEN_PGUSER" -f --if-exists "$GOLDEN_DB" 2>/dev/null || true
PGPASSWORD="$GOLDEN_PGPASS" createdb -h "$GOLDEN_PGHOST" -U "$GOLDEN_PGUSER" -O hfm_app "$GOLDEN_DB"
PGPASSWORD="$GOLDEN_PGPASS" psql -h "$GOLDEN_PGHOST" -U "$GOLDEN_PGUSER" -d "$GOLDEN_DB" -v ON_ERROR_STOP=1 \
  -c "GRANT ALL ON SCHEMA public TO hfm_app; ALTER SCHEMA public OWNER TO hfm_app;" >/dev/null
rec FRESH_DB PASS

step "alembic upgrade head"
if ! (cd "$ROOT/apps/backend" && HFM_DATABASE_URL="$GOLDEN_DB_URL" .venv/bin/python -m alembic upgrade head >/tmp/cf01-alembic.log 2>&1); then
  echo "MIGRATION=FAIL"; tail -20 /tmp/cf01-alembic.log; FAIL=1; fi
rec MIGRATION "$([ $FAIL -eq 0 ] && echo PASS || echo FAIL)"

step "deterministic bootstrap"
if [ $FAIL -eq 0 ]; then
  if ! (cd "$ROOT/apps/backend" && HFM_DATABASE_URL="$GOLDEN_DB_URL" .venv/bin/python scripts/bootstrap_recovery.py >/tmp/cf01-bootstrap.log 2>&1); then
    echo "BOOTSTRAP=FAIL"; tail -20 /tmp/cf01-bootstrap.log; FAIL=1; fi
fi
rec BOOTSTRAP "$([ $FAIL -eq 0 ] && echo PASS || echo FAIL)"

step "start FastAPI backend (:$GOLDEN_BACKEND_PORT)"
if [ $FAIL -eq 0 ]; then
  (cd "$ROOT/apps/backend" && \
    HFM_DATABASE_URL="$GOLDEN_DB_URL" \
    nohup .venv/bin/python -m uvicorn hfm.main:app --host 127.0.0.1 --port "$GOLDEN_BACKEND_PORT" >/tmp/cf01-backend.log 2>&1) &
  for i in $(seq 1 30); do
    if curl -sf "http://127.0.0.1:$GOLDEN_BACKEND_PORT/health" >/dev/null 2>&1; then break; fi
    sleep 1
  done
  if ! curl -sf "http://127.0.0.1:$GOLDEN_BACKEND_PORT/health" >/dev/null 2>&1; then
    echo "BACKEND=FAIL"; tail -20 /tmp/cf01-backend.log; FAIL=1
  else
    BE_PID="$(owned_listener "$GOLDEN_BACKEND_PORT" "$ROOT/apps/backend")" || true
    if [ -n "$BE_PID" ]; then rec BACKEND PASS; else
      echo "BACKEND=FAIL (listener ownership unverifiable on :$GOLDEN_BACKEND_PORT)"; FAIL=1; fi
  fi
fi

step "start Vite dev with real /api proxy (:$GOLDEN_FRONTEND_PORT)"
if [ $FAIL -eq 0 ]; then
  (cd "$ROOT/apps/frontend" && \
    nohup pnpm dev --port "$GOLDEN_FRONTEND_PORT" --strictPort >/tmp/cf01-frontend.log 2>&1) &
  for i in $(seq 1 30); do
    if curl -sf "http://localhost:$GOLDEN_FRONTEND_PORT/" >/dev/null 2>&1; then break; fi
    sleep 1
  done
  if ! curl -sf "http://localhost:$GOLDEN_FRONTEND_PORT/" >/dev/null 2>&1; then
    echo "FRONTEND=FAIL"; tail -20 /tmp/cf01-frontend.log; FAIL=1
  else
    FE_PID="$(owned_listener "$GOLDEN_FRONTEND_PORT" "$ROOT/apps/frontend")" || true
    if [ -n "$FE_PID" ]; then rec FRONTEND PASS; else
      echo "FRONTEND=FAIL (listener ownership unverifiable on :$GOLDEN_FRONTEND_PORT)"; FAIL=1; fi
  fi
fi

step "real browser golden journeys (no mock)"
if [ $FAIL -eq 0 ]; then
  if ! (cd "$ROOT/apps/frontend" && \
        CF01_BASE="http://localhost:$GOLDEN_FRONTEND_PORT" \
        pnpm exec playwright test e2e/golden-runtime.spec.ts >/tmp/cf01-browser.log 2>&1); then
    echo "BROWSER=FAIL"; tail -40 /tmp/cf01-browser.log; FAIL=1
  else rec BROWSER PASS; fi
fi

step "frontend build"
if [ $FAIL -eq 0 ]; then
  if ! (cd "$ROOT/apps/frontend" && pnpm build >/tmp/cf01-build.log 2>&1); then
    echo "BUILD=FAIL"; tail -15 /tmp/cf01-build.log; FAIL=1
  else rec BUILD PASS; fi
fi

step "frontend typecheck"
if [ $FAIL -eq 0 ]; then
  if ! (cd "$ROOT/apps/frontend" && pnpm typecheck >/tmp/cf01-typecheck.log 2>&1); then
    echo "TYPECHECK=FAIL"; tail -15 /tmp/cf01-typecheck.log; FAIL=1
  else rec TYPECHECK PASS; fi
fi

if [ $FAIL -eq 0 ]; then
  echo "FULL_GOLDEN_GATE=PASS"
else
  echo "FULL_GOLDEN_GATE=FAIL"
fi
exit $FAIL
