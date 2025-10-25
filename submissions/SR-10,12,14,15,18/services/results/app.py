# services/results/app.py
from fastapi import FastAPI, Response, HTTPException
from contextlib import asynccontextmanager
from pydantic import BaseModel
import os, secrets

from common.db import engine, Base
from common.models.models import *  # noqa: F401,F403
from .routes import router

# --- SR-15 helpers (minimal inline version; you can split into session.py later) ---
from itsdangerous import TimestampSigner, BadSignature, SignatureExpired

SESSION_COOKIE = "evote_sess"
CSRF_HEADER = "X-CSRF-Token"

def _sess_secret() -> bytes:
    key = os.getenv("RESULTS_SESSION_SECRET", "")
    if len(key) != 64:
        # 32 bytes hex-encoded = 64 chars
        raise RuntimeError("RESULTS_SESSION_SECRET must be 64 hex chars")
    return bytes.fromhex(key)

def _sess_ttl() -> int:
    try:
        return int(os.getenv("RESULTS_SESSION_TTL_MIN", "30")) * 60
    except Exception:
        return 1800

def _sign_session(username: str, roles: list[str], csrf: str) -> str:
    payload = f"{username}|{csrf}|{','.join(roles)}"
    signer = TimestampSigner(_sess_secret())
    return signer.sign(payload.encode()).decode()

def _verify_session(token: str) -> tuple[str, str, list[str]]:
    signer = TimestampSigner(_sess_secret())
    raw = signer.unsign(token, max_age=_sess_ttl()).decode()
    username, csrf, roles_csv = raw.split("|", 2)
    roles = [r for r in roles_csv.split(",") if r]
    return username, csrf, roles
# --- end SR-15 helpers ---


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


# --- keep your existing health/ready endpoints exactly as-is ---
@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.get("/readyz")
def readyz():
    return {"db": "ok"}


def _load_users() -> dict[str, str]:
    """
    Load username -> password map from RESULTS_USERS env (JSON).
    Fallback: two demo admins for local dev.
    """
    raw = os.getenv("RESULTS_USERS")
    if raw:
        try:
            return json.loads(raw)
        except Exception as e:
            print(f"⚠️ RESULTS_USERS JSON parse error: {e}; using defaults")
    return {
        "admin@example.gov": "changeme",
        "chair@ec.gov": "changeme",
    }

USERS = _load_users()

def _check_credentials(username: str, password: str) -> bool:
    return USERS.get(username) == password

# --- replace your existing /results/login endpoint with this one ---
class LoginReq(BaseModel):
    username: str
    password: str

class LoginResp(BaseModel):
    user: str
    csrf: str

@app.post("/results/login", response_model=LoginResp)
def login(req: LoginReq, resp: Response):
    """
    SR-14/SR-18: Admin login. Validates against RESULTS_USERS (JSON) or demo defaults.
    """
    if not _check_credentials(req.username, req.password):
        raise HTTPException(status_code=401, detail="bad credentials")

    csrf = secrets.token_hex(16)
    sess = _sign_session(username=req.username, roles=["admin"], csrf=csrf)

    secure_flag = os.getenv("DEV_INSECURE_COOKIES", "false").lower() != "true"
    resp.set_cookie(
        key=SESSION_COOKIE,
        value=sess,
        httponly=True,
        secure=secure_flag,
        samesite="strict",
        path="/",
        max_age=_sess_ttl(),
    )
    return {"user": req.username, "csrf": csrf}

@app.post("/results/logout")
def logout(resp: Response):
    """Clear the admin session cookie."""
    resp.delete_cookie(SESSION_COOKIE, path="/")
    return {"ok": True}


# All results routes live under /results/*
app.include_router(router, prefix="/results")
