#!/usr/bin/env python3
"""HFM WR00-B2 — canonical local-production runtime env provisioning.

Creates (never overwrites) the local production runtime environment file that
binds the canonical runtime database ``hfm_prod`` and injects a freshly
generated ``HFM_TOKEN_SECRET``:

  - cryptographic-random, high-entropy token secret (secrets.token_urlsafe —
    stdlib CSPRNG; 48 bytes → 64 url-safe chars);
  - SOURCE_HARDCODE=NO  — the secret is generated, never present in source;
  - GIT_COMMIT=NO       — the file is written under the repo ``secrets/``
                          directory (git-ignored) with mode 0600; a tracked
                          target path is refused;
  - REPORT_OUTPUT=NO / LOG_OUTPUT=NO — the secret value is never printed,
                          written to logs, or reported; only the destination
                          path and redacted validation status are printed;
  - CANONICAL_RUNTIME_DATABASE=hfm_prod — the produced HFM_DATABASE_URL names
                          exactly ``hfm_prod`` (no dev/test/scratch/ambiguous
                          default); no real DB password is ever committed
                          (an optional operator DB password is read from the
                          HFM_DB_PASSWORD environment variable only);
  - the produced file is validated with the existing production preflight
    (scripts/validate-production-env.py, redacted) before reporting PASS.

The operator starts the canonical local-production runtime by exporting this
file into the backend process environment, e.g.:
    set -a && source secrets/prod.env && set +a
    HFM_ADMIN_USERNAME=hfm_admin HFM_ADMIN_PASSWORD=<secret> \\
        python scripts/initialize-production.py          # first bootstrap
    (cd apps/backend && exec uvicorn hfm.main:app --port 8000)

Usage:
    python scripts/provision-local-prod-env.py [--out PATH] [--db-user USER]
        [--db-host HOST] [--db-port PORT]
        # optional DB password read from HFM_DB_PASSWORD (never echoed)

Exit codes: 0 = PASS, 1 = FAIL, 2 = usage.
"""

from __future__ import annotations

import argparse
import contextlib
import getpass
import importlib.util
import os
import secrets
import subprocess
import sys
from pathlib import Path
from typing import Any
from urllib.parse import quote, urlsplit

_SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = _SCRIPT_DIR.parent

#: The canonical local-production database name. Fixed by contract — the
#: provisioner refuses any other database name (no fallback / ambiguity).
CANONICAL_RUNTIME_DATABASE = "hfm_prod"

#: Default git-ignored destination (repo .gitignore ignores the secrets/ dir).
DEFAULT_OUT = REPO_ROOT / "secrets" / "prod.env"

#: Default local PostgreSQL endpoint (operator-overridable).
DEFAULT_DB_HOST = "127.0.0.1"
DEFAULT_DB_PORT = 5432

#: Token secret entropy: 48 random bytes → 64 base64url chars (≥ 32 required
#: by the production preflight; well above the minimum).
_TOKEN_SECRET_BYTES = 48


def _load_validator() -> Any:
    """Load scripts/validate-production-env.py by path (shared preflight)."""
    spec = importlib.util.spec_from_file_location(
        "validate_production_env", _SCRIPT_DIR / "validate-production-env.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["validate_production_env"] = module
    spec.loader.exec_module(module)
    return module


def _generate_token_secret() -> str:
    """High-entropy cryptographic-random token secret (never committed)."""
    return secrets.token_urlsafe(_TOKEN_SECRET_BYTES)


def _build_database_url(
    user: str, host: str, port: int, password: str | None
) -> str:
    """Canonical local-production DSN — database name is fixed to hfm_prod."""
    if password:
        credentials = f"{quote(user)}:{quote(password)}"
    else:
        credentials = user
    return f"postgresql+asyncpg://{credentials}@{host}:{port}/{CANONICAL_RUNTIME_DATABASE}"


def _dbname_of(url: str) -> str:
    return urlsplit(url).path.lstrip("/").split("/")[0]


def _is_tracked(path: Path) -> bool:
    """True when git already tracks the target path (refuse — never overwrite
    a tracked file with a secret)."""
    run = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "ls-files", "--error-unmatch", str(path)],
        capture_output=True,
        check=False,
    )
    return run.returncode == 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--db-user", default=getpass.getuser())
    parser.add_argument("--db-host", default=DEFAULT_DB_HOST)
    parser.add_argument("--db-port", type=int, default=DEFAULT_DB_PORT)
    args = parser.parse_args(argv)

    out = args.out.expanduser().resolve()

    # Fail closed: never write into a git-tracked path (a tracked file must
    # never receive a generated secret), never overwrite an existing runtime
    # env (a re-provision must be an explicit operator action after removing
    # the old file), and never allow a non-canonical dbname.
    if _is_tracked(out):
        print("PROVISION_LOCAL_PROD=FAIL (target is a tracked file; refused)")
        return 1
    if out.exists():
        print(f"PROVISION_LOCAL_PROD=FAIL (target exists: {out}; remove it first)")
        return 1

    db_password = os.environ.get("HFM_DB_PASSWORD", "")
    db_url = _build_database_url(args.db_user, args.db_host, args.db_port, db_password or None)
    if _dbname_of(db_url) != CANONICAL_RUNTIME_DATABASE:
        print("PROVISION_LOCAL_PROD=FAIL (canonical runtime database must be hfm_prod)")
        return 1

    token_secret = _generate_token_secret()

    try:
        out.parent.mkdir(parents=True, exist_ok=True)
        # Sensitive file: created before content is written, owner rw only.
        fd = os.open(str(out), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        content = (
            "# HFM canonical local-production runtime (WR00-B2). Generated by\n"
            "# scripts/provision-local-prod-env.py — never edit/commit/report.\n"
            "HFM_ENV=prod\n"
            f"HFM_DATABASE_URL={db_url}\n"
            f"HFM_TOKEN_SECRET={token_secret}\n"
        )
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
        os.chmod(str(out), 0o600)
    except OSError as exc:  # noqa: BLE001
        print(f"PROVISION_LOCAL_PROD=FAIL (cannot write {out}: {exc})")
        return 1

    validator = _load_validator()
    env = validator.parse_env_file(out)
    errors = validator.validate_env(env, environment="prod")
    if errors:
        for reason in errors:
            print(f"ENV_VALIDATION=FAIL ({reason})")
        with contextlib.suppress(OSError):
            out.unlink()
        print("PROVISION_LOCAL_PROD=FAIL")
        return 1

    # Only non-secret status is reported: destination path + dbname.
    print(f"PROVISION_TARGET={out}")
    print(f"CANONICAL_RUNTIME_DATABASE={CANONICAL_RUNTIME_DATABASE}")
    print("ENV_VALIDATION=PASS (redacted)")
    print("PROVISION_LOCAL_PROD=PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
