#!/usr/bin/env python3
"""HFM P2 content import — curated C-domain relations.

Operator-only controlled import of the CURATED acupoint→meridian relationships
(``content-production/08-approved/cdomain-relations-curated.csv``) into
``c_domain_relations``. Unlike the auto-extracted term candidates, these
relations are canonical, well-established TCM taxonomy (e.g. 合谷 located_in
手阳明大肠经) — authored curation, not discovery. Target meridian terms that
are not yet present are added as ``concept``/``meridian`` terms first.

Fail-closed: a relation whose source term does not exist is rejected; unknown
relation types are rejected; idempotent (a duplicate source+target+type is a
no-op); dry-run first; never publishes.

Usage:
    HFM_ENV=prod HFM_DATABASE_URL=<postgres DSN to /hfm_prod> \
    python import-cdomain-relations.py --env-file ~/.hfm/secrets/prod.env
    # add --commit to write; default is --dry-run (report + rollback)
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

RELATIONS_CSV = (
    REPO_ROOT / "content-production" / "08-approved" / "cdomain-relations-curated.csv"
)

#: Provenance marker for curated relations (vs auto-extracted terms).
CURATOR = "content-curator-p2"


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

from hfm.models.c_domain import (  # noqa: E402
    CDomainRelation,
    CDomainRelationType,
    CDomainTerm,
    CDomainTermType,
)
from hfm.models.chapter import Chapter  # noqa: E402,F401
from hfm.models.content_artifact import ContentArtifact  # noqa: E402,F401
from hfm.models.edition import Edition  # noqa: E402,F401
from hfm.models.entity import Entity, EntityType  # noqa: E402
from hfm.models.evidence import Evidence  # noqa: E402,F401
from hfm.models.passage import Passage  # noqa: E402,F401
from hfm.models.source import Source  # noqa: E402,F401
from hfm.models.source_ref import SourceRef  # noqa: E402,F401
from hfm.models.version import Version  # noqa: E402,F401
from hfm.models.work import Work  # noqa: E402,F401
from sqlalchemy import select  # noqa: E402
from sqlalchemy.ext.asyncio import (  # noqa: E402
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

#: Manifest RELATION_TYPE -> enum. Fail-closed on unknown values.
_RELATION_TYPES: dict[str, CDomainRelationType] = {
    r.value: r for r in CDomainRelationType
}


def _term_entity_id(term_name: str) -> str:
    """Deterministic entity id for a curated meridian term (K-MERIDIAN-*)."""
    return f"K-MERIDIAN-{term_name}"


async def _get_term_entity(session: AsyncSession, term_name: str) -> str | None:
    term = (
        await session.execute(
            select(CDomainTerm).where(CDomainTerm.term_name == term_name)
        )
    ).scalar_one_or_none()
    return term.entity_id if term is not None else None


async def _ensure_meridian_term(session: AsyncSession, term_name: str) -> str:
    """Return the entity id for a meridian term, creating it if absent."""
    existing = await _get_term_entity(session, term_name)
    if existing is not None:
        return existing
    entity_id = _term_entity_id(term_name)
    entity = await session.get(Entity, entity_id)
    if entity is None:
        entity = Entity(
            id=entity_id,
            entity_type=EntityType.concept.value,
            name=term_name,
            name_zh=term_name,
        )
        session.add(entity)
        await session.flush()
    session.add(
        CDomainTerm(
            entity_id=entity_id,
            term_type=CDomainTermType.meridian.value,
            term_name=term_name,
            created_by=CURATOR,
        )
    )
    await session.flush()
    return entity_id


async def _relation_exists(
    session: AsyncSession, source: str, target: str, rel_type: CDomainRelationType
) -> bool:
    row = (
        await session.execute(
            select(CDomainRelation).where(
                CDomainRelation.source_term_entity_id == source,
                CDomainRelation.target_term_entity_id == target,
                CDomainRelation.relation_type == rel_type,
            )
        )
    ).scalar_one_or_none()
    return row is not None


async def _run(db_url: str, dry_run: bool) -> tuple[dict[str, int], list[str]]:
    engine = create_async_engine(db_url)
    summary = {"relations_created": 0, "relations_existing": 0, "rejected": 0}
    lines: list[str] = []
    try:
        factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
        async with factory() as session:
            try:
                with RELATIONS_CSV.open(encoding="utf-8-sig", newline="") as handle:
                    rows = list(csv.DictReader(handle))

                for row in rows:
                    source_name = row.get("SOURCE_TERM", "").strip()
                    target_name = row.get("TARGET_TERM", "").strip()
                    raw_type = row.get("RELATION_TYPE", "").strip()
                    rel_type = _RELATION_TYPES.get(raw_type)
                    if not source_name or not target_name or rel_type is None:
                        summary["rejected"] += 1
                        lines.append(
                            f"REJECTED row: bad source/target/type "
                            f"({source_name!r} {target_name!r} {raw_type!r})"
                        )
                        continue

                    source_id = await _get_term_entity(session, source_name)
                    if source_id is None:
                        summary["rejected"] += 1
                        lines.append(f"REJECTED {source_name}: source term not found")
                        continue
                    target_id = await _ensure_meridian_term(session, target_name)

                    if await _relation_exists(session, source_id, target_id, rel_type):
                        summary["relations_existing"] += 1
                        lines.append(f"EXISTS relation {source_name} -> {target_name}")
                        continue

                    session.add(
                        CDomainRelation(
                            source_term_entity_id=source_id,
                            target_term_entity_id=target_id,
                            relation_type=rel_type,
                            created_by=CURATOR,
                        )
                    )
                    summary["relations_created"] += 1
                    lines.append(f"CREATE relation {source_name} -> {target_name} ({raw_type})")

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

    env: dict[str, str] = dict(os.environ)
    if args.env_file is not None:
        if not args.env_file.is_file():
            print(f"ENV_FILE=FAIL (not found: {args.env_file.name})")
            return 1
        try:
            env = validator.merge_env(env, args.env_file)
        except validator.EnvConflictError as exc:
            print(f"ENV_FILE=FAIL ({exc})")
            return 1
    print(f"DB_TARGET={validator.describe_db_target(env)}")

    environment = "prod" if not args.test_mode else env.get("HFM_ENV", "test")
    errors = validator.validate_env(env, environment=environment, allow_sqlite=False)
    if args.test_mode:
        errors = [e for e in errors if "HFM_ENV mismatch" not in e]
    if errors:
        for reason in errors:
            print(f"ENV_VALIDATION=FAIL ({reason})")
        print("IMPORT_CDOMAIN_RELATIONS=FAIL")
        return 1

    db_url = env.get("HFM_DATABASE_URL", "")
    migration_errors = validator.verify_migration(BACKEND_DIR, db_url, "0017")
    if migration_errors:
        for reason in migration_errors:
            print(f"MIGRATION_VERIFY=FAIL ({reason})")
        print("IMPORT_CDOMAIN_RELATIONS=FAIL (database must be migrated at 0017)")
        return 1

    try:
        summary, lines = asyncio.run(_run(db_url, args.dry_run))
    except Exception as exc:  # noqa: BLE001 - operator-facing top-level guard
        print(f"IMPORT_CDOMAIN_RELATIONS=FAIL ({type(exc).__name__}: {exc})")
        return 1

    for line in lines:
        print(line)
    print(f"SUMMARY={summary}")
    print("IMPORT_CDOMAIN_RELATIONS=PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
