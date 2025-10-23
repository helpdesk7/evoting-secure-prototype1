from __future__ import annotations
from fastapi import Depends, HTTPException, Header, Query # type: ignore
from sqlalchemy.orm import Session # type: ignore
from datetime import datetime, timezone
from common.db import get_session
from common.models.models import BallotToken

def require_valid_otbt(
    x_otbt: str | None = Header(default=None, alias="X-OTBT"),
    otbt_q: str | None = Query(default=None, alias="otbt"),
    db: Session = Depends(get_session),
) -> BallotToken:
    token = x_otbt or otbt_q
    if not token:
        raise HTTPException(status_code=422, detail="otbt missing")

    bt = db.query(BallotToken).filter(BallotToken.token == token).first()
    if not bt:
        raise HTTPException(status_code=401, detail="invalid token")

    now = datetime.now(timezone.utc)
    if bt.exp_at and bt.exp_at < now:
        raise HTTPException(status_code=401, detail="token expired")
    if bt.consumed_at is not None:
        raise HTTPException(status_code=401, detail="token already used")

    return bt

def consume_otbt(bt: BallotToken, db: Session) -> None:
    bt.consumed_at = datetime.now(timezone.utc)
    db.add(bt)
    # commit happens in the route
