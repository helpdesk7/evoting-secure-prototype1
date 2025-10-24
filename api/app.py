from fastapi import FastAPI
from .routers import auth, ballots, voters, results  # ✅ added results

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
app.include_router(voters.router, prefix="/api/voters", tags=["voters"])
app.include_router(results.router, prefix="/api/results", tags=["results"])  # ✅ added this
