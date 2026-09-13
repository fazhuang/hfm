#!/usr/bin/env bash
# HFM ND-1 G7 — real-browser authentication evidence gate.
#
# Stable, repeatable, independent real-browser auth verification:
#   isolated PostgreSQL → alembic 0016 → initialize-production (first admin)
#   → admin API creates a STUDENT_RESEARCHER → real backend on :8000
#   (HFM_ENV=prod with valid inputs — also exercises the ND-1 B01 runtime
#   fail-closed PASS path) → Playwright-owned Vite → real Chromium runs
#   apps/frontend/e2e-auth/auth-evidence.spec.ts (NO route fulfillment).
#
# The frontend server is Playwright-owned (see the H01 port contract): the
# target frontend port must be free, Playwright launches with one coherent
# HFM_E2E_* contract, and the owned listener (PID/CWD/port/SHA) is verified
# while Playwright runs. Cleanup stops only this run's recorded children.
#
#   real-browser-auth-evidence.sh [--keep-db] [GOLDEN_DB_NAME] [GOLDEN_APP_PW]
# Output: G7_REAL_AUTH_EVIDENCE=PASS/FAIL (+ per-step lines).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND="$ROOT/apps/backend"
FRONTEND="$ROOT/apps/frontend"
PYTHON="$BACKEND/.venv/bin/python"
FAIL=0
rec() { echo "$1=$2"; }
KEEP_DB=0
DB_NAME="${1:-hfm_g7_auth}"
APP_PW="${2:-g7-auth-pw}"
ADMIN_USER="g7-first-admin"
ADMIN_PW="G7Admin$(openssl rand -hex 8)"
RESEARCH_USER="nd1-researcher"
RESEARCH_PW="ResearcherPass!2026"
PGUSER="${PGUSER:-$(whoami)}"
DB_URL="postgresql+asyncpg://${PGUSER}@127.0.0.1:5432/${DB_NAME}"
BACKEND_PORT=8000
FE_PORT=5199

listener_pid() { lsof -nP -iTCP:"$1" -sTCP:LISTEN -t 2>/dev/null | head -1; }
pid_cwd() { lsof -a -p "$1" -d cwd -Fn 2>/dev/null | sed -n 's/^n//p' | head -1; }
pid_has_env() {
  local pid="$1" token="$2"
  if ps eww -p "$pid" -o command= 2>/dev/null | grep -qF "$token"; then return 0; fi
  return 1
}
child_alive() {
  local s
  s="$(ps -o stat= -p "$1" 2>/dev/null | tr -d ' ')"
  [[ -n "$s" && "$s" != "Z" ]]
}
kill_owned() { # PID PREFIX
  local pid="$1" prefix="$2" cwd
  [[ -n "$pid" ]] || return 0
  cwd="$(pid_cwd "$pid")" || true
  case "$cwd" in
    "$prefix"*) kill "$pid" 2>/dev/null || true ;;
  esac
}

SOURCE_SHA="$(git -C "$ROOT" rev-parse HEAD 2>/dev/null || true)"
BE_PID=""
PW_PID=""
FE_PID=""

cleanup() {
  if [ -n "${PW_PID:-}" ] && child_alive "$PW_PID"; then kill "$PW_PID" 2>/dev/null || true; fi
  kill_owned "${FE_PID:-}" "$FRONTEND"
  kill_owned "${BE_PID:-}" "$BACKEND"
  if [ "$KEEP_DB" -eq 0 ]; then
    dropdb -h 127.0.0.1 -U "$PGUSER" --if-exists "$DB_NAME" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

rec HARNESS_SOURCE_SHA "$SOURCE_SHA"

# ---- preconditions: ports free, PostgreSQL reachable ---------------------
for p in "$BACKEND_PORT" "$FE_PORT"; do
  if [ -n "$(listener_pid "$p")" ]; then
    echo "G7=FAIL (port $p occupied; free it and re-run)"
    exit 1
  fi
done
if ! pg_isready -h 127.0.0.1 -q; then echo "G7=FAIL (PostgreSQL unreachable)"; exit 1; fi

# ---- isolated database at 0016 -------------------------------------------
dropdb -h 127.0.0.1 -U "$PGUSER" --if-exists "$DB_NAME" >/dev/null 2>&1 || true
createdb -h 127.0.0.1 -U "$PGUSER" "$DB_NAME"
export HFM_DATABASE_URL="$DB_URL"
if ! (cd "$BACKEND" && HFM_DATABASE_URL="$DB_URL" "$PYTHON" -m alembic -c alembic.ini upgrade head >/tmp/g7-alembic.log 2>&1); then
  echo "G7=FAIL (migration)"; tail -5 /tmp/g7-alembic.log; exit 1
fi
rec MIGRATION PASS

# ---- first admin (B03 initializer) --------------------------------------
# WR00-B2-R1: the PRODUCTION bootstrap binds the single canonical database
# (hfm_prod); this harness bootstraps an ISOLATED scratch database, so it
# runs the initializer in the documented test-only mode (--test-mode) against
# HFM_ENV=test. The backend runtime below still runs as HFM_ENV=prod (the
# application runtime fail-closed path is exercised separately); the
# bootstrap DB allowlist is proven by scripts/tests/test_production_db_allowlist.py.
ADMIN_ENV="$(mktemp)"
cat >"$ADMIN_ENV" <<ENV
HFM_ENV=test
HFM_DATABASE_URL=$DB_URL
HFM_TOKEN_SECRET=$(openssl rand -hex 24)
HFM_ADMIN_USERNAME=$ADMIN_USER
HFM_ADMIN_PASSWORD=$ADMIN_PW
ENV
if ! "$PYTHON" "$ROOT/scripts/initialize-production.py" --test-mode --env-file "$ADMIN_ENV" | grep -q "INITIALIZE_PRODUCTION=PASS"; then
  echo "G7=FAIL (first admin initialization)"
  rm -f "$ADMIN_ENV"
  exit 1
fi
rm -f "$ADMIN_ENV"
rec BOOTSTRAP PASS

# ---- backend on :8000 with PROD runtime env (valid) -----------------------
(cd "$BACKEND" && exec \
  env HFM_ENV=prod HFM_DATABASE_URL="$DB_URL" HFM_TOKEN_SECRET="$(openssl rand -hex 24)" HFM_TARGET_SHA="$SOURCE_SHA" \
  nohup "$PYTHON" -m uvicorn hfm.main:app --host 127.0.0.1 --port "$BACKEND_PORT" >/tmp/g7-backend.log 2>&1) &
BE_PID=$!
for _ in $(seq 1 30); do
  curl -sf "http://127.0.0.1:$BACKEND_PORT/health" >/dev/null 2>&1 && break
  sleep 1
done
if ! curl -sf "http://127.0.0.1:$BACKEND_PORT/health" >/dev/null 2>&1; then
  echo "G7=FAIL (backend did not start; prod fail-closed runtime passed)"; tail -10 /tmp/g7-backend.log; exit 1
fi
rec BACKEND PASS

# ---- create the student researcher via the admin API (real chain) ----------
ADMIN_LOGIN="$(curl -s -X POST "http://127.0.0.1:$BACKEND_PORT/api/v1/auth/login" \
  -H 'Content-Type: application/json' \
  -d "{\"username\":\"$ADMIN_USER\",\"password\":\"$ADMIN_PW\"}")"
ADMIN_TOKEN="$(printf '%s' "$ADMIN_LOGIN" | "$PYTHON" -c 'import json,sys;print(json.load(sys.stdin)["data"]["token"])')"
CREATE="$(curl -s -X POST "http://127.0.0.1:$BACKEND_PORT/api/v1/admin/users" \
  -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d "{\"username\":\"$RESEARCH_USER\",\"password\":\"$RESEARCH_PW\",\"role\":\"STUDENT_RESEARCHER\"}")"
if ! printf '%s' "$CREATE" | grep -q '"ok":true'; then
  echo "G7=FAIL (could not create researcher via admin API)"; printf '%s' "$CREATE"; exit 1
fi
rec RESEARCHER_SEED PASS

# ---- Playwright-owned frontend + real browser auth journeys ----------------
(cd "$FRONTEND" && \
  HFM_E2E_PORT="$FE_PORT" \
  HFM_E2E_BASE="http://localhost:$FE_PORT" \
  HFM_E2E_TARGET_SHA="$SOURCE_SHA" \
  pnpm exec playwright test -c playwright.real-auth.config.ts >/tmp/g7-browser.log 2>&1) &
PW_PID=$!
FE_PID=""
for _ in $(seq 1 90); do
  pid="$(listener_pid "$FE_PORT")" || true
  if [ -n "$pid" ] && pid_has_env "$pid" "HFM_TARGET_SHA=$SOURCE_SHA"; then
    FE_PID="$pid"
    rec HARNESS_FRONTEND_TARGET_SHA "PASS (pid=$pid port=$FE_PORT cwd=$FRONTEND sha=$SOURCE_SHA)"
    break
  fi
  child_alive "$PW_PID" || break
  sleep 1
done
pw_exit=0
wait "$PW_PID" 2>/dev/null || pw_exit=$?
PW_PID=""
if [ -z "$FE_PID" ]; then
  echo "G7=FAIL (frontend listener not verified while Playwright ran)"
  exit 1
fi
if [ "$pw_exit" -ne 0 ]; then
  echo "G7=FAIL (browser run exit=$pw_exit)"; tail -40 /tmp/g7-browser.log
  exit 1
fi
if grep -q "G7_REAL_AUTH=pass" /tmp/g7-browser.log; then
  rec AUTH_BROWSER_FLOW PASS
  grep -E "G7_REAL_AUTH=|passed|failed" /tmp/g7-browser.log | tail -3
  echo "G7_REAL_AUTH_EVIDENCE=PASS"
  exit 0
fi
echo "G7=FAIL (auth evidence marker missing)"; tail -30 /tmp/g7-browser.log
exit 1
