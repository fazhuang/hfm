#!/usr/bin/env bash
# HFM secret boundary check (P2-07-AC-02).
#
# Scans every tracked file for committed secrets. The *.env.example files
# contain only placeholders (CHANGEME / local dev defaults) and are exempt;
# any real credential pattern in a committed file fails the check.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# Pattern classes considered secrets when found in committed files.
PATTERNS=(
  'BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY'
  'AKIA[0-9A-Z]{16}'
  '(?i)(password|secret|token)[[:space:]]*[=:][[:space:]]*['"][^'"]{8,}['"]'  # quoted literal credential
  '[a-z]+://[^:@/ ]+:(?!change-?me@|changeme@|CHANGEME@|example@)[^:@/ ]+@'  # URL with embedded credentials (non-placeholder)
)

FOUND=0
while IFS= read -r file; do
  [[ -f "$file" ]] || continue
  case "$file" in
    infra/env/*.env.example) continue ;;  # placeholder contracts only
  esac
  for pattern in "${PATTERNS[@]}"; do
    if grep -qE "$pattern" "$file" 2>/dev/null; then
      echo "SECRET FOUND: $file (pattern: ${pattern:0:40})"
      FOUND=$((FOUND + 1))
    fi
  done
done < <(git ls-files)

if [[ "$FOUND" -gt 0 ]]; then
  echo "SECRET_BOUNDARY=FAIL ($FOUND finding(s))"
  exit 1
fi
echo "SECRET_BOUNDARY=PASS (no committed secrets)"
