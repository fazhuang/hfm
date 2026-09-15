# mypy: disable-error-code="import-untyped,import-not-found"
# pyright: reportMissingImports=false
# File-level suppression keeps the per-file guard green (repo convention).
"""Content import schema support tests (B05-SG-R2 — migration 0015)."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest
import sqlalchemy as sa
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool

import hfm.models.document  # noqa: F401
import hfm.models.edition  # noqa: F401
import hfm.models.evidence  # noqa: F401
import hfm.models.person  # noqa: F401
import hfm.models.work  # noqa: F401
from hfm.db.base import Base
from hfm.models.document import ContentDocument
from hfm.models.person import Person, PersonAlias

BACKEND_DIR = Path(__file__).resolve().parent.parent


def _alembic(db_file: Path, *args: str) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "HFM_DATABASE_URL": f"sqlite+aiosqlite:///{db_file}"}
    return subprocess.run(
        [sys.executable, "-m", "alembic", "-c", "alembic.ini", *args],
        cwd=str(BACKEND_DIR),
        env=env,
        capture_output=True,
        text=True,
        timeout=180,
    )


def _tables(db_file: Path) -> set[str]:
    engine = sa.create_engine(f"sqlite:///{db_file}")
    try:
        return set(sa.inspect(engine).get_table_names())
    finally:
        engine.dispose()


def _columns(db_file: Path, table: str) -> set[str]:
    engine = sa.create_engine(f"sqlite:///{db_file}")
    try:
        return {c["name"] for c in sa.inspect(engine).get_columns(table)}
    finally:
        engine.dispose()


def test_migration_0015_single_head_and_fresh_replay(tmp_path: Path) -> None:
    heads = _alembic(tmp_path / "h.db", "heads")
    assert heads.returncode == 0, heads.stderr
    lines = [ln for ln in heads.stdout.splitlines() if ln.strip()]
    assert len(lines) == 1 and lines[0].startswith("0017"), lines

    db_file = tmp_path / "fresh-0015.db"
    up = _alembic(db_file, "upgrade", "head")
    assert up.returncode == 0, up.stderr
    tables = _tables(db_file)
    assert "documents" in tables
    assert "person_aliases" in tables
    assert {"stable_id", "title", "title_normalized", "source_asset_id"} <= _columns(
        db_file, "documents"
    )
    assert {
        "person_id",
        "alias",
        "alias_type",
        "source_asset_id",
        "source_location",
    } <= _columns(db_file, "person_aliases")
    for table in ("persons", "works", "editions", "evidences"):
        assert "stable_id" in _columns(db_file, table), table


def test_migration_0015_downgrade_restores_0014(tmp_path: Path) -> None:
    db_file = tmp_path / "down.db"
    assert _alembic(db_file, "upgrade", "head").returncode == 0
    down = _alembic(db_file, "downgrade", "0014")
    assert down.returncode == 0, down.stderr
    tables = _tables(db_file)
    assert "documents" not in tables
    assert "person_aliases" not in tables
    assert "stable_id" not in _columns(db_file, "persons")


def _engine() -> Any:
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    return engine


async def test_content_document_stable_id_unique() -> None:
    engine = _engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with factory() as s:
        s.add(ContentDocument(stable_id="DOC-HFM-A000003", title="t1"))
        await s.commit()
        s.add(ContentDocument(stable_id="DOC-HFM-A000003", title="t2"))
        with pytest.raises(IntegrityError):
            await s.commit()
        await s.rollback()
    await engine.dispose()


async def test_person_alias_unique_constraint() -> None:
    engine = _engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with factory() as s:
        from hfm.models.entity import Entity, EntityType

        ent = Entity(entity_type=EntityType.person.value, name="皇甫谧")
        s.add(ent)
        await s.flush()
        person = Person(entity_id=ent.id, name_zh="皇甫谧")
        s.add(person)
        await s.flush()
        s.add(PersonAlias(person_id=person.entity_id, alias="士安", alias_type="zi"))
        await s.commit()
        s.add(PersonAlias(person_id=person.entity_id, alias="士安", alias_type="zi"))
        with pytest.raises(IntegrityError):
            await s.commit()
        await s.rollback()
        rows = (await s.execute(select(PersonAlias))).scalars().all()
        assert len(rows) == 1
    await engine.dispose()
