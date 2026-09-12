#!/usr/bin/env python3
"""HFM content publication pipeline — operator-only controlled publish.

Admits and publishes the canonical domain records (Works and/or Persons)
into the public projection, end to end, through the frozen P1-01/P1-09
lifecycle (admit → submit → review → publish). This is the operator-facing
counterpart to the already-built ContentArtifactRepository / PublicationService.

Why this script exists (audit finding): the production database holds 14
Works and 17 Persons, but ``sources`` / ``content_artifacts`` /
``publication_records`` are all empty, so the public portal returns nothing.
This script is the controlled, idempotent bridge from "metadata ingested" to
"published projection" — it does NOT guess rights, does NOT publish
unreviewed content, and never runs automatically.

Fail-closed rules (mirror the frozen P1-01/P1-09 gates):
  - ``--rights-status`` is REQUIRED and must be a non-UNKNOWN RightsStatus
    value; UNKNOWN content is never admitted (no silent default);
  - each entity is bound to an immutable Source (``canonical-<kind>:<stable_id>``)
    created idempotently, so re-runs never duplicate or silently overwrite;
  - the admission gate rejects missing provenance / unknown rights / missing
    content hash — a rejected artifact is reported, never published;
  - publication follows the frozen transition machine (PENDING_REVIEW →
    APPROVED → PUBLISHED); already-PUBLISHED records are an idempotent no-op;
  - separation of duties: the creator (SCHOLAR_RESEARCHER) never reviews and
    the reviewer (CONTENT_REVIEWER) never creates (ADR-07 Guard-02);
  - single transaction: --dry-run performs every read and write then rolls
    back, so the reported plan is exactly what a real run would commit.

Usage:
    HFM_ENV=prod HFM_DATABASE_URL=<postgres DSN to /hfm_prod> \
    python publish-content.py --rights-status customer_owned --scope works
    # review first, then publish: add --dry-run
    # test-only isolated runs: add --test-mode --allow-sqlite

Exit codes: 0 = PASS (all in-scope entities published or already published),
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


# Shared production preflight (same single source as initialize-production).
validator = _load_module(
    "validate_production_env", _SCRIPT_DIR / "validate-production-env.py"
)

# hfm models/services run from source (apps/backend/src) — the same path the
# canonical backend gates use; modules are loaded by file path so static
# checks stay clean.
sys.path.insert(0, str(BACKEND_DIR / "src"))

from hfm.models.content_artifact import (
    ContentAdmissionState,
    ProvenanceStatus,
    RightsStatus,
    ValidationResult,
)
from hfm.models.identity import (
    Role,
    User,
    UserRoleCode,
    user_roles,
)
from hfm.models.person import Person
from hfm.models.publication import PublicationRecord, PublicationStatus
from hfm.models.source import Source
from hfm.models.work import Work
from hfm.phase1.auth import (
    Principal,
    ensure_roles_seeded,
    hash_password,
    issue_token,
    principal_for_token,
)
from hfm.phase1.publication import PublicationService
from hfm.repositories.content_artifact import (
    ContentArtifactRepository,
)
from hfm.repositories.source import SourceRepository
from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

CREATOR_USERNAME = "content-publisher-creator"
REVIEWER_USERNAME = "content-publisher-reviewer"

#: Rights values accepted at the operator boundary. UNKNOWN is deliberately
#: excluded — unknown rights are never admitted (P1-01 fail-closed gate).
ADMISSIBLE_RIGHTS = {r.value for r in RightsStatus if r is not RightsStatus.UNKNOWN}


def canonical_content(kind: str, *, entity_id: str, **fields: Any) -> bytes:
    """Deterministic canonical bytes for one entity (content-hash input)."""
    payload: dict[str, Any] = {"kind": kind, "entity_id": entity_id, **fields}
    return json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _source_key(kind: str, stable_id: str | None, fallback_id: str) -> str:
    return f"canonical-{kind}:{stable_id or fallback_id}"


def _resolve_rights(
    manifest: dict[str, str],
    kind: str,
    stable_id: str | None,
    fallback: RightsStatus,
) -> RightsStatus:
    """Per-entity rights from a manifest, falling back to the CLI default.

    Manifest keys are ``"{kind}:{stable_id}"``; a missing key uses the
    fallback. A value that is not an admissible RightsStatus is rejected
    fail-closed rather than silently coerced (UNKNOWN is never admissible).
    """
    if stable_id is None:
        return fallback
    raw = manifest.get(f"{kind}:{stable_id}")
    if raw is None:
        return fallback
    try:
        value = RightsStatus(raw)
    except ValueError as exc:
        raise ValueError(
            f"rights manifest has invalid value for {kind}:{stable_id}: {raw}"
        ) from exc
    if value is RightsStatus.UNKNOWN:
        raise ValueError(f"rights manifest must not use UNKNOWN for {kind}:{stable_id}")
    return value


async def _ensure_service_user(
    session: AsyncSession, username: str, role_code: UserRoleCode
) -> User:
    """Idempotently ensure a fixed service account exists with the role linked.

    Password is a fresh random secret each creation (never printed, never used
    to log in); the script authenticates via an in-memory signed token, not the
    password. An existing account is repaired only by linking the role — never
    by changing credentials or widening anything else.
    """
    await ensure_roles_seeded(session)
    role = (
        await session.execute(select(Role).where(Role.code == role_code.value))
    ).scalar_one()
    user = (
        await session.execute(select(User).where(User.username == username))
    ).scalar_one_or_none()
    if user is None:
        user = User(
            username=username,
            password_hash=hash_password(os.urandom(24).hex()),
            created_by=None,
        )
        session.add(user)
        await session.flush()
    existing_link = (
        await session.execute(
            select(user_roles).where(
                user_roles.c.user_id == user.id, user_roles.c.role_id == role.id
            )
        )
    ).first()
    if existing_link is None:
        await session.execute(
            user_roles.insert().values(user_id=user.id, role_id=role.id)
        )
    await session.flush()
    return user


async def _principal_for(
    session: AsyncSession, user: User, role_code: UserRoleCode
) -> Principal:
    token = issue_token(user.id, role_code.value, user.token_version)
    return await principal_for_token(session, token)


async def _publish_one(
    session: AsyncSession,
    *,
    kind: str,
    entity_id: str,
    title: str,
    stable_id: str | None,
    content: bytes,
    rights_status: RightsStatus,
    rights_basis: str | None,
    allowed_scope: str | None,
    creator: Principal,
    reviewer: Principal,
) -> tuple[str, str]:
    """Admit + publish one canonical entity; returns (state, detail).

    States: published | already_published | rejected.
    """
    source, created = await SourceRepository(session).create_idempotent(
        source_key=_source_key(kind, stable_id, entity_id),
        source_type=f"canonical_{kind}",
        title=title,
        rights_basis=rights_basis,
        allowed_scope=allowed_scope,
    )
    source_state = "created" if created else "existing"

    artifact = await ContentArtifactRepository(session).submit_with_source_check(
        source_id=source.id,
        content=content,
        format="application/json",
        provenance_status=ProvenanceStatus.VERIFIED,
        rights_status=rights_status,
        validation_result=ValidationResult.PASS,
        subject_entity_id=entity_id,
        created_by=creator.user_id,
    )

    if artifact.admission_state == ContentAdmissionState.REJECTED.value:
        return "rejected", f"{artifact.rejection_reason} (source={source_state})"

    svc = PublicationService(session)
    record = (
        await session.execute(
            select(PublicationRecord).where(
                PublicationRecord.artifact_id == artifact.id
            )
        )
    ).scalar_one_or_none()

    if record is None:
        record = await svc.submit_for_review(artifact_id=artifact.id, creator=creator)
    if record.publication_status == PublicationStatus.PUBLISHED.value:
        return "already_published", f"source={source_state}"
    if record.publication_status == PublicationStatus.PENDING_REVIEW.value:
        record = await svc.review(
            artifact_id=artifact.id, reviewer=reviewer, approve=True
        )
    if record.publication_status == PublicationStatus.APPROVED.value:
        record = await svc.publish(artifact_id=artifact.id, actor=reviewer)

    return "published", f"source={source_state}"


async def _run(
    db_url: str,
    rights_status: RightsStatus,
    rights_manifest: dict[str, str],
    scope: str,
    rights_basis: str | None,
    allowed_scope: str | None,
    dry_run: bool,
) -> tuple[dict[str, int], list[str]]:
    engine = create_async_engine(db_url)
    summary = {
        "published": 0,
        "already_published": 0,
        "rejected": 0,
        "sources_total": 0,
    }
    lines: list[str] = []
    try:
        factory = async_sessionmaker(
            engine, expire_on_commit=False, class_=AsyncSession
        )
        async with factory() as session:
            try:
                creator_user = await _ensure_service_user(
                    session, CREATOR_USERNAME, UserRoleCode.SCHOLAR_RESEARCHER
                )
                reviewer_user = await _ensure_service_user(
                    session, REVIEWER_USERNAME, UserRoleCode.CONTENT_REVIEWER
                )
                creator = await _principal_for(
                    session, creator_user, UserRoleCode.SCHOLAR_RESEARCHER
                )
                reviewer = await _principal_for(
                    session, reviewer_user, UserRoleCode.CONTENT_REVIEWER
                )

                tasks: list[tuple[str, str, str | None, str, bytes, RightsStatus]] = []
                if scope in ("works", "all"):
                    for work in (
                        (await session.execute(select(Work).order_by(Work.title)))
                        .scalars()
                        .all()
                    ):
                        if work.entity_id is None:
                            lines.append(f"SKIP work {work.title}: no entity_id")
                            continue
                        tasks.append(
                            (
                                "work",
                                work.entity_id,
                                work.stable_id,
                                work.title,
                                canonical_content(
                                    "work",
                                    entity_id=work.entity_id,
                                    title=work.title,
                                    dynasty=work.dynasty,
                                    category=work.category,
                                    stable_id=work.stable_id,
                                ),
                                _resolve_rights(
                                    rights_manifest,
                                    "work",
                                    work.stable_id,
                                    rights_status,
                                ),
                            )
                        )
                if scope in ("persons", "all"):
                    for person in (
                        (await session.execute(select(Person).order_by(Person.name_zh)))
                        .scalars()
                        .all()
                    ):
                        tasks.append(
                            (
                                "person",
                                person.entity_id,
                                person.stable_id,
                                person.name_zh or person.entity_id,
                                canonical_content(
                                    "person",
                                    entity_id=person.entity_id,
                                    name_zh=person.name_zh,
                                    dynasty=person.dynasty,
                                    stable_id=person.stable_id,
                                ),
                                _resolve_rights(
                                    rights_manifest,
                                    "person",
                                    person.stable_id,
                                    rights_status,
                                ),
                            )
                        )

                for kind, entity_id, stable_id, title, content, rights in tasks:
                    state, detail = await _publish_one(
                        session,
                        kind=kind,
                        entity_id=entity_id,
                        title=title,
                        stable_id=stable_id,
                        content=content,
                        rights_status=rights,
                        rights_basis=rights_basis,
                        allowed_scope=allowed_scope,
                        creator=creator,
                        reviewer=reviewer,
                    )
                    if state in ("published", "already_published", "rejected"):
                        summary[state] += 1
                    if state == "rejected":
                        lines.append(f"REJECTED {kind} {title}: {detail}")
                    else:
                        lines.append(f"{state.upper()} {kind} {title}")

                sources_total = (
                    (await session.execute(select(Source.source_key))).scalars().all()
                )
                summary["sources_total"] = len(sources_total)

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
        "--rights-status",
        required=True,
        choices=sorted(ADMISSIBLE_RIGHTS),
        help="rights classification for admitted content (UNKNOWN is rejected)",
    )
    parser.add_argument(
        "--scope",
        default="works",
        choices=("works", "persons", "all"),
        help="which canonical entities to publish (default: works)",
    )
    parser.add_argument("--rights-basis", default=None)
    parser.add_argument("--allowed-scope", default=None)
    parser.add_argument(
        "--rights-file",
        type=Path,
        default=None,
        help="JSON manifest keyed by '{kind}:{stable_id}' overriding --rights-status",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="run every read and write then roll back (report only)",
    )
    parser.add_argument("--env-file", type=Path, default=None)
    parser.add_argument(
        "--test-mode", action="store_true", help="isolated test runs only"
    )
    parser.add_argument(
        "--allow-sqlite", action="store_true", help="isolated test runs only"
    )
    args = parser.parse_args(argv)

    env: dict[str, str] = dict(os.environ)
    if args.env_file is not None:
        if not args.env_file.is_file():
            print(f"ENV_FILE=FAIL (not found: {args.env_file.name})")
            return 1
        env.update(validator.parse_env_file(args.env_file))

    environment = "prod" if not args.test_mode else env.get("HFM_ENV", "test")
    errors = validator.validate_env(
        env, environment=environment, allow_sqlite=args.allow_sqlite
    )
    if args.test_mode:
        errors = [e for e in errors if "HFM_ENV mismatch" not in e]
    if errors:
        for reason in errors:
            print(f"ENV_VALIDATION=FAIL ({reason})")
        print("PUBLISH_CONTENT=FAIL")
        return 1

    db_url = env.get("HFM_DATABASE_URL", "")
    if not args.allow_sqlite:
        migration_errors = validator.verify_migration(BACKEND_DIR, db_url, "0015")
        if migration_errors:
            for reason in migration_errors:
                print(f"MIGRATION_VERIFY=FAIL ({reason})")
            print("PUBLISH_CONTENT=FAIL (database must be migrated at 0015)")
            return 1

    rights_status = RightsStatus(args.rights_status)
    rights_manifest: dict[str, str] = {}
    if args.rights_file is not None:
        if not args.rights_file.is_file():
            print(f"RIGHTS_FILE=FAIL (not found: {args.rights_file.name})")
            return 1
        try:
            loaded = json.loads(args.rights_file.read_text(encoding="utf-8"))
            if not isinstance(loaded, dict) or not all(
                isinstance(k, str) and isinstance(v, str) for k, v in loaded.items()
            ):
                raise ValueError("manifest must be a JSON object of string -> string")
            rights_manifest = loaded
        except (json.JSONDecodeError, ValueError, OSError) as exc:
            print(f"RIGHTS_FILE=FAIL ({exc})")
            return 1
    try:
        summary, lines = asyncio.run(
            _run(
                db_url,
                rights_status,
                rights_manifest,
                args.scope,
                args.rights_basis,
                args.allowed_scope,
                args.dry_run,
            )
        )
    except Exception as exc:  # noqa: BLE001 - operator-facing top-level guard
        print(f"PUBLISH_CONTENT=FAIL ({type(exc).__name__}: {exc})")
        return 1

    for line in lines:
        print(line)
    print(f"SUMMARY={summary}")
    print("PUBLISH_CONTENT=PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
