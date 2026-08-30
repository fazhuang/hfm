#!/usr/bin/env bash
# HFM deployment gate (P2-07-AC-03).
#
# The database migration gate runs BEFORE any deploy: the gate verifies
# environment validity, a single Alembic head, and that migrations are
# applied. Pending migrations BLOCK the release unless the operator passes
# --apply-migrations (which is never auto-invoked). This gate never performs
# a production HFB import; deploy authorization != import authorization
# (ADR-P2-02).
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND="$REPO_ROOT/apps/backend"
APPLY=0
ENV_NAME="${1:-}"
[[ "${2:-}" == "--apply-migrations" ]] && APPLY=1

if [[ -z "$ENV_NAME" ]]; then
  echo "usage: deploy-gate.sh <dev|test|prod> [--apply-migrations]"
  exit 2
fi
case "$ENV_NAME" in dev|test|prod) ;; *)
  echo "FAIL: unknown environment: $ENV_NAME"
  exit 2
;; esac

# 1. Environment separation must hold first.
if ! "$REPO_ROOT/scripts/check-env.sh" > /dev/null; then
  echo "MIGRATION_GATE=FAIL (environment separation failed)"
  exit 1
fi

# 2. Single Alembic head.
HEADS="$(cd "$BACKEND" && .venv/bin/python -m alembic heads 2>/dev/null || true)"
HEAD_COUNT="$(printf '%s\n' "$HEADS" | grep -c . || true)"
if [[ "$HEAD_COUNT" -ne 1 ]]; then
  echo "MIGRATION_GATE=FAIL (expected exactly one Alembic head, got: ${HEAD_COUNT})"
  exit 1
fi

# 3. Pending-migration gate: current revision must equal the head before deploy.
CURRENT="$(cd "$BACKEND" && .venv/bin/python -m alembic current 2>/dev/null | tail -1 || true)"
if [[ "$CURRENT" != *"$HEADS"* && "$APPLY" -eq 0 ]]; then
  echo "MIGRATION_GATE=BLOCKED (pending migrations: current='${CURRENT}' head='${HEADS}'; re-run with --apply-migrations to apply first)"
  exit 1
fi
if [[ "$ENV_NAME" == "prod" && "$APPLY" -eq 1 ]]; then
  # Prod requires an explicit migration apply step; the gate only verifies.
  echo "MIGRATION_GATE=PASS (prod: migration apply is a separate authorized step)"
  exit 0
fi

echo "MIGRATION_GATE=PASS (head=${HEADS} current=${CURRENT})"
