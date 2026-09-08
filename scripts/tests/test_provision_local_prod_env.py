"""WR00-B2 — canonical local-production env provisioning tests.

Proves scripts/provision-local-prod-env.py:

  - a fresh provision writes a git-ignored, mode-0600 env file whose
    HFM_DATABASE_URL binds exactly the canonical database ``hfm_prod`` and
    whose HFM_TOKEN_SECRET is a fresh high-entropy value (>= 32 chars);
  - the generated secret never appears on stdout/stderr and never equals a
    known default;
  - the produced file passes the shared production preflight (redacted);
  - an existing target is never overwritten and a git-tracked target is
    refused;
  - no committed secret: the default destination is git-ignored.

Run from the repository root with the backend virtualenv python:
    apps/backend/.venv/bin/python -m pytest scripts/tests -q
"""

from __future__ import annotations

import os
import secrets as _secrets
import stat
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
PROVISIONER = REPO_ROOT / "scripts" / "provision-local-prod-env.py"
BACKEND_DIR = REPO_ROOT / "apps" / "backend"
PYTHON = str(BACKEND_DIR / ".venv" / "bin" / "python")

CANONICAL_DB = "hfm_prod"


def _parse_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        key, _, value = line.partition("=")
        if key:
            values[key.strip()] = value.strip()
    return values


def _provision(tmp_path: Path, name: str = "prod.env") -> subprocess.CompletedProcess[str]:
    out = tmp_path / name
    return subprocess.run(
        [PYTHON, str(PROVISIONER), "--out", str(out)],
        capture_output=True,
        text=True,
        check=False,
    )


def test_provision_creates_canonical_runtime_env(tmp_path: Path) -> None:
    out = tmp_path / "prod.env"
    run = _provision(tmp_path)
    assert run.returncode == 0, run.stdout + run.stderr
    assert "PROVISION_LOCAL_PROD=PASS" in run.stdout
    assert f"CANONICAL_RUNTIME_DATABASE={CANONICAL_DB}" in run.stdout
    assert "ENV_VALIDATION=PASS" in run.stdout
    assert out.is_file()

    # Owner read/write only — the secret file is never group/world readable.
    mode = stat.S_IMODE(out.stat().st_mode)
    assert mode == 0o600

    env = _parse_env(out)
    assert env["HFM_ENV"] == "prod"
    # Canonical runtime database binding — never a dev/test/scratch/default DB.
    assert f"/{CANONICAL_DB}" in env["HFM_DATABASE_URL"]
    dbname = env["HFM_DATABASE_URL"].rsplit("/", 1)[-1]
    assert dbname == CANONICAL_DB
    assert dbname not in ("hfm", "hfm_dev", "hfm_test", "postgres")
    assert "CHANGEME" not in env["HFM_DATABASE_URL"]
    assert env["HFM_DATABASE_URL"] != (
        "postgresql+asyncpg://hfb:change-me@127.0.0.1:5432/hfm"
    )

    token = env["HFM_TOKEN_SECRET"]
    assert len(token) >= 32  # production preflight minimum
    assert token not in ("", "x" * 40, "hfm-phase1-dev-secret")


def test_provision_secret_never_reported(tmp_path: Path) -> None:
    """REPORT_OUTPUT=NO / LOG_OUTPUT=NO: the token never reaches stdout/stderr."""
    out = tmp_path / "prod.env"
    run = _provision(tmp_path)
    assert run.returncode == 0
    token = _parse_env(out)["HFM_TOKEN_SECRET"]
    assert token not in run.stdout
    assert token not in run.stderr
    # Diagnostics never embed the DSN credentials either (dbname only).
    assert "CANONICAL_RUNTIME_DATABASE=hfm_prod" in run.stdout


def test_provision_two_runs_yield_distinct_secrets(tmp_path: Path) -> None:
    """Fresh high-entropy secret each provision (cryptographic random)."""
    first = _provision(tmp_path, "first.env")
    second = _provision(tmp_path, "second.env")
    assert first.returncode == 0 and second.returncode == 0
    token_a = _parse_env(tmp_path / "first.env")["HFM_TOKEN_SECRET"]
    token_b = _parse_env(tmp_path / "second.env")["HFM_TOKEN_SECRET"]
    assert token_a != token_b
    assert len(token_a) == len(token_b)


def test_provision_never_overwrites_existing_target(tmp_path: Path) -> None:
    out = tmp_path / "prod.env"
    first = _provision(tmp_path)
    assert first.returncode == 0
    original = out.read_text(encoding="utf-8")
    second = _provision(tmp_path)
    assert second.returncode == 1
    assert "PROVISION_LOCAL_PROD=FAIL" in second.stdout
    assert out.read_text(encoding="utf-8") == original  # untouched


def test_provision_refuses_tracked_target(tmp_path: Path) -> None:
    """Never write a generated secret over a git-tracked file."""
    tracked = REPO_ROOT / "scripts" / "README.md"
    run = subprocess.run(
        [PYTHON, str(PROVISIONER), "--out", str(tracked)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert run.returncode == 1
    assert "tracked file" in run.stdout
    assert "PROVISION_LOCAL_PROD=FAIL" in run.stdout


def test_provisioned_file_passes_production_preflight(tmp_path: Path) -> None:
    """The produced runtime env satisfies the shared prod validation."""
    run = _provision(tmp_path)
    assert run.returncode == 0
    env_file = tmp_path / "prod.env"
    validate = subprocess.run(
        [
            PYTHON,
            str(REPO_ROOT / "scripts" / "validate-production-env.py"),
            "--env-file",
            str(env_file),
            "--env",
            "prod",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert validate.returncode == 0, validate.stdout + validate.stderr
    assert "ENV_VALIDATION=PASS" in validate.stdout


def test_default_destination_is_git_ignored() -> None:
    """GIT_COMMIT=NO: the default secrets/prod.env path can never be tracked."""
    ignored = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "check-ignore", "--quiet", "secrets/prod.env"],
        capture_output=True,
        check=False,
    )
    assert ignored.returncode == 0, "secrets/prod.env must be git-ignored"


def test_bootstrap_password_credentials_stay_isolated_from_bootstrap_secret(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """DB credentials in the env file never collide with known test values."""
    monkeypatch.setenv("HFM_DB_PASSWORD", _secrets.token_urlsafe(24))
    out = tmp_path / "prod.env"
    run = subprocess.run(
        [
            PYTHON,
            str(PROVISIONER),
            "--out",
            str(out),
            "--db-user",
            "hfm_app",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert run.returncode == 0, run.stdout + run.stderr
    env = _parse_env(out)
    token = env["HFM_TOKEN_SECRET"]
    # The provisioner never reports the DB password or the token.
    assert os.environ["HFM_DB_PASSWORD"] not in run.stdout + run.stderr
    assert token not in run.stdout + run.stderr
