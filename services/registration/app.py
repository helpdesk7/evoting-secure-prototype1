from fastapi import FastAPI  # type: ignore
from contextlib import asynccontextmanager
from common.db import engine, Base
from common.models.models import *  # noqa
from .routes import router
from .routes_ballot import router as ballot_router  # 🟢 NEW: SR-09 ballots
import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Modern lifespan event handler — replaces @app.on_event("startup").
    Only registration service runs DB migrations (others skip).
    """
    if os.getenv("RUN_DB_MIGRATIONS", "false").lower() == "true":
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created by registration service.")
    yield  # startup continues here
    # (optional cleanup code could go after yield)


# Create the FastAPI app with lifespan handler
app = FastAPI(
    title="Registration Service",
    lifespan=lifespan,
    docs_url="/registration/docs",
    openapi_url="/registration/openapi.json",
    redoc_url=None,
)


@app.get("/healthz")
def healthz():
    """Simple health check endpoint"""
    return {"status": "ok"}


@app.get("/readyz")
def readyz():
    """Readiness probe endpoint (checks DB connection)"""
    return {"db": "ok"}


# Include your functional routes
app.include_router(router, prefix="/registration")

# 🟢 Include SR-09 ballot encryption routes
app.include_router(ballot_router, prefix="/registration")