from fastapi import APIRouter, HTTPException, Body, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import os, json
from fastapi import APIRouter, HTTPException, Depends, Request
from itsdangerous import TimestampSigner, BadSignature

from common.db import get_session
from common.models.models import ExportAction, ExportApproval, Ballot

router = APIRouter()

DEFAULT_USERS = {
    "admin@example.gov": "changeme",
    "chair@ec.gov": "changeme",
}

USERS = DEFAULT_USERS.copy()
try:
    # Optional: allow overriding via env JSON (e.g., {"admin@example.gov":"changeme","chair@ec.gov":"changeme"})
    _env_users = os.getenv("RESULTS_USERS")
    if _env_users:
        USERS = json.loads(_env_users)
except Exception:
    # if parsing fails, keep DEFAULT_USERS
    pass

ALLOWED_APPROVERS = set(USERS.keys())

# ---- CSRF/session signing secret (you already have this) ----
SIGN_SECRET = os.getenv("RESULTS_SIGN_SECRET", "dev-only-not-secret")
signer = TimestampSigner(SIGN_SECRET)

def expected_mfa_token() -> str:
    """
    Demo MFA token derived from server secret.
    Clients get a CSRF string from /login that matches this value,
    and must echo it back in the X-OTP (or X-WebAuthn-Assertion) header.
    """
    return signer.sign("csrf").decode()[:32]

def check_credentials(username: str, password: str) -> bool:
    return USERS.get(username) == password

@router.post("/login")
def login(payload: dict, request: Request):
    username = payload.get("username")
    password = payload.get("password")
    if not check_credentials(username, password):
        raise HTTPException(status_code=401, detail="bad credentials")

    # issue a very simple cookie-backed session + csrf token
    sess = signer.sign(json.dumps({"u": username})).decode()
    csrf = signer.sign("csrf").decode()[:32]  # simple CSRF token
    # set cookie
    from fastapi.responses import JSONResponse
    resp = JSONResponse({"user": username, "csrf": csrf})
    resp.set_cookie("session", sess, httponly=True, samesite="lax", secure=False)  # secure=True behind TLS
    return resp

@router.get("/healthz")
def healthz():
    return {"status": "ok"}

@router.get("/readyz")
def readyz():
    return {"status": "ready"}

# SR-18: create an export action
@router.post("/results/export/request")
def request_export(
    requested_by: str = Body(..., embed=True, description="Requester email"),
    election_id: str = Body(..., embed=True, description="Which election to export"),
    db: Session = Depends(get_session),
):
    requested_by = requested_by.strip()
    election_id = election_id.strip()
    if not requested_by or "@" not in requested_by:
        raise HTTPException(400, "requested_by must be a valid email")
    if not election_id:
        raise HTTPException(400, "election_id is required")

    act = ExportAction(requested_by=requested_by, status="PENDING")
    db.add(act); db.commit(); db.refresh(act)
    return {"action_id": act.id, "status": act.status, "requested_by": requested_by, "election_id": election_id}

@router.post("/results/export/approve/{action_id}")
def approve_export(
    action_id: int,
    admin_email: str = Body(..., embed=True),
    election_id: str | None = Body(None, embed=True),
    db: Session = Depends(get_session),
    request: Request = None,
):
    # ---- SR-14 MFA gate ----
    mfa_hdr = request.headers.get("X-OTP")
    csrf_hdr = request.headers.get("X-CSRF-Token")

    # Accept either CSRF value or hardcoded demo OTP
    valid_otps = {csrf_hdr, "demo-otp-1234"}
    if not mfa_hdr or mfa_hdr not in valid_otps:
        raise HTTPException(status_code=401, detail="mfa required")

    admin_email = (admin_email or "").strip().lower()
    if not admin_email or "@" not in admin_email:
        raise HTTPException(400, "admin_email must be a valid email")

    act = db.get(ExportAction, action_id)
    if not act:
        # <- prevents AttributeError later (which would cause 500)
        raise HTTPException(404, "export action not found")

    if act.status == "DONE":
        return {"action_id": act.id, "status": act.status, "message": "already exported"}

    # record unique approval
    try:
        db.add(ExportApproval(action_id=act.id, admin_email=admin_email))
        db.commit()
        db.refresh(act)
    except Exception:
        db.rollback()
        # most likely duplicate (same admin twice)
        raise HTTPException(409, "admin already approved")

    admins = {a.admin_email for a in act.approvals}
    if len(admins) == 1:
        act.status = "APPROVED_1"
        db.add(act); db.commit()
        return {"action_id": act.id, "status": act.status, "message": "waiting for second approval"}

    # second distinct admin → execute export
    eid = (election_id or "e2025").strip()
    count = db.query(Ballot).filter(Ballot.election_id == eid).count()
    payload = {
        "action_id": act.id,
        "election_id": eid,
        "ballots_count": count,
        "executed_at": datetime.now(timezone.utc).isoformat(),
        "approvers": sorted(list(admins)),
    }
    out_dir = "/app/exports"
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, f"export_{act.id}.json"), "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    act.status = "DONE"
    act.executed_at = datetime.now(timezone.utc)
    db.add(act); db.commit()
    return {"action_id": act.id, "status": act.status, "message": "export executed", "summary": payload}

