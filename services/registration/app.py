# services/registration/app.py
from fastapi import FastAPI # type: ignore
from contextlib import asynccontextmanager
import os

from common.db import engine, Base
from .routes import router


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

# keep your existing imports and app setup

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

# add this alias so nginx path works too
@app.get("/registration/healthz")
def healthz_alias():
    return {"status": "ok"}


app.include_router(router, prefix="/registration")
