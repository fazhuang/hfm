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
    # Topology: reverse proxy to the private uvicorn; static served by nginx.
    assert "proxy_pass http://127.0.0.1:8000" in text
    assert "try_files $uri $uri/ /index.html" in text
    assert "ND2_EXECUTION_REQUIRED" in text
    # ND-1 RV-P0-01: NO public alias/root of the persistent media volume.
    assert "location /media/" not in text
    assert "alias /var/lib/hfm/media" not in text
    assert "/api/v1/public/media/{asset_id}/bytes" in text


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
    # RV-P0-01: media served only via the published endpoint; direct alias forbidden.
    assert "media/{asset_id}/bytes" in text
    assert "public alias" in text.lower() or "never alias" in text.lower()


def test_nginx_example_passes_smoke_media_alias_check() -> None:
    run = subprocess.run(
        ["bash", str(SMOKE), "--media-alias-check", str(NGINX), "--check-args"],
        cwd=str(REPO_ROOT),
        env={"PATH": "/usr/bin:/bin:/usr/sbin:/sbin", "HFM_ENV": "prod"},
        capture_output=True,
        text=True,
        check=False,
    )
    assert run.returncode == 0, run.stdout + run.stderr
    assert "SMOKE_MEDIA_ALIAS=PASS" in run.stdout


def test_smoke_media_alias_check_rejects_direct_alias(tmp_path: Path) -> None:
    bad = tmp_path / "bad-nginx.conf"
    bad.write_text(
        "server {\n"
        "    listen 443 ssl;\n"
        "    location /media/ {\n"
        "        alias /var/lib/hfm/media/;\n"
        "    }\n"
        "    location /api/ { proxy_pass http://127.0.0.1:8000; }\n"
        "}\n",
        encoding="utf-8",
    )
    run = subprocess.run(
        ["bash", str(SMOKE), "--media-alias-check", str(bad)],
        cwd=str(REPO_ROOT),
        env={"PATH": "/usr/bin:/bin:/usr/sbin:/sbin"},
        capture_output=True,
        text=True,
        check=False,
    )
    assert run.returncode == 1
    assert "SMOKE_MEDIA_ALIAS=FAIL" in run.stdout


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
    assert (
        "SMOKE_ENV_MIGRATION=FAIL" in run.stdout
        or "PRODUCTION_SMOKE=FAIL" in run.stdout
    )


# ND-2 RUNBOOK-CORRECTION-01: the smoke version probe must equal the real
# product route. The backend mounts system/health at the root (/version,
# /health); /api/v1/system/version does not exist. These tests keep the smoke
# contract and the mounted route graph from diverging again.


def test_smoke_version_probe_matches_real_route() -> None:
    text = SMOKE.read_text(encoding="utf-8")
    assert "for endpoint in health version; do" in text
    assert "api/v1/system/version" not in text


def test_mounted_route_graph_contract() -> None:
    """Real app: GET /version 200; stale /api/v1/system/version 404."""
    import importlib.util
    import sys

    backend_src = REPO_ROOT / "apps" / "backend" / "src"
    if str(backend_src) not in sys.path:
        sys.path.insert(0, str(backend_src))
    spec = importlib.util.spec_from_file_location(
        "nd2_hfm_main", backend_src / "hfm" / "main.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["nd2_hfm_main"] = module
    spec.loader.exec_module(module)

    import asyncio

    import httpx

    async def _probe() -> tuple[int, str, int]:
        transport = httpx.ASGITransport(app=module.app)
        async with httpx.AsyncClient(
            transport=transport, base_url="http://test"
        ) as client:
            version = await client.get("/version")
            stale = await client.get("/api/v1/system/version")
        return (
            version.status_code,
            version.headers.get("content-type", ""),
            stale.status_code,
        )

    version_status, version_ct, stale_status = asyncio.run(_probe())
    assert version_status == 200
    assert version_ct.startswith("application/json")
    assert stale_status == 404
