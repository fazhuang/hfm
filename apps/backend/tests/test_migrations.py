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


def test_migration_existing_cd3_db_upgrade_to_0005(tmp_path: Path) -> None:
    """CD-4 migration must upgrade an existing CD-3 database in place."""
    db_file = tmp_path / "cd3-existing.db"
    assert _alembic(db_file, "upgrade", "0004").returncode == 0
    before = _tables(db_file)
    assert "assertions" not in before
    assert "assertion_evidences" not in before
    assert _alembic(db_file, "upgrade", "head").returncode == 0
    after = _tables(db_file)
    assert {"assertions", "assertion_evidences"} <= after
    assert "evidences" in after  # CD-3 preserved
    cols = _columns(db_file, "assertions")
    assert {
        "id",
        "subject_entity_id",
        "predicate",
        "value",
        "object_entity_id",
        "assertion_type",
        "editorial_status",
    } <= cols
    join_cols = _columns(db_file, "assertion_evidences")
    assert {"assertion_id", "evidence_id"} <= join_cols


def test_migration_0005_downgrade_preserves_cd3(tmp_path: Path) -> None:
    """Downgrading 0005 drops assertion tables but keeps CD-0/1/2/3 tables."""
    db_file = tmp_path / "cd4-downgrade.db"
    assert _alembic(db_file, "upgrade", "head").returncode == 0
    result = _alembic(db_file, "downgrade", "0004")
    assert result.returncode == 0, result.stderr
    tables = _tables(db_file)
    assert not {"assertions", "assertion_evidences"} & tables
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
        "evidences",
    } <= tables


def test_migration_existing_cd4_db_upgrade_to_0006(tmp_path: Path) -> None:
    """CD-5 migration must upgrade an existing CD-4 database in place."""
    db_file = tmp_path / "cd4-existing.db"
    assert _alembic(db_file, "upgrade", "0005").returncode == 0
    before = _tables(db_file)
    assert "citations" not in before
    assert _alembic(db_file, "upgrade", "head").returncode == 0
    after = _tables(db_file)
    assert "citations" in after
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
        "evidences",
        "assertions",
        "assertion_evidences",
    } <= after
    cols = _columns(db_file, "citations")
    assert {
        "id",
        "target_assertion_id",
        "evidence_id",
        "version_id",
        "passage_id",
        "quote_text",
    } <= cols


def test_migration_0006_downgrade_preserves_cd4(tmp_path: Path) -> None:
    """Downgrading 0006 drops citations but keeps CD-0/1/2/3/4 tables."""
    db_file = tmp_path / "cd5-downgrade.db"
    assert _alembic(db_file, "upgrade", "head").returncode == 0
    result = _alembic(db_file, "downgrade", "0005")
    assert result.returncode == 0, result.stderr
    tables = _tables(db_file)
    assert "citations" not in tables
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
        "evidences",
        "assertions",
        "assertion_evidences",
    } <= tables


def test_migration_0007_withdrawal_columns(tmp_path: Path) -> None:
    """0007 adds withdrawn_at to sources/versions; downgrade removes them."""
    db_file = tmp_path / "cd6-withdrawal.db"
    assert _alembic(db_file, "upgrade", "head").returncode == 0
    assert "withdrawn_at" in _columns(db_file, "sources")
    assert "withdrawn_at" in _columns(db_file, "versions")
    result = _alembic(db_file, "downgrade", "0006")
    assert result.returncode == 0, result.stderr
    assert "withdrawn_at" not in _columns(db_file, "sources")
    assert "withdrawn_at" not in _columns(db_file, "versions")


def test_migration_0008_event_tables(tmp_path: Path) -> None:
    """0008 adds events/event_relations/event_assertions; downgrade removes them."""
    db_file = tmp_path / "cd7-event.db"
    assert _alembic(db_file, "upgrade", "head").returncode == 0
    tables = _tables(db_file)
    assert {"events", "event_relations", "event_assertions"} <= tables
    assert {
        "entity_id",
        "event_type",
        "start_year",
        "start_month",
        "start_day",
        "start_precision",
        "start_approximate",
        "end_year",
        "end_month",
        "end_day",
        "end_precision",
        "end_approximate",
    } <= _columns(db_file, "events")
    result = _alembic(db_file, "downgrade", "0007")
    assert result.returncode == 0, result.stderr
    tables = _tables(db_file)
    assert "event_assertions" not in tables
    assert "event_relations" not in tables
    assert "events" not in tables


def test_migration_0008_fresh_chain_preserves_history(tmp_path: Path) -> None:
    """0001 → head still works after 0008; CD-0/1/2/3/4/5 tables preserved."""
    db_file = tmp_path / "cd7-chain.db"
    assert _alembic(db_file, "upgrade", "head").returncode == 0
    tables = _tables(db_file)
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
        "evidences",
        "assertions",
        "assertion_evidences",
        "citations",
        "events",
        "event_relations",
        "event_assertions",
    } <= tables
    # constraint names survive in SQLite (probe table attributes)
    engine = sa.create_engine(f"sqlite:///{db_file}")
    try:
        inspector = sa.inspect(engine)
        ev_checks = {c["name"] for c in inspector.get_check_constraints("events")}
        assert "ck_events_start_le_end" in ev_checks
        assert "ck_events_start_consistency" in ev_checks
        rel_checks = {c["name"] for c in inspector.get_check_constraints("event_relations")}
        assert "ck_event_relations_not_self" in rel_checks
    finally:
        engine.dispose()


def test_migration_0009_content_artifacts(tmp_path: Path) -> None:
    """0009 adds content_artifacts; downgrade removes them; 0001→head works."""
    db_file = tmp_path / "p1-admission.db"
    assert _alembic(db_file, "upgrade", "head").returncode == 0
    tables = _tables(db_file)
    assert "content_artifacts" in tables
    assert {
        "source_id",
        "content_hash",
        "provenance_status",
        "rights_status",
        "validation_result",
        "admission_state",
        "rejection_reason",
        "version_id",
    } <= _columns(db_file, "content_artifacts")
    engine = sa.create_engine(f"sqlite:///{db_file}")
    try:
        inspector = sa.inspect(engine)
        checks = {c["name"] for c in inspector.get_check_constraints("content_artifacts")}
        assert "ck_content_artifacts_rejection_has_reason" in checks
        assert "ck_content_artifacts_source_present" in checks
        uniques = {c["name"] for c in inspector.get_unique_constraints("content_artifacts")}
        assert "uq_content_artifacts_source_hash" in uniques
    finally:
        engine.dispose()
    result = _alembic(db_file, "downgrade", "0008")
    assert result.returncode == 0, result.stderr
    assert "content_artifacts" not in _tables(db_file)
