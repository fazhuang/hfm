#!/usr/bin/env bash
# HFM ND-1 — PRE-RELEASE CHECKLIST (mechanical, machine-executable)
#
# Each item records PASS / FAIL / N/A+justification. Target-infrastructure
# facts (TLS/DNS, real backup point, live auth/bootstrap on the target) are
# operator-declared via flags for ND-2 execution; ND-1 validates the
# mechanism and everything that can be proven without touching the target.
#
#   pre-release-checklist.sh \
#     [--expect-sha SHA] [--env-file FILE] [--allow-sqlite]
#     [--nginx-conf FILE] [--media-root DIR]
#     [--backup-point VALUE] [--tls-dns-ready yes|no]
#     [--rollback-ready yes|no] [--auth-verified yes|no]
#     [--bootstrap-status VALUE]
#
# Exit 0 only when every non-N/A item PASSes. Never a substitute for the
# target ND-2 runbook — it makes each declared fact auditable.
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="$REPO_ROOT/apps/backend/.venv/bin/python"
FAIL=0
RESULTS=()

expect_sha=""
env_file=""
allow_sqlite=0
nginx_conf=""
media_root=""
backup_point=""
tls_dns=""
rollback_ready=""
auth_verified=""
bootstrap_status=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --expect-sha) expect_sha="${2:-}"; shift ;;
    --env-file) env_file="${2:-}"; shift ;;
    --allow-sqlite) allow_sqlite=1 ;;
    --nginx-conf) nginx_conf="${2:-}"; shift ;;
    --media-root) media_root="${2:-}"; shift ;;
    --backup-point) backup_point="${2:-}"; shift ;;
    --tls-dns-ready) tls_dns="${2:-}"; shift ;;
    --rollback-ready) rollback_ready="${2:-}"; shift ;;
    --auth-verified) auth_verified="${2:-}"; shift ;;
    --bootstrap-status) bootstrap_status="${2:-}"; shift ;;
    *) echo "usage error: unknown flag $1"; exit 2 ;;
  esac
  shift
done

record() { # LABEL STATUS DETAIL
  RESULTS+=("$1=$2")
  printf '%s\n' "ITEM_$1=$2 ($3)"
  if [[ "$2" == "FAIL" ]]; then FAIL=1; fi
}

expect_or_na() { # LABEL EXPECTED ACTUAL JUSTIFICATION_WHEN_NA
  if [[ -n "$3" ]]; then
    if [[ "$2" == "$3" ]]; then record "$1" PASS "matches ${3}"; else record "$1" FAIL "expected ${3}, got ${2}"; fi
  else
    record "$1" "N/A" "$4"
  fi
}

expect_yes_na() { # LABEL VALUE JUSTIFICATION_WHEN_NA — PASS only for explicit "yes".
  if [[ -n "$2" ]]; then
    if [[ "$2" == "yes" ]]; then record "$1" PASS "declared ready"; else record "$1" FAIL "declared not-ready (got '$2')"; fi
  else
    record "$1" "N/A" "$3"
  fi
}

# 01 RC SHA -------------------------------------------------------------
sha="$(git -C "$REPO_ROOT" rev-parse HEAD 2>/dev/null || echo unknown)"
expect_or_na "RC_SHA" "$sha" "$expect_sha" "no --expect-sha pinned for this run"

# 02 worktree / artifact identity --------------------------------------
if [[ -z "$(git -C "$REPO_ROOT" status --porcelain)" ]]; then
  record "WORKTREE" PASS "clean porcelain"
else
  record "WORKTREE" FAIL "dirty porcelain"
fi
if git -C "$REPO_ROOT" diff --check --quiet; then
  record "DIFF_CHECK" PASS "no whitespace errors"
else
  record "DIFF_CHECK" FAIL "git diff --check errors"
fi

# 03 required env/secrets + 04/05 PostgreSQL + migration revision --------
BASE_VALIDATOR=(--env prod)
if [[ "$allow_sqlite" -eq 1 ]]; then BASE_VALIDATOR+=(--allow-sqlite); fi
if [[ -n "$env_file" ]]; then BASE_VALIDATOR+=(--env-file "$env_file"); fi
if "$PYTHON" "$REPO_ROOT/scripts/validate-production-env.py" "${BASE_VALIDATOR[@]}" >/tmp/hfm-pre-env.log 2>&1; then
  record "REQUIRED_ENV" PASS "redacted validator accepted HFM_* inputs"
else
  record "REQUIRED_ENV" FAIL "env preflight rejected configuration (see validator)"
fi
if "$PYTHON" "$REPO_ROOT/scripts/validate-production-env.py" "${BASE_VALIDATOR[@]}" --verify-migration >/tmp/hfm-pre-mig.log 2>&1; then
  record "POSTGRES_CONNECTIVITY" PASS "reachable"
  record "MIGRATION_REVISION" PASS "current == head == 0015"
else
  record "POSTGRES_CONNECTIVITY" FAIL "database unreachable or verification failed"
  record "MIGRATION_REVISION" FAIL "current/head not verified as 0015"
fi

# 06 backup/restore point ----------------------------------------------
expect_or_na "BACKUP_POINT" "${backup_point:-}" "$backup_point" "operator must declare a pre-release backup point at ND-2"

# 07 bootstrap status ----------------------------------------------------
expect_or_na "BOOTSTRAP_STATUS" "${bootstrap_status:-}" "$bootstrap_status" "operator must declare bootstrap/admin evidence at ND-2"

# 08 persistent media path ----------------------------------------------
if [[ -n "$media_root" ]]; then
  if [[ -d "$media_root" && -w "$media_root" ]]; then
    record "MEDIA_PATH" PASS "$media_root present and writable"
  else
    record "MEDIA_PATH" FAIL "$media_root missing or not writable"
  fi
else
  record "MEDIA_PATH" "N/A" "no --media-root declared for this run"
fi

# 09 runtime versions ----------------------------------------------------
if bash "$REPO_ROOT/scripts/build-release.sh" --check-runtime >/tmp/hfm-pre-runtime.log 2>&1; then
  record "RUNTIME_VERSIONS" PASS "python/node/pnpm contract verified (see log)"
else
  record "RUNTIME_VERSIONS" FAIL "declared runtime unavailable/mismatched (see log)"
fi

# 10 reverse proxy config -----------------------------------------------
if [[ -n "$nginx_conf" ]]; then
  if bash "$REPO_ROOT/scripts/production-smoke.sh" --media-alias-check "$nginx_conf" >/dev/null 2>&1; then
    record "REVERSE_PROXY_CONFIG" PASS "media-boundary + private /api proxy contract holds"
  else
    record "REVERSE_PROXY_CONFIG" FAIL "nginx contract check failed"
  fi
else
  record "REVERSE_PROXY_CONFIG" "N/A" "no --nginx-conf declared for this run"
fi

# 11 TLS/DNS readiness ---------------------------------------------------
expect_yes_na "TLS_DNS_READINESS" "${tls_dns:-}" "target TLS/DNS readiness is an ND-2 execution fact"

# 12 auth prerequisite ---------------------------------------------------
expect_yes_na "AUTH_PREREQUISITE" "${auth_verified:-}" "real-browser auth evidence is declared at ND-2"

# 13 rollback readiness --------------------------------------------------
expect_yes_na "ROLLBACK_READINESS" "${rollback_ready:-}" "rollback trigger matrix + verified restore declared at ND-2"

echo "---"
printf 'ITEM_SUMMARY=%s\n' "$(IFS=,; echo "${RESULTS[*]}")"
if [[ "$FAIL" -eq 0 ]]; then
  echo "PRE_RELEASE_CHECKLIST=PASS"
  exit 0
fi
echo "PRE_RELEASE_CHECKLIST=FAIL"
exit 1
