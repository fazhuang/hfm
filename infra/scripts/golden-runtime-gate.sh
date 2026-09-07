#!/usr/bin/env bash
# HFM CLEAN FORWARD CF-01 — FULL_GOLDEN_GATE
# (ND-1 H01 + RV-01 hardened; ND1-H01-GOLDEN-PORT-CONTRACT)
#
# Proves the real runtime chain without any mock / route fulfillment:
#   fresh disposable PostgreSQL
#     → alembic upgrade head
#     → deterministic bootstrap_recovery.py
#     → FastAPI backend (:8000, real /api)
#     → Playwright-owned Vite dev (:5199, real /api proxy)   ← ONE owner
#     → real Chromium journeys (HOME/PERSON/JIAYI/HERITAGE/SEARCH/RESEARCH_GUARD)
#     → build + typecheck
#
# FRONTEND OWNERSHIP MODEL (ND1-H01-GOLDEN-PORT-CONTRACT): the gate does NOT
# pre-start the frontend. Playwright is the single frontend-server owner: its
# webServer launches the repository Vite on GOLDEN_FRONTEND_PORT with
# reuseExistingServer:false + strictPort + HFM_TARGET_SHA (see
# apps/frontend/playwright.config.ts). The gate (a) requires the target port
# to be free BEFORE launch (a foreign/stale occupant fails closed and is
# never killed), (b) launches Playwright as a recorded child with one
# coherent contract (HFM_E2E_PORT == HFM_E2E_BASE == CF01_BASE ==
# http://localhost:GOLDEN_FRONTEND_PORT, HFM_E2E_TARGET_SHA == SOURCE_SHA),
# (c) while Playwright runs, resolves the owned listener on
# GOLDEN_FRONTEND_PORT and verifies PID/CWD(apps/frontend)/port/ownership/
# HFM_TARGET_SHA==SOURCE_SHA before emitting HARNESS_FRONTEND_TARGET_SHA,
# and (d) fails the gate if Playwright exits before the listener was
# verified. Cleanup stops only the recorded Playwright child and its
# verified (owned+SHA) child resources — never a foreign listener.
#
# The backend remains gate-managed (Playwright starts no backend): fresh
# disposable PostgreSQL + alembic + bootstrap, then the recorded browser run.
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
SOURCE_SHA="$(git -C "$ROOT" rev-parse HEAD 2>/dev/null || true)"

rec() { echo "$1=$2"; }
# Recorded child resources of THIS run (killed on cleanup only after an
# ownership/SHA re-check). Empty until verified.
BE_PID=""
PW_PID=""
FE_PID=""

# ------------------------------------------------------------------ ownership
listener_pid() { lsof -nP -iTCP:"$1" -sTCP:LISTEN -t 2>/dev/null | head -1; }
pid_cwd() { lsof -a -p "$1" -d cwd -Fn 2>/dev/null | sed -n 's/^n//p' | head -1; }
pid_has_env() { # PID TOKEN — true when the process environment contains TOKEN.
  local pid="$1" token="$2"
  if ps eww -p "$pid" -o command= 2>/dev/null | grep -qF "$token"; then return 0; fi
  if [[ -r "/proc/$pid/environ" ]] && tr '\0' '\n' <"/proc/$pid/environ" 2>/dev/null | grep -qF "$token"; then
    return 0
  fi
  return 1
}
child_alive() { # PID — true while the child exists and is not a zombie.
  local s
  s="$(ps -o stat= -p "$1" 2>/dev/null | tr -d ' ')"
  [[ -n "$s" && "$s" != "Z" ]]
}

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

kill_owned_listener() {
  # PID CWD_DIRPREFIX — stop only when the process is proven owned. SIGTERM,
  # then wait up to 5s; an owned process that ignores SIGTERM is force-killed.
  local pid="$1" prefix="$2" cwd
  [[ -n "$pid" ]] || return 0
  cwd="$(pid_cwd "$pid")" || true
  case "$cwd" in
    "$prefix"*) ;;
    *) echo "HARNESS_SKIP_FOREIGN_KILL pid=$pid (not owned; left intact)"; return 0 ;;
  esac
  kill "$pid" 2>/dev/null || true
  for _ in $(seq 1 10); do
    kill -0 "$pid" 2>/dev/null || return 0
    sleep 0.5
  done
  cwd="$(pid_cwd "$pid")" || true
  case "$cwd" in
    "$prefix"*) kill -9 "$pid" 2>/dev/null || true ;;
    *) echo "HARNESS_SKIP_FORCE_KILL pid=$pid (ownership changed; left intact)" ;;
  esac
}

cleanup() {
  echo "==> cleanup"
  # Only recorded children of this run are stopped: the Playwright child and
  # the frontend listener it spawned (verified owned+SHA while running).
  # Foreign/stale processes are never touched (no broad pkill).
  if [ -n "${PW_PID:-}" ] && child_alive "$PW_PID"; then
    kill "$PW_PID" 2>/dev/null || true
  fi
  kill_owned_listener "${FE_PID:-}" "$ROOT/apps/frontend"
  # Any remaining listener on the frontend port carrying THIS run's
  # HFM_TARGET_SHA is this run's orphaned webServer child; foreign and stale
  # (same-CWD but other-SHA) listeners are never touched.
  FE_LEFT="$(owned_listener "$GOLDEN_FRONTEND_PORT" "$ROOT/apps/frontend")" || true
  if [ -n "$FE_LEFT" ] && pid_has_env "$FE_LEFT" "HFM_TARGET_SHA=$SOURCE_SHA"; then
    kill_owned_listener "$FE_LEFT" "$ROOT/apps/frontend"
  fi
  kill_owned_listener "${BE_PID:-}" "$ROOT/apps/backend"
  PGPASSWORD="$GOLDEN_PGPASS" dropdb -h "$GOLDEN_PGHOST" -U "$GOLDEN_PGUSER" -f --if-exists "$GOLDEN_DB" 2>/dev/null || true
}
trap cleanup EXIT

rec HARNESS_SOURCE_SHA "$SOURCE_SHA"

# port_free_or_fail PORT KIND — any occupant (foreign OR stale) is a hard
# gate failure: gate-managed/Playwright-owned servers are always started
# fresh by this run; occupants are never reused or killed.
port_free_or_fail() {
  local port="$1" kind="$2" pid cwd
  pid="$(listener_pid "$port")" || true
  [[ -z "$pid" ]] && return 0
  cwd="$(pid_cwd "$pid")" || true
  case "$cwd" in
    "$ROOT"*) echo "HARNESS_STALE_OWNER=FAIL kind=$kind port=$port pid=$pid (leftover process; free the port and re-run)" ;;
    *) echo "HARNESS_FOREIGN_OWNER=FAIL kind=$kind port=$port pid=$pid cwd=${cwd:-<unknown>}" ;;
  esac
  FAIL=1
}

# run_playwright_owned_frontend LOG — Playwright is the single frontend
# owner: port must be free; the recorded Playwright child starts the Vite;
# the gate verifies the owned listener while Playwright runs.
run_playwright_owned_frontend() {
  local log="$1" occupant cwd pid found="" pw_exit
  occupant="$(listener_pid "$GOLDEN_FRONTEND_PORT")" || true
  if [ -n "$occupant" ]; then
    cwd="$(pid_cwd "$occupant")" || true
    case "$cwd" in
      "$ROOT/apps/frontend"*)
        echo "HARNESS_STALE_OWNER=FAIL kind=frontend port=$GOLDEN_FRONTEND_PORT pid=$occupant (Playwright owns the frontend; free the port and re-run)"
        ;;
      *)
        echo "HARNESS_FOREIGN_OWNER=FAIL kind=frontend port=$GOLDEN_FRONTEND_PORT pid=$occupant cwd=${cwd:-<unknown>}"
        ;;
    esac
    FAIL=1
    return 1
  fi

  # Launch Playwright with one coherent port/base-url/SHA contract.
  (
    cd "$ROOT/apps/frontend" && \
    HFM_E2E_PORT="$GOLDEN_FRONTEND_PORT" \
    HFM_E2E_BASE="http://localhost:$GOLDEN_FRONTEND_PORT" \
    HFM_E2E_TARGET_SHA="$SOURCE_SHA" \
    CF01_BASE="http://localhost:$GOLDEN_FRONTEND_PORT" \
    pnpm exec playwright test e2e/golden-runtime.spec.ts
  ) >"$log" 2>&1 &
  PW_PID=$!

  # Verify the owned listener while Playwright runs.
  for _ in $(seq 1 90); do
    pid="$(owned_listener "$GOLDEN_FRONTEND_PORT" "$ROOT/apps/frontend")" || true
    if [ -n "$pid" ]; then
      if pid_has_env "$pid" "HFM_TARGET_SHA=$SOURCE_SHA"; then
        found="$pid"
        FE_PID="$pid"
        rec HARNESS_FRONTEND_TARGET_SHA "PASS (pid=$pid port=$GOLDEN_FRONTEND_PORT cwd=$ROOT/apps/frontend sha=$SOURCE_SHA)"
        break
      else
        echo "HARNESS_TARGET_SHA=FAIL kind=frontend port=$GOLDEN_FRONTEND_PORT pid=$pid (owned but stale/unverified)"
        FAIL=1
        break
      fi
    fi
    child_alive "$PW_PID" || break
    sleep 1
  done

  pw_exit=0
  wait "$PW_PID" 2>/dev/null || pw_exit=$?
  PW_PID=""

  if [ -z "$found" ]; then
    echo "BROWSER=FAIL (no owned+SHA frontend listener verified while Playwright ran; exit=$pw_exit)"
    tail -40 "$log" 2>/dev/null || true
    FAIL=1
    return 1
  fi
  if [ "$pw_exit" -ne 0 ]; then
    echo "BROWSER=FAIL (playwright exit=$pw_exit)"
    tail -40 "$log" 2>/dev/null || true
    FAIL=1
    return 1
  fi
  rec BROWSER PASS
  return 0
}

# Refuse to run when any process (foreign or stale) owns a target port.
port_free_or_fail "$GOLDEN_BACKEND_PORT" backend
port_free_or_fail "$GOLDEN_FRONTEND_PORT" frontend
if [ "$FAIL" -ne 0 ]; then
  echo "FULL_GOLDEN_GATE=FAIL (target port occupied; free it and re-run)"
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
  # Deterministic child: exec chain keeps one PID (subshell -> env -> nohup ->
  # python), so $! is the server PID and cleanup can always stop it.
  (cd "$ROOT/apps/backend" && exec \
    env HFM_DATABASE_URL="$GOLDEN_DB_URL" HFM_TARGET_SHA="$SOURCE_SHA" \
    nohup "$ROOT/apps/backend/.venv/bin/python" -m uvicorn hfm.main:app \
      --host 127.0.0.1 --port "$GOLDEN_BACKEND_PORT" >/tmp/cf01-backend.log 2>&1) &
  BE_PID=$!
  for _ in $(seq 1 30); do
    if curl -sf "http://127.0.0.1:$GOLDEN_BACKEND_PORT/health" >/dev/null 2>&1; then break; fi
    sleep 1
  done
  if ! curl -sf "http://127.0.0.1:$GOLDEN_BACKEND_PORT/health" >/dev/null 2>&1; then
    echo "BACKEND=FAIL"; tail -20 /tmp/cf01-backend.log; FAIL=1
  elif ! pid_has_env "$BE_PID" "HFM_TARGET_SHA=$SOURCE_SHA"; then
    # The env read can race the exec; retry briefly before failing.
    for _ in $(seq 1 10); do
      pid_has_env "$BE_PID" "HFM_TARGET_SHA=$SOURCE_SHA" && break
      sleep 0.5
    done
    if pid_has_env "$BE_PID" "HFM_TARGET_SHA=$SOURCE_SHA"; then
      rec BACKEND PASS
      rec HARNESS_BACKEND_TARGET_SHA "PASS ($SOURCE_SHA)"
    else
      echo "BACKEND=FAIL (ownership/SHA unverifiable on :$GOLDEN_BACKEND_PORT)"
      FAIL=1
    fi
  else
    rec BACKEND PASS
    rec HARNESS_BACKEND_TARGET_SHA "PASS ($SOURCE_SHA)"
  fi
fi

step "real browser golden journeys — Playwright-owned Vite (no mock)"
if [ $FAIL -eq 0 ]; then
  run_playwright_owned_frontend /tmp/cf01-browser.log
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
