# services/registration/routes.py  (or your voter route file)

from fastapi import APIRouter, Depends, HTTPException # type: ignore
from sqlalchemy.orm import Session # type: ignore
from pydantic import BaseModel # type: ignore
from common.db import get_session
from common.models.models import Voter
from common.crypto.ballot_crypto import aes_gcm_encrypt  # add this
from common.crypto.kms import LocalKMS # type: ignore
# or import the exact functions you use for voter encryption  # type: ignore # whatever your func is called

router = APIRouter(tags=["registration"])

class VoterIn(BaseModel):
    name: str
    address: str
    dob: str         # ISO date
    eligibility: bool
    region: str

@router.post("/registration/voter", status_code=201)
def register_voter(payload: VoterIn, db: Session = Depends(get_session)):
    # eligibility is used for logic/validation only; not stored in this table
    if not payload.eligibility:
        raise HTTPException(status_code=422, detail="Voter not eligible")

    kms = LocalKMS()
    name_ct, name_nonce = aes_gcm_encrypt(payload.name.encode("utf-8"), kms)
    addr_ct, addr_nonce = aes_gcm_encrypt(payload.address.encode("utf-8"), kms)
    dob_ct, dob_nonce   = aes_gcm_encrypt(payload.dob.encode("utf-8"), kms)  # if dob is a date, str() it first

    v = Voter(
        name_enc=name_ct,
        address_enc=addr_ct,
        dob_enc=dob_ct,
        region=payload.region,
        # created_at will default server-side if your model sets it; otherwise set it here
    )
    db.add(v)
    db.commit()
    db.refresh(v)
    return {"id": v.id}