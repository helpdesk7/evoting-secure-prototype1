from fastapi import FastAPI
from .routers import auth, ballots  # add ballots

app = FastAPI(title="Secure E-Voting Prototype", version="0.1.0")

# Existing routes
app.include_router(auth.router, prefix="/auth", tags=["auth"])

# New ballots route
app.include_router(ballots.router, prefix="/api/ballots", tags=["ballots"])


