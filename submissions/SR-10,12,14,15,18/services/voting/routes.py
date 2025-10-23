# services/voting/routes.py
from fastapi import APIRouter, HTTPException, Depends, Body
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from common.db import get_session
from common.models.models import Ballot, BallotChain
from common.crypto.ballots import (
    canonical_prefs,
    receipt_hash,
    encrypt_ballot,
    hash_chain,
)
from .deps import require_valid_otbt, consume_otbt

router = APIRouter()


def get_chain_head(db: Session) -> bytes:
    """
    Returns the current head of the hash chain (or 32 zero bytes if none).
    """
    last = db.query(BallotChain).order_by(BallotChain.id.desc()).first()
    return last.curr_hash if last else bytes(32)  # genesis = 32 zero bytes


@router.post("/ballot/submit")
def submit_ballot(
    # Make JSON body binding explicit so you can POST a JSON object
    prefs: list[int] = Body(..., embed=True, description="Ordered preference list"),
    election_id: str = Body(..., embed=True),
    db: Session = Depends(get_session),
    tok=Depends(require_valid_otbt),
):
    """
    Cast a ballot:
      - Validates preference order
      - Computes receipt hash (SR-12)
      - Encrypts ballot with AES-GCM (SR-12)
      - Appends to hash chain (SR-12)
      - Consumes one-time ballot token (SR-10)
    Returns: ballot_id, receipt, and chain head.
    """
    # Basic validation (no duplicates, non-empty, ints assumed)
    if not prefs or len(set(prefs)) != len(prefs):
        raise HTTPException(400, "invalid preference order")

    ts = datetime.now(timezone.utc).isoformat()
    blob = canonical_prefs(prefs, election_id, ts)

    # SR-12: ballot-level integrity receipt
    rcp = receipt_hash(blob)

    # SR-12: confidentiality + integrity via AEAD
    ct, nonce = encrypt_ballot(blob)

    # Persist ballot (NOTE: no voter_id stored—SR-10 unlinkability)
    b = Ballot(election_id=election_id, ciphertext=ct, nonce=nonce, receipt=rcp)
    db.add(b)
    db.commit()
    db.refresh(b)

    # SR-12: tamper-evident ledger via hash chain
    prev = get_chain_head(db)
    curr = hash_chain(prev, ct, nonce)
    db.add(BallotChain(ballot_id=b.id, prev_hash=prev, curr_hash=curr))

    # SR-10: consume the one-time token
    consume_otbt(tok, db)

    db.commit()

    return {"ballot_id": b.id, "receipt": rcp, "chain_head": curr.hex()}


# ---- Service health routes (for Nginx and manual checks) ----

@router.get("/healthz")
def healthz():
    """
    Service-scoped health endpoint: /voting/healthz
    """
    return {"status": "ok"}


@router.get("/hello")
def hello():
    """
    Simple identity endpoint for quick smoke tests.
    """
    return {"service": "voting"}
