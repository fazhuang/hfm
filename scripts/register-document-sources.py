#!/usr/bin/env python3
"""HFM P2 content import — document-level source registration.

Operator-only controlled bridge from the normalized ``documents`` table to the
canonical source identity chain (``sources`` + ``source_refs``). This is the
P1-deferred "文档级 source 注册"补强项: the 675 ``documents`` rows carry a
``source_asset_id`` but no ``sources`` entry, and the Evidence lineage
(``evidences``) requires a ``source_ref`` provenance anchor (CHECK
``source_ref_id IS NOT NULL OR source_passage_id IS NOT NULL``).

One immutable ``Source`` (source_key ``document:<stable_id>``) plus one
``SourceRef`` per document. Idempotent (source_key is the natural key),
fail-closed, dry-run first, never publishes.

Rights are NOT guessed: ``--rights-basis`` is required (free-text, e.g.
``customer_owned`` / ``public_domain``) and written to the Source only; no
ContentArtifact / PublicationRecord is created, so nothing becomes public.

Usage:
    HFM_ENV=prod HFM_DATABASE_URL=<postgres DSN to /hfm_prod> \
    python register-document-sources.py \
        --stable-ids DOC-HFM-A000003,DOC-HFM-A000004,DOC-HFM-A000005 \
        --rights-basis customer_owned --env-file ~/.hfm/secrets/prod.env
    # add --commit to write; default is --dry-run (report + rollback)

Exit codes: 0 = PASS, 1 = FAIL, 2 = usage.
"""

from __future__ import annotations

import argparse
import asyncio
import importlib.util
import os
import sys
from pathlib import Path
from typing import Any

_SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = _SCRIPT_DIR.parent
BACKEND_DIR = REPO_ROOT / "apps" / "backend"


def _load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


validator = _load_module(
    "validate_production_env", _SCRIPT_DIR / "validate-production-env.py"
)

sys.path.insert(0, str(BACKEND_DIR / "src"))

from hfm.models.document import ContentDocument  # noqa: E402
from hfm.models.source import Source  # noqa: E402
from hfm.models.source_ref import SourceRef  # noqa: E402
from hfm.repositories.source import SourceRepository  # noqa: E402
from sqlalchemy import select  # noqa: E402
from sqlalchemy.ext.asyncio import (  # noqa: E402
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


def _source_key(stable_id: str) -> str:
    return f"document:{stable_id}"


async def _register_one(
    session: AsyncSession,
    *,
    stable_id: str,
    title: str,
    doc_type: str | None,
    source_asset_id: str | None,
    author: str | None,
    edition: str | None,
    rights_basis: str,
    allowed_scope: str | None,
) -> tuple[str, str]:
    """Register one document as a Source + SourceRef; returns (state, detail)."""
    source, created = await SourceRepository(session).create_idempotent(
        source_key=_source_key(stable_id),
        source_type=(doc_type or "document").lower(),
        title=title,
        rights_basis=rights_basis,
        allowed_scope=allowed_scope,
    )
    source_state = "created" if created else "existing"

    existing_ref = (
        await session.execute(
            select(SourceRef).where(SourceRef.source_id == source.id)
        )
    ).scalar_one_or_none()
    if existing_ref is None:
        session.add(
            SourceRef(
                source_id=source.id,
                title=title,
                author=author or None,
                edition_info=edition or None,
                locator={"asset_id": source_asset_id} if source_asset_id else None,
            )
        )
        return "registered", f"source={source_state}"
    return "already_registered", f"source={source_state}"


async def _run(
    db_url: str,
    stable_ids: list[str],
    rights_basis: str,
    allowed_scope: str | None,
    dry_run: bool,
) -> tuple[dict[str, int], list[str]]:
    engine = create_async_engine(db_url)
    summary = {"registered": 0, "already_registered": 0, "rejected": 0}
    lines: list[str] = []
    try:
        factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
        async with factory() as session:
            try:
                for stable_id in stable_ids:
                    doc = (
                        await session.execute(
                            select(ContentDocument).where(
                                ContentDocument.stable_id == stable_id
                            )
                        )
                    ).scalar_one_or_none()
                    if doc is None:
                        summary["rejected"] += 1
                        lines.append(f"REJECTED {stable_id}: no such document")
                        continue
                    state, detail = await _register_one(
                        session,
                        stable_id=stable_id,
                        title=doc.title,
                        doc_type=doc.doc_type,
                        source_asset_id=doc.source_asset_id,
                        author=doc.author_original,
                        edition=doc.edition,
                        rights_basis=rights_basis,
                        allowed_scope=allowed_scope,
                    )
                    summary[state] += 1
                    lines.append(f"{state.upper()} {stable_id} ({doc.title}): {detail}")

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
    parser.add_argument(
        "--stable-ids",
        required=True,
        help="comma-separated document stable_ids to register (e.g. DOC-HFM-A000003)",
    )
    parser.add_argument(
        "--rights-basis",
        required=True,
        help="rights basis for the registered sources (e.g. customer_owned / public_domain)",
    )
    parser.add_argument("--allowed-scope", default=None)
    parser.add_argument("--env-file", type=Path, default=None)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="run every read and write then roll back (report only; default)",
    )
    parser.add_argument(
        "--commit", dest="dry_run", action="store_false", help="actually write (operator action)"
    )
    parser.add_argument(
        "--test-mode", action="store_true", help="isolated test runs only"
    )
    args = parser.parse_args(argv)

    stable_ids = [s.strip() for s in args.stable_ids.split(",") if s.strip()]
    if not stable_ids:
        print("USAGE=FAIL (--stable-ids must be a non-empty comma-separated list)")
        return 2

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
        print("REGISTER_DOCUMENT_SOURCES=FAIL")
        return 1

    db_url = env.get("HFM_DATABASE_URL", "")
    migration_errors = validator.verify_migration(BACKEND_DIR, db_url, "0015")
    if migration_errors:
        for reason in migration_errors:
            print(f"MIGRATION_VERIFY=FAIL ({reason})")
        print("REGISTER_DOCUMENT_SOURCES=FAIL (database must be migrated at 0015)")
        return 1

    try:
        summary, lines = asyncio.run(
            _run(db_url, stable_ids, args.rights_basis, args.allowed_scope, args.dry_run)
        )
    except Exception as exc:  # noqa: BLE001 - operator-facing top-level guard
        print(f"REGISTER_DOCUMENT_SOURCES=FAIL ({type(exc).__name__}: {exc})")
        return 1

    for line in lines:
        print(line)
    print(f"SUMMARY={summary}")
    print("REGISTER_DOCUMENT_SOURCES=PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
