#!/usr/bin/env python3
"""HFM P3 content import — curated heritage project + lineage relations.

Adds the single 皇甫谧针灸 heritage PROJECT and its inheritor lineage
relations (传承人), which are the "非遗项目 + 传承谱系" named in the roadmap
P3. These facts come from the customer's own materials (person-facts /
非遗佐证): 皇甫谧针灸 is a 市级非物质文化遗产, 李志锋 and 刘君奇 are the
named inheritors. Authored curation — not auto-extracted.

Idempotent, fail-closed, dry-run first, never publishes.

Usage:
    HFM_ENV=prod HFM_DATABASE_URL=<postgres DSN to /hfm_prod> \
    python import-heritage-lineage.py --env-file ~/.hfm/secrets/prod.env
    # add --commit to write; default is --dry-run (report + rollback)
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

CURATOR = "content-curator-p3"

PROJECT_ENTITY_ID = "ENT-HERITAGE-HUANGFUMI-ZHENJIU"
PROJECT_NAME = "皇甫谧针灸"
PROJECT_OFFICIAL = "皇甫谧针灸市级非物质文化遗产代表性项目"
PROJECT_CATEGORY = "传统医药/针灸"

#: (person entity_id, inheritor display name)
INHERITORS = [
    ("ENT-PERSON-LI-ZHIFENG", "李志锋"),
    ("ENT-PERSON-LIU-JUNQI", "刘君奇"),
]


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

from hfm.models.chapter import Chapter  # noqa: E402,F401
from hfm.models.content_artifact import ContentArtifact  # noqa: E402,F401
from hfm.models.edition import Edition  # noqa: E402,F401
from hfm.models.entity import Entity, EntityType  # noqa: E402
from hfm.models.evidence import Evidence  # noqa: E402,F401
from hfm.models.heritage import (  # noqa: E402
    HeritageProject,
    HeritageRelation,
    HeritageRelationRole,
)
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


async def _run(db_url: str, dry_run: bool) -> tuple[dict[str, int], list[str]]:
    engine = create_async_engine(db_url)
    summary = {"project_created": 0, "project_existing": 0, "relations_created": 0,
               "relations_existing": 0, "rejected": 0}
    lines: list[str] = []
    try:
        factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
        async with factory() as session:
            try:
                project = (
                    await session.execute(
                        select(HeritageProject).where(
                            HeritageProject.entity_id == PROJECT_ENTITY_ID
                        )
                    )
                ).scalar_one_or_none()
                if project is None:
                    entity = await session.get(Entity, PROJECT_ENTITY_ID)
                    if entity is None:
                        entity = Entity(
                            id=PROJECT_ENTITY_ID,
                            entity_type=EntityType.concept.value,
                            name=PROJECT_NAME,
                            name_zh=PROJECT_NAME,
                        )
                        session.add(entity)
                        await session.flush()
                    session.add(
                        HeritageProject(
                            entity_id=PROJECT_ENTITY_ID,
                            project_name=PROJECT_NAME,
                            official_name=PROJECT_OFFICIAL,
                            category=PROJECT_CATEGORY,
                            created_by=CURATOR,
                        )
                    )
                    summary["project_created"] += 1
                    lines.append(f"CREATE heritage project {PROJECT_NAME}")
                else:
                    summary["project_existing"] += 1
                    lines.append(f"EXISTS heritage project {PROJECT_NAME}")

                for person_entity_id, name in INHERITORS:
                    person = await session.get(Entity, person_entity_id)
                    if person is None:
                        summary["rejected"] += 1
                        lines.append(f"REJECTED inheritor {name}: entity not found")
                        continue
                    exists = (
                        await session.execute(
                            select(HeritageRelation).where(
                                HeritageRelation.project_entity_id == PROJECT_ENTITY_ID,
                                HeritageRelation.subject_entity_id == person_entity_id,
                                HeritageRelation.relation_role
                                == HeritageRelationRole.inheritor,
                            )
                        )
                    ).scalar_one_or_none()
                    if exists is not None:
                        summary["relations_existing"] += 1
                        lines.append(f"EXISTS relation {PROJECT_NAME} -> {name}")
                        continue
                    session.add(
                        HeritageRelation(
                            project_entity_id=PROJECT_ENTITY_ID,
                            subject_entity_id=person_entity_id,
                            relation_role=HeritageRelationRole.inheritor,
                            official_name=f"{name}（皇甫谧针灸市级非遗传承人）",
                            created_by=CURATOR,
                        )
                    )
                    summary["relations_created"] += 1
                    lines.append(f"CREATE relation {PROJECT_NAME} -> {name} (inheritor)")

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
        print("IMPORT_HERITAGE_LINEAGE=FAIL")
        return 1

    db_url = env.get("HFM_DATABASE_URL", "")
    migration_errors = validator.verify_migration(BACKEND_DIR, db_url, "0016")
    if migration_errors:
        for reason in migration_errors:
            print(f"MIGRATION_VERIFY=FAIL ({reason})")
        print("IMPORT_HERITAGE_LINEAGE=FAIL (database must be migrated at 0016)")
        return 1

    try:
        summary, lines = asyncio.run(_run(db_url, args.dry_run))
    except Exception as exc:  # noqa: BLE001 - operator-facing top-level guard
        print(f"IMPORT_HERITAGE_LINEAGE=FAIL ({type(exc).__name__}: {exc})")
        return 1

    for line in lines:
        print(line)
    print(f"SUMMARY={summary}")
    print("IMPORT_HERITAGE_LINEAGE=PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
