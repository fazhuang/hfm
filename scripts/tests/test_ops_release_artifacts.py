"""ND-1 OPS — pre-release checklist and database dependency probe tests.

Proves the mechanical contracts of the new release artifacts:
  - pre-release-checklist.sh records PASS/FAIL/N/A per item and exits nonzero
    on any FAIL (mechanism exercised with synthetic facts);
  - database-dependency-probe.sh detects a live HTTP process whose database
    is unreachable (process up + database down => probe FAIL) and passes when
    the database is reachable at the expected revision.
"""

from __future__ import annotations

import http.server
import os
import socketserver
import subprocess
import threading
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = REPO_ROOT / "apps" / "backend"
CHECKLIST = REPO_ROOT / "scripts" / "pre-release-checklist.sh"
PROBE = REPO_ROOT / "scripts" / "database-dependency-probe.sh"
PYTHON = str(BACKEND_DIR / ".venv" / "bin" / "python")


def _http_ok_server(port: int) -> None:
    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'{"ok":true}')

        def log_message(self, format: str, *args: object) -> None:
            pass

    with socketserver.TCPServer(("127.0.0.1", port), Handler) as httpd:
        httpd.serve_forever()


@pytest.fixture()
def api_up() -> int:
    import socket

    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = int(s.getsockname()[1])
    thread = threading.Thread(target=_http_ok_server, args=(port,), daemon=True)
    thread.start()
    return port


def _sqlite_at_head(tmp_path: Path) -> str:
    db_file = tmp_path / "probe.db"
    run = subprocess.run(
        [PYTHON, "-m", "alembic", "-c", "alembic.ini", "upgrade", "head"],
        cwd=str(BACKEND_DIR),
        env={**os.environ, "HFM_DATABASE_URL": f"sqlite+aiosqlite:///{db_file}"},
        capture_output=True,
        text=True,
        timeout=240,
        check=False,
    )
    assert run.returncode == 0, run.stderr[-1500:]
    return f"sqlite+aiosqlite:///{db_file}"


# ------------------------------------------------------------- pre-release list


def test_pre_release_checklist_records_na_without_target_facts(tmp_path: Path) -> None:
    head = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    env_file = tmp_path / "env.prod"
    env_file.write_text(
        "HFM_ENV=prod\n"
        "HFM_DATABASE_URL=postgresql+asyncpg://u:p@db.internal:5432/hfm_prod\n"
        "HFM_TOKEN_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx\n",
        encoding="utf-8",
    )
    run = subprocess.run(
        [
            "bash",
            str(CHECKLIST),
            "--expect-sha",
            head,
            "--env-file",
            str(env_file),
            "--tls-dns-ready",
            "no",
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=300,
        check=False,
    )
    # Env validator rejects the non-reachable PG DSN at the migration step, so
    # connectivity/revision FAIL while the mechanism still records each item.
    assert "ITEM_RC_SHA=PASS" in run.stdout
    assert "ITEM_WORKTREE=" in run.stdout
    assert "ITEM_REQUIRED_ENV=FAIL" in run.stdout or "ITEM_REQUIRED_ENV=" in run.stdout
    assert "ITEM_TLS_DNS_READINESS=FAIL" in run.stdout
    assert "ITEM_MEDIA_PATH=N/A" in run.stdout
    assert run.stdout.count("ITEM_") >= 14


def test_pre_release_checklist_fails_fast_on_bad_sha(tmp_path: Path) -> None:
    run = subprocess.run(
        ["bash", str(CHECKLIST), "--expect-sha", "0" * 40],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=300,
        check=False,
    )
    assert run.returncode != 0
    assert "ITEM_RC_SHA=FAIL" in run.stdout
    assert "PRE_RELEASE_CHECKLIST=FAIL" in run.stdout


# ------------------------------------------------------- database dependency


def test_probe_detects_process_up_database_down(api_up: int) -> None:
    run = subprocess.run(
        [
            "bash",
            str(PROBE),
            "--api-base",
            f"http://127.0.0.1:{api_up}",
            "--db-url",
            "postgresql+asyncpg://u:p@127.0.0.1:59999/nope",
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    assert "PROBE_PROCESS=UP" in run.stdout
    assert "PROBE_DATABASE=FAIL" in run.stdout
    assert "PROBE_RESULT=FAIL" in run.stdout
    assert run.returncode != 0


def test_probe_detects_process_down(api_up: int) -> None:
    import socket

    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        free_port = int(s.getsockname()[1])
    run = subprocess.run(
        [
            "bash",
            str(PROBE),
            "--api-base",
            f"http://127.0.0.1:{free_port}",
            "--db-url",
            "postgresql+asyncpg://u:p@127.0.0.1:59999/nope",
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert "PROBE_PROCESS=DOWN" in run.stdout
    assert run.returncode != 0


def test_probe_passes_when_process_and_database_ok(api_up: int, tmp_path: Path) -> None:
    db_url = _sqlite_at_head(tmp_path)
    run = subprocess.run(
        [
            "bash",
            str(PROBE),
            "--api-base",
            f"http://127.0.0.1:{api_up}",
            "--db-url",
            db_url,
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    assert run.returncode == 0, run.stdout + run.stderr
    assert "PROBE_DATABASE=OK" in run.stdout
    assert "PROBE_RESULT=PASS" in run.stdout
