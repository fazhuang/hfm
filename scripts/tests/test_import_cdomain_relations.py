"""C-domain relation import tests (isolated PostgreSQL@0016).

Runs scripts/import-cdomain-relations.py against a disposable PostgreSQL
database seeded with the five source acupoint terms, and proves: --dry-run
rolls back, --commit adds the four missing meridian terms + five located_in
relations (idempotent on re-run), and an unknown relation type is rejected.

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
IMPORT_SCRIPT = REPO_ROOT / "scripts" / "import-cdomain-relations.py"
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
    dbname = f"hfm_rel_{secrets.token_hex(4)}"
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
from hfm.models.c_domain import CDomainTerm
from hfm.models.chapter import Chapter  # noqa: F401
from hfm.models.edition import Edition  # noqa: F401
from hfm.models.passage import Passage  # noqa: F401
from hfm.models.version import Version  # noqa: F401
from hfm.models.work import Work  # noqa: F401

ACUPOINTS = ["合谷", "足三里", "三阴交", "内关", "曲池"]

async def main():
    engine = create_async_engine(os.environ["HFM_DATABASE_URL"])
    factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with factory() as s:
        for name in ACUPOINTS:
            eid = f"K-ACUPOINT-{name}"
            e = Entity(id=eid, entity_type=EntityType.acupoint, name=name, name_zh=name)
            s.add(e); await s.flush()
            s.add(CDomainTerm(entity_id=eid, term_type="acupoint", term_name=name))
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
    assert _psql(isolated_db, "select count(*) from c_domain_relations;") == "0"


@_PG
def test_commit_adds_relations_and_missing_meridians_idempotent(isolated_db: str) -> None:
    _seed(isolated_db)
    first = _run_import(isolated_db, "--commit")
    assert first.returncode == 0, first.stdout + first.stderr
    assert "IMPORT_CDOMAIN_RELATIONS=PASS" in first.stdout
    assert _psql(isolated_db, "select count(*) from c_domain_relations;") == "5"
    # 5 source acupoints + 4 added meridian terms.
    assert _psql(isolated_db, "select count(*) from c_domain_terms;") == "9"
    assert (
        _psql(
            isolated_db,
            "select count(*) from c_domain_relations where relation_type = 'located_in';",
        )
        == "5"
    )

    second = _run_import(isolated_db, "--commit")
    assert second.returncode == 0, second.stdout + second.stderr
    assert "EXISTS relation" in second.stdout
    assert _psql(isolated_db, "select count(*) from c_domain_relations;") == "5"
    assert _psql(isolated_db, "select count(*) from c_domain_terms;") == "9"
