# services/results/app.py
from fastapi import FastAPI  # type: ignore
from contextlib import asynccontextmanager
from common.db import engine, Base
from common.models.models import *  # noqa
from .routes import router
from .routes_audit import router as audit_router
from .routes_signing import router as signing_router
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    if os.getenv("RUN_DB_MIGRATIONS", "false").lower() == "true":
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created by results service (RUN_DB_MIGRATIONS=true).")
    yield

app = FastAPI(
    title="Results Service",
    lifespan=lifespan,
    docs_url="/results/docs",
    openapi_url="/results/openapi.json",
    redoc_url=None,
)

@app.get("/healthz")
def healthz(): return {"status": "ok"}

@app.get("/readyz")
def readyz(): return {"db": "ok"}

app.include_router(router,        prefix="/results")
app.include_router(audit_router,  prefix="/results")
app.include_router(signing_router, prefix="/results")   # 🔗 add signing endpoints