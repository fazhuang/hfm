"""Access-boundary migration and ledger backfill tests (isolated PostgreSQL@0018).

Runs ``alembic upgrade head`` plus ``scripts/backfill-ledger-ids.py`` against
a real, disposable database and proves:

  - a freshly registered asset defaults to the research scope, so the
    portal/research boundary fails closed rather than open;
  - the backfill copies identifiers from the register onto matching rows;
  - an asset with no register entry blocks the commit instead of leaving a
    partial join;
  - re-running the backfill changes nothing (idempotent).

Skipped when no local PostgreSQL is reachable, so the suite stays portable.
No mocks: the column, the constraint and the script all run for real.
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
BACKFILL_SCRIPT = REPO_ROOT / "scripts" / "backfill-ledger-ids.py"
PYTHON = str(BACKEND_DIR / ".venv" / "bin" / "python")


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
    dbname = f"hfm_ledger_{secrets.token_hex(4)}"
    created = subprocess.run(
        ["createdb", "-h", "127.0.0.1", "-U", _user(), dbname],
        capture_output=True,
        text=True,
        check=False,
    )
    if created.returncode != 0:
        pytest.skip(f"cannot create database: {created.stderr.strip()}")
    try:
        env = _env(dbname)
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


def _env(dbname: str) -> dict[str, str]:
    return {
        **os.environ,
        "HFM_ENV": "test",
        "HFM_DATABASE_URL": f"postgresql+asyncpg://{_user()}@127.0.0.1:5432/{dbname}",
    }


#: Two assets whose object keys mirror the register's path shape.
_SEED = """
import asyncio, os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from hfm.phase2.media.models import MediaAsset

KEYS = ["针灸甲乙经/论著/《针灸甲乙经》四库全书本清乾隆/卷一.pdf",
        "针灸甲乙经/论文/针灸甲乙经/19-神志病治疗思路浅析.pdf"]

async def main() -> None:
    engine = create_async_engine(os.environ["HFM_DATABASE_URL"])
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        for i, key in enumerate(KEYS):
            session.add(MediaAsset(
                object_key=key, mime_type="application/pdf", byte_size=100,
                sha256=f"{i:064d}", rights_holder="test", license_basis="customer_owned",
            ))
        await session.commit()
    await engine.dispose()

asyncio.run(main())
"""


def _seed(dbname: str) -> None:
    run = subprocess.run(
        [PYTHON, "-c", _SEED],
        env=_env(dbname),
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )
    assert run.returncode == 0, run.stderr


def _register(
    tmp_path: Path, rows: list[tuple[str, str]], name: str = "register.csv"
) -> Path:
    path = tmp_path / name
    body = "ASSET_ID,RELATIVE_PATH,SOURCE_STATUS,RIGHTS_STATUS,PUBLIC_USE_STATUS,REVIEW_REQUIRED\n"
    body += "".join(
        f"{asset_id},{key},NEEDS_REVIEW,UNKNOWN,UNRESOLVED,YES\n"
        for asset_id, key in rows
    )
    path.write_text(body, encoding="utf-8-sig")
    return path


def _backfill(
    dbname: str, register: Path, *args: str
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [PYTHON, str(BACKFILL_SCRIPT), "--register", str(register), *args],
        env=_env(dbname),
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )


def test_new_asset_defaults_to_research_scope(isolated_db: str) -> None:
    """The boundary fails closed: nothing reaches the portal unasked."""
    _seed(isolated_db)
    assert (
        _psql(isolated_db, "SELECT DISTINCT access_scope FROM media_assets")
        == "research"
    )


def test_backfill_copies_identifiers_from_the_register(
    isolated_db: str, tmp_path: Path
) -> None:
    _seed(isolated_db)
    register = _register(
        tmp_path,
        [
            ("HFM-A000601", "针灸甲乙经/论著/《针灸甲乙经》四库全书本清乾隆/卷一.pdf"),
            ("HFM-A000089", "针灸甲乙经/论文/针灸甲乙经/19-神志病治疗思路浅析.pdf"),
        ],
    )
    dry = _backfill(isolated_db, register)
    assert dry.returncode == 0, dry.stdout + dry.stderr
    assert "LEDGER_BACKFILL=DRY_RUN" in dry.stdout
    assert _psql(isolated_db, "SELECT count(ledger_id) FROM media_assets") == "0"

    run = _backfill(isolated_db, register, "--commit")
    assert run.returncode == 0, run.stdout + run.stderr
    assert "LEDGER_BACKFILL=PASS" in run.stdout
    assert (
        _psql(
            isolated_db,
            "SELECT ledger_id FROM media_assets "
            "WHERE object_key LIKE '针灸甲乙经/论文/%'",
        )
        == "HFM-A000089"
    )


def test_backfill_fails_closed_when_an_asset_has_no_register_entry(
    isolated_db: str, tmp_path: Path
) -> None:
    _seed(isolated_db)
    register = _register(
        tmp_path,
        [("HFM-A000601", "针灸甲乙经/论著/《针灸甲乙经》四库全书本清乾隆/卷一.pdf")],
    )
    run = _backfill(isolated_db, register, "--commit")
    assert run.returncode == 1
    assert "LEDGER_BACKFILL=FAIL" in run.stdout
    # Nothing written, so the gap stays visible rather than half-filled.
    assert _psql(isolated_db, "SELECT count(ledger_id) FROM media_assets") == "0"


def test_backfill_is_idempotent(isolated_db: str, tmp_path: Path) -> None:
    _seed(isolated_db)
    register = _register(
        tmp_path,
        [
            ("HFM-A000601", "针灸甲乙经/论著/《针灸甲乙经》四库全书本清乾隆/卷一.pdf"),
            ("HFM-A000089", "针灸甲乙经/论文/针灸甲乙经/19-神志病治疗思路浅析.pdf"),
        ],
    )
    assert _backfill(isolated_db, register, "--commit").returncode == 0
    again = _backfill(isolated_db, register, "--commit")
    assert again.returncode == 0
    assert "UNCHANGED=2" in again.stdout
    assert "TO_SET=0" in again.stdout
