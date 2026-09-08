"""WR00-B2-R1 — canonical local-production env provisioning + path safety.

Proves scripts/provision-local-prod-env.py:

  - DEFAULT output is OUTSIDE the repository (cannot be committed by a plain
    ``git add .``);
  - a fresh provision writes a mode-0600 env file whose HFM_DATABASE_URL binds
    exactly the canonical database ``hfm_prod`` and whose HFM_TOKEN_SECRET is
    a fresh high-entropy value (>= 32 chars);
  - destination safety is enforced programmatically:
      outside-repo path                    -> ALLOW
      git-tracked repository path          -> REJECT
      untracked + non-ignored repo path    -> REJECT
      git-ignored dedicated secrets/ path  -> ALLOW
    (git ignore coverage is verified with ``git check-ignore``, never inferred
    from the directory name);
  - the generated secret is never printed to stdout/stderr and never written
    to any other file (no logging); nothing is committed.

Run from the repository root with the backend virtualenv python:
    apps/backend/.venv/bin/python -m pytest scripts/tests -q
"""

from __future__ import annotations

import importlib.util
import os
import secrets as _secrets
import stat
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
PROVISIONER = REPO_ROOT / "scripts" / "provision-local-prod-env.py"
BACKEND_DIR = REPO_ROOT / "apps" / "backend"
PYTHON = str(BACKEND_DIR / ".venv" / "bin" / "python")

_spec = importlib.util.spec_from_file_location("provisioner", PROVISIONER)
assert _spec is not None and _spec.loader is not None
provisioner = importlib.util.module_from_spec(_spec)
sys.modules["provisioner"] = provisioner
_spec.loader.exec_module(provisioner)

CANONICAL_DB = "hfm_prod"
DEDICATED_SECRET_DIR = provisioner.DEDICATED_SECRET_DIR
DEFAULT_OUT = provisioner.DEFAULT_OUT


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


def _provision(out: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [PYTHON, str(PROVISIONER), "--out", str(out)],
        capture_output=True,
        text=True,
        check=False,
    )


def test_default_output_is_outside_the_repository() -> None:
    """DEFAULT_SECRET_OUTPUT=OUTSIDE_REPOSITORY."""
    assert provisioner._outside_repo(DEFAULT_OUT)
    try:
        DEFAULT_OUT.relative_to(REPO_ROOT)
        raise AssertionError("default output must live outside the repository")
    except ValueError:
        pass


# ------------------------------------------------------------- path safety


def test_outside_repo_output_allowed(tmp_path: Path) -> None:
    out = tmp_path / "prod.env"
    run = _provision(out)
    assert run.returncode == 0, run.stdout + run.stderr
    assert "PROVISION_LOCAL_PROD=PASS" in run.stdout
    assert out.is_file()
    mode = stat.S_IMODE(out.stat().st_mode)
    assert mode == 0o600
    env = _parse_env(out)
    assert env["HFM_ENV"] == "prod"
    assert env["HFM_DATABASE_URL"].rsplit("/", 1)[-1] == CANONICAL_DB
    assert len(env["HFM_TOKEN_SECRET"]) >= 32
    out.unlink()


def test_tracked_repository_path_rejected() -> None:
    """A git-tracked repository path is REJECTED before any write."""
    tracked = REPO_ROOT / "scripts" / "README.md"
    original = tracked.read_text(encoding="utf-8")
    run = _provision(tracked)
    assert run.returncode == 1
    assert "PROVISION_LOCAL_PROD=FAIL" in run.stdout
    assert "tracked" in run.stdout
    assert tracked.read_text(encoding="utf-8") == original  # untouched


def test_untracked_nonignored_repository_path_rejected() -> None:
    """An untracked + non-ignored repository path is REJECTED (git-ignore is
    verified with git check-ignore, not guessed from the file name)."""
    out = REPO_ROOT / "provision-untracked-nonignored-probe.env"
    with open(out, "w", encoding="utf-8") as handle:
        handle.write("")
    out.unlink(missing_ok=True)
    run = _provision(out)
    assert run.returncode == 1
    assert "PROVISION_LOCAL_PROD=FAIL" in run.stdout
    assert "NOT covered by the current" in run.stdout
    assert not out.exists()  # nothing was written


def test_gitignored_dedicated_secret_path_allowed() -> None:
    """Repo-internal output is allowed ONLY under the dedicated git-ignored
    secrets/ directory (git check-ignore must confirm the ignore rule)."""
    out = DEDICATED_SECRET_DIR / "prod.env"
    out.unlink(missing_ok=True)
    try:
        ignored = subprocess.run(
            ["git", "-C", str(REPO_ROOT), "check-ignore", "--quiet", "--", str(out)],
            capture_output=True,
            check=False,
        )
        assert ignored.returncode == 0, "secrets/prod.env must be git-ignored"
        assert provisioner._under_dedicated_secret_dir(out)
        assert provisioner._secret_path_refusal(out) is None

        run = _provision(out)
        assert run.returncode == 0, run.stdout + run.stderr
        assert out.is_file()
        assert stat.S_IMODE(out.stat().st_mode) == 0o600
        env = _parse_env(out)
        assert env["HFM_DATABASE_URL"].rsplit("/", 1)[-1] == CANONICAL_DB
    finally:
        out.unlink(missing_ok=True)


def test_gitignore_verified_not_name_inferred(tmp_path: Path) -> None:
    """A repo-internal path under a 'secrets'-LOOKING but non-ignored dir is
    still rejected (the ignore rule is what matters, not the directory name)."""
    lookalike_dir = REPO_ROOT / "secrets-notignored"
    lookalike = lookalike_dir / "prod.env"
    run = _provision(lookalike)
    assert run.returncode == 1
    assert "NOT covered by the current" in run.stdout
    assert not lookalike.exists()
    if lookalike_dir.exists():
        lookalike_dir.rmdir()  # never created by the provisioner; defensive


# ------------------------------------------------------- secret containment


def test_secret_never_reported_and_no_auxiliary_output(tmp_path: Path) -> None:
    """REPORT_OUTPUT=NO / LOG_OUTPUT=NO: the token never reaches stdout,
    stderr or any other file in the output directory."""
    out = tmp_path / "prod.env"
    run = _provision(out)
    assert run.returncode == 0
    token = _parse_env(out)["HFM_TOKEN_SECRET"]
    assert token not in run.stdout
    assert token not in run.stderr
    assert not run.stderr
    # No log/report file is created next to the secret (single file only).
    assert sorted(p.name for p in tmp_path.iterdir()) == ["prod.env"]
    assert "CANONICAL_RUNTIME_DATABASE=hfm_prod" in run.stdout
    out.unlink()


def test_provision_two_runs_yield_distinct_secrets(tmp_path: Path) -> None:
    """Fresh high-entropy secret each provision (cryptographic random)."""
    first = _provision(tmp_path / "first.env")
    second = _provision(tmp_path / "second.env")
    assert first.returncode == 0 and second.returncode == 0
    token_a = _parse_env(tmp_path / "first.env")["HFM_TOKEN_SECRET"]
    token_b = _parse_env(tmp_path / "second.env")["HFM_TOKEN_SECRET"]
    assert token_a != token_b
    assert len(token_a) == len(token_b)
    (tmp_path / "first.env").unlink()
    (tmp_path / "second.env").unlink()


def test_provision_never_overwrites_existing_target(tmp_path: Path) -> None:
    out = tmp_path / "prod.env"
    first = _provision(out)
    assert first.returncode == 0
    original = out.read_text(encoding="utf-8")
    second = _provision(out)
    assert second.returncode == 1
    assert "PROVISION_LOCAL_PROD=FAIL" in second.stdout
    assert out.read_text(encoding="utf-8") == original  # untouched
    out.unlink()


def test_provisioned_file_passes_production_preflight(tmp_path: Path) -> None:
    """The produced runtime env satisfies the shared prod validation."""
    run = _provision(tmp_path / "prod.env")
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
    env_file.unlink()


def test_optional_db_password_never_reported(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Optional DB credentials in the env file never collide with known values
    and are never printed."""
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
    assert os.environ["HFM_DB_PASSWORD"] not in run.stdout + run.stderr
    assert env["HFM_TOKEN_SECRET"] not in run.stdout + run.stderr
    assert env["HFM_DATABASE_URL"].rsplit("/", 1)[-1] == CANONICAL_DB
    out.unlink()
