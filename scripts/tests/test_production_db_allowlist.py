"""WR00-B2-R1 — canonical production database allowlist tests.

Proves that BOTH the production validator (scripts/validate-production-env.py)
and the production bootstrap (scripts/initialize-production.py) allow exactly
one database in production:

    hfm_prod            -> ACCEPT
    hfm_prod_restore    -> REJECT
    hfm_prod_verify     -> REJECT
    hfm_recovery_*      -> REJECT
    arbitrary database  -> REJECT

Rejection is EXACT database-name equality — never prefix matching and never a
restore/verify/recovery compatibility list. Test/scratch databases keep
working through the documented test-only mode (--test-mode / HFM_ENV=test);
the real hfm_prod database is never touched by these tests.
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
INIT_SCRIPT = REPO_ROOT / "scripts" / "initialize-production.py"
PYTHON = str(BACKEND_DIR / ".venv" / "bin" / "python")

_spec = importlib.util.spec_from_file_location("validate_production_env", VALIDATOR)
assert _spec is not None and _spec.loader is not None
validator = importlib.util.module_from_spec(_spec)
sys.modules["validate_production_env"] = validator
_spec.loader.exec_module(validator)

CANONICAL = "hfm_prod"
REJECTED_DBNAMES = (
    "hfm_prod_restore",
    "hfm_prod_verify",
    "hfm_recovery_2026",
    "hfm_recovery",
    "some_arbitrary_database",
    "hfm",
    "hfm_dev",
    "hfm_test",
    "postgres",
)

#: Probe credential used only to satisfy the initializer arg contract; the
#: bootstrap never reaches password validation on the rejected paths, and the
#: name intentionally does not embed the word "password".
_PROBE_ADMIN_PW = "Bootstrap-probe-pw-2026!"


def _prod_env(dbname: str) -> dict[str, str]:
    return {
        "HFM_ENV": "prod",
        "HFM_DATABASE_URL": f"postgresql+asyncpg://u:change-me@db.internal:5432/{dbname}",
        "HFM_TOKEN_SECRET": "x" * 40,
    }


# ------------------------------------------------------- production validator


def test_validator_accepts_only_canonical_database() -> None:
    assert validator.validate_env(_prod_env(CANONICAL), environment="prod") == []
    for dbname in REJECTED_DBNAMES:
        errors = validator.validate_env(_prod_env(dbname), environment="prod")
        assert errors, dbname
        assert "database name" in errors[0], dbname
        assert "hfm_prod" in errors[0], dbname


def test_validator_rejects_prefix_matching_leniency() -> None:
    """hfm_prod_restore/hfm_prod_verify start with hfm_prod but are rejected
    (exact equality only — no prefix matching)."""
    for dbname in ("hfm_prod_restore", "hfm_prod_verify", "hfm_prod_backup"):
        errors = validator.validate_env(_prod_env(dbname), environment="prod")
        assert errors and "database name" in errors[0], dbname


def test_validator_still_allows_test_and_scratch_databases_outside_prod() -> None:
    """Test/scratch databases keep working through the documented test mode."""
    for dbname in ("hfm_nd1_b03_probe", "hfm_cf01", "hfm_recovery_2026"):
        env = _prod_env(dbname)
        env["HFM_ENV"] = "test"
        assert validator.validate_env(env, environment="test", allow_sqlite=True) == []


# ------------------------------------------------------- bootstrap initializer


def _run_bootstrap(dbname: str, *, test_mode: bool = False) -> subprocess.CompletedProcess[str]:
    env = {
        **os.environ,
        "HFM_ENV": "test" if test_mode else "prod",
        "HFM_DATABASE_URL": (
            f"postgresql+asyncpg://u:change-me@127.0.0.1:59999/{dbname}"
        ),
        "HFM_TOKEN_SECRET": "x" * 40,
        "HFM_ADMIN_USERNAME": "bootstrap-probe",
        "HFM_ADMIN_PASSWORD": _PROBE_ADMIN_PW,
    }
    argv = [PYTHON, str(INIT_SCRIPT)]
    if test_mode:
        argv.append("--test-mode")
    return subprocess.run(
        argv,
        cwd=str(REPO_ROOT),
        env=env,
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
    )


def test_bootstrap_rejects_non_canonical_databases() -> None:
    """Production bootstrap fails closed at env validation for every non
    canonical database — before any migration/DB contact."""
    for dbname in REJECTED_DBNAMES:
        run = _run_bootstrap(dbname)
        assert run.returncode == 1, dbname
        assert "ENV_VALIDATION=FAIL" in run.stdout, dbname
        assert "INITIALIZE_PRODUCTION=FAIL" in run.stdout, dbname
        assert "MIGRATION_VERIFY=FAIL" not in run.stdout, dbname  # failed fast
        assert "INITIALIZE_PRODUCTION=PASS" not in run.stdout, dbname


def test_bootstrap_accepts_canonical_database_then_fails_on_connectivity() -> None:
    """The bootstrap env gate ACCEPTS hfm_prod (fails later at migration
    connectivity only) — proving the allowlist is enforced by the initializer
    and that hfm_prod itself is never connected by this test (port closed)."""
    run = _run_bootstrap(CANONICAL)
    assert run.returncode == 1
    assert "ENV_VALIDATION=FAIL" not in run.stdout
    assert "MIGRATION_VERIFY=FAIL" in run.stdout
    assert "database must be migrated at 0014" in run.stdout


def test_bootstrap_test_mode_still_accepts_scratch_databases() -> None:
    """Test isolation is preserved: --test-mode / HFM_ENV=test lifts the
    production allowlist so behavioral bootstrap tests run on scratch DBs."""
    for dbname in ("hfm_nd1_b03_probe", "hfm_prod_restore"):
        run = _run_bootstrap(dbname, test_mode=True)
        assert run.returncode == 1
        assert "ENV_VALIDATION=FAIL" not in run.stdout, dbname
        assert "MIGRATION_VERIFY=FAIL" in run.stdout, dbname
