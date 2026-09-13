#!/usr/bin/env python3
"""HFM ND-1 B03 — operator-only production initialization.

Establishes the EXISTING product's minimal production state on an already
migrated database (Alembic at 0017, verified read-only):

  - PROD_REQUIRED: the frozen five-role matrix (ADR-07) seeded via the
    existing `ensure_roles_seeded` (schema-level, idempotent) plus ONE first
    SYSTEM_ADMIN account supplied securely by the operator;
  - PROD_OPTIONAL: none (no invented reference data exists in the product);
  - DEV_ONLY / TEST_ONLY / FORBIDDEN_IN_PRODUCTION: recovery bootstrap data,
    demo content and HFB imports are never created here.

Rules:
  - no committed credentials; the first-admin password is read from
    HFM_ADMIN_PASSWORD (deploy-time secret) or prompted (getpass, TTY only)
    and never printed;
  - repeat execution is defined: an active SYSTEM_ADMIN already present is a
    successful idempotent no-op (ALREADY_PRESENT); a user matching the admin
    username without the SYSTEM_ADMIN role is REPAIRED (role linked); partial
    state never commits half-written data (single transaction, rollback on
    error);
  - the exact role matrix is verified (5 roles, no duplicates) and the admin
    count stays exactly one SYSTEM_ADMIN after first run;
  - the production bootstrap binds the SINGLE canonical database (hfm_prod):
    the shared production preflight rejects restore/verify/recovery/scratch or
    any other database name (no prefix matching);
  - the first-admin password policy is the SAME single source as the runtime
    change-password path (hfm.phase1.auth.password_policy_reasons); only the
    operator-facing display wording differs here;
  - no RBAC change, no new capability, no permission widening, no automatic
    production execution.

Usage:
    HFM_ENV=prod HFM_DATABASE_URL=<postgres DSN to /hfm_prod> \
    HFM_ADMIN_USERNAME=root HFM_ADMIN_PASSWORD=<secret> \
    python initialize-production.py [--env-file PATH]
    # test-only isolated runs: add --test-mode --allow-sqlite
Exit codes: 0 = PASS (CREATED/ALREADY_PRESENT/REPAIRED), 1 = FAIL, 2 = usage.
"""

from __future__ import annotations

import argparse
import asyncio
import getpass
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


# Production preflight rules are shared with the ND-1 B01 validator.
validator = _load_module(
    "validate_production_env", _SCRIPT_DIR / "validate-production-env.py"
)

# hfm models/auth run from source (apps/backend/src) — same path the canonical
# backend gates use; modules are loaded by file path so static checks stay clean.
sys.path.insert(0, str(BACKEND_DIR / "src"))
from hfm.models.identity import Role, User, UserRoleCode, user_roles
from hfm.phase1.auth import (
    MIN_PASSWORD_LENGTH,
    ensure_roles_seeded,
    hash_password,
    password_policy_reasons,
)
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

EXPECTED_ROLE_CODES = {role.value for role in UserRoleCode}


async def _initialize(
    db_url: str, admin_username: str, admin_password: str
) -> tuple[str, str, str]:
    """Run initialization in one transaction; returns (roles, admin_state, admin_id).

    ND-1 RV-P1-03: this function NEVER emits DDL and never repairs schema
    drift. It operates only on the qualified migrated schema (the preflight
    verified current == 0017); every query below targets tables created by the
    migrations. A structurally invalid target (e.g. a dropped table) raises
    and rolls back instead of being silently mutated.
    """
    engine = create_async_engine(db_url)
    try:
        factory = async_sessionmaker(
            engine, expire_on_commit=False, class_=AsyncSession
        )
        async with factory() as session:
            try:
                await ensure_roles_seeded(session)
                # Exact role matrix (PROD_REQUIRED manifest): 5 codes, no dupes.
                rows = (await session.execute(select(Role.code))).scalars().all()
                actual_codes = set(rows)
                if (
                    len(rows) != len(EXPECTED_ROLE_CODES)
                    or actual_codes != EXPECTED_ROLE_CODES
                ):
                    missing = sorted(EXPECTED_ROLE_CODES - actual_codes)
                    extra = sorted(actual_codes - EXPECTED_ROLE_CODES)
                    raise RuntimeError(
                        f"role matrix invalid (missing={missing} extra={extra})"
                    )

                # Existing SYSTEM_ADMIN users decide idempotence.
                admin_role_id = (
                    await session.execute(
                        select(Role.id).where(Role.code == "SYSTEM_ADMIN")
                    )
                ).scalar_one()
                admin_count = (
                    await session.execute(
                        select(func.count())
                        .select_from(User)
                        .join(user_roles, user_roles.c.user_id == User.id)
                        .where(user_roles.c.role_id == admin_role_id)
                    )
                ).scalar_one()

                if int(admin_count) > 0:
                    await session.commit()
                    return "PASS", "ALREADY_PRESENT", ""

                existing_user = (
                    await session.execute(
                        select(User).where(User.username == admin_username)
                    )
                ).scalar_one_or_none()

                if existing_user is not None:
                    # Partial state repair: the operator user exists but lost /
                    # never received the SYSTEM_ADMIN link. Only the bootstrap
                    # path grants SYSTEM_ADMIN — never a permission widening.
                    await session.execute(
                        user_roles.insert().values(
                            user_id=existing_user.id, role_id=admin_role_id
                        )
                    )
                    await session.commit()
                    return "PASS", "REPAIRED", str(existing_user.id)

                user = User(
                    username=admin_username,
                    password_hash=hash_password(admin_password),
                    created_by=None,
                )
                session.add(user)
                await session.flush()
                await session.execute(
                    user_roles.insert().values(user_id=user.id, role_id=admin_role_id)
                )
                await session.commit()
                return "PASS", "CREATED", str(user.id)
            except BaseException:
                await session.rollback()
                raise
    finally:
        await engine.dispose()


#: Operator-facing display wording per shared policy code. Accept/reject
#: semantics live in hfm.phase1.auth.password_policy_reasons (single source);
#: this map ONLY renders codes for the bootstrap operator (display may differ
#: from the runtime wording — no validation logic is duplicated here).
_BOOTSTRAP_POLICY_DISPLAY: dict[str, str] = {
    "required": "HFM_ADMIN_PASSWORD is missing",
    "too-short": f"HFM_ADMIN_PASSWORD is shorter than {MIN_PASSWORD_LENGTH} characters",
    "forbidden-default": "HFM_ADMIN_PASSWORD is a known demo/test/default value",
    "contains-username": "HFM_ADMIN_PASSWORD must not contain the login name",
}


def validate_bootstrap_password(username: str, password: str) -> list[str]:
    """Bootstrap display violations (empty list == accepted by the policy).

    The accept/reject decision is delegated to the single shared policy
    (hfm.phase1.auth.password_policy_reasons) — the same source the runtime
    change-own-password path uses — so a given password is accepted or
    rejected identically at both entry points.
    """
    return [
        _BOOTSTRAP_POLICY_DISPLAY[reason]
        for reason in password_policy_reasons(password, username=username)
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
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
        try:
            env = validator.merge_env(env, args.env_file)
        except validator.EnvConflictError as exc:
            print(f"ENV_FILE=FAIL ({exc})")
            return 1
    print(f"DB_TARGET={validator.describe_db_target(env)}")

    environment = "prod" if not args.test_mode else env.get("HFM_ENV", "test")
    errors = validator.validate_env(
        env, environment=environment, allow_sqlite=args.allow_sqlite
    )
    if args.test_mode:
        errors = [e for e in errors if "HFM_ENV mismatch" not in e]
    if errors:
        for reason in errors:
            print(f"ENV_VALIDATION=FAIL ({reason})")
        print("INITIALIZE_PRODUCTION=FAIL")
        return 1

    db_url = env.get("HFM_DATABASE_URL", "")
    if not args.allow_sqlite:
        migration_errors = validator.verify_migration(BACKEND_DIR, db_url, "0017")
        if migration_errors:
            for reason in migration_errors:
                print(f"MIGRATION_VERIFY=FAIL ({reason})")
            print("INITIALIZE_PRODUCTION=FAIL (database must be migrated at 0017)")
            return 1

    admin_username = env.get("HFM_ADMIN_USERNAME", "")
    admin_password = env.get("HFM_ADMIN_PASSWORD", "")
    if not admin_username:
        print("HFM_ADMIN_USERNAME=FAIL (missing)")
        print("INITIALIZE_PRODUCTION=FAIL")
        return 1
    if not admin_password and sys.stdin.isatty():
        admin_password = getpass.getpass("First SYSTEM_ADMIN password: ")
    if not admin_password:
        print(
            "HFM_ADMIN_PASSWORD=FAIL (missing; provide via environment for non-interactive runs)"
        )
        print("INITIALIZE_PRODUCTION=FAIL")
        return 1
    password_errors = validate_bootstrap_password(admin_username, admin_password)
    if password_errors:
        for reason in password_errors:
            print(f"ADMIN_PASSWORD=FAIL ({reason})")
        print("INITIALIZE_PRODUCTION=FAIL")
        return 1

    try:
        _, admin_state, admin_id = asyncio.run(
            _initialize(db_url, admin_username, admin_password)
        )
    except Exception as exc:  # noqa: BLE001 — operator-facing redacted failure
        print(f"INITIALIZE_PRODUCTION=FAIL ({type(exc).__name__}: {exc})")
        return 1

    print(f"INIT_ROLES=PASS (exact {len(EXPECTED_ROLE_CODES)}-role matrix verified)")
    print(f"INIT_ADMIN={admin_state}")
    if admin_state == "CREATED":
        print(f"INIT_ADMIN_USERNAME={admin_username}")
        print(f"INIT_ADMIN_ID={admin_id}")
    print("INITIALIZE_PRODUCTION=PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
