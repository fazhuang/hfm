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
# The three deselected assertions are governed SUPERSEDED Class H entries in
# HFM-PHASE2-INVARIANT-SUPERSESSION-REGISTER-v1.md (ASN-P200-MIG-0013-HEAD,
# ASN-P200-MIG-NO0014, ASN-P1RW-MIG-0013-HEAD). Their current replacement
# (ASN-P205-MIG-0014-HEAD -> test_p2_current_migration_head_0014) runs in the
# suite; historical replay is verified by the supersession verifier. Exact
# node-id deselection only — no blanket or filename-based exclusion.
(cd "$ROOT/apps/backend" && source .venv/bin/activate && python -m pytest -q \
  --deselect tests/test_phase1_research_workspace.py::test_migration_0013_upgrade_downgrade_upgrade_single_head \
  --deselect tests/test_phase2_guardrails.py::test_frozen_boundary_states \
  --deselect tests/test_phase2_guardrails.py::test_migration_invariant) || FAILURES=$((FAILURES + 1))

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
