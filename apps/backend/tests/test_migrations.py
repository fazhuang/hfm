"""Migration gate tests (CD-0): fresh upgrade + downgrade + schema shape.

Runs Alembic in a subprocess against an isolated SQLite file so the
environment (HFM_DATABASE_URL) is clean.
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
        timeout=120,
    )


def _tables(db_file: Path) -> set[str]:
    engine = sa.create_engine(f"sqlite:///{db_file}")
    try:
        inspector = sa.inspect(engine)
        return set(inspector.get_table_names())
    finally:
        engine.dispose()


def _columns(db_file: Path, table: str) -> set[str]:
    engine = sa.create_engine(f"sqlite:///{db_file}")
    try:
        inspector = sa.inspect(engine)
        return {col["name"] for col in inspector.get_columns(table)}
    finally:
        engine.dispose()


def test_fresh_db_migration_upgrade(tmp_path: Path) -> None:
    db_file = tmp_path / "cd0-fresh.db"
    result = _alembic(db_file, "upgrade", "head")
    assert result.returncode == 0, result.stderr

    tables = _tables(db_file)
    assert {"sources", "source_refs", "institutions"} <= tables
    assert "alembic_version" in tables

    assert {
        "id",
        "source_key",
        "source_type",
        "source_uri",
        "rights_basis",
        "allowed_scope",
        "created_at",
    } <= _columns(db_file, "sources")
    assert {"id", "source_id", "title", "locator"} <= _columns(db_file, "source_refs")
    assert {"id", "name", "type", "status"} <= _columns(db_file, "institutions")


def test_migration_downgrade_drops_tables(tmp_path: Path) -> None:
    db_file = tmp_path / "cd0-downgrade.db"
    assert _alembic(db_file, "upgrade", "head").returncode == 0
    result = _alembic(db_file, "downgrade", "base")
    assert result.returncode == 0, result.stderr
    assert not {"sources", "source_refs", "institutions"} & _tables(db_file)


def test_migration_idempotent_replay_same_state(tmp_path: Path) -> None:
    """Re-running upgrade head on the same DB is a no-op (alembic version pin)."""
    db_file = tmp_path / "cd0-replay.db"
    assert _alembic(db_file, "upgrade", "head").returncode == 0
    first = _tables(db_file)
    assert _alembic(db_file, "upgrade", "head").returncode == 0
    assert _tables(db_file) == first


def test_migration_existing_cd0_db_upgrade_to_0002(tmp_path: Path) -> None:
    """CD-1 migration must upgrade an existing CD-0 database in place."""
    db_file = tmp_path / "cd0-existing.db"
    assert _alembic(db_file, "upgrade", "0001").returncode == 0
    before = _tables(db_file)
    assert "entities" not in before
    assert "persons" not in before
    assert _alembic(db_file, "upgrade", "head").returncode == 0
    after = _tables(db_file)
    assert {"entities", "persons"} <= after
    # CD-0 tables preserved
    assert {"sources", "source_refs", "institutions"} <= after
    # CD-1 schema shape
    assert {"id", "entity_type", "name"} <= _columns(db_file, "entities")
    assert {"entity_id", "domain_status", "dynasty"} <= _columns(db_file, "persons")


def test_migration_0002_downgrade_preserves_cd0(tmp_path: Path) -> None:
    """Downgrading 0002 drops CD-1 tables but keeps CD-0 tables."""
    db_file = tmp_path / "cd1-downgrade.db"
    assert _alembic(db_file, "upgrade", "head").returncode == 0
    result = _alembic(db_file, "downgrade", "0001")
    assert result.returncode == 0, result.stderr
    tables = _tables(db_file)
    assert not {"entities", "persons"} & tables
    assert {"sources", "source_refs", "institutions"} <= tables


def test_migration_existing_cd1_db_upgrade_to_0003(tmp_path: Path) -> None:
    """CD-2 migration must upgrade an existing CD-1 database in place."""
    db_file = tmp_path / "cd1-existing.db"
    assert _alembic(db_file, "upgrade", "0002").returncode == 0
    before = _tables(db_file)
    assert "works" not in before
    assert "passages" not in before
    assert _alembic(db_file, "upgrade", "head").returncode == 0
    after = _tables(db_file)
    assert {"works", "editions", "versions", "chapters", "passages"} <= after
    # CD-0 / CD-1 tables preserved
    assert {"sources", "source_refs", "institutions", "entities", "persons"} <= after
    assert {"id", "title", "author_entity_id"} <= _columns(db_file, "works")
    assert {"id", "work_id", "edition_name"} <= _columns(db_file, "editions")
    assert {"id", "edition_id", "version_name", "parent_version_id"} <= _columns(
        db_file, "versions"
    )
    assert {"id", "work_id", "parent_id", "title"} <= _columns(db_file, "chapters")
    assert {"id", "chapter_id", "version_id", "content_text"} <= _columns(db_file, "passages")


def test_migration_0003_downgrade_preserves_cd1(tmp_path: Path) -> None:
    """Downgrading 0003 drops CD-2 tables but keeps CD-0/CD-1 tables."""
    db_file = tmp_path / "cd2-downgrade.db"
    assert _alembic(db_file, "upgrade", "head").returncode == 0
    result = _alembic(db_file, "downgrade", "0002")
    assert result.returncode == 0, result.stderr
    tables = _tables(db_file)
    assert not {"works", "editions", "versions", "chapters", "passages"} & tables
    assert {"sources", "source_refs", "institutions", "entities", "persons"} <= tables


def test_migration_existing_cd2_db_upgrade_to_0004(tmp_path: Path) -> None:
    """CD-3 migration must upgrade an existing CD-2 database in place."""
    db_file = tmp_path / "cd2-existing.db"
    assert _alembic(db_file, "upgrade", "0003").returncode == 0
    before = _tables(db_file)
    assert "evidences" not in before
    assert _alembic(db_file, "upgrade", "head").returncode == 0
    after = _tables(db_file)
    assert "evidences" in after
    # CD-0/CD-1/CD-2 tables preserved
    assert {
        "sources",
        "source_refs",
        "institutions",
        "entities",
        "persons",
        "works",
        "editions",
        "versions",
        "chapters",
        "passages",
    } <= after
    cols = _columns(db_file, "evidences")
    assert {
        "id",
        "description",
        "evidence_level",
        "source_ref_id",
        "source_passage_id",
        "content_hash",
        "taint_status",
    } <= cols


def test_migration_0004_downgrade_preserves_cd2(tmp_path: Path) -> None:
    """Downgrading 0004 drops the evidences table but keeps CD-0/1/2 tables."""
    db_file = tmp_path / "cd3-downgrade.db"
    assert _alembic(db_file, "upgrade", "head").returncode == 0
    result = _alembic(db_file, "downgrade", "0003")
    assert result.returncode == 0, result.stderr
    tables = _tables(db_file)
    assert "evidences" not in tables
    assert {
        "sources",
        "source_refs",
        "institutions",
        "entities",
        "persons",
        "works",
        "editions",
        "versions",
        "chapters",
        "passages",
    } <= tables
