#!/usr/bin/env bash
# HFM deployment gate (P2-07-AC-03, ND-1 B01 hardening).
#
# The preflight runs BEFORE any deploy and is fail-closed:
#   1. real HFM_* runtime inputs are validated (redacted) by
#      scripts/validate-production-env.py — missing/template/known-dev DB and
#      token-secret values are rejected without printing their values;
#   2. the exact Alembic current revision must equal the head (0014) with a
#      single head — verified read-only against the target database;
#   3. a database/command failure is a non-zero gate failure;
#   4. --apply-migrations can NEVER bypass verification: the preflight does
#      not apply a live migration (operators apply separately, then re-run the
#      gate). No production HFB import is ever performed (ADR-P2-02).
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND="$REPO_ROOT/apps/backend"
PYTHON="$BACKEND/.venv/bin/python"
ENV_NAME="${1:-}"
ENV_FILE=""
APPLY=0

shift || true
while [[ $# -gt 0 ]]; do
  case "$1" in
    --apply-migrations) APPLY=1 ;;
    --env-file)
      ENV_FILE="${2:-}"
      shift || true
      ;;
    *) echo "usage: deploy-gate.sh <dev|test|prod> [--env-file FILE] [--apply-migrations]"; exit 2 ;;
  esac
  shift || true
done

if [[ -z "$ENV_NAME" ]]; then
  echo "usage: deploy-gate.sh <dev|test|prod> [--env-file FILE] [--apply-migrations]"
  exit 2
fi
case "$ENV_NAME" in dev|test|prod) ;; *)
  echo "FAIL: unknown environment: $ENV_NAME"
  exit 2
;; esac

VALIDATOR_ARGS=(--env "$ENV_NAME" --verify-migration)
if [[ -n "$ENV_FILE" ]]; then
  if [[ ! -f "$ENV_FILE" ]]; then
    echo "ENV_FILE=FAIL (not found: $ENV_FILE)"
    exit 1
  fi
  VALIDATOR_ARGS+=(--env-file "$ENV_FILE")
fi
if [[ "$ENV_NAME" == "prod" ]]; then
  # --apply-migrations acknowledges that a separate, authorized migration
  # apply step may be required; it never skips the fail-closed verification.
  if [[ "$APPLY" -eq 1 ]]; then
    echo "MIGRATION_APPLY=ACKNOWLEDGED (operator runs alembic upgrade separately; gate still verifies)"
  fi
else
  # dev/test additionally tolerate SQLite test targets (read-only verification).
  VALIDATOR_ARGS+=(--allow-sqlite)
fi

if ! "$PYTHON" "$REPO_ROOT/scripts/validate-production-env.py" "${VALIDATOR_ARGS[@]}"; then
  echo "MIGRATION_GATE=FAIL (environment/migration preflight failed)"
  exit 1
fi

if [[ "$ENV_NAME" == "prod" ]]; then
  if [[ "$APPLY" -eq 0 ]]; then
    echo "MIGRATION_GATE=PASS (prod: preflight verified current == head == 0014; apply is a separate authorized step)"
  else
    echo "MIGRATION_GATE=PASS (prod: preflight verified current == head == 0014)"
  fi
else
  echo "MIGRATION_GATE=PASS (head=0014 current=0014 verified for $ENV_NAME)"
fi
exit 0
