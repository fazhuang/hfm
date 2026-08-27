"""HFM backend application entrypoint (skeleton).

Only health endpoints exist in this phase. No business API is provided.
"""

from fastapi import FastAPI

from hfm.api.health import router as health_router
from hfm.api.system import router as system_router
from hfm.core.error_handlers import register_error_handlers
from hfm.middleware.request_id import RequestIDMiddleware

app = FastAPI(
    title="HFM",
    description="Huangfu Mi Humanities Digital Platform — backend skeleton",
    version="0.1.0",
)

app.add_middleware(RequestIDMiddleware)
register_error_handlers(app)
app.include_router(health_router)
app.include_router(system_router)
