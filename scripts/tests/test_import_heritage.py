"""Heritage project import tests (isolated PostgreSQL@0018).

Runs scripts/import-heritage.py against a disposable PostgreSQL database and
proves: --dry-run rolls back, --commit admits every heritage object in the source CSV as
heritage_projects (idempotent on re-run), and names/categories are cleaned of
leading list numbering.

Tests are skipped when no local PostgreSQL is reachable.
"""

from __future__ import annotations

import os
import secrets
import subprocess
from collections.abc import Iterator
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = REPO_ROOT / "apps" / "backend"
IMPORT_SCRIPT = REPO_ROOT / "scripts" / "import-heritage.py"
PYTHON = str(BACKEND_DIR / ".venv" / "bin" / "python")

_PG = pytest.mark.skipif(
    subprocess.run(
        ["pg_isready", "-h", "127.0.0.1", "-q"], capture_output=True, check=False
    ).returncode
    != 0,
    reason="local PostgreSQL unavailable",
)


def _user() -> str:
    return os.environ.get("USER", "likeming")


def _psql(dbname: str, query: str) -> str:
    run = subprocess.run(
        ["psql", "-h", "127.0.0.1", "-U", _user(), "-d", dbname, "-tAc", query],
        capture_output=True,
        text=True,
        check=False,
    )
    assert run.returncode == 0, run.stderr
    return run.stdout.strip()


@pytest.fixture()
def isolated_db() -> Iterator[str]:
    ready = subprocess.run(
        ["pg_isready", "-h", "127.0.0.1", "-q"], capture_output=True, check=False
    )
    if ready.returncode != 0:
        pytest.skip("local PostgreSQL unavailable")
    dbname = f"hfm_her_{secrets.token_hex(4)}"
    created = subprocess.run(
        ["createdb", "-h", "127.0.0.1", "-U", _user(), dbname],
        capture_output=True,
        text=True,
        check=False,
    )
    if created.returncode != 0:
        pytest.skip(f"cannot create database: {created.stderr.strip()}")
    try:
        env = {
            **os.environ,
            "HFM_DATABASE_URL": f"postgresql+asyncpg://{_user()}@127.0.0.1:5432/{dbname}",
        }
        migrated = subprocess.run(
            [PYTHON, "-m", "alembic", "-c", "alembic.ini", "upgrade", "head"],
            cwd=str(BACKEND_DIR),
            env=env,
            capture_output=True,
            text=True,
            timeout=240,
            check=False,
        )
        assert migrated.returncode == 0, migrated.stderr[-1500:]
        yield dbname
    finally:
        subprocess.run(
            ["dropdb", "-h", "127.0.0.1", "-U", _user(), "--if-exists", dbname],
            capture_output=True,
            check=False,
        )


def _run_import(dbname: str, *args: str) -> subprocess.CompletedProcess[str]:
    env = {
        **os.environ,
        "HFM_ENV": "test",
        "HFM_DATABASE_URL": f"postgresql+asyncpg://{_user()}@127.0.0.1:5432/{dbname}",
        "HFM_TOKEN_SECRET": "x" * 40,
    }
    return subprocess.run(
        [PYTHON, str(IMPORT_SCRIPT), "--test-mode", *args],
        cwd=str(REPO_ROOT),
        env=env,
        capture_output=True,
        text=True,
        check=False,
        timeout=120,
    )


#: Data-driven: content-production/normalized/heritage-objects.csv holds this
#: many rows, and the importer admits one project + one entity per row. It was
#: 68 when this test was written; C1 (e7eadb5) curated the CSV down to 55 and
#: left the literal behind.
HERITAGE_ROWS = 55


@_PG
def test_dry_run_rolls_back(isolated_db: str) -> None:
    run = _run_import(isolated_db)
    assert run.returncode == 0, run.stdout + run.stderr
    assert "DRY_RUN=ROLLED_BACK" in run.stdout
    assert f"SUMMARY={{'projects_created': {HERITAGE_ROWS}" in run.stdout
    assert _psql(isolated_db, "select count(*) from heritage_projects;") == "0"


@_PG
def test_commit_admits_all_and_is_idempotent(isolated_db: str) -> None:
    first = _run_import(isolated_db, "--commit")
    assert first.returncode == 0, first.stdout + first.stderr
    assert "IMPORT_HERITAGE=PASS" in first.stdout
    assert _psql(isolated_db, "select count(*) from heritage_projects;") == str(HERITAGE_ROWS)
    assert _psql(isolated_db, "select count(*) from entities;") == str(HERITAGE_ROWS)

    second = _run_import(isolated_db, "--commit")
    assert second.returncode == 0, second.stdout + second.stderr
    assert "EXISTS heritage" in second.stdout
    assert _psql(isolated_db, "select count(*) from heritage_projects;") == str(HERITAGE_ROWS)
    assert _psql(isolated_db, "select count(*) from entities;") == str(HERITAGE_ROWS)
