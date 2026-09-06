"""ND-1 B04 — deploy/persistence/recovery package checks (safe, unapplied).

Validates that the shipped operations artifacts are complete, carry the
required operator-input markers, are NOT applied anywhere, and that
scripts/production-smoke.sh validates its inputs without contacting a live
target. Target TLS/reboot/restore drills remain ND2_EXECUTION_REQUIRED and
are not claimed here.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SMOKE = REPO_ROOT / "scripts" / "production-smoke.sh"
NGINX = REPO_ROOT / "infra" / "nginx" / "hfm.conf.example"
SYSTEMD = REPO_ROOT / "infra" / "systemd" / "hfm-backend.service.example"
DOC = REPO_ROOT / "docs" / "operations" / "ND1-RELEASE-QUALIFICATION.md"


def test_nginx_example_contract() -> None:
    text = NGINX.read_text(encoding="utf-8")
    # Topology: reverse proxy to the private uvicorn; static served by nginx;
    # media volume; operator TLS template marked ND2.
    assert "proxy_pass http://127.0.0.1:8000" in text
    assert "try_files $uri $uri/ /index.html" in text
    assert "/media/" in text and "/var/lib/hfm/media" in text
    assert "ND2_EXECUTION_REQUIRED" in text


def test_systemd_example_contract() -> None:
    text = SYSTEMD.read_text(encoding="utf-8")
    assert "EnvironmentFile=/etc/hfm/prod.env" in text
    assert "uvicorn hfm.main:app --host 127.0.0.1 --port 8000" in text
    assert "Restart=on-failure" in text
    assert "/var/lib/hfm/media" in text
    assert "ND2_EXECUTION_REQUIRED" in text
    assert "User=hfm" in text


def test_qualification_doc_distinguishes_rollback_terms() -> None:
    text = DOC.read_text(encoding="utf-8")
    assert "APPLICATION_ROLLBACK" in text
    assert "DATABASE_ROLLBACK" in text
    assert "DATABASE_RESTORE" in text
    assert "0014 → 0013 downgrade is not supported as a release path" in text
    assert "ND2_EXECUTION_REQUIRED" in text


def test_smoke_check_args_accepts_valid_inputs() -> None:
    run = subprocess.run(
        ["bash", str(SMOKE), "--check-args"],
        cwd=str(REPO_ROOT),
        env={
            "PATH": "/usr/bin:/bin:/usr/sbin:/sbin",
            "HFM_ENV": "prod",
            "HFM_DATABASE_URL": "postgresql+asyncpg://real:secret@db.internal:5432/hfm_prod_main",
            "HFM_TOKEN_SECRET": "x" * 40,
        },
        capture_output=True,
        text=True,
        check=False,
    )
    assert run.returncode == 0, run.stdout + run.stderr
    assert "PRODUCTION_SMOKE=PASS" in run.stdout


def test_smoke_check_args_rejects_placeholder_inputs() -> None:
    run = subprocess.run(
        ["bash", str(SMOKE), "--check-args"],
        cwd=str(REPO_ROOT),
        env={
            "PATH": "/usr/bin:/bin:/usr/sbin:/sbin",
            "HFM_ENV": "prod",
            "HFM_DATABASE_URL": "postgresql+asyncpg://CHANGEME:CHANGEME@CHANGEME:5432/CHANGEME",
            "HFM_TOKEN_SECRET": "CHANGEME_AT_LEAST_32_CHARACTERS_LONG",
        },
        capture_output=True,
        text=True,
        check=False,
    )
    assert run.returncode == 1
    assert "SMOKE_ENV_MIGRATION=FAIL" in run.stdout or "PRODUCTION_SMOKE=FAIL" in run.stdout
