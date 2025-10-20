from fastapi import FastAPI # type: ignore
from contextlib import asynccontextmanager
from common.db import engine, Base
from common.models.models import *  # noqa: F401,F403
from .routes import router
import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Results service lifespan handler.
    Only runs DB migrations if RUN_DB_MIGRATIONS=true (usually FALSE here).
    """
    if os.getenv("RUN_DB_MIGRATIONS", "false").lower() == "true":
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created by results service (RUN_DB_MIGRATIONS=true).")
    yield
    # optional: shutdown/cleanup goes here


app = FastAPI(
    title="Results Service",
    lifespan=lifespan,
    docs_url="/results/docs",
    openapi_url="/results/openapi.json",
    redoc_url=None,
)


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/readyz")
def readyz():
    return {"db": "ok"}


# All results routes live under /results/*
app.include_router(router, prefix="/results")
