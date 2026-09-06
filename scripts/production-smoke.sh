#!/usr/bin/env bash
# HFM production smoke check (ND-1 B04).
#
# Operator-run smoke against a LIVE release before/after deploy:
#   1. environment preflight (scripts/validate-production-env.py, redacted);
#   2. exact migration state (current == head == 0014, read-only);
#   3. backend health/live endpoints through the same-origin /api;
#   4. persistent media volume exists and is writable by the service user.
#
#   production-smoke.sh --check-args    # input validation only (no network)
#   production-smoke.sh --api-base URL  # real smoke against a live release
#
# ND2_EXECUTION_REQUIRED: the live run happens against the real target during
# ND-2; ND-1 ships the procedure and its input validation.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="$REPO_ROOT/apps/backend/.venv/bin/python"
API_BASE="http://127.0.0.1:8000"
CHECK_ARGS=0
MEDIA_ROOT="${HFM_MEDIA_ROOT:-/var/lib/hfm/media}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --check-args) CHECK_ARGS=1 ;;
    --api-base) API_BASE="${2:-}"; shift ;;
    *) echo "usage: production-smoke.sh [--check-args] [--api-base URL]"; exit 2 ;;
  esac
  shift
done

# 1 + 2. Environment + exact migration preflight (redacted, read-only).
# --check-args mode validates the environment inputs only (no DB contact);
# the real smoke also verifies the exact migration state against the DB.
VALIDATOR_ARGS=(--env prod)
if [[ "$CHECK_ARGS" -eq 0 ]]; then
  VALIDATOR_ARGS+=(--verify-migration --backend-dir "$REPO_ROOT/apps/backend")
fi
if ! "$PYTHON" "$REPO_ROOT/scripts/validate-production-env.py" "${VALIDATOR_ARGS[@]}"; then
  echo "SMOKE_ENV_MIGRATION=FAIL"
  exit 1
fi
if [[ "$CHECK_ARGS" -eq 1 ]]; then
  echo "SMOKE_ENV=PASS (input validation only — no live endpoints or DB contacted)"
  echo "PRODUCTION_SMOKE=PASS"
  exit 0
fi
echo "SMOKE_ENV_MIGRATION=PASS"

# 4. Persistent media volume.
if [[ ! -d "$MEDIA_ROOT" ]]; then
  echo "SMOKE_MEDIA=FAIL (missing volume: $MEDIA_ROOT)"
  exit 1
fi
if [[ ! -w "$MEDIA_ROOT" ]]; then
  echo "SMOKE_MEDIA=FAIL (volume not writable by the service user)"
  exit 1
fi
echo "SMOKE_MEDIA=PASS ($MEDIA_ROOT)"

# 3. Live backend endpoints through the same-origin /api.
for endpoint in health "api/v1/system/version"; do
  code="$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 "$API_BASE/$endpoint" || true)"
  if [[ "$code" != "200" ]]; then
    echo "SMOKE_API=FAIL ($endpoint -> HTTP $code)"
    exit 1
  fi
done
echo "SMOKE_API=PASS (health + version at $API_BASE)"
echo "PRODUCTION_SMOKE=PASS"
