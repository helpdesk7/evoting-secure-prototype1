# services/registration/routes_ballot.py
from __future__ import annotations

from hashlib import sha256
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path  # type: ignore
from pydantic import BaseModel                                # type: ignore
from sqlalchemy.orm import Session                            # type: ignore

from common.db import get_session
from common.models.models import Ballot, BallotChain
from common.crypto.kms import LocalKMS                        # type: ignore
from common.crypto.ballot_crypto import encrypt_ballot

router = APIRouter(tags=["ballots"])


# ---------- Schemas ----------
class BallotSubmitRequest(BaseModel):
    election_id: str
    ballot: dict
    voter_hash: str  # not stored; used only to derive the chain link hash


# ---------- Routes ----------
@router.post("/ballot/submit", status_code=201)
def submit_ballot(payload: BallotSubmitRequest, db: Session = Depends(get_session)):
    # 1) Encrypt the ballot (AES-GCM via LocalKMS)
    kms = LocalKMS()
    ciphertext, nonce = encrypt_ballot(payload.ballot, kms)

    # Deterministic receipt derived from ciphertext
    receipt = sha256(ciphertext).hexdigest()

    # 2) Persist the encrypted ballot (no voter_hash column)
    rec = Ballot(
        election_id=payload.election_id,
        ciphertext=ciphertext,
        nonce=nonce,
        receipt=receipt,
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)

    # 3) Append to audit chain (prev = zero32 for genesis)
    zero32 = b"\x00" * 32
    prev = db.query(BallotChain).order_by(BallotChain.id.desc()).first()
    prev_bytes = prev.curr_hash if prev else zero32
    curr = sha256(
        prev_bytes + bytes.fromhex(receipt) + payload.voter_hash.encode("utf-8")
    ).digest()

    db.add(BallotChain(ballot_id=rec.id, prev_hash=prev_bytes, curr_hash=curr))
    db.commit()

    # 4) Return receipt
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
        "nonce_hex": rec.nonce.hex() if isinstance(rec.nonce, (bytes, bytearray)) else None,
        "receipt": rec.receipt,
    }


@router.get("/ballot/chain/tip")
def chain_tip(db: Session = Depends(get_session)):
    tip = db.query(BallotChain).order_by(BallotChain.id.desc()).first()
    if not tip:
        return {"height": 0, "tip_hash": "00" * 32, "ballot_id": None}
    return {
        "height": tip.id,
        "tip_hash": tip.curr_hash.hex()
        if isinstance(tip.curr_hash, (bytes, bytearray))
        else None,
        "ballot_id": tip.ballot_id,
    }


@router.get("/ballot/chain/verify")
def verify_chain(db: Session = Depends(get_session)):
    """
    Tamper-detection: validates the append-only chain structure.
    Since voter_hash is not stored, we verify:
      - genesis prev_hash is zero32,
      - each prev_hash equals the previous curr_hash,
      - hashes are present and 32 bytes,
      - created_at exists and is non-decreasing.
    """
    recs: List[BallotChain] = db.query(BallotChain).order_by(BallotChain.id.asc()).all()

    errors: List[str] = []
    zero32 = b"\x00" * 32

    if not recs:
        return {"ok": True, "height": 0, "tip_hash": None, "errors": [], "message": "No chain records."}

    expected_prev = zero32
    last_ts = None

    for i, r in enumerate(recs, start=1):
        # shape checks
        if not isinstance(r.prev_hash, (bytes, bytearray)) or len(r.prev_hash or b"") != 32:
            errors.append(f"id={r.id}: prev_hash missing or wrong length")
        if not isinstance(r.curr_hash, (bytes, bytearray)) or len(r.curr_hash or b"") != 32:
            errors.append(f"id={r.id}: curr_hash missing or wrong length")
        if r.created_at is None:
            errors.append(f"id={r.id}: created_at is NULL")

        # link continuity
        if r.prev_hash != expected_prev:
            if i == 1 and r.prev_hash != zero32:
                errors.append(f"id={r.id}: genesis prev_hash is not zero32")
            else:
                exp = expected_prev.hex() if expected_prev else None
                got = r.prev_hash.hex() if r.prev_hash else None
                errors.append(f"id={r.id}: prev_hash does not match prior curr_hash (expected {exp}, got {got})")

        # monotonic timestamps
        if last_ts and r.created_at and r.created_at < last_ts:
            errors.append(f"id={r.id}: created_at older than previous record")
        if r.created_at:
            last_ts = r.created_at

        expected_prev = r.curr_hash

    tip = recs[-1]
    return {
        "ok": len(errors) == 0,
        "height": len(recs),
        "tip_hash": tip.curr_hash.hex() if isinstance(tip.curr_hash, (bytes, bytearray)) else None,
        "errors": errors[:20],
    }