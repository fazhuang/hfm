#!/usr/bin/env bash
# HFM CLEAN FORWARD CF-01 — FAST_RUNTIME_GATE (ND-1 H01 + RV-01 hardened)
#
# Daily regression: real backend + real frontend + real browser, NO mock.
# Reuses the current database (does NOT create a fresh disposable one) — use
# FULL_GOLDEN_GATE for fresh-DB + migration + bootstrap verification.
#
#   FAST_RUNTIME_GATE = real DB (existing) + real /api proxy + real browser
#
# ND-1 H01 + RV-01 (test-harness hardening): each target port is classified
# BEFORE any reuse or navigation:
#   free     → this run starts its own server (env HFM_TARGET_SHA=SOURCE_SHA),
#              verified after startup;
#   owned    → reused ONLY when the listener PID's cwd is this repository AND
#              its process environment carries HFM_TARGET_SHA == SOURCE_SHA;
#   stale    → same-CWD process without the current SHA: FAIL (never reused);
#   foreign  → process outside this repository: FAIL (never reused).
# Foreign/stale processes are NEVER killed; cleanup stops only recorded PIDs
# owned by this run.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
FAIL=0
rec() { echo "$1=$2"; }
step() { echo "\n==> $*"; }

: "${HFM_DATABASE_URL:?set HFM_DATABASE_URL for FAST_RUNTIME_GATE}"
GOLDEN_BACKEND_PORT="${GOLDEN_BACKEND_PORT:-8000}"
GOLDEN_FRONTEND_PORT="${GOLDEN_FRONTEND_PORT:-5199}"
DB_URL="$HFM_DATABASE_URL"
SOURCE_SHA="$(git -C "$ROOT" rev-parse HEAD 2>/dev/null || true)"
BE_PID=""
FE_PID=""

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

# port_status PORT KIND DIRPREFIX OUTVAR — sets OUTVAR to "free" |
# "reuse <pid>" | "stale <pid>" | "foreign <pid>"; diagnostics go to stdout
# and FAIL is recorded for stale/foreign (never reused, never killed).
port_status() {
  local port="$1" kind="$2" dirprefix="$3" outvar="$4"
  local pid cwd token
  pid="$(listener_pid "$port")" || true
  [[ -z "$pid" ]] && { printf -v "$outvar" "%s" "free"; return 0; }
  cwd="$(pid_cwd "$pid")" || true
  case "$cwd" in
    "$dirprefix"*) ;;
    *)
      echo "HARNESS_FOREIGN_OWNER=FAIL kind=$kind port=$port pid=$pid cwd=${cwd:-<unknown>}"
      FAIL=1
      printf -v "$outvar" "%s" "foreign $pid"
      return 0
      ;;
  esac
  token="HFM_TARGET_SHA=$SOURCE_SHA"
  if pid_has_env "$pid" "$token"; then
    printf -v "$outvar" "%s" "reuse $pid"
  else
    echo "HARNESS_TARGET_SHA=FAIL kind=$kind port=$port pid=$pid expected=$SOURCE_SHA (stale or unverified process; free the port and re-run)"
    FAIL=1
    printf -v "$outvar" "%s" "stale $pid"
  fi
  return 0
}

health_on_port() { curl -sf --max-time 3 "$2" >/dev/null 2>&1; }

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

rec HARNESS_SOURCE_SHA "$SOURCE_SHA"

# Pre-classify both ports; bail before any server/navigation when either is
# stale or foreign (never reused, never killed).
BACKEND_STATUS=""
FRONTEND_STATUS=""
port_status "$GOLDEN_BACKEND_PORT" backend "$ROOT/apps/backend" BACKEND_STATUS
port_status "$GOLDEN_FRONTEND_PORT" frontend "$ROOT/apps/frontend" FRONTEND_STATUS
if [ "$FAIL" -ne 0 ]; then
  echo "FAST_RUNTIME_GATE=FAIL (target port occupied by a foreign or stale process; free the port and re-run)"
  exit 1
fi
case "$BACKEND_STATUS" in free|reuse*) ;; *) echo "FAST_RUNTIME_GATE=FAIL"; exit 1 ;; esac
case "$FRONTEND_STATUS" in free|reuse*) ;; *) echo "FAST_RUNTIME_GATE=FAIL"; exit 1 ;; esac

step "backend on :$GOLDEN_BACKEND_PORT"
if [[ "$BACKEND_STATUS" == "free" ]]; then
  (cd "$ROOT/apps/backend" && \
    HFM_DATABASE_URL="$DB_URL" HFM_TARGET_SHA="$SOURCE_SHA" \
    nohup .venv/bin/python -m uvicorn hfm.main:app --host 127.0.0.1 --port "$GOLDEN_BACKEND_PORT" >/tmp/cf01-fast-backend.log 2>&1) &
  for _ in $(seq 1 30); do
    if health_on_port "$GOLDEN_BACKEND_PORT" "http://127.0.0.1:$GOLDEN_BACKEND_PORT/health"; then break; fi
    sleep 1
  done
  if ! health_on_port "$GOLDEN_BACKEND_PORT" "http://127.0.0.1:$GOLDEN_BACKEND_PORT/health"; then
    echo "BACKEND=FAIL"; tail -20 /tmp/cf01-fast-backend.log; FAIL=1
  else
    BE_PID="$(listener_pid "$GOLDEN_BACKEND_PORT")" || true
    if [ -n "$BE_PID" ] && pid_has_env "$BE_PID" "HFM_TARGET_SHA=$SOURCE_SHA"; then
      rec BACKEND PASS
      rec HARNESS_BACKEND_TARGET_SHA "PASS ($SOURCE_SHA)"
    else
      echo "BACKEND=FAIL (ownership/SHA unverifiable on :$GOLDEN_BACKEND_PORT)"
      BE_PID=""
      FAIL=1
    fi
  fi
else
  BE_PID="${BACKEND_STATUS#reuse }"
  rec BACKEND PASS
  rec HARNESS_BACKEND_TARGET_SHA "MATCH ($SOURCE_SHA)"
fi

step "frontend on :$GOLDEN_FRONTEND_PORT"
if [[ "$FRONTEND_STATUS" == "free" ]]; then
  (cd "$ROOT/apps/frontend" && HFM_TARGET_SHA="$SOURCE_SHA" pnpm dev --port "$GOLDEN_FRONTEND_PORT" --strictPort >/tmp/cf01-fast-frontend.log 2>&1) &
  for _ in $(seq 1 30); do
    if health_on_port "$GOLDEN_FRONTEND_PORT" "http://localhost:$GOLDEN_FRONTEND_PORT/"; then break; fi
    sleep 1
  done
  if ! health_on_port "$GOLDEN_FRONTEND_PORT" "http://localhost:$GOLDEN_FRONTEND_PORT/"; then
    echo "FRONTEND=FAIL"; tail -20 /tmp/cf01-fast-frontend.log; FAIL=1
  else
    FE_PID="$(listener_pid "$GOLDEN_FRONTEND_PORT")" || true
    if [ -n "$FE_PID" ] && pid_has_env "$FE_PID" "HFM_TARGET_SHA=$SOURCE_SHA"; then
      rec FRONTEND PASS
      rec HARNESS_FRONTEND_TARGET_SHA "PASS ($SOURCE_SHA)"
    else
      echo "FRONTEND=FAIL (ownership/SHA unverifiable on :$GOLDEN_FRONTEND_PORT)"
      FE_PID=""
      FAIL=1
    fi
  fi
else
  FE_PID="${FRONTEND_STATUS#reuse }"
  rec FRONTEND PASS
  rec HARNESS_FRONTEND_TARGET_SHA "MATCH ($SOURCE_SHA)"
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
