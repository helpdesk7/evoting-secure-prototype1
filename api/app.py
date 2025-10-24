from fastapi import FastAPI
from .routers import auth, ballots, results, results_backup, ballots_backup  # ✅ added results
from .routers.ballots_backup import start_ballot_backup_scheduler


app = FastAPI(title="Secure E-Voting Prototype", version="0.1.0")


@app.get("/")
def root():
    return {"status": "ok", "docs": "/docs"}

@app.get("/healthz")
def health():
    return {"ok": True}

# Routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(ballots.router, prefix="/api/ballots", tags=["ballots"])
# app.include_router(voters.router, prefix="/api/voters", tags=["voters"])
app.include_router(results.router, prefix="/api/results", tags=["results"])  
app.include_router(results_backup.router, prefix="/api/results/backup", tags=["results-backup"]) # ✅ added this
app.include_router(ballots_backup.router, prefix="/api/ballots/backup", tags=["ballots-backup"]) # ✅ added this


start_ballot_backup_scheduler()
