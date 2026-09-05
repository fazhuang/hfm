#!/usr/bin/env bash
# HFM CLEAN FORWARD CF-01 — FAST_RUNTIME_GATE
#
# Daily regression: real backend + real frontend + real browser, NO mock.
# Reuses the current database (does NOT create a fresh disposable one) — use
# FULL_GOLDEN_GATE for fresh-DB + migration + bootstrap verification.
#
#   FAST_RUNTIME_GATE  = real DB (existing) + real /api proxy + real browser
#                        (NO mocked API / no route fulfillment)
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
FAIL=0
rec() { echo "$1=$2"; }
step() { echo "\n==> $*"; }

: "${HFM_DATABASE_URL:?set HFM_DATABASE_URL for FAST_RUNTIME_GATE}"
GOLDEN_BACKEND_PORT="${GOLDEN_BACKEND_PORT:-8000}"
GOLDEN_FRONTEND_PORT="${GOLDEN_FRONTEND_PORT:-5199}"
DB_URL="$HFM_DATABASE_URL"

cleanup() {
  pkill -f "uvicorn hfm.main:app.*--port $GOLDEN_BACKEND_PORT" 2>/dev/null || true
  pkill -f "vite.*--port $GOLDEN_FRONTEND_PORT" 2>/dev/null || true
  if [ -n "${BE_PID:-}" ]; then kill "$BE_PID" 2>/dev/null || true; fi
  if [ -n "${FE_PID:-}" ]; then kill "$FE_PID" 2>/dev/null || true; fi
}
trap cleanup EXIT

step "start FastAPI backend (:$GOLDEN_BACKEND_PORT)"
if ! curl -sf "http://127.0.0.1:$GOLDEN_BACKEND_PORT/health" >/dev/null 2>&1; then
  (cd "$ROOT/apps/backend" && \
    HFM_DATABASE_URL="$DB_URL" \
    .venv/bin/python -m uvicorn hfm.main:app --host 127.0.0.1 --port "$GOLDEN_BACKEND_PORT" >/tmp/cf01-fast-backend.log 2>&1) &
  BE_PID=$!
  for i in $(seq 1 30); do
    if curl -sf "http://127.0.0.1:$GOLDEN_BACKEND_PORT/health" >/dev/null 2>&1; then break; fi
    sleep 1
  done
  if ! curl -sf "http://127.0.0.1:$GOLDEN_BACKEND_PORT/health" >/dev/null 2>&1; then
    echo "BACKEND=FAIL"; tail -20 /tmp/cf01-fast-backend.log; FAIL=1
  else rec BACKEND PASS; fi
else rec BACKEND PASS; fi

step "start Vite dev with real /api proxy (:$GOLDEN_FRONTEND_PORT)"
if ! curl -sf "http://127.0.0.1:$GOLDEN_FRONTEND_PORT/" >/dev/null 2>&1; then
  (cd "$ROOT/apps/frontend" && pnpm dev --port "$GOLDEN_FRONTEND_PORT" --strictPort >/tmp/cf01-fast-frontend.log 2>&1) &
  FE_PID=$!
  for i in $(seq 1 30); do
    if curl -sf "http://localhost:$GOLDEN_FRONTEND_PORT/" >/dev/null 2>&1; then break; fi
    sleep 1
  done
  if ! curl -sf "http://localhost:$GOLDEN_FRONTEND_PORT/" >/dev/null 2>&1; then
    echo "FRONTEND=FAIL"; tail -20 /tmp/cf01-fast-frontend.log; FAIL=1
  else rec FRONTEND PASS; fi
else rec FRONTEND PASS; fi

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
