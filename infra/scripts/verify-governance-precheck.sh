#!/usr/bin/env bash
# HFM governance fail-closed precheck (P0-01 correction).
#
# Before any governed test deselection may proceed, this precheck MUST pass:
#   1. the canonical supersession verifier executes successfully and emits the
#      formal signal SUPERSESSION_REGISTER=PASS (exit 0 required);
#   2. the supersession register yields a non-empty set of formally superseded
#      Class H test scopes;
#   3. every governed deselection node is covered by a superseded Class H
#      REPLAY_TEST scope (exact node match or file-scope prefix);
#   4. every governed deselection node is disjoint from ACTIVE
#      CURRENT_REPLACEMENT_TEST values (no active assertion deselected).
#
# Any failure (verifier missing/failing/non-PASS, malformed register, missing
# mapping, unauthorized or injected deselection, active-assertion deselection)
# FAILS CLOSED: exit non-zero and no governed deselection may proceed.
#
# Env overrides (test seams only; defaults are the canonical paths):
#   HFM_VERIFIER, HFM_SUPERSESSION_REGISTER
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
VERIFIER="${HFM_VERIFIER:-$ROOT/scripts/verify-invariant-supersessions.py}"
REGISTER="${HFM_SUPERSESSION_REGISTER:-$ROOT/docs/governance/HFM-PHASE2-INVARIANT-SUPERSESSION-REGISTER-v1.md}"

fail() {
  echo "GOVERNANCE_PRECHECK=FAIL ($1)"
  exit 1
}

# 1. Canonical verifier must exist, execute, and emit the formal PASS signal.
if [ ! -f "$VERIFIER" ]; then
  fail "governance verifier unavailable: $VERIFIER"
fi
verifier_out="$("$VERIFIER" 2>&1)" || fail "governance verifier failed (exit $?)"
if ! echo "$verifier_out" | grep -q "SUPERSESSION_REGISTER=PASS"; then
  fail "governance verifier did not produce formal PASS signal"
fi

# 2. Extract formally superseded Class H REPLAY_TEST scopes from the register.
superseded_scopes="$(
  python3 - "$REGISTER" <<'PY'
import re, sys
text = open(sys.argv[1], encoding="utf-8").read()
scopes = set()
for sec in re.split(r"^### ", text, flags=re.M)[1:]:
    cls = re.search(r"^CLASS: (\w+)", sec, re.M)
    status = re.search(r"^STATUS: (\w+)", sec, re.M)
    replay = re.search(r"^REPLAY_TEST: (\S+)", sec, re.M)
    if status and cls and replay:
        if status.group(1) == "SUPERSEDED" and cls.group(1) == "H" and replay.group(1) != "N/A":
            scopes.add(replay.group(1))
for s in sorted(scopes):
    print(s)
PY
)" || fail "supersession register malformed (unparseable)"
if [ -z "$superseded_scopes" ]; then
  fail "no formally superseded Class H test scopes found (governed node mapping missing)"
fi

# 3. Every governed deselection must be covered by a superseded scope.
for node in "$@"; do
  authorized=0
  while IFS= read -r scope; do
    if [ "$node" = "$scope" ] || [[ "$node" == "$scope::"* ]]; then
      authorized=1
    fi
  done <<< "$superseded_scopes"
  if [ "$authorized" -ne 1 ]; then
    fail "deselection not formally authorized by supersession register: $node"
  fi
done

# 4. Governed deselections must be disjoint from ACTIVE replacement tests.
active_replacements="$(
  python3 - "$REGISTER" <<'PY'
import re, sys
text = open(sys.argv[1], encoding="utf-8").read()
reps = set()
for sec in re.split(r"^### ", text, flags=re.M)[1:]:
    status = re.search(r"^STATUS: (\w+)", sec, re.M)
    repl = re.search(r"^CURRENT_REPLACEMENT_TEST: (\S+)", sec, re.M)
    if status and repl and status.group(1) == "ACTIVE" and repl.group(1) != "N/A":
        reps.add(repl.group(1).removeprefix("apps/backend/"))
for r in sorted(reps):
    print(r)
PY
)"
for node in "$@"; do
  if echo "$active_replacements" | grep -qxF "$node"; then
    fail "active replacement assertion proposed for deselection: $node"
  fi
done

echo "GOVERNANCE_PRECHECK=PASS (supersession register verified; governed deselections authorized)"
