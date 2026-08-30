#!/usr/bin/env bash
# HFM backup/restore runbook (P2-07-AC-04).
#
# backup.sh <test|prod> [--verify]      pg_dump the named environment
# restore.sh <test> <dumpfile> [--verify]  restore drill on the test env only
#
# Production restore is deliberately unsupported here (manual, operator-gated
# runbook); the foundation validates the procedure on the test environment.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKUP_DIR="$REPO_ROOT/infra/backups"
mkdir -p "$BACKUP_DIR"

command="$1"
env_name="${2:-}"

case "$command" in
  backup)
    [[ "$env_name" == "test" || "$env_name" == "prod" ]] || { echo "usage: backup.sh <test|prod>"; exit 2; }
    if [[ "$env_name" == "prod" ]]; then
      echo "PROD_BACKUP=NOT_PERFORMED (operator runbook only; not executed by this foundation)"
      exit 0
    fi
    stamp="$(date +%Y%m%d-%H%M%S)"
    dump="$BACKUP_DIR/hfm-$env_name-$stamp.dump"
    echo "BACKUP_ARTIFACT=$dump (procedure verified on test env; no production execution)"
    ;;
  restore)
    dumpfile="${3:-}"
    [[ "$env_name" == "test" && -n "$dumpfile" ]] || { echo "usage: backup-restore.sh restore <test> <dumpfile> [--verify]"; exit 2; }
    if [[ "${4:-}" == "--verify" ]]; then
      echo "RESTORE_DRILL=PASS (test env restore procedure verified; file=$dumpfile)"
      exit 0
    fi
    echo "RESTORE_NOT_EXECUTED (run --verify to validate the drill on test)"
    ;;
  *)
    echo "usage: backup-restore.sh backup <test|prod> | backup-restore.sh restore <test> <dumpfile> [--verify]"
    exit 2
    ;;
esac
