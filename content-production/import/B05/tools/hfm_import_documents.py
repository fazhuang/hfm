#!/usr/bin/env python3
"""HFM CONTENT-B05 — minimal DOCUMENTS PostgreSQL importer.

CONTENT IMPORT TOOLING (separate from product runtime; never auto-runs).

Targets the migration-0015 ``documents`` table only, from the frozen
``package/documents.csv``. Fails closed:

  * refuses the canonical ``hfm_prod`` database unless EVERY explicit
    production authorization condition is met;
  * verifies the target's real identity (engine + actual connected database
    name via ``current_database()``) rather than trusting the DSN string;
  * verifies the target is on the single expected migration head (0015);
  * writes all rows in ONE database transaction (all-or-nothing);
  * rejects a re-run of the same frozen package (REJECT_DUPLICATE) instead of
    creating duplicates;
  * emits a machine-readable KEY=VALUE summary that never contains a password,
    credential-bearing DSN, token, or secret.

Run against a DISPOSABLE PostgreSQL database only (never canonical hfm_prod
during development):

  apps/backend/.venv/bin/python hfm_import_documents.py \
      --csv package/documents.csv \
      --database-url postgresql+asyncpg://USER:PASS@127.0.0.1:5432/scratch \
      --expected-sha256 27bccdd6cf9bb610de694bc88ae83bea8db532ba8146226e6ebcf56c98048da7 \
      --expected-count 675
"""

from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import io
import os
import sys
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import func, select, text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from hfm.models.document import ContentDocument

EXPECTED_MIGRATION_HEAD = "0015"
PRODUCTION_DB = "hfm_prod"
#: Frozen B05 package size; production authorization additionally requires
#: ``--expected-count`` to equal this exact value.
FROZEN_DOCUMENT_COUNT = 675

#: Summary fields are emitted in this fixed order for stable machine parsing.
_SUMMARY_ORDER = [
    "INPUT_SHA256",
    "INPUT_ROWS",
    "VALID_ROWS",
    "INVALID_ROWS",
    "INSERT_ATTEMPTED",
    "INSERTED",
    "SKIPPED",
    "DUPLICATES",
    "FAILED",
    "TRANSACTION_RESULT",
    "DATABASE_ENGINE",
    "DATABASE_NAME",
    "DATABASE_TARGET_CLASS",
    "MIGRATION_CURRENT",
    "EXPECTED_MIGRATION_HEAD",
    "INPUT_HASH_GUARD",
    "INPUT_COUNT_GUARD",
    "INPUT_IDENTITY_GUARD",
    "REQUIRED_FIELD_GUARD",
    "DATABASE_IDENTITY_GUARD",
    "MIGRATION_HEAD_GUARD",
    "HFM_PROD_DEFAULT_REFUSAL",
    "EXPLICIT_HFM_PROD_AUTHORIZATION_REQUIRED",
    "RECONCILIATION_EXPECTED",
    "RECONCILIATION_ACTUAL",
    "MISSING",
    "UNEXPECTED",
    "DUPLICATE_GROUPS",
    "NULL_STABLE_ID",
    "NULL_TITLE",
]


class _DuplicateReject(Exception):
    """Internal signal: existing rows already hold some input stable_ids."""

    def __init__(self, count: int) -> None:
        super().__init__(count)
        self.count = count


@dataclass
class ImportSummary:
    """All machine-readable outcomes for one import/reconcile run."""

    input_sha256: str = ""
    input_rows: int = 0
    valid_rows: int = 0
    invalid_rows: int = 0
    insert_attempted: int = 0
    inserted: int = 0
    skipped: int = 0
    duplicates: int = 0
    failed: int = 0
    transaction_result: str = "NOT_RUN"
    database_engine: str = ""
    database_name: str = ""
    database_target_class: str = ""
    migration_current: str = ""
    expected_migration_head: str = EXPECTED_MIGRATION_HEAD
    input_hash_guard: str = ""
    input_count_guard: str = ""
    input_identity_guard: str = ""
    required_field_guard: str = ""
    database_identity_guard: str = ""
    migration_head_guard: str = ""
    hfm_prod_default_refusal: str = ""
    explicit_hfm_prod_authorization_required: str = "YES"
    reconciliation_expected: int = 0
    reconciliation_actual: int = 0
    missing: int = 0
    unexpected: int = 0
    duplicate_groups: int = 0
    null_stable_id: int = 0
    null_title: int = 0

    def render(self) -> str:
        lines = [f"{key}={getattr(self, key.lower())}" for key in _SUMMARY_ORDER]
        return "\n".join(lines)

    def apply_reconciliation(self, rec: dict[str, int]) -> None:
        self.reconciliation_expected = rec["expected"]
        self.reconciliation_actual = rec["actual"]
        self.missing = rec["missing"]
        self.unexpected = rec["unexpected"]
        self.duplicate_groups = rec["duplicate_groups"]
        self.null_stable_id = rec["null_stable_id"]
        self.null_title = rec["null_title"]


def _field(row: dict[str, str], name: str) -> str | None:
    """Return a stripped CSV cell, or None when empty (B05 mapping)."""
    value = (row.get(name) or "").strip()
    return value or None


def _doc_id(row: dict[str, str]) -> str:
    return (row.get("DOCUMENT_ID") or "").strip()


def load_rows(csv_bytes: bytes) -> list[dict[str, str]]:
    """Parse the frozen package CSV (UTF-8 BOM tolerated)."""
    text_data = csv_bytes.decode("utf-8-sig")
    return list(csv.DictReader(io.StringIO(text_data)))


def sha256_of_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def validate_input(
    rows: list[dict[str, str]],
    expected_sha256: str,
    expected_count: int,
    actual_sha256: str,
) -> tuple[str, int, int, int]:
    """Run the four offline input guards; return (result, valid, invalid, duplicates).

    ``result`` is one of COMMITTED-eligible (""), REFUSED_INPUT_HASH,
    REFUSED_INPUT_COUNT, REFUSED_INPUT_IDENTITY, REFUSED_REQUIRED_FIELD.
    """
    if actual_sha256 != expected_sha256:
        return ("REFUSED_INPUT_HASH", 0, 0, 0)
    if len(rows) != expected_count:
        return ("REFUSED_INPUT_COUNT", 0, 0, 0)
    ids = [_doc_id(r) for r in rows]
    unique = set(ids)
    if len(unique) != len(ids):
        return ("REFUSED_INPUT_IDENTITY", 0, 0, len(ids) - len(unique))
    valid = 0
    invalid = 0
    for r in rows:
        if _doc_id(r) and (r.get("TITLE_ORIGINAL") or "").strip():
            valid += 1
        else:
            invalid += 1
    if invalid:
        return ("REFUSED_REQUIRED_FIELD", valid, invalid, 0)
    return ("", valid, invalid, 0)


def classify_target(backend: str, actual_db_name: str) -> str:
    """Map engine + actual connected database name to a target class."""
    if backend == "postgresql":
        return "PRODUCTION" if actual_db_name == PRODUCTION_DB else "DISPOSABLE_POSTGRESQL"
    if backend == "sqlite":
        return "SQLITE"
    return "UNKNOWN"


def production_authorized(
    *,
    env: str,
    backend: str,
    actual_db_name: str,
    allow_hfm_prod: bool,
    expected_sha256: str,
    expected_count: int,
) -> bool:
    """True only when every explicit hfm_prod write condition is satisfied."""
    return (
        env == "prod"
        and backend == "postgresql"
        and actual_db_name == PRODUCTION_DB
        and allow_hfm_prod
        and bool(expected_sha256)
        and expected_count == FROZEN_DOCUMENT_COUNT
    )


async def actual_database_name(conn, backend: str, url) -> str:
    """Resolve the REAL connected database name (PostgreSQL: current_database())."""
    if backend == "postgresql":
        return str((await conn.execute(text("SELECT current_database()"))).scalar_one())
    # SQLite has no server-side identity; report only the file basename to avoid
    # leaking a local filesystem path into the machine summary.
    if url.database:
        return Path(url.database).name
    return ":memory:"


async def current_migration_head(conn) -> list[str] | None:
    """Return the sorted alembic version_num rows, or None when absent."""
    try:
        rows = (await conn.execute(text("SELECT version_num FROM alembic_version"))).scalars().all()
        return sorted({str(r) for r in rows})
    except Exception:  # noqa: BLE001 — alembic_version may not exist on a raw target
        return None


def _build_document(row: dict[str, str]) -> ContentDocument:
    """Map a frozen CSV row to a ContentDocument (B05 mapping, verbatim)."""
    return ContentDocument(
        stable_id=_field(row, "DOCUMENT_ID"),
        title=_field(row, "TITLE_ORIGINAL") or "UNKNOWN",
        title_normalized=_field(row, "TITLE_NORMALIZED"),
        author_original=_field(row, "AUTHOR_ORIGINAL"),
        author_normalized=_field(row, "AUTHOR_NORMALIZED"),
        publication=_field(row, "PUBLICATION"),
        year=_field(row, "YEAR"),
        doc_type=_field(row, "DOCUMENT_TYPE"),
        language=_field(row, "LANGUAGE") or "zh",
        edition=_field(row, "EDITION"),
        source_asset_id=_field(row, "SOURCE_ASSET_ID"),
        source_pages=_field(row, "SOURCE_PAGES"),
        source_sha256=_field(row, "SHA256"),
        processing_status=_field(row, "PROCESSING_STATUS"),
        review_status=_field(row, "REVIEW_STATUS"),
    )


async def insert_documents_transaction(
    engine: AsyncEngine, rows: list[dict[str, str]]
) -> tuple[str, int, int]:
    """Write all rows in ONE transaction (all-or-nothing).

    Returns (result, inserted, duplicates). The third element is the TRUE
    duplicate count only: non-zero only for REJECTED_DUPLICATE (a re-run of an
    already-present package). A generic rollback reports duplicates=0 — it is a
    failure, not a duplicate.
    """
    factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with factory() as session:
        try:
            async with session.begin():
                existing = set(
                    (await session.execute(select(ContentDocument.stable_id))).scalars().all()
                )
                input_ids = {_doc_id(r) for r in rows}
                collisions = existing & input_ids
                if collisions:
                    raise _DuplicateReject(len(collisions))
                for r in rows:
                    session.add(_build_document(r))
                await session.flush()
            return ("COMMITTED", len(rows), 0)
        except _DuplicateReject as exc:
            return ("REJECTED_DUPLICATE", 0, exc.count)
        except Exception:  # noqa: BLE001 — any mid-transaction error must roll back cleanly
            return ("ROLLED_BACK", 0, 0)


async def reconcile(engine: AsyncEngine, expected_ids: set[str]) -> dict[str, int]:
    """Compare the manifest stable_id set against the live documents table."""
    expected = set(expected_ids)
    async with engine.connect() as conn:
        actual_rows = (await conn.execute(select(ContentDocument.stable_id))).scalars().all()
    actual_ids = [s for s in actual_rows if s is not None]
    actual = set(actual_ids)
    counter = collections.Counter(actual_ids)

    async with engine.connect() as conn:
        null_stable = (
            await conn.execute(
                select(func.count())
                .select_from(ContentDocument)
                .where(ContentDocument.stable_id.is_(None))
            )
        ).scalar_one()
        null_title = (
            await conn.execute(
                select(func.count())
                .select_from(ContentDocument)
                .where(ContentDocument.title.is_(None))
            )
        ).scalar_one()

    missing = expected.difference(actual)
    unexpected = actual.difference(expected)
    return {
        "expected": len(expected),
        "actual": len(actual),
        "missing": len(missing),
        "unexpected": len(unexpected),
        "duplicate_groups": sum(1 for v in counter.values() if v > 1),
        "null_stable_id": int(null_stable),
        "null_title": int(null_title),
    }


async def run_import(
    *,
    csv_path: Path,
    database_url: str,
    expected_sha256: str,
    expected_count: int,
    allow_hfm_prod: bool,
    env: str,
    reconcile_only: bool = False,
) -> ImportSummary:
    summary = ImportSummary()
    url = make_url(database_url)
    backend = url.get_backend_name()
    summary.database_engine = backend

    # --- offline input guards (no connection) ---
    # One-shot blocking read of the frozen CSV before any DB I/O (CLI tool).
    csv_bytes = csv_path.read_bytes()  # noqa: ASYNC240
    summary.input_sha256 = sha256_of_bytes(csv_bytes)
    rows = load_rows(csv_bytes)
    summary.input_rows = len(rows)
    summary.input_hash_guard = "PASS" if summary.input_sha256 == expected_sha256 else "FAIL"
    summary.input_count_guard = "PASS" if len(rows) == expected_count else "FAIL"

    result, valid, invalid, duplicates = validate_input(
        rows, expected_sha256, expected_count, summary.input_sha256
    )
    if result:
        summary.transaction_result = result
        summary.valid_rows = valid
        summary.invalid_rows = invalid
        summary.duplicates = duplicates
        summary.input_identity_guard = "FAIL" if result == "REFUSED_INPUT_IDENTITY" else "PASS"
        summary.required_field_guard = "FAIL" if result == "REFUSED_REQUIRED_FIELD" else "PASS"
        return summary

    summary.valid_rows = valid
    summary.invalid_rows = invalid
    summary.input_identity_guard = "PASS"
    summary.required_field_guard = "PASS"
    input_ids = {_doc_id(r) for r in rows}

    engine = create_async_engine(database_url, future=True)
    try:
        # --- online target-identity + migration-head guards (read-only) ---
        async with engine.connect() as conn:
            summary.database_name = await actual_database_name(conn, backend, url)
            summary.database_target_class = classify_target(backend, summary.database_name)
            summary.database_identity_guard = (
                "PASS" if summary.database_target_class != "UNKNOWN" else "FAIL"
            )
            if summary.database_target_class == "UNKNOWN":
                summary.transaction_result = "REFUSED_TARGET_IDENTITY"
                return summary

            if summary.database_target_class == "PRODUCTION":
                authorized = production_authorized(
                    env=env,
                    backend=backend,
                    actual_db_name=summary.database_name,
                    allow_hfm_prod=allow_hfm_prod,
                    expected_sha256=expected_sha256,
                    expected_count=expected_count,
                )
                summary.hfm_prod_default_refusal = "REFUSED" if not authorized else "AUTHORIZED"
                if not authorized:
                    summary.transaction_result = "REFUSED_HFM_PROD"
                    return summary

            heads = await current_migration_head(conn)
            summary.migration_current = ",".join(heads) if heads is not None else "<missing>"
            summary.migration_head_guard = "PASS" if heads == [EXPECTED_MIGRATION_HEAD] else "FAIL"
            if summary.migration_head_guard == "FAIL":
                summary.transaction_result = "REFUSED_MIGRATION_HEAD"
                return summary

        if reconcile_only:
            rec = await reconcile(engine, input_ids)
            summary.apply_reconciliation(rec)
            summary.transaction_result = "RECONCILED"
            return summary

        # --- single-transaction write ---
        summary.insert_attempted = len(rows)
        result, inserted, duplicates = await insert_documents_transaction(engine, rows)
        summary.transaction_result = result
        summary.inserted = inserted
        summary.duplicates = duplicates
        if result == "ROLLED_BACK":
            summary.failed = len(rows)

        if result == "COMMITTED":
            rec = await reconcile(engine, input_ids)
            summary.apply_reconciliation(rec)
    finally:
        await engine.dispose()

    return summary


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--csv", type=Path, required=True, help="frozen package documents.csv")
    ap.add_argument(
        "--database-url",
        required=True,
        help="SQLAlchemy async DSN (postgresql+asyncpg://... or sqlite+aiosqlite://...). "
        "Never logged.",
    )
    ap.add_argument(
        "--expected-sha256",
        required=True,
        help="authoritative SHA-256 of the CSV file (from package/checksums.sha256)",
    )
    ap.add_argument("--expected-count", type=int, required=True, help="expected row count")
    ap.add_argument(
        "--allow-hfm-prod",
        action="store_true",
        help="explicit production write authorization (requires HFM_ENV=prod + all guards)",
    )
    ap.add_argument(
        "--reconcile-only",
        action="store_true",
        help="verify the target against the manifest without writing anything",
    )
    args = ap.parse_args(argv)

    env = os.environ.get("HFM_ENV", "development")

    import asyncio

    summary = asyncio.run(
        run_import(
            csv_path=args.csv,
            database_url=args.database_url,
            expected_sha256=args.expected_sha256,
            expected_count=args.expected_count,
            allow_hfm_prod=args.allow_hfm_prod,
            env=env,
            reconcile_only=args.reconcile_only,
        )
    )

    print(summary.render())
    return 0 if summary.transaction_result == "COMMITTED" else 1


if __name__ == "__main__":
    sys.exit(main())
