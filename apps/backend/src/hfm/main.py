"""HFM backend application entrypoint (skeleton).

Only health endpoints exist in this phase. No business API is provided.
"""

from fastapi import FastAPI

from hfm.api.health import router as health_router

app = FastAPI(
    title="HFM",
    description="Huangfu Mi Humanities Digital Platform — backend skeleton",
    version="0.1.0",
)

app.include_router(health_router)
