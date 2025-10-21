# services/registration/app.py
from fastapi import FastAPI # type: ignore
from contextlib import asynccontextmanager
import os

from common.db import engine, Base

# 🔴 ADD THIS LINE to ensure all models (Voter, UserAuth, etc.) are imported
import common.models.models  # noqa: F401

from .routes import router
from .routes_auth import router as auth_router  # make sure this import stays

@asynccontextmanager
async def lifespan(app: FastAPI):
    if os.getenv("RUN_DB_MIGRATIONS", "false").lower() == "true":
        Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title="Registration Service",
    lifespan=lifespan,
    docs_url="/registration/docs",
    openapi_url="/registration/openapi.json",
    redoc_url=None,
)

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.get("/registration/healthz")
def healthz_alias():
    return {"status": "ok"}

app.include_router(router, prefix="/registration")
app.include_router(auth_router, prefix="/registration")