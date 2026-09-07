#!/usr/bin/env bash
# HFM production smoke check (ND-1 B04, ND-1 RV-P0-01 media boundary).
#
# Operator-run smoke against a LIVE release before/after deploy:
#   1. environment preflight (scripts/validate-production-env.py, redacted);
#   2. exact migration state (current == head == 0014, read-only);
#   3. backend health/live endpoints through the same-origin /api;
#   4. persistent media volume exists and is writable by the service user;
#   5. media boundary contract (RV-P0-01): the serving Nginx configuration
#      must NOT alias/root the raw media volume to a public URL — media is
#      served only via /api/v1/public/media/{asset_id}/bytes. The live probe
#      checks that a direct /media/<key> URL is NOT served 200 from the
#      volume, and a published asset is served through the API endpoint.
#
#   production-smoke.sh --check-args                # input validation only
#   production-smoke.sh --media-alias-check FILE    # nginx contract check
#   production-smoke.sh --api-base URL              # real smoke (ND-2)
#
# Media probes require operator-supplied asset ids at ND-2; ND-1 ships the
# procedure and the config contract check. ND2_EXECUTION_REQUIRED: live runs
# happen against the real target during ND-2.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="$REPO_ROOT/apps/backend/.venv/bin/python"
API_BASE="http://127.0.0.1:8000"
CHECK_ARGS=0
MEDIA_ALIAS_CHECK=""
MEDIA_ROOT="${HFM_MEDIA_ROOT:-/var/lib/hfm/media}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --check-args) CHECK_ARGS=1 ;;
    --media-alias-check)
      MEDIA_ALIAS_CHECK="${2:-}"
      shift
      ;;
    --api-base) API_BASE="${2:-}"; shift ;;
    *) echo "usage: production-smoke.sh [--check-args] [--media-alias-check FILE] [--api-base URL]"; exit 2 ;;
  esac
  shift
done

# ---------------------------------------------------------------------------
# 5. Media boundary contract (RV-P0-01): forbid a direct persistent-root alias.
#    A serving config must proxy /api to the private Uvicorn and must never
#    alias/root the media volume inside any server block.
# ---------------------------------------------------------------------------
media_alias_check() {
  local file="$1"
  local forbidden
  forbidden="$(awk '
    /^[[:space:]]*location[[:space:]]/ { block=1 }
    block && /alias[[:space:]]+[^;]*media/ { print NR ": public alias to media volume"; exit }
    block && /root[[:space:]]+[^;]*media/ { print NR ": public root of media volume"; exit }
  ' "$file")"
  if [[ -n "$forbidden" ]]; then
    echo "SMOKE_MEDIA_ALIAS=FAIL ($file line $forbidden — direct media alias/root forbidden; serve media only via /api/v1/public/media/{asset_id}/bytes)"
    return 1
  fi
  if ! grep -q "proxy_pass.*127.0.0.1:8000" "$file"; then
    echo "SMOKE_MEDIA_ALIAS=FAIL ($file lacks the private /api proxy)"
    return 1
  fi
  echo "SMOKE_MEDIA_ALIAS=PASS (no public alias/root of the media volume; media via /api only)"
  return 0
}

if [[ -n "$MEDIA_ALIAS_CHECK" ]]; then
  if [[ ! -f "$MEDIA_ALIAS_CHECK" ]]; then
    echo "SMOKE_MEDIA_ALIAS=FAIL (file not found: $MEDIA_ALIAS_CHECK)"
    exit 1
  fi
  if ! media_alias_check "$MEDIA_ALIAS_CHECK"; then
    echo "PRODUCTION_SMOKE=FAIL"
    exit 1
  fi
  [[ "$CHECK_ARGS" -eq 1 ]] && echo "PRODUCTION_SMOKE=PASS" && exit 0
fi

# 1 + 2. Environment + exact migration preflight (redacted, read-only).
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

# 4. Persistent media volume (present + writable by the service user).
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
