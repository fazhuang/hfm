"""Content publication pipeline tests (isolated PostgreSQL@0018).

Runs scripts/publish-content.py against a real, disposable PostgreSQL
database migrated to 0018 and proves: end-to-end admit → submit → review →
publish populates sources/content_artifacts/publication_records, re-run is an
idempotent no-op, --dry-run rolls back without committing, and UNKNOWN rights
are rejected at the CLI boundary.

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
PUBLISH_SCRIPT = REPO_ROOT / "scripts" / "publish-content.py"
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
    dbname = f"hfm_pub_{secrets.token_hex(4)}"
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
from hfm.models.work import Work
from hfm.models.person import Person

async def main():
    engine = create_async_engine(os.environ["HFM_DATABASE_URL"])
    factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with factory() as s:
        e1 = Entity(entity_type=EntityType.work, name="Test Work")
        s.add(e1); await s.flush()
        s.add(Work(title="Test Work", entity_id=e1.id, stable_id="WORK-TEST"))
        e2 = Entity(entity_type=EntityType.person, name="Test Person")
        s.add(e2); await s.flush()
        s.add(Person(entity_id=e2.id, name_zh="Test Person", stable_id="PERSON-TEST"))
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


def _run_publish(dbname: str, *args: str) -> subprocess.CompletedProcess[str]:
    env = {
        **os.environ,
        "HFM_ENV": "test",
        "HFM_DATABASE_URL": f"postgresql+asyncpg://{_user()}@127.0.0.1:5432/{dbname}",
        "HFM_TOKEN_SECRET": "x" * 40,
    }
    return subprocess.run(
        [PYTHON, str(PUBLISH_SCRIPT), "--test-mode", *args],
        cwd=str(REPO_ROOT),
        env=env,
        capture_output=True,
        text=True,
        check=False,
        timeout=120,
    )


@_PG
def test_publish_roundtrip_and_idempotent(isolated_db: str) -> None:
    _seed(isolated_db)

    first = _run_publish(
        isolated_db, "--rights-status", "customer_owned", "--scope", "all"
    )
    assert first.returncode == 0, first.stdout + first.stderr
    assert "PUBLISH_CONTENT=PASS" in first.stdout
    assert _psql(isolated_db, "select count(*) from sources;") == "2"
    assert _psql(isolated_db, "select count(*) from content_artifacts;") == "2"
    assert (
        _psql(
            isolated_db,
            "select count(*) from publication_records where publication_status = 'PUBLISHED';",
        )
        == "2"
    )

    second = _run_publish(
        isolated_db, "--rights-status", "customer_owned", "--scope", "all"
    )
    assert second.returncode == 0, second.stdout + second.stderr
    assert "already_published" in second.stdout
    # Idempotent: still exactly two sources/artifacts/records — no duplicates.
    assert _psql(isolated_db, "select count(*) from sources;") == "2"
    assert _psql(isolated_db, "select count(*) from content_artifacts;") == "2"
    assert _psql(isolated_db, "select count(*) from publication_records;") == "2"


@_PG
def test_dry_run_rolls_back(isolated_db: str) -> None:
    _seed(isolated_db)
    run = _run_publish(
        isolated_db, "--rights-status", "public_domain", "--scope", "all", "--dry-run"
    )
    assert run.returncode == 0, run.stdout + run.stderr
    assert "DRY_RUN=ROLLED_BACK" in run.stdout
    assert _psql(isolated_db, "select count(*) from sources;") == "0"
    assert _psql(isolated_db, "select count(*) from publication_records;") == "0"


@_PG
def test_unknown_rights_rejected_at_cli(isolated_db: str) -> None:
    _seed(isolated_db)
    run = _run_publish(isolated_db, "--rights-status", "unknown", "--scope", "all")
    assert run.returncode == 2  # argparse choices rejects UNKNOWN before any write
    assert _psql(isolated_db, "select count(*) from publication_records;") == "0"


@_PG
def test_rights_manifest_overrides_fallback(isolated_db: str, tmp_path: Path) -> None:
    _seed(isolated_db)
    manifest = tmp_path / "rights.json"
    manifest.write_text(
        '{"work:WORK-TEST": "licensed", "person:PERSON-TEST": "customer_owned"}',
        encoding="utf-8",
    )
    run = _run_publish(
        isolated_db,
        "--rights-status",
        "public_domain",
        "--rights-file",
        str(manifest),
        "--scope",
        "all",
    )
    assert run.returncode == 0, run.stdout + run.stderr
    assert (
        _psql(
            isolated_db,
            "select rights_status from content_artifacts "
            "where subject_entity_id = (select entity_id from works where stable_id='WORK-TEST');",
        )
        == "licensed"
    )
    assert (
        _psql(
            isolated_db,
            "select rights_status from content_artifacts "
            "where subject_entity_id = (select entity_id from persons where stable_id='PERSON-TEST');",
        )
        == "customer_owned"
    )
