#!/usr/bin/env python3
"""HFM 0018 follow-up — backfill ``media_assets.ledger_id`` from the register.

``documents.source_asset_id`` carries the customer register identifier
(``HFM-A000013``) while ``media_assets.id`` is a UUID, so nothing joined a
document to the media object it was extracted from. Migration 0018 adds the
``ledger_id`` column but deliberately does not fill it: the register in
``content-production/07-review/rights-review.csv`` owns those identifiers, and
an earlier attempt to derive them from object-key sort order produced 681
wrong values (the register's 689 rows include eight non-media files that
occupy numbering positions).

The register is the authority. This script reads it and copies the
identifier onto the matching row, keyed by ``object_key`` == ``RELATIVE_PATH``
(verified 1:1 for all 681 assets).

Idempotent: re-running sets the same values. Fail-closed: a single asset with
no register entry blocks the commit rather than leaving a partial join.

Usage:
    HFM_DATABASE_URL=<postgres DSN> python backfill-ledger-ids.py
    HFM_DATABASE_URL=<postgres DSN> python backfill-ledger-ids.py --commit

    # default is --dry-run (report only, nothing written)

Exit codes: 0 = PASS, 1 = FAIL (unresolved rows or write error), 2 = usage.
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import os
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = _SCRIPT_DIR.parent
BACKEND_DIR = REPO_ROOT / "apps" / "backend"

sys.path.insert(0, str(BACKEND_DIR / "src"))

from hfm.phase2.media.models import MediaAsset
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

DEFAULT_REGISTER = REPO_ROOT / "content-production" / "07-review" / "rights-review.csv"

#: Expected asset count for the customer dataset; a mismatch is reported but
#: not fatal, so the script also works on a subset.
EXPECTED_ASSETS = 681


def load_register(path: Path) -> dict[str, str]:
    """RELATIVE_PATH -> ASSET_ID. The CSV carries a UTF-8 BOM."""
    if not path.is_file():
        raise FileNotFoundError(f"register not found: {path}")
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    register = {row["RELATIVE_PATH"]: row["ASSET_ID"] for row in rows}
    if len(register) != len(rows):
        raise ValueError(
            f"register has duplicate RELATIVE_PATH entries ({len(rows)} rows)"
        )
    return register


async def run(register_path: Path, commit: bool) -> int:
    register = load_register(register_path)
    db_url = os.environ.get("HFM_DATABASE_URL", "")
    if not db_url:
        print("HFM_DATABASE_URL is not set")
        return 2

    engine = create_async_engine(db_url)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with session_factory() as session:
            assets = (
                await session.execute(
                    select(MediaAsset.id, MediaAsset.object_key, MediaAsset.ledger_id)
                )
            ).all()
            if not assets:
                print("LEDGER_BACKFILL=FAIL (no media_assets rows — wrong database?)")
                return 1

            updates: list[dict[str, str]] = []
            unchanged = 0
            unresolved: list[str] = []
            conflicting: list[str] = []

            for asset_id, object_key, current in assets:
                expected = register.get(object_key)
                if expected is None:
                    unresolved.append(object_key)
                    continue
                if current == expected:
                    unchanged += 1
                    continue
                if current is not None:
                    conflicting.append(f"{object_key}: {current} -> {expected}")
                updates.append({"ledger_id": expected, "id": asset_id})

            matched = len(assets) - len(unresolved)
            unused = len(register) - matched if matched <= len(register) else 0

            print(f"REGISTER_ROWS={len(register)}")
            print(f"ASSETS={len(assets)} (expected {EXPECTED_ASSETS})")
            print(f"MATCHED={matched}")
            print(f"UNCHANGED={unchanged}")
            print(f"TO_SET={len(updates)}")
            print(f"UNRESOLVED={len(unresolved)}")
            for key in unresolved[:20]:
                print(f"  unresolved: {key}")
            if conflicting:
                print(f"LEDGER_ID_CONFLICTS={len(conflicting)}")
                for line in conflicting[:20]:
                    print(f"  conflict: {line}")
            if unused > 0:
                print(f"REGISTER_ENTRIES_WITHOUT_ASSET={unused} (non-media files)")

            if unresolved:
                print(
                    "LEDGER_BACKFILL=FAIL (assets with no register entry; nothing written)"
                )
                return 1

            if not commit:
                print("LEDGER_BACKFILL=DRY_RUN (add --commit to write)")
                return 0

            if updates:
                await session.execute(
                    text(
                        "UPDATE media_assets SET ledger_id = :ledger_id WHERE id = :id"
                    ),
                    updates,
                )
            await session.commit()

            remaining = (
                await session.execute(
                    text("SELECT count(*) FROM media_assets WHERE ledger_id IS NULL")
                )
            ).scalar_one()
            distinct = (
                await session.execute(
                    text(
                        "SELECT count(DISTINCT ledger_id) FROM media_assets WHERE ledger_id IS NOT NULL"
                    )
                )
            ).scalar_one()
            print(f"LEDGER_ID_NULL_AFTER={remaining}")
            print(f"LEDGER_ID_DISTINCT={distinct}")
            if remaining:
                print("LEDGER_BACKFILL=FAIL (rows still unresolved after write)")
                return 1
            if distinct != len(assets):
                print("LEDGER_BACKFILL=FAIL (ledger_id values are not unique)")
                return 1
            print("LEDGER_BACKFILL=PASS")
            return 0
    finally:
        await engine.dispose()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--register", type=Path, default=DEFAULT_REGISTER)
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--commit", dest="dry_run", action="store_false")
    args = parser.parse_args(argv)
    return asyncio.run(run(args.register, commit=not args.dry_run))


if __name__ == "__main__":
    sys.exit(main())
