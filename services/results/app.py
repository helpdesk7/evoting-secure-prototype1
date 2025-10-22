# services/results/app.py
from __future__ import annotations

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI  # type: ignore

from common.db import engine, Base
from common.models.models import *  # noqa: F401,F403

# Import routers
from .routes import router as results_router
from .routes_audit import router as audit_router


# -------------------------------------------------------------
# Lifespan event: optional DB initialization for the results service
# -------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle handler for the Results service.
    Creates DB tables only when RUN_DB_MIGRATIONS=true (mainly for dev/demo).
    """
    if os.getenv("RUN_DB_MIGRATIONS", "false").lower() == "true":
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created by results service (RUN_DB_MIGRATIONS=true).")

    yield
    # Optional cleanup/shutdown logic can go here in the future.


# -------------------------------------------------------------
# FastAPI app definition
# -------------------------------------------------------------
app = FastAPI(
    title="Results Service",
    lifespan=lifespan,
    docs_url="/results/docs",
    openapi_url="/results/openapi.json",
    redoc_url=None,
)


# -------------------------------------------------------------
# Health & readiness probes
# -------------------------------------------------------------
@app.get("/healthz", tags=["system"])
def healthz():
    """Simple liveness probe."""
    return {"status": "ok"}


@app.get("/readyz", tags=["system"])
def readyz():
    """Readiness probe to confirm DB and app are running."""
    return {"db": "ok"}


# -------------------------------------------------------------
# Route registration
# -------------------------------------------------------------
# All results-related APIs are served under /results/*
app.include_router(results_router, prefix="/results")
app.include_router(audit_router, prefix="/results")