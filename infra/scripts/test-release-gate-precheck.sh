#!/usr/bin/env bash
# P0-01 adversarial tests for the governance fail-closed precheck.
# Proves the release gate blocks governed deselection in every governance
# failure mode (A–J) and proceeds only on the valid state.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PRECHECK="$ROOT/infra/scripts/verify-governance-precheck.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

NODE_P1RW="tests/test_phase1_research_workspace.py::test_migration_0013_upgrade_downgrade_upgrade_single_head"
NODE_FB="tests/test_phase2_guardrails.py::test_frozen_boundary_states"
NODE_MI="tests/test_phase2_guardrails.py::test_migration_invariant"
AUTHORIZED_NODES=("$NODE_P1RW" "$NODE_FB" "$NODE_MI")

expect_fail() {
  local label="$1"
  shift
  if HFM_VERIFIER="${HFM_VERIFIER:-$ROOT/scripts/verify-invariant-supersessions.py}" \
     HFM_SUPERSESSION_REGISTER="${HFM_SUPERSESSION_REGISTER:-$ROOT/docs/governance/HFM-PHASE2-INVARIANT-SUPERSESSION-REGISTER-v1.md}" \
     "$PRECHECK" "$@" > /dev/null 2>&1; then
    echo "FAIL: $label did not fail closed"
    exit 1
  fi
  echo "P0 adversarial: $label -> FAIL (closed) OK"
}

# Stub verifiers.
cat > "$TMP/verifier-fail.sh" <<'SH'
#!/bin/sh
echo "SUPERSESSION_REGISTER=FAIL"
exit 1
SH
cat > "$TMP/verifier-nopass.sh" <<'SH'
#!/bin/sh
echo "SUPERSESSION_REGISTER=UNKNOWN"
exit 0
SH
chmod +x "$TMP/verifier-fail.sh" "$TMP/verifier-nopass.sh"

# A. governance verifier fails
HFM_VERIFIER="$TMP/verifier-fail.sh" expect_fail "A verifier fails" "${AUTHORIZED_NODES[@]}"

# B. verifier executable unavailable
HFM_VERIFIER="$TMP/nonexistent-verifier.py" expect_fail "B verifier unavailable" "${AUTHORIZED_NODES[@]}"

# G/H. verifier detects invalid authority/baseline binding (non-PASS signal)
HFM_VERIFIER="$TMP/verifier-nopass.sh" expect_fail "G/H verifier non-PASS signal" "${AUTHORIZED_NODES[@]}"

# C. malformed register
echo "not a valid register" > "$TMP/malformed-register.md"
HFM_SUPERSESSION_REGISTER="$TMP/malformed-register.md" expect_fail "C malformed register" "${AUTHORIZED_NODES[@]}"

# D. historical assertion no longer SUPERSEDED (entries ACTIVE)
cat > "$TMP/active-register.md" <<'MD'
### ASN-P200-MIG-0013-HEAD
CLASS: H
STATUS: ACTIVE
REPLAY_TEST: tests/test_phase2_guardrails.py
MD
HFM_SUPERSESSION_REGISTER="$TMP/active-register.md" expect_fail "D no longer superseded" "${AUTHORIZED_NODES[@]}"

# I. governed node mapping missing (superseded entry without REPLAY_TEST)
cat > "$TMP/nomapping-register.md" <<'MD'
### ASN-P200-MIG-0013-HEAD
CLASS: H
STATUS: SUPERSEDED
REPLAY_TEST: N/A
MD
HFM_SUPERSESSION_REGISTER="$TMP/nomapping-register.md" expect_fail "I governed node mapping missing" "${AUTHORIZED_NODES[@]}"

# E. deselected node not formally authorized (outside superseded scopes)
HFM_SUPERSESSION_REGISTER="$ROOT/docs/governance/HFM-PHASE2-INVARIANT-SUPERSESSION-REGISTER-v1.md" \
  expect_fail "E unauthorized deselection" \
  tests/test_phase2_media.py::test_p2_current_migration_head_0014 "${AUTHORIZED_NODES[@]}"

# J. extra unregistered deselection injected
HFM_SUPERSESSION_REGISTER="$ROOT/docs/governance/HFM-PHASE2-INVARIANT-SUPERSESSION-REGISTER-v1.md" \
  expect_fail "J injected unregistered deselection" \
  "${AUTHORIZED_NODES[@]}" tests/test_phase2_observability.py::test_ac01_health_probe_ok

# F. ACTIVE replacement assertion proposed for deselection
HFM_SUPERSESSION_REGISTER="$ROOT/docs/governance/HFM-PHASE2-INVARIANT-SUPERSESSION-REGISTER-v1.md" \
  expect_fail "F active replacement deselection" \
  tests/test_phase2_media.py::test_p2_current_migration_head_0014

# Valid state: canonical verifier + canonical register + authorized nodes -> PASS
if ! HFM_VERIFIER="$ROOT/scripts/verify-invariant-supersessions.py" \
     HFM_SUPERSESSION_REGISTER="$ROOT/docs/governance/HFM-PHASE2-INVARIANT-SUPERSESSION-REGISTER-v1.md" \
     "$PRECHECK" "${AUTHORIZED_NODES[@]}" > /dev/null 2>&1; then
  echo "FAIL: valid state did not pass"
  exit 1
fi
echo "P0 adversarial: valid state -> PASS OK"

echo "RELEASE_GATE_PRECHECK_ADVERSARIAL=PASS"
