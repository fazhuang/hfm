#!/usr/bin/env bash
# HFM health/ready probe check (P2-08-AC-01).
# Executes the deterministic probes; exits non-zero when readiness fails.
set -euo pipefail

BACKEND="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)/apps/backend"

"$BACKEND/.venv/bin/python" - <<'PY'
from hfm.core.logging_probes import probe_health, probe_ready

health = probe_health()
print(f"health={health.status} ({health.detail})")
ready = probe_ready(dependencies_ready=True, detail="all required dependencies ok")
print(f"ready={ready.status} ({ready.detail})")
if health.status != "ok" or ready.status != "ok":
    raise SystemExit(1)
PY
echo "HEALTH_CHECK=PASS"
