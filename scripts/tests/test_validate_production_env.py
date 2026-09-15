"""ND-1 B01 — production environment preflight tests (synthetic + isolated DB).

Validates scripts/validate-production-env.py and scripts/deploy-gate.sh:

  - missing / template / known-dev / dev-dbname / sqlite-in-prod / weak
    token-secret configurations are rejected with REDACTED diagnostics;
  - a valid synthetic production configuration passes;
  - the read-only migration verification accepts an isolated database at 0017
    and blocks one at 0013; an unreachable database is a hard failure;
  - the deploy-gate launcher exits non-zero on invalid configs and cannot have
    verification bypassed by --apply-migrations.

Run from the repository root with the backend virtualenv python:
    apps/backend/.venv/bin/python -m pytest scripts/tests -q
"""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = REPO_ROOT / "apps" / "backend"
VALIDATOR = REPO_ROOT / "scripts" / "validate-production-env.py"
DEPLOY_GATE = REPO_ROOT / "scripts" / "deploy-gate.sh"

_spec = importlib.util.spec_from_file_location("validate_production_env", VALIDATOR)
assert _spec is not None and _spec.loader is not None
validator = importlib.util.module_from_spec(_spec)
sys.modules["validate_production_env"] = validator
_spec.loader.exec_module(validator)

PYTHON = str(BACKEND_DIR / ".venv" / "bin" / "python")


def _valid_prod_env() -> dict[str, str]:
    return {
        "HFM_ENV": "prod",
        "HFM_DATABASE_URL": "postgresql+asyncpg://real:user-secret@db.internal:5432/hfm_prod",
        "HFM_TOKEN_SECRET": "x" * 40,
        "LOG_LEVEL": "warn",
    }


def _write_env(path: Path, values: dict[str, str]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(f"{key}={value}\n" for key, value in values.items()), encoding="utf-8"
    )
    return path


# ---------------------------------------------------------------- env checks


def test_valid_production_configuration_passes() -> None:
    assert validator.validate_env(_valid_prod_env(), environment="prod") == []


def test_missing_database_url_fails() -> None:
    env = _valid_prod_env()
    del env["HFM_DATABASE_URL"]
    errors = validator.validate_env(env, environment="prod")
    assert errors and "HFM_DATABASE_URL" in errors[0] and "missing" in errors[0]


def test_template_database_url_fails() -> None:
    env = _valid_prod_env()
    env["HFM_DATABASE_URL"] = (
        "postgresql+asyncpg://CHANGEME:CHANGEME@CHANGEME:5432/CHANGEME"
    )
    errors = validator.validate_env(env, environment="prod")
    assert errors and "template placeholder" in errors[0]


def test_local_default_database_url_fails() -> None:
    env = _valid_prod_env()
    env["HFM_DATABASE_URL"] = "postgresql+asyncpg://hfb:change-me@127.0.0.1:5432/hfm"
    errors = validator.validate_env(env, environment="prod")
    assert errors and "local development default" in errors[0]


def test_development_database_name_fails() -> None:
    for dbname in ("hfm_dev", "hfm_test", "hfm"):
        env = _valid_prod_env()
        env["HFM_DATABASE_URL"] = (
            f"postgresql+asyncpg://real:user-secret@db.internal:5432/{dbname}"
        )
        errors = validator.validate_env(env, environment="prod")
        assert errors and "database name" in errors[0], dbname


def test_sqlite_scheme_in_production_fails() -> None:
    env = _valid_prod_env()
    env["HFM_DATABASE_URL"] = "sqlite+aiosqlite:////tmp/hfm.db"
    errors = validator.validate_env(env, environment="prod")
    assert errors and "scheme" in errors[0]


def test_token_secret_validation_fails() -> None:
    for value in ("", "CHANGEME_LONG_VALUE", "hfm-phase1-dev-secret", "short"):
        env = _valid_prod_env()
        env["HFM_TOKEN_SECRET"] = value
        errors = validator.validate_env(env, environment="prod")
        assert errors and "HFM_TOKEN_SECRET" in errors[0], repr(value)


def test_wrong_environment_fails() -> None:
    env = _valid_prod_env()
    env["HFM_ENV"] = "dev"
    errors = validator.validate_env(env, environment="prod")
    assert errors and "HFM_ENV mismatch" in errors[0]


def test_test_environment_sqlite_and_no_token_secret_allowed() -> None:
    env = {
        "HFM_ENV": "test",
        "HFM_DATABASE_URL": "sqlite+aiosqlite:////tmp/hfm-test.db",
    }
    assert validator.validate_env(env, environment="test", allow_sqlite=True) == []


def test_diagnostics_are_redacted(tmp_path: Path) -> None:
    env_file = _write_env(
        tmp_path / "redacted.env",
        {
            "HFM_ENV": "prod",
            "HFM_DATABASE_URL": "CHANGEME",
            "HFM_TOKEN_SECRET": "CHANGEME",
        },
    )
    result = subprocess.run(
        [PYTHON, str(VALIDATOR), "--env-file", str(env_file), "--env", "prod"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1
    assert "CHANGEME" not in result.stdout.split("ENV_VALIDATION=FAIL")[1]


# ------------------------------------------------- migration verification


def _sqlite_at_revision(db_file: Path, revision: str) -> None:
    """Migrate an isolated sqlite file to the requested revision (0013/0014/0017)."""
    env = {**os.environ, "HFM_DATABASE_URL": f"sqlite+aiosqlite:///{db_file}"}
    run = subprocess.run(
        [PYTHON, "-m", "alembic", "-c", "alembic.ini", "upgrade", revision],
        cwd=str(BACKEND_DIR),
        env=env,
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
    )
    assert run.returncode == 0, run.stderr[-2000:]


def test_migration_verification_accepts_0017(tmp_path: Path) -> None:
    db_file = tmp_path / "at0017.db"
    _sqlite_at_revision(db_file, "0017")
    errors = validator.verify_migration(
        BACKEND_DIR, f"sqlite+aiosqlite:///{db_file}", "0017"
    )
    assert errors == []


def test_migration_verification_blocks_stale_0014(tmp_path: Path) -> None:
    db_file = tmp_path / "at0014.db"
    _sqlite_at_revision(db_file, "0014")
    errors = validator.verify_migration(
        BACKEND_DIR, f"sqlite+aiosqlite:///{db_file}", "0017"
    )
    assert errors and "current revision" in errors[0]


def test_migration_verification_fails_on_unreachable_database() -> None:
    errors = validator.verify_migration(
        BACKEND_DIR,
        "postgresql+asyncpg://user:secret@127.0.0.1:59999/nope",
        "0017",
    )
    assert errors and ("database unreachable" in errors[0] or "heads" in errors[0])


# ------------------------------------------------------- deploy-gate launcher


def test_deploy_gate_test_env_0017_passes(tmp_path: Path) -> None:
    db_file = tmp_path / "gate-ok.db"
    _sqlite_at_revision(db_file, "0017")
    env_file = _write_env(
        tmp_path / "gate-test.env",
        {
            "HFM_ENV": "test",
            "HFM_DATABASE_URL": f"sqlite+aiosqlite:///{db_file}",
            "HFM_TOKEN_SECRET": "x" * 40,
        },
    )
    run = subprocess.run(
        ["bash", str(DEPLOY_GATE), "test", "--env-file", str(env_file)],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert run.returncode == 0, run.stdout + run.stderr
    assert "MIGRATION_GATE=PASS" in run.stdout


def test_deploy_gate_blocks_pending_migration_even_with_apply(tmp_path: Path) -> None:
    db_file = tmp_path / "gate-pending.db"
    _sqlite_at_revision(db_file, "0013")
    env_file = _write_env(
        tmp_path / "gate-pending.env",
        {
            "HFM_ENV": "test",
            "HFM_DATABASE_URL": f"sqlite+aiosqlite:///{db_file}",
            "HFM_TOKEN_SECRET": "x" * 40,
        },
    )
    run = subprocess.run(
        [
            "bash",
            str(DEPLOY_GATE),
            "test",
            "--env-file",
            str(env_file),
            "--apply-migrations",
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert run.returncode == 1
    assert "MIGRATION_GATE=FAIL" in run.stdout


def test_deploy_gate_rejects_template_prod_config(tmp_path: Path) -> None:
    env_file = _write_env(
        tmp_path / "prod-bad.env",
        {
            "HFM_ENV": "prod",
            "HFM_DATABASE_URL": "postgresql+asyncpg://CHANGEME:CHANGEME@CHANGEME:5432/CHANGEME",
            "HFM_TOKEN_SECRET": "CHANGEME_AT_LEAST_32_CHARACTERS_LONG",
        },
    )
    run = subprocess.run(
        ["bash", str(DEPLOY_GATE), "prod", "--env-file", str(env_file)],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert run.returncode == 1
    assert "MIGRATION_GATE=FAIL" in run.stdout
    # Redacted: the placeholder value itself never appears after the FAIL line.
    assert "CHANGEME:CHANGEME" not in run.stdout.split("MIGRATION_GATE=FAIL")[1]


# --------------------------------------------------- operator env-file guardrail


def _env_file(tmp_path: Path, values: dict[str, str]) -> Path:
    path = tmp_path / "operator.env"
    path.write_text(
        "\n".join(f"{k}={v}" for k, v in values.items()) + "\n", encoding="utf-8"
    )
    return path


def test_env_file_may_not_silently_override_an_explicit_database_url(tmp_path: Path) -> None:
    """The bug this guards: a run aimed at a scratch database landing on prod.

    The operator sets HFM_DATABASE_URL, passes the production --env-file, and
    the file used to replace it with nothing said. Now the two must agree.
    """
    env_file = _env_file(tmp_path, {"HFM_DATABASE_URL": "postgresql+asyncpg://db/hfm_prod"})
    base = {"HFM_DATABASE_URL": "postgresql+asyncpg://db/hfm_scratch"}

    try:
        validator.merge_env(base, env_file)
        raise AssertionError("a differing HFM_DATABASE_URL must not be silently overridden")
    except validator.EnvConflictError as exc:
        assert "HFM_DATABASE_URL" in str(exc)
        # Values may carry credentials, so the message must not echo them.
        assert "hfm_prod" not in str(exc) and "hfm_scratch" not in str(exc)


def test_env_file_conflict_message_names_only_keys(tmp_path: Path) -> None:
    env_file = _env_file(
        tmp_path,
        {"HFM_DATABASE_URL": "postgresql+asyncpg://u:pw@db/hfm_prod", "HFM_ENV": "prod"},
    )
    base = {"HFM_DATABASE_URL": "postgresql+asyncpg://u:pw@db/hfm_other", "HFM_ENV": "dev"}
    try:
        validator.merge_env(base, env_file)
        raise AssertionError("expected a conflict")
    except validator.EnvConflictError as exc:
        assert "pw" not in str(exc)
        assert "HFM_DATABASE_URL" in str(exc) and "HFM_ENV" in str(exc)


def test_env_file_fills_keys_absent_from_the_environment(tmp_path: Path) -> None:
    env_file = _env_file(tmp_path, {"HFM_DATABASE_URL": "postgresql+asyncpg://db/hfm_prod"})
    merged = validator.merge_env({}, env_file)
    assert merged["HFM_DATABASE_URL"] == "postgresql+asyncpg://db/hfm_prod"


def test_env_file_agreeing_with_the_environment_is_allowed(tmp_path: Path) -> None:
    """The documented invocation sets both to the same DSN; that must keep working."""
    dsn = "postgresql+asyncpg://db/hfm_prod"
    env_file = _env_file(tmp_path, {"HFM_DATABASE_URL": dsn})
    assert validator.merge_env({"HFM_DATABASE_URL": dsn}, env_file)["HFM_DATABASE_URL"] == dsn


def test_db_target_never_echoes_credentials() -> None:
    described = validator.describe_db_target(
        {"HFM_DATABASE_URL": "postgresql+asyncpg://hfm_user:S3cr3t@db.internal:5432/hfm_prod"}
    )
    assert described == "postgresql+asyncpg://db.internal:5432/hfm_prod"
    assert "S3cr3t" not in described and "hfm_user" not in described


def test_db_target_reports_a_missing_url_rather_than_guessing() -> None:
    assert "not set" in validator.describe_db_target({})
