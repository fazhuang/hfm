#!/usr/bin/env python3
"""HFM P3 content import — media assets (hfmzl source files).

Operator-only controlled import of the physical source files under ``hfmzl/``
into ``media_assets``: one row per media file (PDF/DOCX/video/image) with its
byte size, sha256 and MIME type, plus customer-owned rights metadata.
Publication is fail-closed (publication_permission=false, draft state).

Idempotent (object_key is the natural key), dry-run first, never publishes.

Usage:
    HFM_ENV=prod HFM_DATABASE_URL=<postgres DSN to /hfm_prod> \
    python import-media-assets.py --env-file ~/.hfm/secrets/prod.env
    # add --commit to write; default is --dry-run (report + rollback)
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import importlib.util
import os
import sys
from pathlib import Path
from typing import Any

_SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = _SCRIPT_DIR.parent
BACKEND_DIR = REPO_ROOT / "apps" / "backend"
HFMZL = REPO_ROOT / "hfmzl"

IMPORTER = "content-importer-p3"

#: extension -> MIME type (only the media families we register).
_MIME: dict[str, str] = {
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".doc": "application/msword",
    ".mpg": "video/mpeg",
    ".mpeg": "video/mpeg",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
}

#: extensions that are media, not housekeeping artifacts.
_SKIP_SUFFIXES = {".DS_Store", ".db", ".lnk", ".zip"}


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

from hfm.phase2.media.models import MediaAsset  # noqa: E402
from sqlalchemy import select  # noqa: E402
from sqlalchemy.ext.asyncio import (  # noqa: E402
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def iter_media_files() -> list[tuple[str, Path]]:
    """Return (object_key, path) for every media file under hfmzl/."""
    out: list[tuple[str, Path]] = []
    for path in sorted(HFMZL.rglob("*")):
        if not path.is_file():
            continue
        suffix = path.suffix.lower()
        if suffix in _SKIP_SUFFIXES or suffix not in _MIME:
            continue
        rel = path.relative_to(HFMZL).as_posix()
        out.append((rel, path))
    return out


async def _run(db_url: str, dry_run: bool) -> tuple[dict[str, int], list[str]]:
    engine = create_async_engine(db_url)
    summary = {"created": 0, "existing": 0}
    lines: list[str] = []
    try:
        factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
        async with factory() as session:
            try:
                for object_key, path in iter_media_files():
                    existing = (
                        await session.execute(
                            select(MediaAsset).where(MediaAsset.object_key == object_key)
                        )
                    ).scalar_one_or_none()
                    if existing is not None:
                        summary["existing"] += 1
                        lines.append(f"EXISTS media {object_key}")
                        continue

                    session.add(
                        MediaAsset(
                            object_key=object_key,
                            mime_type=_MIME[path.suffix.lower()],
                            byte_size=path.stat().st_size,
                            sha256=sha256_of(path),
                            rights_holder="皇甫谧文化（客户提供）",
                            license_basis="customer_owned",
                            publication_permission=False,
                            provenance=f"本地源文件 hfmzl/{object_key}",
                        )
                    )
                    summary["created"] += 1
                    lines.append(f"CREATE media {object_key}")

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
        print("IMPORT_MEDIA_ASSETS=FAIL")
        return 1

    db_url = env.get("HFM_DATABASE_URL", "")
    migration_errors = validator.verify_migration(BACKEND_DIR, db_url, "0018")
    if migration_errors:
        for reason in migration_errors:
            print(f"MIGRATION_VERIFY=FAIL ({reason})")
        print("IMPORT_MEDIA_ASSETS=FAIL (database must be migrated at 0018)")
        return 1

    try:
        summary, lines = asyncio.run(_run(db_url, args.dry_run))
    except Exception as exc:  # noqa: BLE001 - operator-facing top-level guard
        print(f"IMPORT_MEDIA_ASSETS=FAIL ({type(exc).__name__}: {exc})")
        return 1

    for line in lines:
        print(line)
    print(f"SUMMARY={summary}")
    print("IMPORT_MEDIA_ASSETS=PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
