# services/registration/routes_ballot.py
from __future__ import annotations

from hashlib import sha256
from fastapi import APIRouter, Depends, HTTPException, Path  # type: ignore
from pydantic import BaseModel                                # type: ignore
from sqlalchemy.orm import Session                            # type: ignore

from common.db import get_session
from common.models.models import Ballot, BallotChain
from common.crypto.kms import LocalKMS                        # type: ignore
from common.crypto.ballot_crypto import encrypt_ballot

router = APIRouter(tags=["ballots"])


class BallotSubmitRequest(BaseModel):
    election_id: str
    ballot: dict
    voter_hash: str  # not stored; used only in the chain hash


@router.post("/ballot/submit", status_code=201)
def submit_ballot(payload: BallotSubmitRequest, db: Session = Depends(get_session)):
    # 1) Encrypt with AES-GCM (key provided via KMS / env)
    kms = LocalKMS()
    ciphertext, nonce = encrypt_ballot(payload.ballot, kms)

    # Deterministic receipt from ciphertext (includes tag)
    receipt = sha256(ciphertext).hexdigest()

    # 2) Persist the encrypted ballot (NO voter_hash column!)
    rec = Ballot(
        election_id=payload.election_id,
        ciphertext=ciphertext,
        nonce=nonce,
        receipt=receipt,
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)

    # 3) Append to audit chain (prev = 00..00 when empty)
    prev = db.query(BallotChain).order_by(BallotChain.id.desc()).first()
    prev_bytes = prev.curr_hash if prev else b"\x00" * 32
    curr = sha256(
        prev_bytes + bytes.fromhex(receipt) + payload.voter_hash.encode("utf-8")
    ).digest()

    db.add(BallotChain(ballot_id=rec.id, prev_hash=prev_bytes, curr_hash=curr))
    db.commit()

    # 4) Return the receipt to the client
    return {"receipt": receipt}


@router.get("/ballot/receipt/{receipt}")
def get_by_receipt(
    receipt: str = Path(..., min_length=64, max_length=64),
    db: Session = Depends(get_session),
):
    rec = db.query(Ballot).filter(Ballot.receipt == receipt).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Receipt not found")

    return {
        "election_id": rec.election_id,
        "created_at": rec.created_at.isoformat() if hasattr(rec, "created_at") else None,
        "ciphertext_bytes": len(rec.ciphertext or b""),
        "nonce_hex": rec.nonce.hex() if isinstance(rec.nonce, bytes) else None,
        "receipt": rec.receipt,
    }


@router.get("/ballot/chain/tip")
def chain_tip(db: Session = Depends(get_session)):
    tip = db.query(BallotChain).order_by(BallotChain.id.desc()).first()
    if not tip:
        return {"height": 0, "tip_hash": "00" * 32}
    return {
        "height": tip.id,
        "tip_hash": tip.curr_hash.hex() if isinstance(tip.curr_hash, bytes) else None,
        "ballot_id": tip.ballot_id,
    }