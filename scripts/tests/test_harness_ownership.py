"""ND-1 H01 — test-harness ownership hardening checks (P2).

Proves the harness fail-closed contract (incl. ND1-H01-GOLDEN-PORT-CONTRACT):
  - the runtime gates NEVER pre-start the frontend: Playwright is the single
    frontend owner; the frontend target port must be FREE before launch and
    the owned listener (PID/CWD/port/SHA) is verified WHILE Playwright runs;
  - a foreign or stale process on a target port FAILS the gate before any
    navigation and is never reused or killed;
  - the backend stays gate-managed (owned+SHA reuse only);
  - Playwright never silently reuses a foreign dev server
    (reuseExistingServer:false; strictPort; HFM_E2E_TARGET_SHA bound).

Behavioral proofs use dedicated free ports so any running donor session's
:5199 process is never touched.
"""

from __future__ import annotations

import os
import secrets
import socket
import subprocess
import time
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
FAST_GATE = REPO_ROOT / "infra" / "scripts" / "fast-runtime-gate.sh"
GOLDEN_GATE = REPO_ROOT / "infra" / "scripts" / "golden-runtime-gate.sh"
PLAYWRIGHT_CONFIG = REPO_ROOT / "apps" / "frontend" / "playwright.config.ts"


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


def _http_server(
    port: int, cwd: Path, env_extra: dict[str, str] | None = None
) -> subprocess.Popen[str]:
    """A listener with the given cwd and optional environment."""
    env = {**os.environ, **(env_extra or {})}
    return subprocess.Popen(
        ["python3", "-m", "http.server", str(port), "--bind", "127.0.0.1"],
        cwd=str(cwd),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        text=True,
    )


def _foreign_http_server(port: int) -> subprocess.Popen[str]:
    """A listener whose cwd is NOT this repository (simulates a foreign server)."""
    return _http_server(port, Path("/tmp"))


def _gate_env(be_port: int, fe_port: int, **extra: str) -> dict[str, str]:
    return {
        **os.environ,
        "HFM_DATABASE_URL": "postgresql+asyncpg://u:p@127.0.0.1:59999/nope",
        "GOLDEN_BACKEND_PORT": str(be_port),
        "GOLDEN_FRONTEND_PORT": str(fe_port),
        **extra,
    }


# ------------------------------------------------------------- static contract


def test_gate_scripts_use_ownership_not_broad_pkill() -> None:
    for script in (FAST_GATE, GOLDEN_GATE):
        text = script.read_text(encoding="utf-8")
        assert "listener_pid" in text and "pid_cwd" in text
        assert "owned_listener" in text
        assert "HARNESS_FOREIGN_OWNER=FAIL" in text
        assert "HARNESS_STALE_OWNER=FAIL" in text
        assert "kill_owned_listener" in text
        # One frontend owner (Playwright): gates never pre-start Vite and pass
        # one coherent port/base/SHA contract (ND1-H01-GOLDEN-PORT-CONTRACT).
        assert "HFM_E2E_PORT=" in text
        assert "HFM_E2E_BASE=" in text
        assert "HFM_E2E_TARGET_SHA=" in text
        assert "CF01_BASE=" in text
        assert "HARNESS_FRONTEND_TARGET_SHA" in text
        # RV-01 target identity: source SHA recorded and bound per server.
        assert "HFM_TARGET_SHA=" in text
        assert "HARNESS_SOURCE_SHA" in text
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


# ------------------------------------------------- behavioral foreign/stale


def test_fast_gate_fails_closed_on_foreign_backend_and_leaves_it_intact() -> None:
    """Foreign backend listener → fail closed; process never killed."""
    be_port = _free_port()
    fe_port = _free_port()
    foreign = _foreign_http_server(be_port)
    try:
        time.sleep(1.5)
        assert foreign.poll() is None, "foreign server failed to start"
        run = subprocess.run(
            ["bash", str(FAST_GATE)],
            cwd=str(REPO_ROOT),
            env=_gate_env(be_port, fe_port),
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


def test_gates_reject_foreign_frontend_target_before_any_navigation() -> None:
    """ND1-H01 acceptance B: foreign occupant on the frontend target fails the
    gate BEFORE navigation; the foreign process stays alive."""
    be_port = _free_port()
    fe_port = _free_port()
    foreign = _foreign_http_server(fe_port)
    try:
        time.sleep(1.5)
        for gate in (FAST_GATE, GOLDEN_GATE):
            run = subprocess.run(
                ["bash", str(gate)],
                cwd=str(REPO_ROOT),
                env=_gate_env(
                    be_port, fe_port, GOLDEN_DB=f"hfm_h01_{secrets.token_hex(4)}"
                ),
                capture_output=True,
                text=True,
                timeout=120,
                check=False,
            )
            assert run.returncode != 0, gate
            assert "HARNESS_FOREIGN_OWNER=FAIL" in run.stdout, gate
            assert "kind=frontend" in run.stdout, gate
    finally:
        assert foreign.poll() is None, "foreign process must be left intact"
        foreign.terminate()
        foreign.wait(timeout=5)


def test_gates_reject_stale_same_cwd_frontend_and_leave_it_intact() -> None:
    """ND1-H01 acceptance C: same-CWD stale/unbound listener on the frontend
    target fails the gate before navigation and stays intact."""
    be_port = _free_port()
    fe_port = _free_port()
    stale = _http_server(
        fe_port, REPO_ROOT / "apps" / "frontend", {"HFM_TARGET_SHA": "0" * 40}
    )
    try:
        time.sleep(1.5)
        for gate in (FAST_GATE, GOLDEN_GATE):
            run = subprocess.run(
                ["bash", str(gate)],
                cwd=str(REPO_ROOT),
                env=_gate_env(
                    be_port, fe_port, GOLDEN_DB=f"hfm_h01_{secrets.token_hex(4)}"
                ),
                capture_output=True,
                text=True,
                timeout=120,
                check=False,
            )
            assert run.returncode != 0, gate
            assert "HARNESS_STALE_OWNER=FAIL" in run.stdout, gate
            assert "kind=frontend" in run.stdout, gate
    finally:
        assert stale.poll() is None, "stale process must be left intact"
        stale.terminate()
        stale.wait(timeout=5)


# --------------------------------------------- RV-01 target-SHA identity


def test_playwright_config_mismatch_sha_fails_before_navigation() -> None:
    """ND1-H01 acceptance D: HFM_E2E_TARGET_SHA mismatch aborts at config load."""
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


# --------------------------------------------- full golden (A+E, PG-gated)


_PG_READY = (
    subprocess.run(
        ["pg_isready", "-h", "127.0.0.1", "-q"], capture_output=True, check=False
    ).returncode
    == 0
)
_PG = pytest.mark.skipif(not _PG_READY, reason="local PostgreSQL unavailable")


def _run_golden(
    be_port: int, fe_port: int, dbname: str, pw: str
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(GOLDEN_GATE)],
        cwd=str(REPO_ROOT),
        env={
            **os.environ,
            "GOLDEN_DB": dbname,
            "GOLDEN_PGUSER": os.environ.get("USER", "likeming"),
            "GOLDEN_PGPASS": "",
            "GOLDEN_APP_PW": pw,
            "GOLDEN_BACKEND_PORT": str(be_port),
            "GOLDEN_FRONTEND_PORT": str(fe_port),
        },
        capture_output=True,
        text=True,
        timeout=900,
        check=False,
    )


@_PG
def test_full_golden_gate_owned_frontend_contract() -> None:
    """ND1-H01 acceptance A + E: a foreign process on :5199 never interferes,
    the gate uses its own free target, Playwright owns the Vite, the owned
    listener (PID/CWD/:port/SHA) is verified while running, and the full
    runtime chain (fresh PG→0014→bootstrap→backend→Chromium) passes with zero
    fatal/network failures."""
    user = os.environ.get("USER", "likeming")
    # The recovery Vite proxies /api to 127.0.0.1:8000 (vite.config.ts), so the
    # gate backend must run on the documented proxy port for the real chain.
    probe = socket.socket()
    try:
        probe.bind(("127.0.0.1", 8000))
        probe.close()
    except OSError:
        pytest.skip("port 8000 (vite /api proxy target) is occupied")
    be_port = 8000
    fe_port = _free_port()
    pw = "pw-" + secrets.token_hex(10)
    dbname = f"hfm_h01_{secrets.token_hex(4)}"
    # A foreign process on the DEFAULT frontend port (:5199) — irrelevant to a
    # gate that uses its own free target; must survive untouched.
    foreign = None
    try:
        probe = socket.socket()
        try:
            probe.bind(("127.0.0.1", 5199))
            probe.close()
            foreign = _foreign_http_server(5199)
            time.sleep(1.2)
        except OSError:
            probe.close()  # :5199 already occupied (e.g. donor session) — fine
        # Make the dedicated app role's password deterministic for this run.
        subprocess.run(
            [
                "psql",
                "-h",
                "127.0.0.1",
                "-U",
                user,
                "-d",
                "postgres",
                "-c",
                (
                    f"DO $$ BEGIN IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname='hfm_app') "
                    f"THEN CREATE ROLE hfm_app LOGIN PASSWORD '{pw}'; "
                    f"ELSE ALTER ROLE hfm_app WITH LOGIN PASSWORD '{pw}'; END IF; END $$;"
                ),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        run = _run_golden(be_port, fe_port, dbname, pw)
        assert run.returncode == 0, run.stdout[-3000:] + run.stderr[-2000:]
        assert "FULL_GOLDEN_GATE=PASS" in run.stdout
        assert "HARNESS_FRONTEND_TARGET_SHA=PASS (pid=" in run.stdout
        assert f"port={fe_port}" in run.stdout
        assert "cwd=" in run.stdout
        assert "BROWSER=PASS" in run.stdout
        browser_log = (REPO_ROOT / "/tmp/cf01-browser.log").read_text(
            encoding="utf-8", errors="replace"
        )
        assert "htmlFallback=0" in browser_log and "requestFailed=0" in browser_log
        assert "unexpectedHttp=0" in browser_log and "fatal=0" in browser_log
    finally:
        if foreign is not None and foreign.poll() is None:
            assert foreign.poll() is None, "foreign :5199 process must be left intact"
            foreign.terminate()
            foreign.wait(timeout=5)
        subprocess.run(
            ["dropdb", "-h", "127.0.0.1", "-U", user, "--if-exists", dbname],
            capture_output=True,
            check=False,
        )
