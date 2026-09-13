#!/usr/bin/env python3
"""HFM P2 content import — assertion citations (biographical evidence chain).

Operator-only controlled import of Citations for the frozen biographical
assertions (皇甫谧 evidence chain). Each Citation binds an Assertion to its
Evidence and carries the source quote (``quote_text``) recovered from
``content-production/normalized/evidence.csv`` (SOURCE_CONTEXT column).

Why passage_id stays NULL: the 23 assertions are *biographical* claims about
皇甫谧 sourced from 晋书/论文 documents, NOT quotes from 《针灸甲乙经》. The
``passages`` table holds 甲乙经 structured text only, so there is no honest
甲乙经 passage to pin these biographical citations to. The citation is still a
reproducible reference via evidence_id + quote_text (the source document text).

Idempotent (skips an existing citation for the same assertion+evidence),
fail-closed, dry-run first, never publishes.

Usage:
    python import-citations.py --env-file ~/.hfm/secrets/prod.env            # dry-run
    python import-citations.py --env-file ~/.hfm/secrets/prod.env --commit   # write
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

EVIDENCE_CSV = REPO_ROOT / "content-production" / "normalized" / "evidence.csv"
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

from hfm.models.assertion import Assertion, assertion_evidences  # noqa: E402,F401  # registers assertions
from hfm.models.citation import Citation  # noqa: E402
from hfm.models.evidence import Evidence  # noqa: E402
from hfm.models.passage import Passage  # noqa: E402,F401  # registers passages (citation FK)
from hfm.models.version import Version  # noqa: E402,F401  # registers versions (citation FK)
from sqlalchemy import select  # noqa: E402
from sqlalchemy.ext.asyncio import (  # noqa: E402
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


def load_source_context() -> dict[str, str]:
    """EVIDENCE-XXX → SOURCE_CONTEXT (the quoted source text)."""
    out: dict[str, str] = {}
    with EVIDENCE_CSV.open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            eid = (row.get("EVIDENCE_ID") or "").strip()
            ctx = (row.get("SOURCE_CONTEXT") or "").strip()
            if eid:
                out[eid] = ctx
    return out


async def _run(db_url: str, dry_run: bool) -> tuple[dict[str, int], list[str]]:
    engine = create_async_engine(db_url)
    summary = {"citations_created": 0, "citations_existing": 0, "skipped_no_context": 0}
    lines: list[str] = []
    try:
        factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
        async with factory() as session:
            try:
                source_context = load_source_context()

                # evidence stable_id → (id, description) for quote lookup
                evidence_rows = (await session.execute(
                    select(Evidence.id, Evidence.stable_id)
                )).all()
                evidence_by_id = {eid: sid for eid, sid in evidence_rows}

                # existing citations keyed by (assertion_id, evidence_id)
                existing = set(
                    (await session.execute(
                        select(Citation.target_assertion_id, Citation.evidence_id)
                    )).all()
                )

                pairs = (await session.execute(select(assertion_evidences))).all()
                for assertion_id, evidence_id in pairs:
                    if (assertion_id, evidence_id) in existing:
                        summary["citations_existing"] += 1
                        continue
                    stable_id = evidence_by_id.get(evidence_id)
                    quote = source_context.get(stable_id or "", "")
                    if not quote:
                        summary["skipped_no_context"] += 1
                        lines.append(f"SKIP (no SOURCE_CONTEXT) evidence {stable_id}")
                        continue
                    session.add(
                        Citation(
                            target_assertion_id=assertion_id,
                            evidence_id=evidence_id,
                            quote_text=quote,
                            note="传记性断言引用（来源见证据 source 文档）",
                            created_by=IMPORTER,
                        )
                    )
                    existing.add((assertion_id, evidence_id))
                    summary["citations_created"] += 1
                    lines.append(f"CREATE citation for {stable_id}")
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
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--commit", dest="dry_run", action="store_false")
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
        print("IMPORT_CITATIONS=FAIL")
        return 1

    db_url = env.get("HFM_DATABASE_URL", "")
    migration_errors = validator.verify_migration(BACKEND_DIR, db_url, "0016")
    if migration_errors:
        for reason in migration_errors:
            print(f"MIGRATION_VERIFY=FAIL ({reason})")
        print("IMPORT_CITATIONS=FAIL (database must be migrated at 0016)")
        return 1

    try:
        summary, lines = asyncio.run(_run(db_url, args.dry_run))
    except Exception as exc:  # noqa: BLE001
        print(f"IMPORT_CITATIONS=FAIL ({type(exc).__name__}: {exc})")
        return 1

    for line in lines:
        print(line)
    print(f"SUMMARY={summary}")
    print("IMPORT_CITATIONS=PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
