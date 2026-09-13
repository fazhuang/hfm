#!/usr/bin/env python3
"""HFM P2 content import — C-domain terms (acupoints/meridians/etc.).

Operator-only controlled import of the frozen knowledge-object candidates
(``content-production/normalized/knowledge-object-candidates.csv``) into the
canonical C-domain projection: one typed ``Entity`` (stable identity) plus one
``CDomainTerm`` per candidate. This is the P2 counterpart to
``publish-content.py`` — idempotent, fail-closed, dry-run first, never
publishes.

Why this script exists: the C-domain tables (``c_domain_terms`` /
``c_domain_relations``) and the ``entities`` bootstrap for concepts/acupoints
are empty, while 26 auto-extracted term candidates are frozen in the
normalized corpus. This script is the controlled bridge from "discovery
candidate" to "canonical term record" — it does NOT invent relations, does
NOT publish anything, and never runs automatically.

Fail-closed rules:
  - every OBJECT_TYPE must map to a known (EntityType, CDomainTermType);
    an unknown type is rejected, never silently coerced;
  - the entity id reuses the frozen candidate CANDIDATE_ID (stable, unique),
    so re-runs never duplicate and never silently overwrite;
  - single transaction: --dry-run performs every read and write then rolls
    back, so the reported plan is exactly what a real run would commit.

Notes:
  - c_domain_terms carry no review/publication state. Populating them is NOT
    publishing: public visibility is gated separately by a PUBLISHED
    ContentArtifact bound to the term's entity (P1-09), out of scope here.
  - candidate MENTIONS counts are reported but not stored — the term
    description stays None (no curated semantics to invent).

Usage:
    HFM_ENV=prod HFM_DATABASE_URL=<postgres DSN to /hfm_prod> \
    python import-cdomain-terms.py --env-file ~/.hfm/secrets/prod.env
    # add --commit to write; default is --dry-run (report + rollback)

Exit codes: 0 = PASS (all candidates admitted or already present),
1 = FAIL, 2 = usage.
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

CANDIDATES_CSV = (
    REPO_ROOT / "content-production" / "normalized" / "knowledge-object-candidates.csv"
)

#: Provenance marker for this import (CDomainTerm.created_by is a placeholder
#: bridge with no User FK — Auth red line, CA-026).
IMPORTER = "content-importer-p2"


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

from hfm.models.c_domain import CDomainTerm, CDomainTermType  # noqa: E402
from hfm.models.chapter import Chapter  # noqa: E402,F401  # registers chapters (FK chain)
from hfm.models.edition import Edition  # noqa: E402,F401  # registers editions
from hfm.models.entity import Entity, EntityType  # noqa: E402
from hfm.models.passage import Passage  # noqa: E402,F401  # registers passages
from hfm.models.version import Version  # noqa: E402,F401  # registers versions
from hfm.models.work import Work  # noqa: E402,F401  # registers works
from sqlalchemy import select  # noqa: E402
from sqlalchemy.ext.asyncio import (  # noqa: E402
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

#: OBJECT_TYPE → (EntityType, CDomainTermType). Medical-specific subtypes were
#: deliberately removed from the frozen EntityType families (G1 boundary), so
#: everything except acupoint maps to the ``concept`` entity family.
_TYPE_MAP: dict[str, tuple[EntityType, CDomainTermType]] = {
    "ACUPOINT": (EntityType.acupoint, CDomainTermType.acupoint),
    "MERIDIAN": (EntityType.concept, CDomainTermType.meridian),
    "DISEASE": (EntityType.concept, CDomainTermType.disease_symptom),
    "SYMPTOM": (EntityType.concept, CDomainTermType.disease_symptom),
    "TREATMENT": (EntityType.concept, CDomainTermType.technique),
    "METHOD": (EntityType.concept, CDomainTermType.technique),
}


def load_candidates(path: Path) -> list[dict[str, str]]:
    """Read the frozen candidate CSV (BOM-safe)."""
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


async def _run(db_url: str, dry_run: bool) -> tuple[dict[str, int], list[str]]:
    engine = create_async_engine(db_url)
    summary = {"terms_created": 0, "terms_existing": 0, "rejected": 0}
    lines: list[str] = []
    try:
        factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
        async with factory() as session:
            try:
                for cand in load_candidates(CANDIDATES_CSV):
                    candidate_id = cand.get("CANDIDATE_ID", "").strip()
                    object_type = cand.get("OBJECT_TYPE", "").strip()
                    name = cand.get("NAME", "").strip()
                    mentions = cand.get("MENTIONS", "").strip()
                    if not candidate_id or not name:
                        summary["rejected"] += 1
                        lines.append(f"REJECTED candidate: missing id/name")
                        continue
                    mapping = _TYPE_MAP.get(object_type)
                    if mapping is None:
                        summary["rejected"] += 1
                        lines.append(
                            f"REJECTED {candidate_id}: unknown OBJECT_TYPE {object_type!r}"
                        )
                        continue
                    entity_type, term_type = mapping
                    entity_id = candidate_id  # stable identity reuses frozen CANDIDATE_ID

                    entity = await session.get(Entity, entity_id)
                    if entity is None:
                        entity = Entity(
                            id=entity_id,
                            entity_type=entity_type.value,
                            name=name,
                            name_zh=name,
                        )
                        session.add(entity)
                        await session.flush()

                    existing = (
                        await session.execute(
                            select(CDomainTerm).where(CDomainTerm.entity_id == entity_id)
                        )
                    ).scalar_one_or_none()
                    if existing is None:
                        session.add(
                            CDomainTerm(
                                entity_id=entity_id,
                                term_type=term_type.value,
                                term_name=name,
                                created_by=IMPORTER,
                            )
                        )
                        summary["terms_created"] += 1
                        lines.append(
                            f"CREATE term {name} "
                            f"({object_type} -> {entity_type.value}/{term_type.value}) "
                            f"mentions={mentions}"
                        )
                    else:
                        summary["terms_existing"] += 1
                        lines.append(f"EXISTS term {name}")

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
        env.update(validator.parse_env_file(args.env_file))

    environment = "prod" if not args.test_mode else env.get("HFM_ENV", "test")
    errors = validator.validate_env(env, environment=environment, allow_sqlite=False)
    if args.test_mode:
        errors = [e for e in errors if "HFM_ENV mismatch" not in e]
    if errors:
        for reason in errors:
            print(f"ENV_VALIDATION=FAIL ({reason})")
        print("IMPORT_CDOMAIN_TERMS=FAIL")
        return 1

    db_url = env.get("HFM_DATABASE_URL", "")
    migration_errors = validator.verify_migration(BACKEND_DIR, db_url, "0016")
    if migration_errors:
        for reason in migration_errors:
            print(f"MIGRATION_VERIFY=FAIL ({reason})")
        print("IMPORT_CDOMAIN_TERMS=FAIL (database must be migrated at 0016)")
        return 1

    try:
        summary, lines = asyncio.run(_run(db_url, args.dry_run))
    except Exception as exc:  # noqa: BLE001 - operator-facing top-level guard
        print(f"IMPORT_CDOMAIN_TERMS=FAIL ({type(exc).__name__}: {exc})")
        return 1

    for line in lines:
        print(line)
    print(f"SUMMARY={summary}")
    print("IMPORT_CDOMAIN_TERMS=PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
