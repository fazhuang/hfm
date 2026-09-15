"""Document source registration tests (isolated PostgreSQL@0018).

Runs scripts/register-document-sources.py against a real, disposable
PostgreSQL database migrated to head and proves: --dry-run rolls back without
writing, --commit registers one Source + one SourceRef per document (idempotent
on re-run), and a missing stable_id is rejected fail-closed.

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
REGISTER_SCRIPT = REPO_ROOT / "scripts" / "register-document-sources.py"
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
    dbname = f"hfm_src_{secrets.token_hex(4)}"
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


_SEED = """
import asyncio, os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from hfm.models.document import ContentDocument

async def main():
    engine = create_async_engine(os.environ["HFM_DATABASE_URL"])
    factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with factory() as s:
        s.add(ContentDocument(
            stable_id="DOC-TEST", title="Test Doc",
            doc_type="PLANNING_DOC", source_asset_id="HFM-A999999",
        ))
        await s.commit()
    await engine.dispose()

asyncio.run(main())
"""


def _seed(dbname: str) -> None:
    env = {
        **os.environ,
        "HFM_ENV": "test",
        "HFM_DATABASE_URL": f"postgresql+asyncpg://{_user()}@127.0.0.1:5432/{dbname}",
    }
    run = subprocess.run(
        [PYTHON, "-c", _SEED],
        env=env,
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )
    assert run.returncode == 0, run.stderr


def _run_register(dbname: str, *args: str) -> subprocess.CompletedProcess[str]:
    env = {
        **os.environ,
        "HFM_ENV": "test",
        "HFM_DATABASE_URL": f"postgresql+asyncpg://{_user()}@127.0.0.1:5432/{dbname}",
        "HFM_TOKEN_SECRET": "x" * 40,
    }
    return subprocess.run(
        [PYTHON, str(REGISTER_SCRIPT), "--test-mode", *args],
        cwd=str(REPO_ROOT),
        env=env,
        capture_output=True,
        text=True,
        check=False,
        timeout=120,
    )


@_PG
def test_dry_run_rolls_back(isolated_db: str) -> None:
    _seed(isolated_db)
    run = _run_register(
        isolated_db, "--stable-ids", "DOC-TEST", "--rights-basis", "customer_owned"
    )
    assert run.returncode == 0, run.stdout + run.stderr
    assert "DRY_RUN=ROLLED_BACK" in run.stdout
    assert _psql(isolated_db, "select count(*) from sources;") == "0"
    assert _psql(isolated_db, "select count(*) from source_refs;") == "0"


@_PG
def test_commit_registers_source_and_ref_idempotent(isolated_db: str) -> None:
    _seed(isolated_db)
    first = _run_register(
        isolated_db,
        "--stable-ids",
        "DOC-TEST",
        "--rights-basis",
        "customer_owned",
        "--commit",
    )
    assert first.returncode == 0, first.stdout + first.stderr
    assert _psql(isolated_db, "select count(*) from sources;") == "1"
    assert _psql(isolated_db, "select count(*) from source_refs;") == "1"
    assert _psql(isolated_db, "select source_key from sources;") == "document:DOC-TEST"
    assert (
        _psql(isolated_db, "select rights_basis from sources;") == "customer_owned"
    )

    second = _run_register(
        isolated_db,
        "--stable-ids",
        "DOC-TEST",
        "--rights-basis",
        "customer_owned",
        "--commit",
    )
    assert second.returncode == 0, second.stdout + second.stderr
    assert "ALREADY_REGISTERED" in second.stdout
    # Idempotent: still one source + one source_ref — no duplicates.
    assert _psql(isolated_db, "select count(*) from sources;") == "1"
    assert _psql(isolated_db, "select count(*) from source_refs;") == "1"


@_PG
def test_missing_document_rejected_fail_closed(isolated_db: str) -> None:
    _seed(isolated_db)
    run = _run_register(
        isolated_db,
        "--stable-ids",
        "DOC-NOT-EXISTS",
        "--rights-basis",
        "customer_owned",
        "--commit",
    )
    assert run.returncode == 0, run.stdout + run.stderr
    assert "REJECTED DOC-NOT-EXISTS" in run.stdout
    assert _psql(isolated_db, "select count(*) from sources;") == "0"
    assert _psql(isolated_db, "select count(*) from source_refs;") == "0"
