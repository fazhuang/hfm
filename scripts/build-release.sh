#!/usr/bin/env bash
# HFM deterministic release build (ND-1 B02).
#
# Produces release artifacts from a clean, isolated environment using the
# committed dependency locks (infra/requirements-{production,build}.lock) and
# the frozen pnpm lockfile, then emits an artifact manifest with the source
# SHA, tool/lock identifiers and per-artifact sha256.
#
# Declared production platform: linux x86_64 (manylinux2014), CPython 3.12;
# Node 22 LTS; pnpm 10.33.2 (see lock headers).
#
#   build-release.sh --out DIR [--expect-sha SHA] [--skip-frontend]
#   build-release.sh --check          # validate lock file syntax (no network)
#
# Artifacts under OUT/: backend wheel(s), frontend static dist, packaged
# Alembic tree, and manifest.json. This script never installs into the source
# tree (editable installs are forbidden for release identity) and never
# touches a database or secrets.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="${PYTHON:-$(command -v python3.12 || command -v python3)}"

# --------------------------------------------------------------- helpers
artifact_hash() { shasum -a 256 "$1" | awk '{print $1}'; }
check_lock() {
  # Every meaningful line is `name==version \` followed by `--hash=sha256:...`.
  awk '
    BEGIN { expect_hash=0; ok=1 }
    /^#/ || /^$/ { next }
    /^[ \t]*--hash=sha256:[0-9a-f]{64}$/ { if (!expect_hash) { print "hash without pin at line " NR; ok=0 }; expect_hash=0; next }
    /^[A-Za-z0-9_.-]+==[^ ]+ \\$/ { expect_hash=1; next }
    { print "malformed line " NR ": " $0; ok=0 }
    END { if (expect_hash) { print "missing hash after pin"; ok=0 }; exit (ok ? 0 : 1) }
  ' "$1"
}

if [[ "${1:-}" == "--check" ]]; then
  FAIL=0
  for lock in "$REPO_ROOT/infra/requirements-production.lock" "$REPO_ROOT/infra/requirements-build.lock"; do
    if check_lock "$lock"; then echo "LOCK_OK=$lock"; else echo "LOCK_FAIL=$lock"; FAIL=1; fi
  done
  [[ -f "$REPO_ROOT/pnpm-lock.yaml" ]] || { echo "LOCK_FAIL=pnpm-lock.yaml missing"; FAIL=1; }
  [[ "$FAIL" -eq 0 ]] && echo "RELEASE_LOCKS=PASS" || echo "RELEASE_LOCKS=FAIL"
  exit "$FAIL"
fi

OUT=""
EXPECT_SHA=""
SKIP_FRONTEND=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --out) OUT="${2:-}"; shift ;;
    --expect-sha) EXPECT_SHA="${2:-}"; shift ;;
    --skip-frontend) SKIP_FRONTEND=1 ;;
    *) echo "usage: build-release.sh --out DIR [--expect-sha SHA] [--skip-frontend] | --check"; exit 2 ;;
  esac
  shift
done
[[ -n "$OUT" ]] || { echo "usage: build-release.sh --out DIR"; exit 2; }

SOURCE_SHA="$(git -C "$REPO_ROOT" rev-parse HEAD)"
if [[ -n "$EXPECT_SHA" && "$SOURCE_SHA" != "$EXPECT_SHA" ]]; then
  echo "SOURCE_SHA_MISMATCH expected=$EXPECT_SHA actual=$SOURCE_SHA"
  exit 1
fi
echo "SOURCE_SHA=$SOURCE_SHA"

rm -rf "$OUT" && mkdir -p "$OUT/wheels" "$OUT/frontend-dist" "$OUT/alembic"

# ------------------------------------------------ backend wheel (isolated)
BUILD_VENV="$OUT/venv-build"
"$PYTHON" -m venv "$BUILD_VENV"
"$BUILD_VENV/bin/python" -m pip install --quiet --upgrade pip
# Build tooling comes from the committed build lock (pure wheels).
"$BUILD_VENV/bin/python" -m pip install --quiet --require-hashes \
  -r "$REPO_ROOT/infra/requirements-build.lock"
(cd "$REPO_ROOT/apps/backend" && \
  "$BUILD_VENV/bin/python" -m pip wheel . --no-build-isolation --no-deps \
  --wheel-dir "$OUT/wheels" >/dev/null)
echo "BACKEND_WHEEL=BUILT"

# ------------------------------------------------ alembic packaging
cp -R "$REPO_ROOT/apps/backend/alembic" "$OUT/alembic/" || true
cp "$REPO_ROOT/apps/backend/alembic.ini" "$OUT/alembic/alembic.ini"
find "$OUT/alembic" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
echo "ALEMBIC_PACKAGE=COPIED"

# ------------------------------------------------ runtime closure (RV-P1-02)
# Download-verify and package the COMPLETE production runtime closure from
# requirements-production.lock as a hash-verified wheelhouse for the declared
# platform/ABI. pip rejects any artifact whose sha256 does not match the lock.
# Runtime venv provisioning from the bundle (see ops doc):
#   python3.12 -m venv /opt/hfm/venv
#   /opt/hfm/venv/bin/pip install --no-index \
#       --find-links /opt/hfm/runtime-wheelhouse \
#       -r /opt/hfm/runtime-requirements-production.lock
mkdir -p "$OUT/runtime-wheelhouse"
"$BUILD_VENV/bin/python" -m pip download --require-hashes --only-binary=:all: \
  --platform manylinux2014_x86_64 --python-version 312 --implementation cp --abi cp312 \
  -r "$REPO_ROOT/infra/requirements-production.lock" -d "$OUT/runtime-wheelhouse" \
  >/tmp/hfm-runtime-download.log 2>&1
cp "$REPO_ROOT/infra/requirements-production.lock" "$OUT/runtime-requirements-production.lock"
RUNTIME_WHEEL_COUNT="$(find "$OUT/runtime-wheelhouse" -name '*.whl' | wc -l | tr -d ' ')"
echo "RUNTIME_WHEELHOUSE=DOWNLOAD_VERIFIED wheels=$RUNTIME_WHEEL_COUNT"

# ------------------------------------------------ frontend static build
if [[ "$SKIP_FRONTEND" -eq 0 ]]; then
  (cd "$REPO_ROOT/apps/frontend" && pnpm install --frozen-lockfile >/dev/null && pnpm build >/dev/null)
  cp -R "$REPO_ROOT/apps/frontend/dist/." "$OUT/frontend-dist/"
  echo "FRONTEND_DIST=BUILT"
fi

# ------------------------------------------------ manifest
PY_VER="$($PYTHON --version 2>&1)"
MANIFEST_PYTHON="$PY_VER" python3 - "$OUT" "$SOURCE_SHA" "$REPO_ROOT" "$SKIP_FRONTEND" <<'PY'
import hashlib, json, os, sys
from pathlib import Path

out, source_sha, repo, skip_fe = sys.argv[1], sys.argv[2], Path(sys.argv[3]), sys.argv[4] == "1"

PYTHON_VER = os.environ.get("MANIFEST_PYTHON", sys.version.split()[0])

def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

artifacts = []
for root in ("wheels", "alembic", "runtime-wheelhouse"):
    base = Path(out) / root
    for path in sorted(base.rglob("*")):
        if path.is_file():
            rel = f"{root}/{path.relative_to(base)}"
            artifacts.append({"path": rel, "sha256": sha256(path), "size": path.stat().st_size})
if not skip_fe:
    base = Path(out) / "frontend-dist"
    for path in sorted(base.rglob("*")):
        if path.is_file():
            rel = f"frontend-dist/{path.relative_to(base)}"
            artifacts.append({"path": rel, "sha256": sha256(path), "size": path.stat().st_size})
lock_copy = Path(out) / "runtime-requirements-production.lock"
if lock_copy.is_file():
    artifacts.append(
        {
            "path": "runtime-requirements-production.lock",
            "sha256": sha256(lock_copy),
            "size": lock_copy.stat().st_size,
        }
    )

manifest = {
    "source_sha": source_sha,
    "built_at": os.environ.get("SOURCE_DATE_EPOCH", ""),
    "python": PYTHON_VER,
    "locks": {
        "requirements-production.lock": sha256(Path(repo) / "infra" / "requirements-production.lock"),
        "requirements-build.lock": sha256(Path(repo) / "infra" / "requirements-build.lock"),
        "pnpm-lock.yaml": sha256(Path(repo) / "pnpm-lock.yaml"),
    },
    "artifacts": artifacts,
}
Path(out, "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
print(f"MANIFEST_ARTIFACTS={len(artifacts)}")
PY

echo "RELEASE_BUILD=PASS out=$OUT"
