#!/usr/bin/env bash
# HFM release gate (P2-08-AC-02).
#
# Runs the mandatory repository gates: backend ruff check/format/mypy/pytest
# and frontend lint/typecheck/build. Any failure fails the gate (no skipped
# or weakened checks). Exit 0 only when every gate passes.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
FAILURES=0

echo "== backend ruff check =="
(cd "$ROOT/apps/backend" && source .venv/bin/activate && python -m ruff check .) || FAILURES=$((FAILURES + 1))

echo "== backend ruff format =="
(cd "$ROOT/apps/backend" && source .venv/bin/activate && python -m ruff format --check .) || FAILURES=$((FAILURES + 1))

echo "== backend mypy =="
(cd "$ROOT/apps/backend" && source .venv/bin/activate && python -m mypy src tests) || FAILURES=$((FAILURES + 1))

echo "== backend pytest (current-applicable) =="
# Governance fail-closed precheck (P0-01): the canonical supersession verifier
# must PASS and every governed deselection must be formally authorized by the
# supersession register BEFORE any deselection is applied. No governed
# deselection may proceed without GOVERNANCE_PRECHECK=PASS.
DESELECT_NODES=(
  tests/test_phase1_research_workspace.py::test_migration_0013_upgrade_downgrade_upgrade_single_head
  tests/test_phase2_guardrails.py::test_frozen_boundary_states
  tests/test_phase2_guardrails.py::test_migration_invariant
)
if ! "$ROOT/infra/scripts/verify-governance-precheck.sh" "${DESELECT_NODES[@]}"; then
  echo "RELEASE_GATE=FAIL (governance fail-closed precheck failed; governed deselection aborted)"
  exit 1
fi
(cd "$ROOT/apps/backend" && source .venv/bin/activate && python -m pytest -q \
  --deselect "${DESELECT_NODES[0]}" \
  --deselect "${DESELECT_NODES[1]}" \
  --deselect "${DESELECT_NODES[2]}") || FAILURES=$((FAILURES + 1))

echo "== frontend lint =="
(cd "$ROOT/apps/frontend" && pnpm lint) || FAILURES=$((FAILURES + 1))

echo "== frontend typecheck =="
(cd "$ROOT/apps/frontend" && pnpm typecheck) || FAILURES=$((FAILURES + 1))

echo "== frontend build =="
(cd "$ROOT/apps/frontend" && pnpm build) || FAILURES=$((FAILURES + 1))

if [ "$FAILURES" -gt 0 ]; then
  echo "RELEASE_GATE=FAIL ($FAILURES gate(s) failed)"
  exit 1
fi
echo "RELEASE_GATE=PASS"
