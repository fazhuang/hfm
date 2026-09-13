#!/usr/bin/env python3
"""HFM P2 redaction pipeline — stage 3: publish redacted derivatives.

The only path by which P2 material reaches the public projection. A P2
*original* can never be published (policy ``HFM-ASSET-PRESENTATION-POLICY.md``
§4.1; enforced by the ``ck_media_assets_p2_original_never_published`` check
constraint), so this script grants and publishes **derivatives only**, and the
grant itself is refused on anything without an ``original_object_key``.

This is the derivative counterpart of ``publish-media.py``, which covers the
P0/P1 originals published directly. Same operator-only, manifest-driven,
dry-run-first shape.

What it checks beyond ``publish-media.py``:

  - the asset really is a derivative, carries a redaction token, and is
    registered P2 (never P3 — ``ck_media_assets_p3_never_published``);
  - the derivative file on disk hashes to the sha256 the registry recorded,
    so a derivative whose bytes were swapped after redaction cannot be
    published (``verify_asset_bytes``);
  - every derivative's **original** is still ``draft`` with
    ``publication_permission = false`` after the run — the whole premise is
    that the unredacted bytes stay sealed, so the run fails if that moved;
  - every derivative named in the manifest is checked, and the run fails on
    any that is already published outside the manifest (drift).

Usage:
    HFM_ENV=prod HFM_DATABASE_URL=<postgres DSN to /hfm_prod> \
    python publish-media-derivatives.py \
        --clearance-file content-production/07-review/heritage-derivative-clearance.json \
        --env-file ~/.hfm/secrets/prod.env
    # review first: omit --commit (default is dry-run, report + rollback)

Exit codes: 0 = PASS, 1 = FAIL, 2 = usage.
"""

from __future__ import annotations

import argparse
import asyncio
import importlib.util
import json
import os
import sys
from dataclasses import dataclass
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


validator = _load_module("validate_production_env", _SCRIPT_DIR / "validate-production-env.py")

sys.path.insert(0, str(BACKEND_DIR / "src"))

from hfm.core.config import DERIVATIVE_ROOT, MEDIA_ROOT  # noqa: E402
from hfm.phase2.media.models import MediaAsset, MediaAssetState, PrivacyClass  # noqa: E402
from hfm.phase2.media.service import MediaService, compute_sha256  # noqa: E402
from sqlalchemy import select  # noqa: E402
from sqlalchemy.ext.asyncio import (  # noqa: E402
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


class ClearanceError(ValueError):
    """Raised when a derivative clearance manifest is malformed."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ClearanceError(message)


def load_clearance(path: Path) -> dict[str, Any]:
    """Parse + validate the derivative clearance manifest (fail-closed)."""
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
        _require(
            rule.get("privacy_class") == PrivacyClass.P2,
            f"{where}.privacy_class must be 'P2' — this pipeline publishes redacted "
            f"P2 derivatives only (P0/P1 go through publish-media.py; P3 is never "
            f"published), got {rule.get('privacy_class')!r}",
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


def _read_bytes(object_key: str) -> bytes | None:
    """Read a derivative's bytes from the derivative root (then the media root)."""
    for root in (DERIVATIVE_ROOT, MEDIA_ROOT):
        candidate = Path(root) / object_key
        if candidate.is_file():
            return candidate.read_bytes()
    return None


@dataclass
class Plan:
    cleared: list[MediaAsset]
    errors: list[str]


async def _plan(session: AsyncSession, manifest: dict[str, Any]) -> Plan:
    """Resolve the manifest against the registry. Read-only; collects every error."""
    errors: list[str] = []
    assets = list(
        (await session.execute(select(MediaAsset).order_by(MediaAsset.object_key)))
        .scalars()
        .all()
    )
    derivatives = [a for a in assets if a.original_object_key is not None]

    cleared: dict[str, MediaAsset] = {}
    for index, rule in enumerate(manifest["rules"]):
        matched = [a for a in derivatives if _rule_matches(rule, str(a.object_key))]
        if len(matched) != rule["expected_count"]:
            errors.append(
                f"rules[{index}] matched {len(matched)} derivatives, "
                f"expected {rule['expected_count']} "
                f"({rule.get('prefix') or rule.get('object_key')})"
            )
            continue
        for asset in matched:
            key = str(asset.object_key)
            if key in cleared:
                errors.append(f"rules[{index}] re-clears {key} (duplicate coverage)")
                continue
            if str(asset.privacy_class) != PrivacyClass.P2:
                errors.append(f"{key} is registered {asset.privacy_class}, not P2")
                continue
            if not asset.redaction_token:
                errors.append(f"{key} carries no redaction token — refusing to publish")
                continue
            if not str(asset.rights_holder).strip() or not str(asset.license_basis).strip():
                errors.append(f"{key} lacks rights holder or license basis")
                continue
            cleared[key] = asset

    # Byte binding: the file on disk must still hash to what the registry
    # recorded at redaction time. A swapped or edited derivative is not the
    # artefact that was verified.
    for key, asset in cleared.items():
        data = _read_bytes(key)
        if data is None:
            errors.append(f"{key} has no file under the derivative root")
            continue
        actual = compute_sha256(data)
        if actual != str(asset.sha256):
            errors.append(
                f"{key} bytes hash to {actual[:12]}… but the registry binds "
                f"{str(asset.sha256)[:12]}… — the derivative changed after redaction"
            )

    # Drift: a derivative already public that this manifest does not account for.
    for asset in derivatives:
        if (
            asset.publication_state == MediaAssetState.PUBLISHED
            and str(asset.object_key) not in cleared
        ):
            errors.append(
                f"{asset.object_key} is already PUBLISHED but not covered by the "
                f"clearance manifest — resolve the drift before re-running"
            )

    return Plan(cleared=[cleared[k] for k in sorted(cleared)], errors=errors)


async def _run(
    db_url: str, manifest: dict[str, Any], dry_run: bool
) -> tuple[dict[str, Any], list[str], list[str]]:
    engine = create_async_engine(db_url)
    lines: list[str] = []
    summary: dict[str, Any] = {"cleared": 0, "published": 0, "already_published": 0}
    try:
        factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
        async with factory() as session:
            try:
                plan = await _plan(session, manifest)
                summary["cleared"] = len(plan.cleared)
                if plan.errors:
                    return summary, lines, plan.errors

                service = MediaService(session)
                for asset in plan.cleared:
                    key = str(asset.object_key)
                    if asset.publication_state == MediaAssetState.PUBLISHED:
                        summary["already_published"] += 1
                        lines.append(f"ALREADY_PUBLISHED media {key}")
                        continue
                    # Grant on the derivative, then publish through the gated
                    # service. The grant is refused on anything that is not a
                    # token-bearing derivative, and the original is never touched.
                    await service.grant_derivative_publication(key)
                    await service.publish(key)
                    summary["published"] += 1
                    lines.append(f"PUBLISHED derivative {key}")

                # The premise is that the originals stay sealed. Prove it rather
                # than assume it: a published derivative whose original also went
                # public would defeat the entire pipeline.
                originals = {
                    a.object_key: a
                    for a in (
                        await session.execute(select(MediaAsset))
                    ).scalars().all()
                    if a.original_object_key is not None
                }
                errors: list[str] = []
                for derivative in originals.values():
                    original_key = str(derivative.original_object_key)
                    original = (
                        await session.execute(
                            select(MediaAsset).where(MediaAsset.object_key == original_key)
                        )
                    ).scalar_one_or_none()
                    if original is None:
                        errors.append(f"{derivative.object_key}: original {original_key} missing")
                        continue
                    if original.publication_state != MediaAssetState.DRAFT:
                        errors.append(
                            f"{original_key} is {original.publication_state}, not draft — "
                            f"the unredacted original must stay sealed"
                        )
                    if original.publication_permission:
                        errors.append(
                            f"{original_key} carries a publication permission — the "
                            f"unredacted original must stay sealed"
                        )
                if errors:
                    return summary, lines, errors

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
    return summary, lines, []


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--clearance-file",
        type=Path,
        required=True,
        help="JSON manifest of redacted P2 derivatives cleared for publication",
    )
    parser.add_argument("--dry-run", action="store_true", default=True, help="report only (default)")
    parser.add_argument(
        "--commit", dest="dry_run", action="store_false", help="actually write (operator action)"
    )
    parser.add_argument("--env-file", type=Path, default=None)
    parser.add_argument("--test-mode", action="store_true")
    parser.add_argument("--allow-sqlite", action="store_true")
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
    if errors:
        for error in errors:
            print(f"ENV=FAIL ({error})")
        return 1
    db_url = env.get("HFM_DATABASE_URL")
    if not db_url:
        print("ENV=FAIL (HFM_DATABASE_URL missing)")
        return 1

    summary, lines, run_errors = asyncio.run(_run(db_url, manifest, args.dry_run))
    for line in lines:
        print(line)
    for error in run_errors:
        print(f"ERROR {error}")

    print(f"MODE={'DRY_RUN' if args.dry_run else 'COMMIT'}")
    print(
        f"CLEARED={summary['cleared']} PUBLISHED={summary['published']} "
        f"ALREADY_PUBLISHED={summary['already_published']}"
    )
    if run_errors:
        print("RESULT=FAIL")
        return 1
    print("RESULT=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
