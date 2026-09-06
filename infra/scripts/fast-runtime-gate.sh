#!/usr/bin/env bash
# HFM CLEAN FORWARD CF-01 — FAST_RUNTIME_GATE (ND-1 H01 hardened)
#
# Daily regression: real backend + real frontend + real browser, NO mock.
# Reuses the current database (does NOT create a fresh disposable one) — use
# FULL_GOLDEN_GATE for fresh-DB + migration + bootstrap verification.
#
#   FAST_RUNTIME_GATE = real DB (existing) + real /api proxy + real browser
#
# ND-1 H01 (test-harness hardening): a running server is REUSED only when its
# listener PID's working directory is proven to be THIS repository (owned).
# A foreign process on the backend/frontend port FAILS the gate (never
# reused, never killed). Only processes recorded and owned by this run are
# stopped on exit.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
FAIL=0
rec() { echo "$1=$2"; }
step() { echo "\n==> $*"; }

: "${HFM_DATABASE_URL:?set HFM_DATABASE_URL for FAST_RUNTIME_GATE}"
GOLDEN_BACKEND_PORT="${GOLDEN_BACKEND_PORT:-8000}"
GOLDEN_FRONTEND_PORT="${GOLDEN_FRONTEND_PORT:-5199}"
DB_URL="$HFM_DATABASE_URL"
BE_PID=""
FE_PID=""

listener_pid() { lsof -nP -iTCP:"$1" -sTCP:LISTEN -t 2>/dev/null | head -1; }
pid_cwd() { lsof -a -p "$1" -d cwd -Fn 2>/dev/null | sed -n 's/^n//p' | head -1; }

# owned_listener PORT DIRPREFIX — listener PID when its cwd is under DIRPREFIX.
owned_listener() {
  local pid cwd
  pid="$(listener_pid "$1")" || true
  [[ -z "$pid" ]] && return 0
  cwd="$(pid_cwd "$pid")" || true
  case "$cwd" in
    "$2"*) echo "$pid" ;;
  esac
}

# health_on_port PORT URL — true when the URL answers.
health_on_port() {
  curl -sf --max-time 3 "$2" >/dev/null 2>&1
}

fail_on_foreign() {
  local pid cwd
  pid="$(listener_pid "$1")" || true
  [[ -z "$pid" ]] && return 0
  cwd="$(pid_cwd "$pid")" || true
  case "$cwd" in
    "$ROOT"*) return 0 ;;
  esac
  echo "HARNESS_FOREIGN_OWNER=FAIL kind=$2 port=$1 pid=$pid cwd=${cwd:-<unknown>}"
  FAIL=1
}

kill_owned_listener() {
  local pid="$1" prefix="$2" cwd
  [[ -n "$pid" ]] || return 0
  cwd="$(pid_cwd "$pid")" || true
  case "$cwd" in
    "$prefix"*) kill "$pid" 2>/dev/null || true ;;
    *) echo "HARNESS_SKIP_FOREIGN_KILL pid=$pid (not owned; left intact)" ;;
  esac
}

cleanup() {
  kill_owned_listener "${BE_PID:-}" "$ROOT/apps/backend"
  kill_owned_listener "${FE_PID:-}" "$ROOT/apps/frontend"
}
trap cleanup EXIT

# H01: fail closed on foreign port owners BEFORE any reuse or navigation.
fail_on_foreign "$GOLDEN_BACKEND_PORT" backend
fail_on_foreign "$GOLDEN_FRONTEND_PORT" frontend
if [ "$FAIL" -ne 0 ]; then
  echo "FAST_RUNTIME_GATE=FAIL (foreign process on a target port; free the port and re-run)"
  exit 1
fi

step "backend on :$GOLDEN_BACKEND_PORT (owned or started by this run)"
if health_on_port "$GOLDEN_BACKEND_PORT" "http://127.0.0.1:$GOLDEN_BACKEND_PORT/health"; then
  BE_PID="$(owned_listener "$GOLDEN_BACKEND_PORT" "$ROOT/apps/backend")" || true
  if [ -n "$BE_PID" ]; then
    rec BACKEND PASS
  else
    echo "BACKEND=FAIL (healthy listener on :$GOLDEN_BACKEND_PORT is not owned by this repository)"
    FAIL=1
  fi
else
  (cd "$ROOT/apps/backend" && \
    HFM_DATABASE_URL="$DB_URL" \
    nohup .venv/bin/python -m uvicorn hfm.main:app --host 127.0.0.1 --port "$GOLDEN_BACKEND_PORT" >/tmp/cf01-fast-backend.log 2>&1) &
  for i in $(seq 1 30); do
    if health_on_port "$GOLDEN_BACKEND_PORT" "http://127.0.0.1:$GOLDEN_BACKEND_PORT/health"; then break; fi
    sleep 1
  done
  if ! health_on_port "$GOLDEN_BACKEND_PORT" "http://127.0.0.1:$GOLDEN_BACKEND_PORT/health"; then
    echo "BACKEND=FAIL"; tail -20 /tmp/cf01-fast-backend.log; FAIL=1
  else
    BE_PID="$(owned_listener "$GOLDEN_BACKEND_PORT" "$ROOT/apps/backend")" || true
    [ -n "$BE_PID" ] && rec BACKEND PASS || { echo "BACKEND=FAIL (ownership unverifiable)"; FAIL=1; }
  fi
fi

step "frontend on :$GOLDEN_FRONTEND_PORT (owned or started by this run)"
if health_on_port "$GOLDEN_FRONTEND_PORT" "http://localhost:$GOLDEN_FRONTEND_PORT/"; then
  FE_PID="$(owned_listener "$GOLDEN_FRONTEND_PORT" "$ROOT/apps/frontend")" || true
  if [ -n "$FE_PID" ]; then
    rec FRONTEND PASS
  else
    echo "FRONTEND=FAIL (healthy listener on :$GOLDEN_FRONTEND_PORT is not owned by this repository)"
    FAIL=1
  fi
else
  (cd "$ROOT/apps/frontend" && pnpm dev --port "$GOLDEN_FRONTEND_PORT" --strictPort >/tmp/cf01-fast-frontend.log 2>&1) &
  for i in $(seq 1 30); do
    if health_on_port "$GOLDEN_FRONTEND_PORT" "http://localhost:$GOLDEN_FRONTEND_PORT/"; then break; fi
    sleep 1
  done
  if ! health_on_port "$GOLDEN_FRONTEND_PORT" "http://localhost:$GOLDEN_FRONTEND_PORT/"; then
    echo "FRONTEND=FAIL"; tail -20 /tmp/cf01-fast-frontend.log; FAIL=1
  else
    FE_PID="$(owned_listener "$GOLDEN_FRONTEND_PORT" "$ROOT/apps/frontend")" || true
    [ -n "$FE_PID" ] && rec FRONTEND PASS || { echo "FRONTEND=FAIL (ownership unverifiable)"; FAIL=1; }
  fi
fi

step "real browser golden journeys (no mock)"
if [ $FAIL -eq 0 ]; then
  if ! (cd "$ROOT/apps/frontend" && \
        CF01_BASE="http://localhost:$GOLDEN_FRONTEND_PORT" \
        pnpm exec playwright test e2e/golden-runtime.spec.ts >/tmp/cf01-fast-browser.log 2>&1); then
    echo "BROWSER=FAIL"; tail -40 /tmp/cf01-fast-browser.log; FAIL=1
  else rec BROWSER PASS; fi
fi

if [ $FAIL -eq 0 ]; then
  echo "FAST_RUNTIME_GATE=PASS"
else
  echo "FAST_RUNTIME_GATE=FAIL"
fi
exit $FAIL
