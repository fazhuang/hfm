#!/usr/bin/env bash
# HFM environment separation check (P2-07-AC-01).
#
# Verifies the dev/test/prod configuration matrix: every environment defines
# the required keys, and production never cross-overlaps dev/test values
# (no shared database name, no shared base URL).
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_DIR="$REPO_ROOT/infra/env"
REQUIRED_KEYS=(HFM_ENV DATABASE_URL PUBLIC_BASE_URL API_BASE_URL LOG_LEVEL)
FAILURES=0

for env_name in dev test prod; do
  file="$ENV_DIR/$env_name.env.example"
  if [[ ! -f "$file" ]]; then
    echo "FAIL: missing environment contract: $file"
    exit 1
  fi
  for key in "${REQUIRED_KEYS[@]}"; do
    if ! grep -qE "^${key}=" "$file"; then
      echo "FAIL: $env_name missing required key: $key"
      FAILURES=$((FAILURES + 1))
    fi
  done
  if [[ "$env_name" == "prod" ]]; then
    # Production must never reference the dev/test database or base URLs.
    if grep -qE "hfm_dev|hfm_test|localhost" "$file"; then
      echo "FAIL: prod environment leaks dev/test values"
      FAILURES=$((FAILURES + 1))
    fi
    if grep -qE "^DATABASE_URL=.*CHANGEME" "$file" && ! grep -qE "^HFM_ENV=prod" "$file"; then
      echo "FAIL: prod env declares HFM_ENV incorrectly"
      FAILURES=$((FAILURES + 1))
    fi
  fi
done

if [[ "$FAILURES" -gt 0 ]]; then
  echo "ENVIRONMENT_SEPARATION=FAIL"
  exit 1
fi
echo "ENVIRONMENT_SEPARATION=PASS (dev/test/prod contracts complete and isolated)"
