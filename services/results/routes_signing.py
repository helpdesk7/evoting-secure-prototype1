# services/results/routes_signing.py
from __future__ import annotations
from fastapi import APIRouter, HTTPException  # type: ignore
from pydantic import BaseModel  # type: ignore
import json

from common.crypto.signing import (
    get_public_key_b64, sign_detached_b64, verify_detached_b64
)

router = APIRouter(tags=["signing"])

class SignRequest(BaseModel):
    results: dict

class VerifyRequest(BaseModel):
    results: dict
    signature: str
    public_key: str

@router.get("/results/pubkey")
def get_pubkey():
    try:
        return {"algorithm": "Ed25519", "public_key": get_public_key_b64()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"pubkey_error: {e}")

@router.post("/results/sign")
def sign_results(payload: SignRequest):
    try:
        # deterministic JSON for hashing/signature (sort keys + no spaces)
        message = json.dumps(payload.results, separators=(",", ":"), sort_keys=True).encode()
        signature = sign_detached_b64(message)
        return {
            "algorithm": "Ed25519",
            "public_key": get_public_key_b64(),
            "signature": signature,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"sign_error: {e}")

@router.post("/results/verify")
def verify_results(payload: VerifyRequest):
    try:
        message = json.dumps(payload.results, separators=(",", ":"), sort_keys=True).encode()
        ok = verify_detached_b64(message, payload.signature, payload.public_key)
        return {"ok": ok}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"verify_error: {e}")