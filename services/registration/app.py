from fastapi import FastAPI # type: ignore
from contextlib import asynccontextmanager
from common.db import Base, engine

# ✅ Import models & routes
import common.models.models  # ensures tables are registered
from services.registration import routes  # ensures endpoints are loaded


@asynccontextmanager
async def lifespan(app: FastAPI):
    import os
    if os.getenv("RUN_DB_MIGRATIONS", "false").lower() == "true":
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created.")
    yield


# ✅ Make sure docs and openapi URLs are set
app = FastAPI(
    lifespan=lifespan,
    docs_url="/registration/docs",
    openapi_url="/registration/openapi.json",
    title="Registration Service",
    version="0.1.0"
)

# ✅ Include the router
app.include_router(routes.router, prefix="/registration", tags=["Registration"])