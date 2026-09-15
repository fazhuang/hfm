#!/usr/bin/env bash
# HFM ND-1 — DATABASE DEPENDENCY PROBE (post-start, repeatable)
#
# Minimal operational probe proving a real database dependency, not just an
# HTTP process: given a live API base and a target DSN it (1) confirms the
# process answers /health, then (2) performs a read-only Alembic revision
# check against the target database. A process that is UP while its database
# is unreachable (or not at the expected revision) is detected as FAIL.
#
#   database-dependency-probe.sh --api-base URL --db-url DSN
#       [--backend-dir DIR] [--expected-head 0017]
#
# Output lines: PROBE_PROCESS=UP|DOWN, PROBE_DATABASE=OK|FAIL, PROBE_RESULT=PASS|FAIL.
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="$REPO_ROOT/apps/backend/.venv/bin/python"
API_BASE=""
DB_URL=""
BACKEND_DIR="$REPO_ROOT/apps/backend"
EXPECTED_HEAD="0017"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --api-base) API_BASE="${2:-}"; shift ;;
    --db-url) DB_URL="${2:-}"; shift ;;
    --backend-dir) BACKEND_DIR="${2:-}"; shift ;;
    --expected-head) EXPECTED_HEAD="${2:-}"; shift ;;
    *) echo "usage: database-dependency-probe.sh --api-base URL --db-url DSN"; exit 2 ;;
  esac
  shift
done
[[ -n "$API_BASE" && -n "$DB_URL" ]] || { echo "usage: database-dependency-probe.sh --api-base URL --db-url DSN"; exit 2; }

# 1. Process dependency: the API base must answer (process is up).
if curl -sf --max-time 5 "$API_BASE/health" >/dev/null 2>&1; then
  echo "PROBE_PROCESS=UP"
else
  echo "PROBE_PROCESS=DOWN"
  echo "PROBE_DATABASE=UNKNOWN"
  echo "PROBE_RESULT=FAIL"
  exit 1
fi

# 2. Database dependency: read-only exact-revision check (never writes).
if HFM_DATABASE_URL="$DB_URL" PYTHONPATH="$BACKEND_DIR/src" \
    "$PYTHON" - "$EXPECTED_HEAD" <<'PY' >/tmp/hfm-dbprobe.log 2>&1
import asyncio, sys
from pathlib import Path

async def main() -> int:
    import os
    from sqlalchemy.ext.asyncio import create_async_engine
    from sqlalchemy import text

    expected = sys.argv[1]
    engine = create_async_engine(os.environ["HFM_DATABASE_URL"])
    try:
        async with engine.connect() as conn:
            row = (await conn.execute(text("SELECT version_num FROM alembic_version"))).scalar_one()
        return 0 if str(row) == expected else 1
    finally:
        await engine.dispose()

sys.exit(asyncio.run(main()))
PY
then
  echo "PROBE_DATABASE=OK (revision $EXPECTED_HEAD)"
  echo "PROBE_RESULT=PASS"
  exit 0
else
  echo "PROBE_DATABASE=FAIL (unreachable or not at revision $EXPECTED_HEAD)"
  echo "PROBE_RESULT=FAIL"
  exit 1
fi
