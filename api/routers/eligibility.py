"""
api/routers/eligibility.py
Implements the Eligibility Verification API (SR-04, Commit 10).
Currently provides a mock eligibility check.
"""

from fastapi import APIRouter, Query

router = APIRouter()

@router.get("/check")
def check_eligibility(email: str = Query(..., description="Voter's email address")):
    """
    Mock eligibility verification endpoint.
    Later commits will integrate real voter database logic.
    """
    if email.endswith("@example.com"):
        return {"email": email, "eligible": True, "reason": "Registered demo user"}
    else:
        return {"email": email, "eligible": False, "reason": "Not found in registry"}
