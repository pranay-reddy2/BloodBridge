import logging

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import text
from sqlalchemy.orm import Session

from .config import settings
from .db import get_db
from .metrics import register_inventory_collector
from .routers import donors, inventory, requests, units
from .schemas import MetaOut

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
log = logging.getLogger("bloodbridge")

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Blood donor registry, component inventory and hospital request fulfilment.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

Instrumentator(excluded_handlers=["/metrics", "/health", "/ready"]).instrument(app).expose(
    app, endpoint="/metrics", include_in_schema=False
)
register_inventory_collector()

app.include_router(donors.router)
app.include_router(units.router)
app.include_router(requests.router)
app.include_router(inventory.router)


@app.get("/", include_in_schema=False)
def root():
    return {"service": settings.app_name, "version": settings.app_version, "docs": "/docs"}


@app.get("/health", tags=["ops"])
def health():
    """Liveness: the process is up and serving HTTP. Deliberately does not touch the database,
    so a database outage does not make Kubernetes restart every backend pod."""
    return {"status": "UP"}


@app.get("/ready", tags=["ops"])
def ready(db: Session = Depends(get_db)):
    """Readiness: only accept traffic once the database is reachable."""
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        log.warning("readiness check failed: database unreachable", exc_info=True)
        return JSONResponse(status_code=503, content={"status": "NOT_READY", "database": "DOWN"})
    return {"status": "READY", "database": "UP"}


@app.get("/api/meta", response_model=MetaOut, tags=["ops"])
def meta():
    """Exposed under /api so the UI can show which build is serving it through the Ingress."""
    return MetaOut(service=settings.app_name, version=settings.app_version, environment=settings.environment)
