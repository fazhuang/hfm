"""Media publication pipeline tests (isolated PostgreSQL@0018).

Runs scripts/publish-media.py against a real, disposable PostgreSQL database
migrated to 0018 and proves: only manifest-cleared P0/P1 assets are published,
P2 assets stay draft, re-run is an idempotent no-op, the default dry-run rolls
back without committing, an expected_count mismatch fails closed, a P2
declaration is rejected at the manifest boundary, and an already-published
asset outside the manifest is reported as drift instead of being re-scoped.

Tests are skipped when no local PostgreSQL is reachable, so the suite stays
portable; on machines with PostgreSQL they run for real (no mocks).
"""

from __future__ import annotations

import json
import os
import secrets
import subprocess
from collections.abc import Iterator
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = REPO_ROOT / "apps" / "backend"
PUBLISH_SCRIPT = REPO_ROOT / "scripts" / "publish-media.py"
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
    dbname = f"hfm_media_{secrets.token_hex(4)}"
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


#: 3 cleared assets (2 P0 + 1 P1) and 1 withheld P2 certificate.
_SEED = """
import asyncio, os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from hfm.phase2.media.models import MediaAsset, MediaAssetState

ROWS = [
    ("针灸甲乙经/juan01.pdf", "application/pdf", "P0"),
    ("针灸甲乙经/juan02.pdf", "application/pdf", "P0"),
    ("皇甫谧/portrait.jpg", "image/jpeg", "P1"),
    ("非遗佐证/cert.pdf", "application/pdf", "P2"),
    # Not covered by DEFAULT_RULES: used to construct the "published but
    # uncleared" drift state. It has to be a class that CAN be published —
    # the P2 certificate above is now refused by the schema, which is the
    # point of the privacy gate, so it can no longer play that role.
    ("其他材料/extra.pdf", "application/pdf", "P0"),
]

async def main():
    engine = create_async_engine(os.environ["HFM_DATABASE_URL"])
    factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with factory() as s:
        for i, (key, mime, privacy) in enumerate(ROWS):
            s.add(MediaAsset(
                object_key=key,
                mime_type=mime,
                byte_size=1024 + i,
                sha256=f"{i:064x}",
                rights_holder="皇甫谧文化（客户提供）",
                license_basis="customer_owned",
                publication_permission=False,
                privacy_class=privacy,
                publication_state=MediaAssetState.DRAFT,
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


def _clearance(tmp_path: Path, rules: list[dict], name: str = "clearance.json") -> Path:
    path = tmp_path / name
    path.write_text(
        json.dumps(
            {"version": 1, "basis": "客户授权公开（测试）", "rules": rules}, ensure_ascii=False
        ),
        encoding="utf-8",
    )
    return path


DEFAULT_RULES = [
    {"privacy_class": "P0", "prefix": "针灸甲乙经/", "expected_count": 2},
    {"privacy_class": "P1", "object_key": "皇甫谧/portrait.jpg", "expected_count": 1},
]


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


def _published(dbname: str) -> str:
    return _psql(dbname, "select count(*) from media_assets where publication_state='published';")


@_PG
def test_commit_publishes_cleared_only(isolated_db: str, tmp_path: Path) -> None:
    _seed(isolated_db)
    run = _run_publish(
        isolated_db,
        "--clearance-file",
        str(_clearance(tmp_path, DEFAULT_RULES)),
        "--commit",
    )
    assert run.returncode == 0, run.stdout + run.stderr
    assert "PUBLISH_MEDIA=PASS" in run.stdout
    # Only the 3 cleared assets are public; the P2 certificate is untouched.
    assert _published(isolated_db) == "3"
    assert (
        _psql(
            isolated_db,
            "select publication_state from media_assets where object_key='非遗佐证/cert.pdf';",
        )
        == "draft"
    )
    # The rights bit is granted only for cleared assets.
    assert (
        _psql(
            isolated_db,
            "select count(*) from media_assets where publication_permission;",
        )
        == "3"
    )


@_PG
def test_dry_run_rolls_back(isolated_db: str, tmp_path: Path) -> None:
    _seed(isolated_db)
    run = _run_publish(isolated_db, "--clearance-file", str(_clearance(tmp_path, DEFAULT_RULES)))
    assert run.returncode == 0, run.stdout + run.stderr
    assert "DRY_RUN=ROLLED_BACK" in run.stdout
    assert _published(isolated_db) == "0"
    assert (
        _psql(isolated_db, "select count(*) from media_assets where publication_permission;") == "0"
    )


@_PG
def test_rerun_is_idempotent(isolated_db: str, tmp_path: Path) -> None:
    _seed(isolated_db)
    clearance = str(_clearance(tmp_path, DEFAULT_RULES))
    first = _run_publish(isolated_db, "--clearance-file", clearance, "--commit")
    assert first.returncode == 0, first.stdout + first.stderr
    second = _run_publish(isolated_db, "--clearance-file", clearance, "--commit")
    assert second.returncode == 0, second.stdout + second.stderr
    assert "ALREADY_PUBLISHED" in second.stdout
    assert _published(isolated_db) == "3"


@_PG
def test_expected_count_mismatch_fails_closed(isolated_db: str, tmp_path: Path) -> None:
    _seed(isolated_db)
    rules = [{"privacy_class": "P0", "prefix": "针灸甲乙经/", "expected_count": 99}]
    run = _run_publish(
        isolated_db, "--clearance-file", str(_clearance(tmp_path, rules)), "--commit"
    )
    assert run.returncode == 1
    assert "CLEARANCE=FAIL" in run.stdout
    assert _published(isolated_db) == "0"


@_PG
def test_p2_declaration_rejected(isolated_db: str, tmp_path: Path) -> None:
    _seed(isolated_db)
    rules = [{"privacy_class": "P2", "prefix": "非遗佐证/", "expected_count": 1}]
    run = _run_publish(
        isolated_db, "--clearance-file", str(_clearance(tmp_path, rules)), "--commit"
    )
    assert run.returncode == 1
    assert "CLEARANCE_FILE=FAIL" in run.stdout
    assert _published(isolated_db) == "0"


@_PG
def test_uncleared_published_asset_is_drift(isolated_db: str, tmp_path: Path) -> None:
    _seed(isolated_db)
    _psql(
        isolated_db,
        "update media_assets set publication_state='published', publication_permission=true "
        "where object_key='其他材料/extra.pdf';",
    )
    run = _run_publish(
        isolated_db,
        "--clearance-file",
        str(_clearance(tmp_path, DEFAULT_RULES)),
        "--commit",
    )
    assert run.returncode == 1
    assert "drift" in run.stdout
    # Fail-closed: the cleared assets were NOT published by the failed run.
    assert _published(isolated_db) == "1"


@_PG
def test_missing_clearance_file_fails(isolated_db: str) -> None:
    _seed(isolated_db)
    run = _run_publish(isolated_db, "--clearance-file", "/nonexistent/clearance.json")
    assert run.returncode == 1
    assert "CLEARANCE_FILE=FAIL" in run.stdout
    assert _published(isolated_db) == "0"
