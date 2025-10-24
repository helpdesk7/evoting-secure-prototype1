
from fastapi import APIRouter, HTTPException
from ..models.ballot import Ballot

router = APIRouter()
VALID_CANDIDATES = {"c1", "c2", "c3"}

@router.post("", status_code=201)
def submit_ballot(b: Ballot):
    # validate candidate IDs
    for r in b.rankings:
        if r.candidateId not in VALID_CANDIDATES:
            raise HTTPException(
                status_code=400,
                detail={"code": "unknown_candidate", "detail": r.candidateId}
            )
    return {"ok": True}

