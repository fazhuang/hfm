#!/usr/bin/env bash
# P1-07 synthetic secret-detection tests (fail-closed).
# Creates fixture files with obvious secrets and safe placeholders, runs the
# scanner against each, and asserts the expected exit codes. Real secret
# values are never printed.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCANNER="$ROOT/scripts/check-secrets.py"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

run_scan() {
  local dir="$1"
  # Run the scanner over a single file via a temp git-tracked illusion:
  # point the scanner at a file we directly scan with a helper call.
  python3 - "$SCANNER" "$dir" <<'PY'
import sys
from pathlib import Path
import importlib.util
spec = importlib.util.spec_from_file_location("cs", sys.argv[1])
sys.modules["cs"] = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sys.modules["cs"])
mod = sys.modules["cs"]
findings = []
for f in Path(sys.argv[2]).iterdir():
    findings.extend(mod.scan_file(f))
if findings:
    print("FAIL: " + ", ".join(f.cls for f in findings))
    raise SystemExit(1)
print("PASS")
PY
}

# 1. Obvious committed literal password -> FAIL
mkdir -p "$TMP/obvious"
cat > "$TMP/obvious/config.json" <<'JSON'
{ "database": { "password": "S3cr3t-P@ssw0rd!" } }
JSON
if run_scan "$TMP/obvious" >/dev/null 2>&1; then
  echo "FAIL: obvious password was not detected"
  exit 1
fi
echo "P1-07 synthetic: obvious literal password -> detected (FAIL path) OK"

# 2. Cloud/token style credential -> FAIL
mkdir -p "$TMP/token"
cat > "$TMP/token/app.py" <<'PY'
token = "ghp_1234567890123456789012345678901234"
PY
if run_scan "$TMP/token" >/dev/null 2>&1; then
  echo "FAIL: token credential was not detected"
  exit 1
fi
echo "P1-07 synthetic: token credential -> detected (FAIL path) OK"

# 3. Private key -> FAIL
mkdir -p "$TMP/key"
cat > "$TMP/key/id_rsa" <<'KEY'
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEAabcdefghijklmnopqrstuvwxyz0123456789
-----END RSA PRIVATE KEY-----
KEY
if run_scan "$TMP/key" >/dev/null 2>&1; then
  echo "FAIL: private key was not detected"
  exit 1
fi
echo "P1-07 synthetic: private key -> detected (FAIL path) OK"

# 4. Safe placeholder -> PASS (allowed through explicit safe pattern)
mkdir -p "$TMP/safe"
cat > "$TMP/safe/env.local" <<'CFG'
password = "CHANGEME"
api_token = "your-token-here"
CFG
if ! run_scan "$TMP/safe" >/dev/null 2>&1; then
  echo "FAIL: safe placeholders should be allowed"
  exit 1
fi
echo "P1-07 synthetic: safe placeholders -> allowed (PASS path) OK"


# --- P1-01 adversarial exemption tests (exact-path fixture exemption) ----

# A. exact fixture path exempt
python3 - "$SCANNER" "$ROOT" <<'PY' >/dev/null 2>&1
import sys
from pathlib import Path
import importlib.util
spec = importlib.util.spec_from_file_location("cs", sys.argv[1])
sys.modules["cs"] = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sys.modules["cs"])
mod = sys.modules["cs"]
root = Path(sys.argv[2])
checks = [
    (True,  "scripts/test-check-secrets.sh", "exact fixture path"),
    (False, "scripts/test-check-secrets2.sh", "similarly named file"),
    (False, "scripts/sub/test-check-secrets.sh", "nested different path"),
    (False, "scripts/renamed-check-secrets.sh", "renamed fixture"),
    (False, "scripts/test-check-secrets.sh.bak", "extension-variant fixture"),
]
for expected, rel, label in checks:
    got = mod.is_exempt_tracked_fixture(root, root / rel)
    if got != expected:
        print(f"FAIL: {label} exempt={got} (expected {expected})")
        raise SystemExit(1)
print("PASS")
PY
adv_exit=$?
if [ "$adv_exit" -ne 0 ]; then
  echo "FAIL: adversarial exemption semantics"
  exit 1
fi
echo "P1-01 adversarial: exact-path exemption (similar/nested/renamed NOT exempt) OK"

# B. non-exempt synthetic secret still detected (fail-closed retained)
mkdir -p "$TMP/other"
cat > "$TMP/other/app.py" <<'PY'
secret = "AKIA1234567890ABCDEF"
PY
if run_scan "$TMP/other" >/dev/null 2>&1; then
  echo "FAIL: non-exempt secret fixture was not detected"
  exit 1
fi
echo "P1-01 adversarial: non-exempt secret still detected (fail-closed) OK"

echo "SECRET_SCANNER_ADVERSARIAL=PASS"

echo "SECRET_SCANNER_SYNTHETIC=PASS"
