#!/usr/bin/env bash
# HFM backup/restore runbook with REAL drill (P1-08 correction).
#
# backup.sh <test> [--verify]       create a real backup artifact from the
#                                   local test database fixture
# restore.sh <test> <dumpfile> [--verify]
#                                   restore into an isolated target database,
#                                   validate schema/data, detect corruption
#
# Production backup stays NOT_PERFORMED (operator runbook); the drill runs
# only against the isolated local test fixture.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKUP_DIR="$REPO_ROOT/infra/backups"
mkdir -p "$BACKUP_DIR"

command="$1"
env_name="${2:-}"

case "$command" in
  backup)
    [[ "$env_name" == "test" ]] || { echo "usage: backup-restore.sh backup <test>"; exit 2; }
    python3 - "$BACKUP_DIR" <<'PY'
import sqlite3, sys, time
from pathlib import Path
backup_dir = Path(sys.argv[1])
# Real backup artifact: dump the local test fixture database.
fixture = backup_dir / "fixture.db"
fixture.parent.mkdir(parents=True, exist_ok=True)
if not fixture.exists():
    con = sqlite3.connect(fixture)
    con.execute("CREATE TABLE demo_items (id TEXT PRIMARY KEY, title TEXT)")
    con.execute("INSERT INTO demo_items VALUES ('a1', 'restore-drill-item')")
    con.commit()
    con.close()
dump = backup_dir / f"hfm-test-{int(time.time())}.db"
dst = sqlite3.connect(dump)
src = sqlite3.connect(fixture)
src.backup(dst)
src.close()
dst.close()
print(f"BACKUP_ARTIFACT={dump}")
PY
    ;;
  restore)
    dumpfile="${3:-}"
    [[ "$env_name" == "test" && -n "$dumpfile" ]] || { echo "usage: backup-restore.sh restore <test> <dumpfile> [--verify]"; exit 2; }
    python3 - "$BACKUP_DIR" "$dumpfile" "${4:-}" <<'PY'
import sqlite3, sys
from pathlib import Path
backup_dir = Path(sys.argv[1])
dump = backup_dir / sys.argv[2]
verify = sys.argv[3] == "--verify"
target = backup_dir / "restored-test.db"
if target.exists():
    target.unlink()
try:
    dst = sqlite3.connect(target)
    src = sqlite3.connect(dump)
    src.backup(dst)
    src.close()
    dst.close()
except sqlite3.DatabaseError as exc:
    print(f"RESTORE_VERIFY=FAIL (corrupt or invalid backup: {exc})")
    raise SystemExit(1)

if verify:
    con = sqlite3.connect(target)
    try:
        integrity = con.execute("PRAGMA integrity_check").fetchone()[0]
        tables = [r[0] for r in con.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]
        marker = con.execute("SELECT title FROM demo_items WHERE id='a1'").fetchone()
    finally:
        con.close()
    if integrity != "ok" or "demo_items" not in tables or not marker:
        print("RESTORE_VERIFY=FAIL (restored data invalid)")
        raise SystemExit(1)
    print(f"RESTORE_DRILL=PASS (restored target={target}, integrity={integrity}, tables={tables}, marker={marker[0]})")
else:
    print("RESTORE_NOT_EXECUTED (run --verify to validate the drill on test)")
PY
    ;;
  prod-backup)
    echo "PROD_BACKUP=NOT_PERFORMED (operator runbook only; not executed by this foundation)"
    exit 0
    ;;
  *)
    echo "usage: backup-restore.sh backup <test> | restore <test> <dumpfile> [--verify]"
    exit 2
    ;;
esac
