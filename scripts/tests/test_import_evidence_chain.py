"""Evidence chain import tests (isolated PostgreSQL@0017).

Runs scripts/import-evidence-chain.py against a real, disposable PostgreSQL
database seeded with the person + document sources the frozen evidence.csv
references, and proves: --dry-run rolls back, --commit admits 23 of the 24
candidates (EVIDENCE-006 is rejected fail-closed for its malformed
SOURCE_ASSET_ID), and re-run is an idempotent no-op.

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
IMPORT_SCRIPT = REPO_ROOT / "scripts" / "import-evidence-chain.py"
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
    dbname = f"hfm_ev_{secrets.token_hex(4)}"
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
from hfm.models.entity import Entity, EntityType
from hfm.models.person import Person
from hfm.models.document import ContentDocument
from hfm.models.source import Source
from hfm.models.source_ref import SourceRef

DOCS = [
    ("DOC-HFM-A000003", "HFM-A000003", "其传"),
    ("DOC-HFM-A000004", "HFM-A000004", "其言"),
    ("DOC-HFM-A000005", "HFM-A000005", "后论"),
]

async def main():
    engine = create_async_engine(os.environ["HFM_DATABASE_URL"])
    factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with factory() as s:
        e = Entity(entity_type=EntityType.person, name="皇甫谧", name_zh="皇甫谧")
        s.add(e); await s.flush()
        s.add(Person(entity_id=e.id, name_zh="皇甫谧", stable_id="PERSON-HFM-HUANGFUMI"))
        for stable_id, asset_id, title in DOCS:
            s.add(ContentDocument(
                stable_id=stable_id, title=title,
                doc_type="PLANNING_DOC", source_asset_id=asset_id,
            ))
            src = Source(source_key=f"document:{stable_id}", title=title)
            s.add(src); await s.flush()
            s.add(SourceRef(source_id=src.id, title=title))
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
    _seed(isolated_db)
    run = _run_import(isolated_db)
    assert run.returncode == 0, run.stdout + run.stderr
    assert "DRY_RUN=ROLLED_BACK" in run.stdout
    assert _psql(isolated_db, "select count(*) from evidences;") == "0"
    assert _psql(isolated_db, "select count(*) from assertions;") == "0"


@_PG
def test_commit_admits_23_and_rejects_malformed(isolated_db: str) -> None:
    _seed(isolated_db)
    run = _run_import(isolated_db, "--commit")
    assert run.returncode == 0, run.stdout + run.stderr
    assert "IMPORT_EVIDENCE_CHAIN=PASS" in run.stdout
    # EVIDENCE-006 is malformed (unquoted comma shifts its SOURCE_ASSET_ID).
    assert "REJECTED EVIDENCE-006" in run.stdout
    assert _psql(isolated_db, "select count(*) from evidences;") == "23"
    assert _psql(isolated_db, "select count(*) from assertions;") == "23"
    assert _psql(isolated_db, "select count(*) from assertion_evidences;") == "23"
    # Every assertion is admitted as draft (never approved) with conservative confidence.
    assert _psql(isolated_db, "select count(*) from assertions where editorial_status='draft';") == "23"


@_PG
def test_commit_is_idempotent(isolated_db: str) -> None:
    _seed(isolated_db)
    first = _run_import(isolated_db, "--commit")
    assert first.returncode == 0, first.stdout + first.stderr
    second = _run_import(isolated_db, "--commit")
    assert second.returncode == 0, second.stdout + second.stderr
    assert "EXISTS evidence" in second.stdout
    assert _psql(isolated_db, "select count(*) from evidences;") == "23"
    assert _psql(isolated_db, "select count(*) from assertions;") == "23"
    assert _psql(isolated_db, "select count(*) from assertion_evidences;") == "23"
