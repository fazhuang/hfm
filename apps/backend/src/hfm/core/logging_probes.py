"""Health/ready probes (P2-08 observability/release gates).

Deterministic probe functions with fail-closed semantics: readiness is only
true when every required dependency reports ready — never a false-healthy
state (P2-08-AC-01 negative). Lives under the authorized ``core/logging*``
module glob (sibling of ``core/logging.py``).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ProbeResult:
    """A probe outcome with a machine-readable status."""

    name: str
    status: str  # ok | not_ready
    detail: str


def probe_health() -> ProbeResult:
    """Liveness probe: the service process is up."""
    return ProbeResult(name="health", status="ok", detail="process up")


def probe_ready(
    *, dependencies_ready: bool, detail: str = "no external dependencies"
) -> ProbeResult:
    """Readiness probe: fail-closed — not ready unless every required
    dependency reports ready (no false-healthy state)."""
    if not dependencies_ready:
        return ProbeResult(name="ready", status="not_ready", detail="required dependency not ready")
    return ProbeResult(name="ready", status="ok", detail=detail)
