from fastapi import FastAPI
from contextlib import asynccontextmanager
from common.db import engine, Base
from common.models.models import *  # noqa: F401,F403
from .routes import router
import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Voting service lifespan handler.
    Only runs DB migrations if RUN_DB_MIGRATIONS=true (usually FALSE here).
    """
    if os.getenv("RUN_DB_MIGRATIONS", "false").lower() == "true":
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created by voting service (RUN_DB_MIGRATIONS=true).")
    yield
    # optional: shutdown/cleanup goes here


app = FastAPI(
    title="Voting Service",
    lifespan=lifespan,
    docs_url="/voting/docs",
    openapi_url="/voting/openapi.json",
    redoc_url=None,
)


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/readyz")
def readyz():
    # In a fuller version you can try a short DB query here.
    return {"db": "ok"}


# All voting routes live under /voting/*
app.include_router(router, prefix="/voting")
