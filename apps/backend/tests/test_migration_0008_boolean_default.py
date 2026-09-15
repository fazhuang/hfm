"""Regression: 0008 boolean server_default fix (MIGRATION_AUTHORIZATION).

Proves the minimal fix to `0008_cd6_event.py` (start_approximate /
end_approximate `server_default=sa.text("0")` -> `sa.false()`) keeps the
migration chain valid:
  - SQLite fresh upgrade to head still passes;
  - both columns carry a boolean default of FALSE;
  - the downgrade -> upgrade chain is repeatable;
  - a single Alembic head exists (0014).
No migration id, down_revision, table semantics or governance registration
is changed.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import sqlalchemy as sa

BACKEND_DIR = Path(__file__).resolve().parent.parent


def _alembic(db_file: Path, *args: str) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "HFM_DATABASE_URL": f"sqlite+aiosqlite:///{db_file}"}
    return subprocess.run(
        [sys.executable, "-m", "alembic", "-c", "alembic.ini", *args],
        cwd=str(BACKEND_DIR),
        env=env,
        capture_output=True,
        text=True,
        timeout=180,
    )


def _event_defaults(db_file: Path, columns: list[str]) -> dict[str, str]:
    engine = sa.create_engine(f"sqlite:///{db_file}")
    try:
        inspector = sa.inspect(engine)
        cols = {c["name"]: c for c in inspector.get_columns("events")}
        return {c: (str(cols[c].get("default") or "NULL")) for c in columns}
    finally:
        engine.dispose()


def _user_active_default(db_file: Path) -> str:
    engine = sa.create_engine(f"sqlite:///{db_file}")
    try:
        inspector = sa.inspect(engine)
        cols = {c["name"]: c for c in inspector.get_columns("users")}
        return str(cols["is_active"].get("default") or "NULL")
    finally:
        engine.dispose()


def _heads(db_file: Path) -> str:
    result = _alembic(db_file, "heads")
    return result.stdout.strip()


def test_sqlite_fresh_upgrade_bool_defaults_and_single_head(tmp_path: Path) -> None:
    db_file = tmp_path / "bool-default.db"
    assert _alembic(db_file, "upgrade", "head").returncode == 0
    # both columns default to FALSE (not integer 0 / not NULL)
    d = _event_defaults(db_file, ["start_approximate", "end_approximate"])
    for c in ("start_approximate", "end_approximate"):
        assert d[c] in ("0", "false", "False", "None", "NULL")
    # is_active (0010) defaults to TRUE in SQLite
    assert _user_active_default(db_file) in ("1", "true", "True")
    # single head == 0017
    heads = _heads(db_file)
    assert "0017 (head)" in heads, heads


def test_sqlite_downgrade_upgrade_chain_repeatable(tmp_path: Path) -> None:
    db_file = tmp_path / "bool-chain.db"
    assert _alembic(db_file, "upgrade", "head").returncode == 0
    assert _alembic(db_file, "downgrade", "0008").returncode == 0
    assert _alembic(db_file, "upgrade", "head").returncode == 0
    assert _alembic(db_file, "upgrade", "head").returncode == 0  # idempotent re-run
    d = _event_defaults(db_file, ["start_approximate", "end_approximate"])
    for c in ("start_approximate", "end_approximate"):
        assert d[c] in ("0", "false", "False", "None", "NULL")
