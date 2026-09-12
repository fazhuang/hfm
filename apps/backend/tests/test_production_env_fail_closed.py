# mypy: disable-error-code="import-untyped,import-not-found"
# pyright: reportMissingImports=false
"""ND-1 B01 — production runtime fail-closed probes.

Proves the application RUNTIME itself refuses development fallbacks when
HFM_ENV=prod (no silent localhost database, no development token secret):

  CASE 1  prod + missing HFM_DATABASE_URL  → import/startup FAILS clearly
  CASE 2  prod + missing HFM_TOKEN_SECRET  → import/startup FAILS clearly
  CASE 3  prod + valid required env        → application imports/starts
  CASE 4  dev/test mode                    → existing developer defaults remain

Probes run in isolated subprocesses so they never affect the host test env.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]


def _probe(env: dict[str, str], code: str) -> subprocess.CompletedProcess[str]:
    run_env = {**os.environ, "PYTHONPATH": str(BACKEND_DIR / "src"), **env}
    return subprocess.run(
        [sys.executable, "-c", code],
        cwd=str(BACKEND_DIR),
        env=run_env,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )


_VALID_DB = "postgresql+asyncpg://u:p@db.internal:5432/hfm_prod_main"
_VALID_TOKEN = "s" * 40
_IMPORT = "import hfm.core.config, hfm.phase1.auth"


def test_case1_prod_missing_database_url_fails() -> None:
    run = _probe({"HFM_ENV": "prod", "HFM_TOKEN_SECRET": _VALID_TOKEN}, _IMPORT)
    assert run.returncode != 0
    assert "HFM_DATABASE_URL" in run.stderr
    assert "fail-closed" in run.stderr


def test_case2_prod_missing_token_secret_fails() -> None:
    run = _probe({"HFM_ENV": "prod", "HFM_DATABASE_URL": _VALID_DB}, _IMPORT)
    assert run.returncode != 0
    assert "HFM_TOKEN_SECRET" in run.stderr
    assert "fail-closed" in run.stderr


def test_case2_prod_dev_default_token_secret_fails() -> None:
    run = _probe(
        {
            "HFM_ENV": "prod",
            "HFM_DATABASE_URL": _VALID_DB,
            "HFM_TOKEN_SECRET": "hfm-phase1-dev-secret",
        },
        _IMPORT,
    )
    assert run.returncode != 0
    assert "HFM_TOKEN_SECRET" in run.stderr


def test_case3_prod_valid_env_imports() -> None:
    run = _probe(
        {"HFM_ENV": "prod", "HFM_DATABASE_URL": _VALID_DB, "HFM_TOKEN_SECRET": _VALID_TOKEN},
        _IMPORT,
    )
    assert run.returncode == 0, run.stderr
    # Full application import (all routers/modules) also succeeds.
    run_app = _probe(
        {"HFM_ENV": "prod", "HFM_DATABASE_URL": _VALID_DB, "HFM_TOKEN_SECRET": _VALID_TOKEN},
        "import hfm.main",
    )
    assert run_app.returncode == 0, run_app.stderr


def test_case4_dev_and_unset_env_defaults_remain() -> None:
    for env in ({"HFM_ENV": "dev"}, {"HFM_ENV": "test"}, {}):
        run = _probe(env, "import hfm.core.config")
        assert run.returncode == 0, run.stderr
