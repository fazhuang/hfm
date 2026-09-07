"""ND-1 H01 — test-harness ownership hardening checks (P2).

Proves the harness fail-closed contract:
  - the runtime gate scripts refuse a FOREIGN process on a target port and
    clean up ONLY processes they recorded as owned (never a broad pkill);
  - Playwright never silently reuses a foreign dev server (reuseExistingServer
    false; strictPort bind failure = run fails before navigation);
  - alternate explicit ports apply consistently (HFM_E2E_PORT / CF01_BASE).

Behavioral foreign-owner proof uses dedicated free ports so the running donor
session's :5199 process is never touched.
"""

from __future__ import annotations

import os
import socket
import subprocess
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
FAST_GATE = REPO_ROOT / "infra" / "scripts" / "fast-runtime-gate.sh"
GOLDEN_GATE = REPO_ROOT / "infra" / "scripts" / "golden-runtime-gate.sh"
PLAYWRIGHT_CONFIG = REPO_ROOT / "apps" / "frontend" / "playwright.config.ts"


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


def _foreign_http_server(port: int) -> subprocess.Popen[str]:
    """A listener whose cwd is NOT this repository (simulates a foreign server)."""
    return subprocess.Popen(
        ["python3", "-m", "http.server", str(port), "--bind", "127.0.0.1"],
        cwd="/tmp",
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        text=True,
    )


# ------------------------------------------------------------- static contract


def test_gate_scripts_use_ownership_not_broad_pkill() -> None:
    for script in (FAST_GATE, GOLDEN_GATE):
        text = script.read_text(encoding="utf-8")
        assert "listener_pid" in text and "pid_cwd" in text
        assert "owned_listener" in text
        assert "HARNESS_FOREIGN_OWNER=FAIL" in text
        assert "kill_owned_listener" in text
        # RV-01 target identity: source SHA recorded and bound per server.
        assert "HFM_TARGET_SHA=" in text
        assert "HARNESS_SOURCE_SHA" in text
        assert "TARGET_SHA" in text
        # No broad pkill of server processes (would touch foreign processes).
        assert 'pkill -f "uvicorn' not in text
        assert 'pkill -f "vite' not in text
        syntax = subprocess.run(
            ["bash", "-n", str(script)], capture_output=True, text=True, check=False
        )
        assert syntax.returncode == 0, syntax.stderr


def test_playwright_config_fails_closed_on_foreign_server() -> None:
    text = PLAYWRIGHT_CONFIG.read_text(encoding="utf-8")
    assert "reuseExistingServer: false" in text
    assert "--strictPort" in text
    assert "HFM_E2E_PORT" in text and "HFM_E2E_BASE" in text
    # RV-01: the launched source SHA is bound and enforced at config load.
    assert "rev-parse" in text
    assert "HFM_E2E_TARGET_SHA" in text
    assert "HARNESS_TARGET_SHA_MISMATCH" in text
    assert "HFM_TARGET_SHA" in text


# ------------------------------------------------- behavioral foreign-owner


def test_fast_gate_fails_closed_on_foreign_backend_and_leaves_it_intact() -> None:
    be_port = _free_port()
    fe_port = _free_port()
    foreign = _foreign_http_server(be_port)
    try:
        time.sleep(1.5)
        assert foreign.poll() is None, "foreign server failed to start"
        run = subprocess.run(
            ["bash", str(FAST_GATE)],
            cwd=str(REPO_ROOT),
            env={
                **os.environ,
                "HFM_DATABASE_URL": "postgresql+asyncpg://u:p@127.0.0.1:59999/nope",
                "GOLDEN_BACKEND_PORT": str(be_port),
                "GOLDEN_FRONTEND_PORT": str(fe_port),
            },
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        assert run.returncode != 0
        assert "HARNESS_FOREIGN_OWNER=FAIL" in run.stdout
        assert "kind=backend" in run.stdout
    finally:
        assert foreign.poll() is None, (
            "foreign process was killed — must be left intact"
        )
        foreign.terminate()
        foreign.wait(timeout=5)


# --------------------------------------------- RV-01 target-SHA identity


def test_playwright_config_mismatch_sha_fails_before_navigation() -> None:
    """RV-01: HFM_E2E_TARGET_SHA mismatch aborts at config load (no server)."""
    head = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    wrong = "0" * 40 if head != "0" * 40 else "1" * 40
    run = subprocess.run(
        ["pnpm", "exec", "playwright", "test", "--list"],
        cwd=str(REPO_ROOT / "apps" / "frontend"),
        env={
            **os.environ,
            "HFM_E2E_TARGET_SHA": wrong,
            "HFM_E2E_PORT": str(_free_port()),
        },
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    assert run.returncode != 0
    assert "HARNESS_TARGET_SHA_MISMATCH" in (run.stdout + run.stderr)


def test_fast_gate_rejects_stale_owned_frontend_and_leaves_it_intact() -> None:
    """RV-01: same-CWD process with a stale/unbound SHA is never reused."""
    be_port = _free_port()
    fe_port = _free_port()
    stale = subprocess.Popen(
        ["python3", "-m", "http.server", str(fe_port), "--bind", "127.0.0.1"],
        cwd=str(REPO_ROOT / "apps" / "frontend"),
        env={**os.environ, "HFM_TARGET_SHA": "0" * 40},
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        text=True,
    )
    try:
        time.sleep(1.5)
        assert stale.poll() is None
        run = subprocess.run(
            ["bash", str(FAST_GATE)],
            cwd=str(REPO_ROOT),
            env={
                **os.environ,
                "HFM_DATABASE_URL": "postgresql+asyncpg://u:p@127.0.0.1:59999/nope",
                "GOLDEN_BACKEND_PORT": str(be_port),
                "GOLDEN_FRONTEND_PORT": str(fe_port),
            },
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        assert run.returncode != 0
        assert "HARNESS_TARGET_SHA=FAIL" in run.stdout
    finally:
        assert stale.poll() is None, "stale process must be left intact (never killed)"
        stale.terminate()
        stale.wait(timeout=5)


def test_vite_strict_port_bind_failure_when_port_occupied() -> None:
    """The exact failure mode the Playwright webServer surfaces pre-navigation."""
    occupied = _free_port()
    foreign = _foreign_http_server(occupied)
    try:
        time.sleep(1.5)
        # --host 127.0.0.1 forces the IPv4 family so the bind conflict with the
        # 127.0.0.1 contender is deterministic across dual-stack hosts.
        run = subprocess.run(
            [
                "pnpm",
                "dev",
                "--host",
                "127.0.0.1",
                "--port",
                str(occupied),
                "--strictPort",
            ],
            cwd=str(REPO_ROOT / "apps" / "frontend"),
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        assert run.returncode != 0
        combined = (run.stdout + run.stderr).lower()
        assert "port" in combined and "strict" in combined
    finally:
        foreign.terminate()
        foreign.wait(timeout=5)
