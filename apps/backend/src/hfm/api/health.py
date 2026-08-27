"""Health endpoints for the HFM backend skeleton.

Only /health and /ready are exposed. No external dependencies are required:
the skeleton phase has no database, cache, object store, or message bus.
"""

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    """Liveness probe: the service process is up."""
    return {"status": "ok", "service": "hfm"}


@router.get("/ready")
def ready() -> dict[str, str]:
    """Readiness probe: skeleton has no external dependencies yet."""
    return {"status": "ready", "service": "hfm"}
