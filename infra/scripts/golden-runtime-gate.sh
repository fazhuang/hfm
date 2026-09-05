#!/usr/bin/env bash
# HFM CLEAN FORWARD CF-01 — FULL_GOLDEN_GATE
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

cleanup() {
  echo "==> cleanup"
  # Kill the exact uvicorn/vite processes by their target port (robust vs the
  # nohup subshell PID which is not the real server process).
  pkill -f "uvicorn hfm.main:app.*--port $GOLDEN_BACKEND_PORT" 2>/dev/null || true
  pkill -f "vite.*--port $GOLDEN_FRONTEND_PORT" 2>/dev/null || true
  if [ -n "${BE_PID:-}" ]; then kill "$BE_PID" 2>/dev/null || true; fi
  if [ -n "${FE_PID:-}" ]; then kill "$FE_PID" 2>/dev/null || true; fi
  PGPASSWORD="$GOLDEN_PGPASS" dropdb -h "$GOLDEN_PGHOST" -U "$GOLDEN_PGUSER" -f --if-exists "$GOLDEN_DB" 2>/dev/null || true
}
trap cleanup EXIT

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
  BE_PID=$!
  for i in $(seq 1 30); do
    if curl -sf "http://127.0.0.1:$GOLDEN_BACKEND_PORT/health" >/dev/null 2>&1; then break; fi
    sleep 1
  done
  if ! curl -sf "http://127.0.0.1:$GOLDEN_BACKEND_PORT/health" >/dev/null 2>&1; then
    echo "BACKEND=FAIL"; tail -20 /tmp/cf01-backend.log; FAIL=1
  else rec BACKEND PASS; fi
fi

step "start Vite dev with real /api proxy (:$GOLDEN_FRONTEND_PORT)"
if [ $FAIL -eq 0 ]; then
  (cd "$ROOT/apps/frontend" && \
    nohup pnpm dev --port "$GOLDEN_FRONTEND_PORT" --strictPort >/tmp/cf01-frontend.log 2>&1) &
  FE_PID=$!
  for i in $(seq 1 30); do
    if curl -sf "http://localhost:$GOLDEN_FRONTEND_PORT/" >/dev/null 2>&1; then break; fi
    sleep 1
  done
  if ! curl -sf "http://localhost:$GOLDEN_FRONTEND_PORT/" >/dev/null 2>&1; then
    echo "FRONTEND=FAIL"; tail -20 /tmp/cf01-frontend.log; FAIL=1
  else rec FRONTEND PASS; fi
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
