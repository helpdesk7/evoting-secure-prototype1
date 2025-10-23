# services/results/routes_audit.py
from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException # type: ignore
from sqlalchemy.orm import Session # type: ignore
from common.db import get_session
from common.models.models import BallotChain

router = APIRouter(tags=["audit"])

@router.get("/audit/tip")
def audit_tip(db: Session = Depends(get_session)):
    tip = db.query(BallotChain).order_by(BallotChain.id.desc()).first()
    if not tip:
        return {"height": 0, "tip_hash": "00" * 32, "ballot_id": None}
    return {
        "height": tip.id,
        "tip_hash": tip.curr_hash.hex() if isinstance(tip.curr_hash, bytes) else None,
        "ballot_id": tip.ballot_id,
    }

@router.get("/audit/verify")
def audit_verify(db: Session = Depends(get_session)):
    """
    Verifies append-only linkage:
    - record 1 must have prev_hash = 32 zero-bytes
    - for every i>1: chain[i].prev_hash == chain[i-1].curr_hash
    NOTE: This checks tamper-evidence of the chain structure. It doesn't
    re-compute curr_hash (which may depend on data not stored here).
    """
    chain = db.query(BallotChain).order_by(BallotChain.id.asc()).all()
    if not chain:
        return {"ok": True, "height": 0, "breaks": []}

    breaks = []
    zero32 = b"\x00" * 32
    if chain[0].prev_hash != zero32:
        breaks.append({"at_id": chain[0].id, "reason": "first.prev_hash != 0x00..00"})

    for i in range(1, len(chain)):
        if chain[i].prev_hash != chain[i-1].curr_hash:
            breaks.append({
                "at_id": chain[i].id,
                "expected_prev": chain[i-1].curr_hash.hex(),
                "actual_prev": chain[i].prev_hash.hex(),
            })

    return {"ok": len(breaks) == 0, "height": chain[-1].id, "breaks": breaks}