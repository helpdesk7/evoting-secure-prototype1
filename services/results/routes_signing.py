# services/results/routes_signing.py
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Dict, Any

from fastapi import APIRouter, Depends  # type: ignore
from pydantic import BaseModel          # type: ignore
from sqlalchemy.orm import Session      # type: ignore

from common.db import get_session
from common.models.models import Ballot
from common.crypto.signing import sign_bytes, verify_bytes, get_public_key_pem

router = APIRouter(tags=["signing"])

# ---------- models ----------
class VerifyRequest(BaseModel):
    bundle: Dict[str, Any]
    signature_hex: str


# ---------- utils ----------
def _build_results_bundle(db: Session) -> dict:
    # Very simple demonstrator bundle: counts per election_id.
    # You can expand later with full aggregation.
    rows = db.query(Ballot.election_id).all()
    by_election: Dict[str, int] = {}
    for (eid,) in rows:
        by_election[eid] = by_election.get(eid, 0) + 1

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "schema": "sr17.v1",
        "totals": [{"election_id": k, "ballots": v} for k, v in sorted(by_election.items())],
    }


# ---------- endpoints ----------
@router.get("/results/pubkey")
def get_pubkey():
    return {"public_key_pem": get_public_key_pem().decode("utf-8")}

@router.post("/results/sign")
def sign_results(db: Session = Depends(get_session)):
    bundle = _build_results_bundle(db)
    payload = json.dumps(bundle, separators=(",", ":"), sort_keys=True).encode("utf-8")
    sig = sign_bytes(payload)
    return {
        "bundle": bundle,
        "signature_hex": sig.hex(),
        "public_key_pem": get_public_key_pem().decode("utf-8"),
        "status": "signed",
    }

@router.post("/results/verify")
def verify_results(body: VerifyRequest):
    payload = json.dumps(body.bundle, separators=(",", ":"), sort_keys=True).encode("utf-8")
    ok = verify_bytes(payload, bytes.fromhex(body.signature_hex))
    return {"valid": ok}