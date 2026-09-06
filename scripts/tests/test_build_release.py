"""ND-1 B02 — deterministic release build checks.

Proves the release locks parse (scripts/build-release.sh --check) and that a
real release build from the frozen source emits the backend wheel, packaged
Alembic tree and a manifest whose source SHA matches HEAD with valid
per-artifact sha256 (no __pycache__, no editable reuse).

The full build downloads the pure-wheel build lock from PyPI; it is skipped
when the index is unreachable so the suite stays portable.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
BUILD_SCRIPT = REPO_ROOT / "scripts" / "build-release.sh"
PYTHON = "/usr/local/bin/python3.12"


def _pypi_reachable() -> bool:
    run = subprocess.run(
        ["curl", "-s", "-m", "8", "-o", "/dev/null", "-w", "%{http_code}", "https://pypi.org/simple/"],
        capture_output=True,
        text=True,
        check=False,
    )
    return run.stdout.strip() == "200"


@pytest.mark.skipif(not _pypi_reachable(), reason="PyPI unreachable")
def test_release_locks_parse() -> None:
    run = subprocess.run(["bash", str(BUILD_SCRIPT), "--check"], capture_output=True, text=True, check=False)
    assert run.returncode == 0, run.stdout
    assert "RELEASE_LOCKS=PASS" in run.stdout


@pytest.mark.skipif(not _pypi_reachable(), reason="PyPI unreachable")
def test_release_build_emits_manifest_with_expected_artifacts(tmp_path: Path) -> None:
    out = tmp_path / "release"
    head = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"], capture_output=True, text=True, check=True
    ).stdout.strip()
    run = subprocess.run(
        [
            "bash",
            str(BUILD_SCRIPT),
            "--out",
            str(out),
            "--expect-sha",
            head,
            "--skip-frontend",
        ],
        capture_output=True,
        text=True,
        timeout=600,
        check=False,
    )
    assert run.returncode == 0, run.stdout + run.stderr
    manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["source_sha"] == head
    paths = {artifact["path"]: artifact["sha256"] for artifact in manifest["artifacts"]}
    assert any(p.startswith("wheels/hfm_backend-") for p in paths)
    assert "alembic/alembic/env.py" in paths
    assert not any("__pycache__" in p for p in paths)
    for path, digest in paths.items():
        blob = (out / path).read_bytes()
        assert hashlib.sha256(blob).hexdigest() == digest
