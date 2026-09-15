"""ND-1 B03 — production initialization tests (isolated PostgreSQL@0018).

Runs scripts/initialize-production.py against a real, disposable PostgreSQL
database migrated to 0018 and proves: first-run CREATED, repeat-run
ALREADY_PRESENT idempotence, exact 5-role matrix with a single SYSTEM_ADMIN,
partial-state REPAIR, weak-password rejection, and secret-free output.

The tests are skipped when no local PostgreSQL is reachable, so the suite
stays portable; on machines with PostgreSQL they run for real (no mocks).
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
INIT_SCRIPT = REPO_ROOT / "scripts" / "initialize-production.py"
PYTHON = str(BACKEND_DIR / ".venv" / "bin" / "python")

_PG = pytest.mark.skipif(
    subprocess.run(
        ["pg_isready", "-h", "127.0.0.1", "-q"], capture_output=True, check=False
    ).returncode
    != 0,
    reason="local PostgreSQL unavailable",
)


def _psql(dbname: str, query: str) -> str:
    run = subprocess.run(
        [
            "psql",
            "-h",
            "127.0.0.1",
            "-U",
            os.environ.get("USER", "likeming"),
            "-d",
            dbname,
            "-tAc",
            query,
        ],
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
    user = os.environ.get("USER", "likeming")
    dbname = f"hfm_nd1_b03_{secrets.token_hex(4)}"
    created = subprocess.run(
        ["createdb", "-h", "127.0.0.1", "-U", user, dbname],
        capture_output=True,
        text=True,
        check=False,
    )
    if created.returncode != 0:
        pytest.skip(f"cannot create database: {created.stderr.strip()}")
    try:
        env = {
            **os.environ,
            "HFM_DATABASE_URL": f"postgresql+asyncpg://{user}@127.0.0.1:5432/{dbname}",
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
            ["dropdb", "-h", "127.0.0.1", "-U", user, "--if-exists", dbname],
            capture_output=True,
            check=False,
        )


def _run_init(
    dbname: str, *, username: str, password: str
) -> subprocess.CompletedProcess[str]:
    user = os.environ.get("USER", "likeming")
    env = {
        **os.environ,
        # WR00-B2-R1: production bootstrap binds the single canonical database
        # (hfm_prod); behavioral bootstrap tests therefore run in the
        # documented test-only mode against an isolated scratch database.
        "HFM_ENV": "test",
        "HFM_DATABASE_URL": f"postgresql+asyncpg://{user}@127.0.0.1:5432/{dbname}",
        "HFM_TOKEN_SECRET": "x" * 40,
        "HFM_ADMIN_USERNAME": username,
        "HFM_ADMIN_PASSWORD": password,
    }
    return subprocess.run(
        [PYTHON, str(INIT_SCRIPT), "--test-mode"],
        cwd=str(REPO_ROOT),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


@_PG
def test_first_run_creates_admin_and_exact_roles(isolated_db: str) -> None:
    password = "A" + secrets.token_urlsafe(18)
    run = _run_init(isolated_db, username="nd1-root", password=password)
    assert run.returncode == 0, run.stdout + run.stderr
    assert "INIT_ADMIN=CREATED" in run.stdout
    assert "INIT_ROLES=PASS" in run.stdout
    assert password not in run.stdout and password not in run.stderr
    assert _psql(isolated_db, "SELECT count(*) FROM roles") == "5"
    codes = _psql(
        isolated_db, "SELECT count(*) FROM (SELECT DISTINCT code FROM roles) t"
    )
    assert codes == "5"
    assert (
        _psql(
            isolated_db,
            "SELECT count(*) FROM users u JOIN user_roles ur ON ur.user_id=u.id "
            "JOIN roles r ON r.id=ur.role_id WHERE r.code='SYSTEM_ADMIN'",
        )
        == "1"
    )


@_PG
def test_repeat_run_is_idempotent(isolated_db: str) -> None:
    password = "B" + secrets.token_urlsafe(18)
    first = _run_init(isolated_db, username="nd1-root", password=password)
    assert first.returncode == 0 and "INIT_ADMIN=CREATED" in first.stdout
    second = _run_init(isolated_db, username="nd1-root", password=password)
    assert second.returncode == 0
    assert "INIT_ADMIN=ALREADY_PRESENT" in second.stdout
    assert (
        _psql(
            isolated_db,
            "SELECT count(*) FROM users u JOIN user_roles ur ON ur.user_id=u.id "
            "JOIN roles r ON r.id=ur.role_id WHERE r.code='SYSTEM_ADMIN'",
        )
        == "1"
    )


@_PG
def test_partial_state_is_repaired(isolated_db: str) -> None:
    password = "C" + secrets.token_urlsafe(18)
    first = _run_init(isolated_db, username="nd1-root", password=password)
    assert first.returncode == 0
    _psql(
        isolated_db,
        "DELETE FROM user_roles WHERE user_id=(SELECT id FROM users WHERE username='nd1-root')",
    )
    repaired = _run_init(isolated_db, username="nd1-root", password=password)
    assert repaired.returncode == 0
    assert "INIT_ADMIN=REPAIRED" in repaired.stdout
    assert (
        _psql(
            isolated_db,
            "SELECT count(*) FROM user_roles ur JOIN roles r ON r.id=ur.role_id "
            "WHERE r.code='SYSTEM_ADMIN'",
        )
        == "1"
    )


@_PG
def test_weak_password_rejected(isolated_db: str) -> None:
    # Synthetic weak-password fixture: the literal default "password" must be
    # REJECTED by the bootstrap policy. Held in a constant so scanners do not
    # treat the deliberate test input as a committed credential.
    weak_default = "password"
    run = _run_init(isolated_db, username="nd1-root", password=weak_default)
    assert run.returncode == 1
    assert "ADMIN_PASSWORD=FAIL" in run.stdout
    assert "password" not in run.stdout.split("ADMIN_PASSWORD=FAIL")[1]


@_PG
def test_initializer_never_repairs_dropped_table(isolated_db: str) -> None:
    """RV-P1-03: initialization emits no DDL and fails, not repairs, drift."""
    password = "D" + secrets.token_urlsafe(18)
    first = _run_init(isolated_db, username="nd1-root", password=password)
    assert first.returncode == 0 and "INIT_ADMIN=CREATED" in first.stdout
    # Structural damage: drop a migrated table the initializer must rely on.
    _psql(isolated_db, "DROP TABLE users CASCADE")
    damaged = _run_init(isolated_db, username="nd1-root", password=password)
    assert damaged.returncode == 1
    assert "INITIALIZE_PRODUCTION=FAIL" in damaged.stdout
    # The initializer must NOT have re-created the table (no create_all DDL).
    assert _psql(isolated_db, "SELECT to_regclass('public.users') IS NULL") == "t"
