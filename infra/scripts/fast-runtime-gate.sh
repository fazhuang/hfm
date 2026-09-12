#!/usr/bin/env bash
# HFM CLEAN FORWARD CF-01 — FAST_RUNTIME_GATE
# (ND-1 H01 + RV-01 hardened; ND1-H01-GOLDEN-PORT-CONTRACT)
#
# Daily regression: real backend + real frontend + real browser, NO mock.
# Reuses the current database (does NOT create a fresh disposable one) — use
# FULL_GOLDEN_GATE for fresh-DB + migration + bootstrap verification.
#
#   FAST_RUNTIME_GATE = real DB (existing) + real /api proxy + real browser
#
# FRONTEND OWNERSHIP MODEL (ND1-H01-GOLDEN-PORT-CONTRACT): identical to the
# golden gate — the gate never pre-starts the frontend. Playwright is the
# single frontend-server owner: its webServer launches the repository Vite
# on GOLDEN_FRONTEND_PORT (reuseExistingServer:false + strictPort +
# HFM_TARGET_SHA). The gate requires the port to be free BEFORE launch
# (foreign/stale occupant fails closed and is never killed), launches
# Playwright as a recorded child with one coherent contract
# (HFM_E2E_PORT == HFM_E2E_BASE == CF01_BASE ==
# http://localhost:GOLDEN_FRONTEND_PORT, HFM_E2E_TARGET_SHA == SOURCE_SHA),
# and verifies the owned listener (PID/CWD/port/SHA) while Playwright runs,
# emitting HARNESS_FRONTEND_TARGET_SHA only after the check passes. If
# Playwright exits before the listener is verified the gate fails. Cleanup
# stops only the recorded Playwright child and its verified child resources.
#
# The BACKEND stays gate-managed: reuse is allowed ONLY when the listener is
# owned (cwd under this repo) AND its env carries HFM_TARGET_SHA == current
# source SHA; stale/foreign occupants fail closed and are never killed.
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
PW_PID=""
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
child_alive() { # PID — true while the child exists and is not a zombie.
  local s
  s="$(ps -o stat= -p "$1" 2>/dev/null | tr -d ' ')"
  [[ -n "$s" && "$s" != "Z" ]]
}

owned_listener() {
  local pid cwd
  pid="$(listener_pid "$1")" || true
  [[ -z "$pid" ]] && return 0
  cwd="$(pid_cwd "$pid")" || true
  case "$cwd" in
    "$2"*) echo "$pid" ;;
  esac
}

health_on_port() { curl -sf --max-time 3 "$2" >/dev/null 2>&1; }

# backend_status OUTVAR — sets OUTVAR to "free" | "reuse <pid>" | "stale" |
# "foreign"; diagnostics to stdout; FAIL recorded for stale/foreign.
backend_status() {
  local outvar="$1" pid cwd
  pid="$(listener_pid "$GOLDEN_BACKEND_PORT")" || true
  [[ -z "$pid" ]] && { printf -v "$outvar" "%s" "free"; return 0; }
  cwd="$(pid_cwd "$pid")" || true
  case "$cwd" in
    "$ROOT/apps/backend"*) ;;
    *)
      echo "HARNESS_FOREIGN_OWNER=FAIL kind=backend port=$GOLDEN_BACKEND_PORT pid=$pid cwd=${cwd:-<unknown>}"
      FAIL=1
      printf -v "$outvar" "%s" "foreign"
      return 0
      ;;
  esac
  if pid_has_env "$pid" "HFM_TARGET_SHA=$SOURCE_SHA"; then
    printf -v "$outvar" "%s" "reuse $pid"
  else
    echo "HARNESS_TARGET_SHA=FAIL kind=backend port=$GOLDEN_BACKEND_PORT pid=$pid expected=$SOURCE_SHA (stale or unverified process; free the port and re-run)"
    FAIL=1
    printf -v "$outvar" "%s" "stale"
  fi
  return 0
}

# frontend_must_be_free — Playwright owns the frontend; any occupant is FAIL.
frontend_must_be_free() {
  local pid cwd
  pid="$(listener_pid "$GOLDEN_FRONTEND_PORT")" || true
  [[ -z "$pid" ]] && return 0
  cwd="$(pid_cwd "$pid")" || true
  case "$cwd" in
    "$ROOT/apps/frontend"*)
      echo "HARNESS_STALE_OWNER=FAIL kind=frontend port=$GOLDEN_FRONTEND_PORT pid=$pid (Playwright owns the frontend; free the port and re-run)"
      ;;
    *)
      echo "HARNESS_FOREIGN_OWNER=FAIL kind=frontend port=$GOLDEN_FRONTEND_PORT pid=$pid cwd=${cwd:-<unknown>}"
      ;;
  esac
  FAIL=1
  return 1
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
}
trap cleanup EXIT

rec HARNESS_SOURCE_SHA "$SOURCE_SHA"

# Pre-classify the backend; require the frontend port to be free for the
# Playwright-owned Vite. Bail before any server/navigation on stale/foreign.
BACKEND_STATUS=""
backend_status BACKEND_STATUS
frontend_must_be_free
if [ "$FAIL" -ne 0 ]; then
  echo "FAST_RUNTIME_GATE=FAIL (backend foreign/stale or frontend port occupied; free the port and re-run)"
  exit 1
fi

step "backend on :$GOLDEN_BACKEND_PORT"
if [[ "$BACKEND_STATUS" == "free" ]]; then
  # Deterministic child: exec chain keeps one PID, so $! is the server PID.
  (cd "$ROOT/apps/backend" && exec \
    env HFM_DATABASE_URL="$DB_URL" HFM_TARGET_SHA="$SOURCE_SHA" \
    nohup "$ROOT/apps/backend/.venv/bin/python" -m uvicorn hfm.main:app \
      --host 127.0.0.1 --port "$GOLDEN_BACKEND_PORT" >/tmp/cf01-fast-backend.log 2>&1) &
  BE_PID=$!
  for _ in $(seq 1 30); do
    if health_on_port "$GOLDEN_BACKEND_PORT" "http://127.0.0.1:$GOLDEN_BACKEND_PORT/health"; then break; fi
    sleep 1
  done
  if ! health_on_port "$GOLDEN_BACKEND_PORT" "http://127.0.0.1:$GOLDEN_BACKEND_PORT/health"; then
    echo "BACKEND=FAIL"; tail -20 /tmp/cf01-fast-backend.log; FAIL=1
  elif ! pid_has_env "$BE_PID" "HFM_TARGET_SHA=$SOURCE_SHA"; then
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
else
  BE_PID="${BACKEND_STATUS#reuse }"
  rec BACKEND PASS
  rec HARNESS_BACKEND_TARGET_SHA "MATCH ($SOURCE_SHA)"
fi

# run_playwright_owned_frontend LOG — Playwright is the single frontend
# owner; verified while running (see golden-runtime-gate.sh for semantics).
run_playwright_owned_frontend() {
  local log="$1" pid found="" pw_exit
  occupant="$(listener_pid "$GOLDEN_FRONTEND_PORT")" || true
  if [ -n "$occupant" ]; then
    echo "HARNESS_FOREIGN_OWNER=FAIL kind=frontend port=$GOLDEN_FRONTEND_PORT pid=$occupant (port became occupied before launch)"
    FAIL=1
    return 1
  fi
  (
    cd "$ROOT/apps/frontend" && \
    HFM_E2E_PORT="$GOLDEN_FRONTEND_PORT" \
    HFM_E2E_BASE="http://localhost:$GOLDEN_FRONTEND_PORT" \
    HFM_E2E_TARGET_SHA="$SOURCE_SHA" \
    CF01_BASE="http://localhost:$GOLDEN_FRONTEND_PORT" \
    pnpm exec playwright test e2e/golden-runtime.spec.ts
  ) >"$log" 2>&1 &
  PW_PID=$!
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

step "real browser golden journeys — Playwright-owned Vite (no mock)"
if [ $FAIL -eq 0 ]; then
  run_playwright_owned_frontend /tmp/cf01-fast-browser.log
fi

if [ $FAIL -eq 0 ]; then
  echo "FAST_RUNTIME_GATE=PASS"
else
  echo "FAST_RUNTIME_GATE=FAIL"
fi
exit $FAIL
