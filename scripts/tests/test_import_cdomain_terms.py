"""C-domain term import tests (isolated PostgreSQL@0016).

Runs scripts/import-cdomain-terms.py against a real, disposable PostgreSQL
database migrated to head and proves: --dry-run rolls back without writing,
--commit admits the 26 frozen knowledge-object candidates into entities +
c_domain_terms (5 acupoint / 21 concept), and re-run is an idempotent no-op.

Tests are skipped when no local PostgreSQL is reachable, so the suite stays
portable; on machines with PostgreSQL they run for real (no mocks).
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
IMPORT_SCRIPT = REPO_ROOT / "scripts" / "import-cdomain-terms.py"
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
    """Create + migrate a disposable database; drop it afterwards."""
    ready = subprocess.run(
        ["pg_isready", "-h", "127.0.0.1", "-q"], capture_output=True, check=False
    )
    if ready.returncode != 0:
        pytest.skip("local PostgreSQL unavailable")
    dbname = f"hfm_cterm_{secrets.token_hex(4)}"
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


@_PG
def test_dry_run_rolls_back(isolated_db: str) -> None:
    run = _run_import(isolated_db)
    assert run.returncode == 0, run.stdout + run.stderr
    assert "DRY_RUN=ROLLED_BACK" in run.stdout
    assert "SUMMARY={'terms_created': 26" in run.stdout
    assert _psql(isolated_db, "select count(*) from entities;") == "0"
    assert _psql(isolated_db, "select count(*) from c_domain_terms;") == "0"


@_PG
def test_commit_admits_26_terms_and_is_idempotent(isolated_db: str) -> None:
    first = _run_import(isolated_db, "--commit")
    assert first.returncode == 0, first.stdout + first.stderr
    assert "IMPORT_CDOMAIN_TERMS=PASS" in first.stdout
    assert _psql(isolated_db, "select count(*) from c_domain_terms;") == "26"
    assert _psql(isolated_db, "select count(*) from entities;") == "26"
    # Type mapping: 5 acupoints + 21 concepts (medical subtypes -> concept).
    assert (
        _psql(isolated_db, "select count(*) from entities where entity_type = 'acupoint';")
        == "5"
    )
    assert (
        _psql(isolated_db, "select count(*) from entities where entity_type = 'concept';")
        == "21"
    )

    second = _run_import(isolated_db, "--commit")
    assert second.returncode == 0, second.stdout + second.stderr
    assert "EXISTS term" in second.stdout
    # Idempotent: still exactly 26 entities / 26 terms — no duplicates.
    assert _psql(isolated_db, "select count(*) from entities;") == "26"
    assert _psql(isolated_db, "select count(*) from c_domain_terms;") == "26"
