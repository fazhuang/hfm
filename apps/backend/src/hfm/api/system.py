"""System information endpoints (migrated Batch 3 asset — ADAPT).

Source: HFB `apps/backend/app/api/version.py` @ `03755b5`.
Adapted:
  - replaced HFB `app.core.config.settings` dependency with module-level
    constants (VERSION from the package __version__, ENVIRONMENT from the
    HFM_ENV env var, PROJECT_NAME = "HFM");
  - strict typing (`dict[str, Any]`).
No HFB-specific configuration assumption remains.
"""

import os
from typing import Any

from fastapi import APIRouter

from hfm import __version__
from hfm.utils.response import api_response

router = APIRouter(tags=["system"])

PROJECT_NAME = "HFM"
ENVIRONMENT = os.environ.get("HFM_ENV", "development")


@router.get("/version")
async def get_version() -> dict[str, Any]:
    """Return application version and environment info."""
    return api_response(
        data={
            "version": __version__,
            "environment": ENVIRONMENT,
            "project": PROJECT_NAME,
        }
    )


@router.get("/live")
async def liveness_check() -> dict[str, Any]:
    """Liveness probe — minimal check that the process is alive."""
    return api_response(data={"alive": True}, message="Process is alive")


@router.get("/config")
async def public_config() -> dict[str, Any]:
    """Return public (non-sensitive) configuration."""
    return api_response(
        data={
            "project_name": PROJECT_NAME,
            "version": __version__,
            "environment": ENVIRONMENT,
        }
    )
