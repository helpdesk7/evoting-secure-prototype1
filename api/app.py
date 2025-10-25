from fastapi import FastAPI
from .routers import (
    auth,
    ballots,
    results,
    eligibility,
    results_backup,
    ballots_backup,
    backup,
    secure,
)
from .routers.ballots_backup import start_ballot_backup_scheduler
from api.middleware.anon_session import AnonSessionMiddleware

app = FastAPI(title="Secure E-Voting Prototype", version="0.1.0")


@app.get("/")
def root():
    return {"status": "ok", "docs": "/docs"}


@app.get("/healthz")
def health():
    return {"ok": True}


# ✅ Register anonymized session logging middleware (SR-08)
app.add_middleware(AnonSessionMiddleware)


# ✅ Include all routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(ballots.router, prefix="/api/ballots", tags=["ballots"])
app.include_router(results.router, prefix="/api/results", tags=["results"])
app.include_router(eligibility.router, prefix="/api/eligibility", tags=["eligibility"])
app.include_router(backup.router, prefix="/api/backup", tags=["backup"])
app.include_router(results_backup.router, prefix="/api/results/backup", tags=["results-backup"])
app.include_router(ballots_backup.router, prefix="/api/ballots/backup", tags=["ballots-backup"])
app.include_router(secure.router, prefix="/secure", tags=["secure"])

# ✅ Start scheduled ballot backup job
start_ballot_backup_scheduler()
