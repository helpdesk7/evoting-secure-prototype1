"""
api/routers/eligibility.py
Implements real eligibility verification logic (SR-04, Commit 12).
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from common.db import get_db
from common.models.voter import Voter

router = APIRouter(tags=["eligibility"])


@router.get("/check")
def check_eligibility(
    email: str = Query(..., description="Voter's email address"),
    db: Session = Depends(get_db),
):
    """
    Checks voter eligibility by querying the voter registry.
    Returns eligibility status and division.
    """
    voter = db.query(Voter).filter(Voter.email == email).first()

    if not voter:
        raise HTTPException(status_code=404, detail="Voter not found in registry")

    if not voter.is_active:
        return {
            "email": email,
            "eligible": False,
            "reason": "Inactive or suspended registration",
        }

    return {
        "email": email,
        "eligible": True,
        "division": voter.division,
        "reason": "Voter found and active",
    }
