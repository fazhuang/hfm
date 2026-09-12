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
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
BUILD_SCRIPT = REPO_ROOT / "scripts" / "build-release.sh"
PYTHON = "/usr/local/bin/python3.12"


def _shim_bin(tmp_path: Path, name: str, reported: str, real: str) -> Path:
    """A PATH shim that reports a chosen --version but delegates everything
    else to the real tool (no permanent system change)."""
    bin_dir = tmp_path / "shims"
    bin_dir.mkdir(exist_ok=True)
    shim = bin_dir / name
    shim.write_text(
        "#!/usr/bin/env bash\n"
        'if [[ "${1:-}" == "--version" ]]; then echo "' + reported + '"; exit 0; fi\n'
        f'exec {real} "$@"\n',
        encoding="utf-8",
    )
    shim.chmod(0o755)
    return bin_dir


def _runtime_env(tmp_path: Path, **overrides: str) -> dict[str, str]:
    """PATH with a Node-22 shim; real pnpm (10.33.2) and python3.12 remain."""
    real_node = subprocess.run(
        ["bash", "-lc", "command -v node"], capture_output=True, text=True, check=True
    ).stdout.strip()
    bin_dir = _shim_bin(tmp_path, "node", "v22.19.0", real_node)
    env = {
        **os.environ,
        "PATH": f"{bin_dir}:{os.environ.get('PATH', '')}",
        "PYTHON": PYTHON,
        **overrides,
    }
    return env


def _pypi_reachable() -> bool:
    run = subprocess.run(
        [
            "curl",
            "-s",
            "-m",
            "8",
            "-o",
            "/dev/null",
            "-w",
            "%{http_code}",
            "https://pypi.org/simple/",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    return run.stdout.strip() == "200"


@pytest.mark.skipif(not _pypi_reachable(), reason="PyPI unreachable")
def test_release_locks_parse() -> None:
    run = subprocess.run(
        ["bash", str(BUILD_SCRIPT), "--check"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert run.returncode == 0, run.stdout
    assert "RELEASE_LOCKS=PASS" in run.stdout


@pytest.mark.skipif(not _pypi_reachable(), reason="PyPI unreachable")
def test_release_build_emits_manifest_with_expected_artifacts(tmp_path: Path) -> None:
    out = tmp_path / "release"
    head = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
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
        timeout=900,
        check=False,
        env=_runtime_env(tmp_path),
    )
    assert run.returncode == 0, run.stdout + run.stderr
    assert "RUNTIME_WHEELHOUSE=DOWNLOAD_VERIFIED" in run.stdout
    manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["source_sha"] == head
    paths = {artifact["path"]: artifact["sha256"] for artifact in manifest["artifacts"]}
    assert any(p.startswith("wheels/hfm_backend-") for p in paths)
    assert "alembic/alembic/env.py" in paths
    assert not any("__pycache__" in p for p in paths)
    for path, digest in paths.items():
        blob = (out / path).read_bytes()
        assert hashlib.sha256(blob).hexdigest() == digest


@pytest.mark.skipif(not _pypi_reachable(), reason="PyPI unreachable")
def test_release_build_packages_hash_verified_runtime_closure(tmp_path: Path) -> None:
    """RV-P1-02: the full production runtime closure is packaged + hash-verified."""
    import re

    out = tmp_path / "release"
    head = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
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
        timeout=900,
        check=False,
        env=_runtime_env(tmp_path),
    )
    assert run.returncode == 0, run.stdout + run.stderr

    # The bundled lock copy and every runtime wheel must exist with the locked
    # sha256 (download was already pip --require-hashes verified).
    bundle_lock = (out / "runtime-requirements-production.lock").read_text(
        encoding="utf-8"
    )
    pinned = {}
    cur = None
    for line in bundle_lock.splitlines():
        m = re.match(r"^([A-Za-z0-9_.-]+==[^ ]+) \\$", line)
        if m:
            cur = m.group(1)
            continue
        hm = re.match(r"^\s*--hash=sha256:([0-9a-f]{64})$", line)
        if hm and cur:
            pinned.setdefault(cur.split("==")[0].replace("-", "_").lower(), set()).add(
                hm.group(1)
            )
    wheelhouse = out / "runtime-wheelhouse"
    wheels = sorted(wheelhouse.glob("*.whl"))
    assert len(wheels) >= 20, "runtime closure should contain the full wheel set"
    seen = {}
    for wheel in wheels:
        name = wheel.name.split("-")[0].replace("-", "_").lower()
        seen.setdefault(name, set()).add(hashlib.sha256(wheel.read_bytes()).hexdigest())
    for name in ("alembic", "asyncpg", "fastapi", "sqlalchemy", "uvicorn"):
        assert name in seen, f"missing runtime package: {name}"
        assert seen[name] & pinned.get(name, set()), f"hash mismatch for {name}"

    manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
    assert any(
        a["path"].startswith("runtime-wheelhouse/") for a in manifest["artifacts"]
    )
    assert any(
        a["path"] == "runtime-requirements-production.lock"
        for a in manifest["artifacts"]
    )

    # Clean-platform install from ONLY the bundle is executable on the declared
    # platform (linux x86_64 + CPython 3.12); skipped on other hosts.
    if sys.platform.startswith("linux") and sys.version_info[:2] == (3, 12):
        env_dir = tmp_path / "runtime-venv"
        subprocess.run([PYTHON, "-m", "venv", str(env_dir)], check=True)
        install = subprocess.run(
            [
                str(env_dir / "bin" / "pip"),
                "install",
                "--no-index",
                "--find-links",
                str(wheelhouse),
                "-r",
                str(out / "runtime-requirements-production.lock"),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        assert install.returncode == 0, install.stderr[-2000:]
        probe = subprocess.run(
            [
                str(env_dir / "bin" / "python"),
                "-c",
                "import fastapi, sqlalchemy, asyncpg, alembic, uvicorn",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        assert probe.returncode == 0, probe.stderr


# ------------------------------------------------ ND-1 B02 runtime contract


def _run_runtime(tmp_path: Path, **overrides: str) -> subprocess.CompletedProcess[str]:
    env = _runtime_env(tmp_path, **overrides)
    return subprocess.run(
        ["bash", str(BUILD_SCRIPT), "--check-runtime"],
        cwd=str(REPO_ROOT),
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )


def test_runtime_contract_passes_with_declared_runtimes(tmp_path: Path) -> None:
    run = _run_runtime(tmp_path)
    assert run.returncode == 0, run.stdout + run.stderr
    assert "RUNTIME_CONTRACT=PASS" in run.stdout
    assert "SOURCE_SHA=" in run.stdout
    assert "PYTHON_VERSION=Python 3.12." in run.stdout
    assert "NODE_VERSION=v22." in run.stdout
    assert "PNPM_VERSION=10.33.2" in run.stdout


def test_runtime_contract_fails_on_missing_python(tmp_path: Path) -> None:
    run = _run_runtime(tmp_path, PYTHON="/nonexistent/python3.12")
    assert run.returncode != 0
    assert "PYTHON=FAIL" in run.stdout
    assert "RUNTIME_CONTRACT=FAIL" in run.stdout


def test_runtime_contract_fails_on_wrong_python_minor(tmp_path: Path) -> None:
    real = "/usr/local/bin/python3.12"
    py_dir = _shim_bin(tmp_path, "pyfake", "Python 3.13.9", real)
    run = subprocess.run(
        ["bash", str(BUILD_SCRIPT), "--check-runtime"],
        cwd=str(REPO_ROOT),
        env={
            **os.environ,
            "PYTHON": str(py_dir / "pyfake"),
            "PATH": _runtime_env(tmp_path)["PATH"],
        },
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    assert run.returncode != 0
    assert "PYTHON=FAIL" in run.stdout
    assert "3.12" in run.stdout


def test_runtime_contract_fails_on_wrong_node_major(tmp_path: Path) -> None:
    real_node = subprocess.run(
        ["bash", "-lc", "command -v node"], capture_output=True, text=True, check=True
    ).stdout.strip()
    bin_dir = _shim_bin(tmp_path, "node", "v24.0.0", real_node)
    run = subprocess.run(
        ["bash", str(BUILD_SCRIPT), "--check-runtime"],
        cwd=str(REPO_ROOT),
        env={
            **os.environ,
            "PATH": f"{bin_dir}:{os.environ.get('PATH', '')}",
            "PYTHON": PYTHON,
        },
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    assert run.returncode != 0
    assert "NODE=FAIL" in run.stdout
    assert "RUNTIME_CONTRACT=FAIL" in run.stdout


def test_runtime_contract_fails_on_wrong_pnpm(tmp_path: Path) -> None:
    real_pnpm = subprocess.run(
        ["bash", "-lc", "command -v pnpm"], capture_output=True, text=True, check=True
    ).stdout.strip()
    bin_dir = _shim_bin(tmp_path, "pnpm", "9.15.0", real_pnpm)
    run = subprocess.run(
        ["bash", str(BUILD_SCRIPT), "--check-runtime"],
        cwd=str(REPO_ROOT),
        env={
            **os.environ,
            "PATH": f"{bin_dir}:{os.environ.get('PATH', '')}",
            "PYTHON": PYTHON,
        },
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    assert run.returncode != 0
    assert "PNPM=FAIL" in run.stdout
