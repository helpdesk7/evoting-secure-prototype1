# services/registration/routes.py
from fastapi import APIRouter, Depends, HTTPException # type: ignore
from pydantic import BaseModel # type: ignore
from sqlalchemy.orm import Session # type: ignore
from datetime import date
from common.db import get_session
from common.models.models import Voter
from cryptoutils.encryption import encrypt_voter_data  # takes ONE dict

router = APIRouter()

class VoterIn(BaseModel):
    name: str
    address: str
    dob: date
    eligibility: bool
    region: str | None = None

@router.post("/registration/voter", response_model=str, status_code=201)
def register_voter(payload: VoterIn, db: Session = Depends(get_session)) -> str:
    try:
        # Build the dict expected by encrypt_voter_data
        data = {
            "name": payload.name,
            "address": payload.address,
            "dob": payload.dob.isoformat(),
            "eligibility": payload.eligibility,
            "region": payload.region or "",
        }

        enc = encrypt_voter_data(data)  # <-- ONE dict argument

        # Save encrypted fields
        voter = Voter(
            name_enc=enc["name_enc"],
            address_enc=enc["address_enc"],
            dob_enc=enc["dob_enc"],
            eligibility_enc=enc["eligibility_enc"],
            region=data["region"],
        )
        db.add(voter)
        db.commit()
        db.refresh(voter)
        return str(voter.id)

    except Exception as e:
        db.rollback()
        print("register_voter error:", repr(e))
        raise HTTPException(status_code=500, detail="internal error")
