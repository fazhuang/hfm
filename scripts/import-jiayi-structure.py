#!/usr/bin/env python3
"""HFM P2 content import — 《针灸甲乙经》篇章段落 (chapters + passages).

Operator-only controlled import of the parsed Wikisource 宋校本 structure
(``content-production/normalized/jiayi-chapters.csv`` + ``jiayi-passages.csv``)
into the canonical ``chapters`` (卷=level1, 篇=level2) and ``passages`` (段)
tables, anchored to ``WORK-JIAYI``.

Idempotent, fail-closed, dry-run first, never publishes. Single transaction:
--dry-run performs every read+write then rolls back, so the report is exactly
what --commit would commit.

Provenance/gaps are recorded in
``content-production/reports/HFM-CONTENT-P2-JIAYI-STRUCTURE-SOURCE.md``
(卷03 篇八/九/十 missing, 卷02 篇五 title incomplete) — this import creates
only what the parsed CSVs contain; it does not invent the missing 篇.

Usage:
    HFM_ENV=prod python import-jiayi-structure.py \
        --env-file ~/.hfm/secrets/prod.env            # dry-run (report + rollback)
    HFM_ENV=prod python import-jiayi-structure.py \
        --env-file ~/.hfm/secrets/prod.env --commit   # actually write

Exit codes: 0 = PASS, 1 = FAIL, 2 = usage.
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import importlib.util
import os
import sys
from pathlib import Path
from typing import Any

_SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = _SCRIPT_DIR.parent
BACKEND_DIR = REPO_ROOT / "apps" / "backend"

CHAPTERS_CSV = REPO_ROOT / "content-production" / "normalized" / "jiayi-chapters.csv"
PASSAGES_CSV = REPO_ROOT / "content-production" / "normalized" / "jiayi-passages.csv"
WORK_ID = "WORK-JIAYI"

IMPORTER = "content-importer-p2"


def _load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


validator = _load_module("validate_production_env", _SCRIPT_DIR / "validate-production-env.py")

sys.path.insert(0, str(BACKEND_DIR / "src"))

from hfm.models.chapter import Chapter  # noqa: E402
from hfm.models.passage import Passage  # noqa: E402
from hfm.models.version import Version  # noqa: E402,F401  # registers versions (passages FK)
from hfm.models.work import Work  # noqa: E402
from sqlalchemy import select  # noqa: E402
from sqlalchemy.ext.asyncio import (  # noqa: E402
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


def _load_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def _opt(v: str) -> str | None:
    s = v.strip()
    return s if s else None


async def _run(db_url: str, dry_run: bool) -> tuple[dict[str, int], list[str]]:
    engine = create_async_engine(db_url)
    summary = {
        "chapters_created": 0,
        "chapters_existing": 0,
        "passages_created": 0,
        "passages_existing": 0,
        "rejected": 0,
    }
    lines: list[str] = []
    try:
        factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
        async with factory() as session:
            try:
                # fail closed: WORK-JIAYI must exist before we anchor chapters to it
                work = await session.get(Work, WORK_ID)
                if work is None:
                    raise RuntimeError(f"WORK-JIAYI not found (refusing to import orphans)")

                chapters = _load_rows(CHAPTERS_CSV)
                # level-1 (卷) before level-2 (篇) so parent_id FK resolves
                chapters.sort(key=lambda r: (int(r.get("level", "0") or 0), int(r.get("order", "0") or 0)))
                existing_chapters = set(
                    (await session.execute(select(Chapter.id))).scalars().all()
                )
                for ch in chapters:
                    chapter_id = ch.get("chapter_id", "").strip()
                    work_id = ch.get("work_id", "").strip()
                    level = int(ch.get("level", "0") or 0)
                    parent_id = _opt(ch.get("parent_id", ""))
                    title = ch.get("title", "").strip()
                    order = int(ch.get("order", "0") or 0)
                    if not chapter_id or not title:
                        summary["rejected"] += 1
                        lines.append(f"REJECTED chapter: missing id/title")
                        continue
                    if work_id != WORK_ID:
                        summary["rejected"] += 1
                        lines.append(f"REJECTED chapter {chapter_id}: work_id={work_id!r}")
                        continue
                    if chapter_id in existing_chapters:
                        summary["chapters_existing"] += 1
                        continue
                    session.add(
                        Chapter(
                            id=chapter_id,
                            work_id=work_id,
                            parent_id=parent_id,
                            title=title,
                            order=order,
                        )
                    )
                    existing_chapters.add(chapter_id)
                    summary["chapters_created"] += 1
                    lines.append(f"CREATE chapter[{level}] {title}")
                await session.flush()

                passages = _load_rows(PASSAGES_CSV)
                existing_passages = set(
                    (await session.execute(select(Passage.id))).scalars().all()
                )
                for ps in passages:
                    passage_id = ps.get("passage_id", "").strip()
                    chapter_id = ps.get("chapter_id", "").strip()
                    content_text = ps.get("content_text", "").strip()
                    notes = _opt(ps.get("notes", ""))
                    order = int(ps.get("order", "0") or 0)
                    if not passage_id or not chapter_id or not content_text:
                        summary["rejected"] += 1
                        lines.append(f"REJECTED passage: missing id/chapter/text")
                        continue
                    if chapter_id not in existing_chapters:
                        summary["rejected"] += 1
                        lines.append(f"REJECTED passage {passage_id}: chapter {chapter_id} missing")
                        continue
                    if passage_id in existing_passages:
                        summary["passages_existing"] += 1
                        continue
                    session.add(
                        Passage(
                            id=passage_id,
                            chapter_id=chapter_id,
                            content_text=content_text,
                            notes=notes,
                            order=order,
                        )
                    )
                    existing_passages.add(passage_id)
                    summary["passages_created"] += 1
                await session.flush()

                if dry_run:
                    await session.rollback()
                    lines.append("DRY_RUN=ROLLED_BACK (no commit)")
                else:
                    await session.commit()
            except BaseException:
                await session.rollback()
                raise
    finally:
        await engine.dispose()
    return summary, lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env-file", type=Path, default=None)
    parser.add_argument("--dry-run", action="store_true", default=True,
                        help="read+write then roll back (default)")
    parser.add_argument("--commit", dest="dry_run", action="store_false",
                        help="actually write (operator action)")
    parser.add_argument("--test-mode", action="store_true")
    args = parser.parse_args(argv)

    env: dict[str, str] = dict(os.environ)
    if args.env_file is not None:
        if not args.env_file.is_file():
            print(f"ENV_FILE=FAIL (not found: {args.env_file.name})")
            return 1
        env.update(validator.parse_env_file(args.env_file))

    environment = "prod" if not args.test_mode else env.get("HFM_ENV", "test")
    errors = validator.validate_env(env, environment=environment, allow_sqlite=False)
    if args.test_mode:
        errors = [e for e in errors if "HFM_ENV mismatch" not in e]
    if errors:
        for reason in errors:
            print(f"ENV_VALIDATION=FAIL ({reason})")
        print("IMPORT_JIAYI_STRUCTURE=FAIL")
        return 1

    db_url = env.get("HFM_DATABASE_URL", "")
    migration_errors = validator.verify_migration(BACKEND_DIR, db_url, "0015")
    if migration_errors:
        for reason in migration_errors:
            print(f"MIGRATION_VERIFY=FAIL ({reason})")
        print("IMPORT_JIAYI_STRUCTURE=FAIL (database must be migrated at 0015)")
        return 1

    try:
        summary, lines = asyncio.run(_run(db_url, args.dry_run))
    except Exception as exc:  # noqa: BLE001
        print(f"IMPORT_JIAYI_STRUCTURE=FAIL ({type(exc).__name__}: {exc})")
        return 1

    for line in lines:
        print(line)
    print(f"SUMMARY={summary}")
    print("IMPORT_JIAYI_STRUCTURE=PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
