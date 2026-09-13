# mypy: disable-error-code="import-untyped,import-not-found"
# pyright: reportMissingImports=false
# File-level suppression keeps the per-file guard green (repo convention).
"""DOCUMENTS importer tests (B05 — minimal PostgreSQL importer, guard + transaction).

T01..T10 map to the development spec. Guards are proven against a real SQLite
engine (no mocks on the transaction path); the PostgreSQL-specific identity
classification is unit-tested so Pi can point these same cases at a disposable
PostgreSQL database for real integration verification.
"""

from __future__ import annotations

import csv
import io
import sys
from pathlib import Path
from typing import Any, cast

from sqlalchemy import Table, text
from sqlalchemy.ext.asyncio import create_async_engine

REPO_ROOT = Path(__file__).resolve().parents[3]
TOOLS_DIR = REPO_ROOT / "content-production" / "import" / "B05" / "tools"
PKG_DIR = REPO_ROOT / "content-production" / "import" / "B05" / "package"
sys.path.insert(0, str(TOOLS_DIR))

import hfm_import_documents as imp  # noqa: E402

from hfm.models.document import ContentDocument  # noqa: E402

#: Authoritative frozen digest recorded in package/checksums.sha256.
FROZEN_SHA256 = "27bccdd6cf9bb610de694bc88ae83bea8db532ba8146226e6ebcf56c98048da7"

COLUMNS = [
    "DOCUMENT_ID",
    "TITLE_ORIGINAL",
    "TITLE_NORMALIZED",
    "AUTHOR_ORIGINAL",
    "AUTHOR_NORMALIZED",
    "PUBLICATION",
    "YEAR",
    "DOCUMENT_TYPE",
    "LANGUAGE",
    "EDITION",
    "SOURCE_ASSET_ID",
    "SOURCE_PAGES",
    "SHA256",
    "PROCESSING_STATUS",
    "REVIEW_STATUS",
]


def _csv_bytes(rows: list[dict[str, str]]) -> bytes:
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=COLUMNS, extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    return buf.getvalue().encode("utf-8")


def _rows(n: int = 3) -> list[dict[str, str]]:
    return [
        {
            "DOCUMENT_ID": f"DOC-{i:03d}",
            "TITLE_ORIGINAL": f"标题 {i}",
            "LANGUAGE": "ZH",
            "SOURCE_ASSET_ID": f"ASSET-{i:03d}",
        }
        for i in range(n)
    ]


async def _migrated_sqlite_url(tmp_path: Path, head: str = "0017") -> str:
    """Create a SQLite file with the documents table + alembic_version at ``head``."""
    db = tmp_path / "imp.db"
    url = f"sqlite+aiosqlite:///{db}"
    engine = create_async_engine(url)
    try:
        async with engine.begin() as conn:
            documents_table = cast(Table, ContentDocument.__table__)
            await conn.run_sync(documents_table.create)
            await conn.execute(
                text("CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL PRIMARY KEY)")
            )
            await conn.execute(
                text("INSERT INTO alembic_version (version_num) VALUES (:v)"), {"v": head}
            )
    finally:
        await engine.dispose()
    return url


async def _count_documents(url: str) -> int:
    engine = create_async_engine(url)
    try:
        async with engine.connect() as conn:
            return int((await conn.execute(text("SELECT count(*) FROM documents"))).scalar_one())
    finally:
        await engine.dispose()


def _write_csv(tmp_path: Path, rows: list[dict[str, str]]) -> Path:
    p = tmp_path / "documents.csv"
    p.write_bytes(_csv_bytes(rows))
    return p


# --- T01: checksum mismatch -> refuse before write ---------------------------------


async def test_T01_checksum_mismatch_refuses_before_write(tmp_path: Path) -> None:
    url = await _migrated_sqlite_url(tmp_path)
    csv_path = _write_csv(tmp_path, _rows(3))
    summary = await imp.run_import(
        csv_path=csv_path,
        database_url=url,
        expected_sha256="0" * 64,
        expected_count=3,
        allow_hfm_prod=False,
        env="development",
    )
    assert summary.transaction_result == "REFUSED_INPUT_HASH"
    assert summary.input_hash_guard == "FAIL"
    assert summary.inserted == 0
    assert await _count_documents(url) == 0


# --- T02: expected count mismatch -> refuse before write ---------------------------


async def test_T02_count_mismatch_refuses_before_write(tmp_path: Path) -> None:
    url = await _migrated_sqlite_url(tmp_path)
    csv_path = _write_csv(tmp_path, _rows(3))
    sha = imp.sha256_of_bytes(csv_path.read_bytes())
    summary = await imp.run_import(
        csv_path=csv_path,
        database_url=url,
        expected_sha256=sha,
        expected_count=99,
        allow_hfm_prod=False,
        env="development",
    )
    assert summary.transaction_result == "REFUSED_INPUT_COUNT"
    assert summary.input_count_guard == "FAIL"
    assert summary.inserted == 0
    assert await _count_documents(url) == 0


# --- T03: duplicate stable_id in input -> refuse before write ----------------------


async def test_T03_duplicate_stable_id_refuses_before_write(tmp_path: Path) -> None:
    url = await _migrated_sqlite_url(tmp_path)
    rows = _rows(3)
    rows.append({"DOCUMENT_ID": "DOC-000", "TITLE_ORIGINAL": "dup"})
    csv_path = _write_csv(tmp_path, rows)
    sha = imp.sha256_of_bytes(csv_path.read_bytes())
    summary = await imp.run_import(
        csv_path=csv_path,
        database_url=url,
        expected_sha256=sha,
        expected_count=4,
        allow_hfm_prod=False,
        env="development",
    )
    assert summary.transaction_result == "REFUSED_INPUT_IDENTITY"
    assert summary.input_identity_guard == "FAIL"
    assert summary.duplicates == 1
    assert summary.inserted == 0
    assert await _count_documents(url) == 0


# --- T04: missing required field -> refuse before write ----------------------------


async def test_T04_missing_required_field_refuses_before_write(tmp_path: Path) -> None:
    url = await _migrated_sqlite_url(tmp_path)
    rows = _rows(2)
    rows.append({"DOCUMENT_ID": "DOC-999", "TITLE_ORIGINAL": ""})
    csv_path = _write_csv(tmp_path, rows)
    sha = imp.sha256_of_bytes(csv_path.read_bytes())
    summary = await imp.run_import(
        csv_path=csv_path,
        database_url=url,
        expected_sha256=sha,
        expected_count=3,
        allow_hfm_prod=False,
        env="development",
    )
    assert summary.transaction_result == "REFUSED_REQUIRED_FIELD"
    assert summary.required_field_guard == "FAIL"
    assert summary.invalid_rows == 1
    assert summary.inserted == 0
    assert await _count_documents(url) == 0


# --- T05: unsupported / non-PostgreSQL production target -> refuse -----------------


def test_T05_target_classification_and_non_postgres_production() -> None:
    assert imp.classify_target("postgresql", "hfm_prod") == "PRODUCTION"
    assert imp.classify_target("postgresql", "scratch") == "DISPOSABLE_POSTGRESQL"
    assert imp.classify_target("sqlite", "hfm_prod") == "SQLITE"
    assert imp.classify_target("mysql", "hfm_prod") == "UNKNOWN"
    # A non-PostgreSQL engine can never satisfy the production authorization gate.
    assert (
        imp.production_authorized(
            env="prod",
            backend="sqlite",
            actual_db_name="hfm_prod",
            allow_hfm_prod=True,
            expected_sha256="x" * 64,
            expected_count=675,
        )
        is False
    )


async def test_T05_unsupported_engine_refuses(tmp_path: Path, monkeypatch: Any) -> None:
    url = await _migrated_sqlite_url(tmp_path)
    csv_path = _write_csv(tmp_path, _rows(3))
    sha = imp.sha256_of_bytes(csv_path.read_bytes())
    monkeypatch.setattr(imp, "classify_target", lambda backend, name: "UNKNOWN")
    summary = await imp.run_import(
        csv_path=csv_path,
        database_url=url,
        expected_sha256=sha,
        expected_count=3,
        allow_hfm_prod=False,
        env="development",
    )
    assert summary.transaction_result == "REFUSED_TARGET_IDENTITY"
    assert summary.inserted == 0
    assert await _count_documents(url) == 0


# --- T06: hfm_prod without explicit authorization -> refuse -------------------------


def test_T06_production_authorization_requires_all_conditions() -> None:
    base: dict[str, Any] = dict(
        env="prod",
        backend="postgresql",
        actual_db_name="hfm_prod",
        allow_hfm_prod=True,
        expected_sha256="x" * 64,
        expected_count=675,
    )
    assert imp.production_authorized(**base) is True
    for drop in ("allow_hfm_prod", "env", "backend", "actual_db_name", "expected_sha256"):
        kwargs = dict(base)
        kwargs[drop] = (
            "" if drop in ("env", "backend", "actual_db_name", "expected_sha256") else False
        )
        assert imp.production_authorized(**kwargs) is False, drop
    assert imp.production_authorized(**{**base, "env": "development"}) is False
    assert imp.production_authorized(**{**base, "expected_count": 100}) is False
    assert imp.production_authorized(**{**base, "actual_db_name": "scratch"}) is False


async def test_T06_hfm_prod_without_authorization_refuses(tmp_path: Path, monkeypatch: Any) -> None:
    url = await _migrated_sqlite_url(tmp_path)
    csv_path = _write_csv(tmp_path, _rows(3))
    sha = imp.sha256_of_bytes(csv_path.read_bytes())

    async def _fake_name(conn: Any, backend: str, url_obj: Any) -> str:
        return "hfm_prod"

    monkeypatch.setattr(imp, "actual_database_name", _fake_name)
    monkeypatch.setattr(imp, "classify_target", lambda backend, name: "PRODUCTION")
    summary = await imp.run_import(
        csv_path=csv_path,
        database_url=url,
        expected_sha256=sha,
        expected_count=3,
        allow_hfm_prod=False,
        env="development",
    )
    assert summary.transaction_result == "REFUSED_HFM_PROD"
    assert summary.hfm_prod_default_refusal == "REFUSED"
    assert summary.inserted == 0
    assert await _count_documents(url) == 0


# --- T07: wrong migration head -> refuse before write ------------------------------


async def test_T07_wrong_migration_head_refuses(tmp_path: Path) -> None:
    url = await _migrated_sqlite_url(tmp_path, head="0014")
    csv_path = _write_csv(tmp_path, _rows(3))
    sha = imp.sha256_of_bytes(csv_path.read_bytes())
    summary = await imp.run_import(
        csv_path=csv_path,
        database_url=url,
        expected_sha256=sha,
        expected_count=3,
        allow_hfm_prod=False,
        env="development",
    )
    assert summary.transaction_result == "REFUSED_MIGRATION_HEAD"
    assert summary.migration_head_guard == "FAIL"
    assert summary.inserted == 0
    assert await _count_documents(url) == 0


# --- T08: forced NON-duplicate transaction failure -> rollback, DUPLICATES=0 ---------


async def test_T08_generic_rollback_reports_zero_duplicates(
    tmp_path: Path, monkeypatch: Any
) -> None:
    url = await _migrated_sqlite_url(tmp_path)
    engine = create_async_engine(url)
    rows = _rows(3)
    # Inject a NON-duplicate failure (NOT NULL violation on title) so the generic
    # rollback branch is exercised and must NOT mislabel it as duplicates.
    monkeypatch.setattr(
        imp,
        "_build_document",
        lambda row: ContentDocument(stable_id=row["DOCUMENT_ID"], title=None),
    )
    try:
        result, inserted, duplicates = await imp.insert_documents_transaction(engine, rows)
    finally:
        await engine.dispose()
    assert result == "ROLLED_BACK"
    assert inserted == 0
    assert duplicates == 0
    assert await _count_documents(url) == 0


async def test_T08_generic_rollback_summary_duplicates_zero(
    tmp_path: Path, monkeypatch: Any
) -> None:
    url = await _migrated_sqlite_url(tmp_path)
    rows = _rows(3)
    csv_path = _write_csv(tmp_path, rows)
    sha = imp.sha256_of_bytes(csv_path.read_bytes())
    monkeypatch.setattr(
        imp,
        "_build_document",
        lambda row: ContentDocument(stable_id=row["DOCUMENT_ID"], title=None),
    )
    summary = await imp.run_import(
        csv_path=csv_path,
        database_url=url,
        expected_sha256=sha,
        expected_count=3,
        allow_hfm_prod=False,
        env="development",
    )
    assert summary.transaction_result == "ROLLED_BACK"
    assert summary.inserted == 0
    assert summary.duplicates == 0
    assert summary.failed == 3
    assert await _count_documents(url) == 0


# --- T09: duplicate / rerun -> no duplicate pollution -------------------------------


async def test_T09_rerun_rejects_duplicate_and_adds_no_rows(tmp_path: Path) -> None:
    url = await _migrated_sqlite_url(tmp_path)
    rows = _rows(3)
    csv_path = _write_csv(tmp_path, rows)
    sha = imp.sha256_of_bytes(csv_path.read_bytes())

    first = await imp.run_import(
        csv_path=csv_path,
        database_url=url,
        expected_sha256=sha,
        expected_count=3,
        allow_hfm_prod=False,
        env="development",
    )
    assert first.transaction_result == "COMMITTED"
    assert first.inserted == 3
    assert first.reconciliation_expected == 3
    assert first.reconciliation_actual == 3
    assert first.missing == 0
    assert first.unexpected == 0

    second = await imp.run_import(
        csv_path=csv_path,
        database_url=url,
        expected_sha256=sha,
        expected_count=3,
        allow_hfm_prod=False,
        env="development",
    )
    assert second.transaction_result == "REJECTED_DUPLICATE"
    assert second.inserted == 0
    assert second.duplicates == 3
    assert second.failed == 0
    assert await _count_documents(url) == 3


# --- T10: reconciliation -> exact identity-set comparison ---------------------------


async def test_T10_reconciliation_exact_identity_set(tmp_path: Path) -> None:
    url = await _migrated_sqlite_url(tmp_path)
    engine = create_async_engine(url)
    try:
        async with engine.begin() as conn:
            # Real schema: stable_id is unique (so duplicate groups are structurally 0)
            # and title is NOT NULL. Both metrics are defensive; they report 0 here.
            for sid, title in [("DOC-1", "a"), ("DOC-2", "b"), (None, "c")]:
                await conn.execute(
                    text(
                        "INSERT INTO documents (id, stable_id, title, created_at, updated_at) "
                        "VALUES (:id, :sid, :title, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
                    ),
                    {"id": f"id-{sid}-{title}", "sid": sid, "title": title},
                )
    finally:
        await engine.dispose()

    rec_engine = create_async_engine(url)
    try:
        rec = await imp.reconcile(rec_engine, {"DOC-1", "DOC-3"})
    finally:
        await rec_engine.dispose()
    assert rec["expected"] == 2
    assert rec["actual"] == 2  # DOC-1, DOC-2 (non-null stable_ids)
    assert rec["missing"] == 1  # DOC-3
    assert rec["unexpected"] == 1  # DOC-2
    assert rec["duplicate_groups"] == 0
    assert rec["null_stable_id"] == 1
    assert rec["null_title"] == 0


# --- Real frozen package end-to-end (SQLite) ----------------------------------------


async def test_frozen_package_imports_and_is_idempotent(tmp_path: Path) -> None:
    pkg_csv = PKG_DIR / "documents.csv"
    frozen_sha = imp.sha256_of_bytes(pkg_csv.read_bytes())
    assert frozen_sha == FROZEN_SHA256  # guard against accidental CSV modification

    url = await _migrated_sqlite_url(tmp_path)
    first = await imp.run_import(
        csv_path=pkg_csv,
        database_url=url,
        expected_sha256=frozen_sha,
        expected_count=675,
        allow_hfm_prod=False,
        env="development",
    )
    assert first.transaction_result == "COMMITTED"
    assert first.inserted == 675
    assert first.duplicates == 0
    assert first.failed == 0
    assert first.reconciliation_expected == 675
    assert first.reconciliation_actual == 675
    assert first.missing == 0
    assert first.unexpected == 0
    assert first.null_stable_id == 0
    assert first.null_title == 0

    second = await imp.run_import(
        csv_path=pkg_csv,
        database_url=url,
        expected_sha256=frozen_sha,
        expected_count=675,
        allow_hfm_prod=False,
        env="development",
    )
    assert second.transaction_result == "REJECTED_DUPLICATE"
    assert second.inserted == 0
    assert await _count_documents(url) == 675
