"""HFM backend application entrypoint.

Health/system endpoints plus Phase 1 v1 API namespaces (ADR-05).
"""

from fastapi import FastAPI

from hfm.api.health import router as health_router
from hfm.api.system import router as system_router
from hfm.api.v1.phase1 import (
    admin_router,
    auth_router,
    public_router,
    research_router,
)
from hfm.core.error_handlers import register_error_handlers
from hfm.middleware.request_id import RequestIDMiddleware

app = FastAPI(
    title="HFM",
    description="Huangfu Mi Humanities Digital Platform — backend",
    version="0.2.0",
)

app.add_middleware(RequestIDMiddleware)
register_error_handlers(app)
app.include_router(health_router)
app.include_router(system_router)
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(public_router)
app.include_router(research_router)
