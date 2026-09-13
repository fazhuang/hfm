#!/usr/bin/env python3
"""HFM media publication pipeline — operator-only controlled publish.

Publishes already-ingested ``media_assets`` (registered fail-closed as draft by
``import-media-assets.py``) into the public projection consumed by
``GET /api/v1/public/media``. This is the media counterpart of
``publish-content.py``, which covers works/persons/c-terms/heritage only.

Why this script exists (audit finding, 2026-09-14): ``hfm_prod.media_assets``
holds 681 rows and every one is ``draft`` with ``publication_permission=false``,
so ``/public/media`` returns 0. There was no code path to publish media at all —
no CLI, no admin endpoint, and ``MediaService.publish`` gate 1 (rights
sufficiency, ``phase2/media/service.py``) can never pass while the permission
flag is false. This script is that missing path; it does NOT invent rights and
never runs automatically.

Privacy gate (``docs/design/HFM-ASSET-PRESENTATION-POLICY.md`` §4): only P0
(ordinary public content) and P1 (professional / academic / public-identity
information) may be published directly. P2 (certificate numbers, signatures,
ID numbers, private contact details — requires a redacted public derivative per
§4.1) and P3 (never in the public projection) are REJECTED at the manifest
boundary: declaring one in a clearance manifest is a hard failure, not a
warning. The 67 ``非遗佐证`` certificates are the P2 set and stay draft.

Fail-closed rules:
  - ``--clearance-file`` is REQUIRED: the manifest *is* the authorization
    record (same precedent as ``07-review/publication-rights-manifest.json``),
    so an unpublished asset is never published by omission;
  - only object keys matched by an explicit P0/P1 rule are published; every
    other asset is reported as withheld and left untouched;
  - each rule declares ``expected_count`` and the run FAILS if the match count
    differs — this catches both a typo'd prefix (0 matches) and silent drift
    (new files landing under a cleared prefix);
  - an asset already PUBLISHED but absent from the manifest is drift and FAILS
    rather than being silently re-scoped or withdrawn;
  - every published asset must already carry a rights holder and license basis,
    or the run FAILS before writing anything;
  - single transaction, and no writes at all unless every rule validates.

Usage:
    HFM_ENV=prod HFM_DATABASE_URL=<postgres DSN to /hfm_prod> \
    python publish-media.py --clearance-file <manifest.json> --env-file ~/.hfm/secrets/prod.env
    # review first: omit --commit (default is dry-run, report + rollback)
    # test-only isolated runs: add --test-mode [--allow-sqlite]

Exit codes: 0 = PASS (all cleared assets published or already published),
1 = FAIL, 2 = usage.
"""

from __future__ import annotations

import argparse
import asyncio
import importlib.util
import json
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


# Shared production preflight (same single source as publish-content).
validator = _load_module("validate_production_env", _SCRIPT_DIR / "validate-production-env.py")

sys.path.insert(0, str(BACKEND_DIR / "src"))

from hfm.phase2.media.models import MediaAsset, MediaAssetState
from hfm.phase2.media.service import MediaService
from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

#: Privacy classes that may be published directly (policy §4). P2 needs a
#: redacted public derivative first; P3 must never enter the public projection.
PUBLISHABLE_PRIVACY_CLASSES = frozenset({"P0", "P1"})


class ClearanceError(ValueError):
    """Raised when a clearance manifest is malformed or cannot be satisfied."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ClearanceError(message)


def load_clearance(path: Path) -> dict[str, Any]:
    """Parse + validate the clearance manifest schema (fail-closed)."""
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise ClearanceError(f"cannot read clearance manifest: {exc}") from exc
    _require(isinstance(raw, dict), "clearance manifest must be a JSON object")

    basis = raw.get("basis")
    _require(
        isinstance(basis, str) and basis.strip() != "",
        "clearance manifest requires a non-empty 'basis' (the authorization record)",
    )

    rules = raw.get("rules")
    _require(isinstance(rules, list) and len(rules) > 0, "'rules' must be a non-empty list")
    for index, rule in enumerate(rules):
        where = f"rules[{index}]"
        _require(isinstance(rule, dict), f"{where} must be an object")

        privacy_class = rule.get("privacy_class")
        _require(
            privacy_class in PUBLISHABLE_PRIVACY_CLASSES,
            f"{where}.privacy_class must be one of "
            f"{sorted(PUBLISHABLE_PRIVACY_CLASSES)} (P2 requires a redacted public "
            f"derivative and P3 must never be published — policy §4/§4.1), "
            f"got {privacy_class!r}",
        )

        has_key = isinstance(rule.get("object_key"), str)
        has_prefix = isinstance(rule.get("prefix"), str)
        _require(
            has_key != has_prefix,
            f"{where} must set exactly one of 'object_key' or 'prefix'",
        )
        if has_prefix:
            _require(rule["prefix"] != "", f"{where}.prefix must not be empty")

        expected = rule.get("expected_count")
        _require(
            isinstance(expected, int) and not isinstance(expected, bool) and expected > 0,
            f"{where}.expected_count must be a positive integer",
        )
    return raw


def _rule_matches(rule: dict[str, Any], object_key: str) -> bool:
    if "object_key" in rule:
        return object_key == rule["object_key"]
    return object_key.startswith(rule["prefix"])


def _top_group(object_key: str) -> str:
    """First path segment, used to summarise withheld assets by source folder."""
    return object_key.split("/", 1)[0] if "/" in object_key else "(root)"


def _plan(assets: list[MediaAsset], manifest: dict[str, Any]) -> tuple[list[MediaAsset], list[str]]:
    """Resolve the manifest against the registry; returns (cleared, errors).

    Read-only: every failure is collected so one run reports every problem
    instead of stopping at the first.
    """
    errors: list[str] = []
    cleared: dict[str, MediaAsset] = {}

    for index, rule in enumerate(manifest["rules"]):
        matched = [a for a in assets if _rule_matches(rule, str(a.object_key))]
        if len(matched) != rule["expected_count"]:
            errors.append(
                f"rules[{index}] matched {len(matched)} assets, "
                f"expected {rule['expected_count']} "
                f"({rule.get('prefix') or rule.get('object_key')})"
            )
            continue
        for asset in matched:
            key = str(asset.object_key)
            if key in cleared:
                errors.append(f"rules[{index}] re-clears {key} (duplicate coverage)")
                continue
            cleared[key] = asset

    # Rights precondition: publication is impossible without holder + basis.
    for asset in cleared.values():
        if not str(asset.rights_holder).strip() or not str(asset.license_basis).strip():
            errors.append(
                f"{asset.object_key} lacks rights holder or license basis — cannot be published"
            )

    # Drift: something is already public that this manifest does not account for.
    for asset in assets:
        if (
            asset.publication_state == MediaAssetState.PUBLISHED
            and str(asset.object_key) not in cleared
        ):
            errors.append(
                f"{asset.object_key} is already PUBLISHED but not covered by the "
                f"clearance manifest — resolve the drift before re-running"
            )

    return [cleared[k] for k in sorted(cleared)], errors


async def _run(
    db_url: str, manifest: dict[str, Any], dry_run: bool
) -> tuple[dict[str, Any], list[str], list[str]]:
    engine = create_async_engine(db_url)
    lines: list[str] = []
    errors: list[str] = []
    summary: dict[str, Any] = {
        "cleared": 0,
        "published": 0,
        "already_published": 0,
        "withheld": 0,
    }
    try:
        factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
        async with factory() as session:
            try:
                assets = list(
                    (await session.execute(select(MediaAsset).order_by(MediaAsset.object_key)))
                    .scalars()
                    .all()
                )
                cleared, errors = _plan(assets, manifest)
                summary["cleared"] = len(cleared)
                summary["withheld"] = len(assets) - len(cleared)

                if errors:
                    return summary, lines, errors

                service = MediaService(session)
                for asset in cleared:
                    object_key = str(asset.object_key)
                    if asset.publication_state == MediaAssetState.PUBLISHED:
                        summary["already_published"] += 1
                        lines.append(f"ALREADY_PUBLISHED media {object_key}")
                        continue
                    # Grant the rights bit the fail-closed importer withheld,
                    # then publish through the gated service (AC-01).
                    asset.publication_permission = True
                    await service.publish(object_key)
                    summary["published"] += 1
                    lines.append(f"PUBLISHED media {object_key}")

                cleared_keys = {str(a.object_key) for a in cleared}
                withheld: dict[str, int] = {}
                for asset in assets:
                    key = str(asset.object_key)
                    if key not in cleared_keys:
                        group = _top_group(key)
                        withheld[group] = withheld.get(group, 0) + 1
                summary["withheld_groups"] = dict(sorted(withheld.items()))

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
    return summary, lines, errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--clearance-file",
        type=Path,
        required=True,
        help="JSON manifest of P0/P1 assets cleared for publication (the authorization record)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="run every read and write then roll back (report only; default)",
    )
    parser.add_argument(
        "--commit", dest="dry_run", action="store_false", help="actually write (operator action)"
    )
    parser.add_argument("--env-file", type=Path, default=None)
    parser.add_argument("--test-mode", action="store_true", help="isolated test runs only")
    parser.add_argument("--allow-sqlite", action="store_true", help="isolated test runs only")
    args = parser.parse_args(argv)

    if not args.clearance_file.is_file():
        print(f"CLEARANCE_FILE=FAIL (not found: {args.clearance_file.name})")
        return 1
    try:
        manifest = load_clearance(args.clearance_file)
    except ClearanceError as exc:
        print(f"CLEARANCE_FILE=FAIL ({exc})")
        return 1
    print(f"CLEARANCE_BASIS={manifest['basis']}")

    env: dict[str, str] = dict(os.environ)
    if args.env_file is not None:
        if not args.env_file.is_file():
            print(f"ENV_FILE=FAIL (not found: {args.env_file.name})")
            return 1
        env.update(validator.parse_env_file(args.env_file))

    environment = "prod" if not args.test_mode else env.get("HFM_ENV", "test")
    errors = validator.validate_env(env, environment=environment, allow_sqlite=args.allow_sqlite)
    if args.test_mode:
        errors = [e for e in errors if "HFM_ENV mismatch" not in e]
    if errors:
        for reason in errors:
            print(f"ENV_VALIDATION=FAIL ({reason})")
        print("PUBLISH_MEDIA=FAIL")
        return 1

    db_url = env.get("HFM_DATABASE_URL", "")
    if not args.allow_sqlite:
        migration_errors = validator.verify_migration(BACKEND_DIR, db_url, "0016")
        if migration_errors:
            for reason in migration_errors:
                print(f"MIGRATION_VERIFY=FAIL ({reason})")
            print("PUBLISH_MEDIA=FAIL (database must be migrated at 0016)")
            return 1

    try:
        summary, lines, plan_errors = asyncio.run(_run(db_url, manifest, args.dry_run))
    except Exception as exc:  # noqa: BLE001 - operator-facing top-level guard
        print(f"PUBLISH_MEDIA=FAIL ({type(exc).__name__}: {exc})")
        return 1

    for line in lines:
        print(line)
    for reason in plan_errors:
        print(f"CLEARANCE=FAIL ({reason})")
    print(f"SUMMARY={summary}")
    if plan_errors:
        print("PUBLISH_MEDIA=FAIL")
        return 1
    print("PUBLISH_MEDIA=PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
