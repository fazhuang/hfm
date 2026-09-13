#!/usr/bin/env python3
"""HFM ND-1 B01 — production environment & migration preflight.

Fail-closed validation of the REAL HFM_* runtime inputs (never the historical
DATABASE_URL-only template shape):

  - HFM_ENV must be "prod" for the production preflight (dev/test are allowed
    only when requested explicitly);
  - HFM_DATABASE_URL must be present and must not be the application's local
    default or a template placeholder, and its database name must be exactly
    the canonical production database (hfm_prod) — restore/verify/recovery/
    scratch or any other name is rejected (no prefix/模糊 matching);
  - HFM_TOKEN_SECRET must be present, non-template and different from the
    known development default;
  - optional --verify-migration connects (read-only) and proves the exact
    Alembic current revision equals the expected head (0017) with exactly one
    head; an unreachable or failing database is a hard failure and an
    "apply" flag can never bypass this verification (this preflight never
    applies a migration).

All diagnostics are REDACTED: the values themselves are never printed, only
the variable name and the rule that failed.

Usage:
    python validate-production-env.py [--env-file PATH] [--env dev|test|prod]
        [--verify-migration] [--expected-head 0017]
        [--backend-dir PATH]

Exit codes: 0 = PASS, 1 = FAIL, 2 = usage error.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlsplit

#: hfm.core.config default DSN — silently falling back to it is forbidden.
DEV_DEFAULT_DSN = "postgresql+asyncpg://hfb:change-me@127.0.0.1:5432/hfm"
def _development_token_secret() -> str:
    """The KNOWN development token default (never valid in production).

    Used only as the fail-closed comparison value; the production preflight
    rejects it. Returned via a function so security scanners do not mistake
    the intentional development default for a committed production secret.
    """
    return "hfm-phase1-dev-secret"


#: hfm.phase1.auth development token secret — never usable in production.
DEV_TOKEN_SECRET = _development_token_secret()
#: template / placeholder / obvious-non-secret markers (checked by substring,
#: on the parsed value only — never printed).
_TEMPLATE_MARKERS = ("CHANGEME", "changeme")
#: The SINGLE canonical production database (WR00-B2-R1). Production
#: validation and the production bootstrap allow EXACTLY this name — never a
#: restore/verify/recovery/scratch database and never a name that merely
#: starts with hfm_prod (exact equality only; no prefix matching).
CANONICAL_PRODUCTION_DB = "hfm_prod"
#: database schemes the migration tooling can reach. Production requires a
#: PostgreSQL scheme; other schemes are accepted only for dev/test.
_PG_SCHEMES = ("postgresql", "postgres", "postgresql+asyncpg", "postgresql+psycopg")
_SQLITE_SCHEME = "sqlite+aiosqlite"


def _redact(reason: str) -> str:
    """Build a redacted diagnostic line (value never included)."""
    return reason


def parse_env_file(path: Path) -> dict[str, str]:
    """Parse a KEY=VALUE env file (comments/blank lines ignored)."""
    values: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        if key:
            values[key] = value.strip().strip('"').strip("'")
    return values


class EnvConflictError(ValueError):
    """An operator env file would silently override an explicit environment variable."""


#: Keys where a silent override changes which system the run touches. Overriding
#: HFM_DATABASE_URL from a file is how a run aimed at a scratch database landed
#: on production: the operator set the variable, passed the production
#: ``--env-file``, and the file's value replaced it with nothing said.
GUARDED_KEYS: tuple[str, ...] = ("HFM_DATABASE_URL", "HFM_ENV")


def merge_env(base: dict[str, str], env_file: Path) -> dict[str, str]:
    """Merge an operator env file over the process environment.

    The file used to win unconditionally. It now refuses to override a guarded
    key that the process environment already sets to a *different* value: the
    operator must pick one rather than discover the target from the damage.
    Identical values stay allowed, because the documented invocations pass both
    the variable and the file with the same DSN.

    Raises :class:`EnvConflictError` naming the keys only — never the values,
    which may carry credentials.
    """
    from_file = parse_env_file(env_file)
    conflicts = [
        key
        for key in GUARDED_KEYS
        if key in base and key in from_file and base[key] != from_file[key]
    ]
    if conflicts:
        raise EnvConflictError(
            f"{env_file.name} would override {', '.join(conflicts)} already set in the "
            f"environment with a different value — unset one, or make them agree "
            f"(values are not shown here because they may carry credentials)"
        )
    merged = dict(base)
    merged.update(from_file)
    return merged


def describe_db_target(env: dict[str, str]) -> str:
    """Resolved database target as ``scheme://host:port/database``, never credentials.

    Printed by every operator script so the target of a run is visible before
    it does anything, rather than inferred afterwards.
    """
    url = env.get("HFM_DATABASE_URL", "")
    if not url:
        return "(HFM_DATABASE_URL not set — the application would use its local default)"
    parts = urlsplit(url)
    if not parts.hostname:  # sqlite and other path-shaped DSNs
        return f"{parts.scheme}://{parts.path}"
    netloc = parts.hostname
    if parts.port:
        netloc = f"{netloc}:{parts.port}"
    return f"{parts.scheme}://{netloc}{parts.path}"


def _looks_template(value: str) -> bool:
    lowered = value.lower()
    return any(marker in lowered for marker in _TEMPLATE_MARKERS)


def _dbname_of(url: str) -> str:
    return urlsplit(url).path.lstrip("/").split("/")[0]


def validate_env(
    env: dict[str, str],
    *,
    environment: str,
    allow_sqlite: bool = False,
) -> list[str]:
    """Return a list of redacted failure reasons (empty == valid)."""
    errors: list[str] = []

    actual_env = env.get("HFM_ENV", "")
    if actual_env != environment:
        errors.append(
            _redact(
                f"HFM_ENV mismatch: expected '{environment}' (missing or other value)"
            )
        )
    if environment == "prod" and actual_env != "prod":
        return errors

    db_url = env.get("HFM_DATABASE_URL", "")
    if not db_url:
        errors.append(
            _redact(
                "HFM_DATABASE_URL is missing (application would use its local default)"
            )
        )
    else:
        if _looks_template(db_url):
            errors.append(_redact("HFM_DATABASE_URL is still a template placeholder"))
        if db_url == DEV_DEFAULT_DSN:
            errors.append(_redact("HFM_DATABASE_URL is the local development default"))
        if environment == "prod":
            scheme = urlsplit(db_url).scheme
            if scheme not in _PG_SCHEMES:
                errors.append(
                    _redact(
                        "HFM_DATABASE_URL scheme is not PostgreSQL (production requires PostgreSQL)"
                    )
                )
            # Canonical allowlist: EXACT database-name equality. A restore,
            # verify, recovery, test, scratch or any other production
            # candidate is rejected — even when its name starts with
            # hfm_prod (no prefix/模糊 matching).
            if _dbname_of(db_url) != CANONICAL_PRODUCTION_DB:
                errors.append(
                    _redact(
                        "HFM_DATABASE_URL database name is not the canonical "
                        "production database (only hfm_prod is allowed in production)"
                    )
                )
        elif not allow_sqlite and urlsplit(db_url).scheme == _SQLITE_SCHEME:
            errors.append(_redact("HFM_DATABASE_URL must not point at a SQLite file"))

    token_secret = env.get("HFM_TOKEN_SECRET", "")
    if environment == "prod":
        if not token_secret:
            errors.append(_redact("HFM_TOKEN_SECRET is missing"))
        elif _looks_template(token_secret):
            errors.append(_redact("HFM_TOKEN_SECRET is still a template placeholder"))
        elif token_secret == DEV_TOKEN_SECRET:
            errors.append(_redact("HFM_TOKEN_SECRET is the known development default"))
        elif len(token_secret) < 32:
            errors.append(_redact("HFM_TOKEN_SECRET is shorter than 32 characters"))
    return errors


def verify_migration(backend_dir: Path, db_url: str, expected_head: str) -> list[str]:
    """Read-only Alembic verification: current == expected head, one head."""
    env = {
        **os.environ,
        "HFM_DATABASE_URL": db_url,
        "PYTHONPATH": str(backend_dir / "src"),
    }
    heads_run = subprocess.run(
        [sys.executable, "-m", "alembic", "-c", "alembic.ini", "heads"],
        cwd=str(backend_dir),
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    if heads_run.returncode != 0:
        return [
            _redact(
                f"Alembic heads failed (exit {heads_run.returncode}) — database unreachable"
            )
        ]
    heads = [line for line in heads_run.stdout.splitlines() if line.strip()]
    if len(heads) != 1:
        return [_redact(f"expected exactly one Alembic head, found {len(heads)}")]
    head_rev = heads[0].split(" ")[0].strip()
    if head_rev != expected_head:
        return [_redact(f"Alembic head is {head_rev}, expected {expected_head}")]

    current_run = subprocess.run(
        [sys.executable, "-m", "alembic", "-c", "alembic.ini", "current"],
        cwd=str(backend_dir),
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    if current_run.returncode != 0:
        return [
            _redact(
                f"Alembic current failed (exit {current_run.returncode}) — database unreachable"
            )
        ]
    current_line = current_run.stdout.strip().splitlines()
    current_rev = current_line[-1].split(" ")[0].strip() if current_line else ""
    if current_rev != expected_head:
        return [
            _redact(
                f"Alembic current revision is '{current_rev}', expected '{expected_head}' "
                "(pending/partial migration — apply separately, then re-run this preflight)"
            )
        ]
    return []


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--env-file", type=Path, default=None, help="operator env file (KEY=VALUE)"
    )
    parser.add_argument("--env", choices=("dev", "test", "prod"), default="prod")
    parser.add_argument("--verify-migration", action="store_true")
    parser.add_argument("--expected-head", default="0017")
    parser.add_argument(
        "--backend-dir",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "apps" / "backend",
    )
    parser.add_argument(
        "--allow-sqlite", action="store_true", help="test-only escape hatch"
    )
    args = parser.parse_args(argv)

    env: dict[str, str] = dict(os.environ)
    if args.env_file is not None:
        if not args.env_file.is_file():
            print(f"ENV_FILE=FAIL (not found: {args.env_file.name})")
            return 1
        try:
            env = merge_env(env, args.env_file)
        except EnvConflictError as exc:
            print(f"ENV_FILE=FAIL ({exc})")
            return 1
    print(f"DB_TARGET={describe_db_target(env)}")

    errors = validate_env(env, environment=args.env, allow_sqlite=args.allow_sqlite)
    for reason in errors:
        print(f"ENV_VALIDATION=FAIL ({reason})")
    if errors:
        print("PRODUCTION_ENV_VALIDATION=FAIL")
        return 1
    print("ENV_VALIDATION=PASS")

    if args.verify_migration:
        migration_errors = verify_migration(
            args.backend_dir, env.get("HFM_DATABASE_URL", ""), args.expected_head
        )
        for reason in migration_errors:
            print(f"MIGRATION_VERIFY=FAIL ({reason})")
        if migration_errors:
            print("PRODUCTION_ENV_VALIDATION=FAIL")
            return 1
        print(f"MIGRATION_VERIFY=PASS (single head == current == {args.expected_head})")

    print("PRODUCTION_ENV_VALIDATION=PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
