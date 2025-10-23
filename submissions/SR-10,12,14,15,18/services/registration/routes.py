from fastapi import APIRouter, HTTPException, Depends, Body
from datetime import datetime, timedelta, timezone
import secrets
from sqlalchemy.orm import Session
from common.db import get_session
from common.models.models import BallotToken

router = APIRouter()

@router.get("/healthz")
def healthz():
    """
    Service-scoped health endpoint for Registration microservice.
    """
    return {"status": "ok"}

@router.post("/eligibility/check")
def eligibility_check(voter_ref: str = Body(..., embed=True)):
    if not voter_ref.strip():
        raise HTTPException(400, "invalid voter ref")
    return {"eligible": True, "voter_ref": voter_ref}

@router.post("/ballot/token")
def issue_token(
    voter_ref: str = Body(..., embed=True),
    minutes_valid: int = Body(10, embed=True),
    db: Session = Depends(get_session),
):
    if not voter_ref.strip():
        raise HTTPException(400, "invalid voter ref")
    token = secrets.token_hex(32)  # 64-hex
    exp = datetime.now(timezone.utc) + timedelta(minutes=minutes_valid)
    db.add(BallotToken(token=token, voter_ref=voter_ref, exp_at=exp))
    db.commit()
    return {"otbt": token, "exp": exp.isoformat()}
