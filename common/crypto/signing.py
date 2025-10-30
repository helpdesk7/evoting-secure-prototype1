# common/crypto/signing.py
from __future__ import annotations
import base64
import hashlib
import os
from typing import Tuple
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey, Ed25519PublicKey
)
from cryptography.hazmat.primitives import serialization

# single in-process key (for demo; swap with HSM/KMS in prod)
_PRIV: Ed25519PrivateKey | None = None

def _load_or_create_key() -> Ed25519PrivateKey:
    global _PRIV
    if _PRIV is not None:
        return _PRIV

    # Option A: load from base64-encoded private key (raw seed/private bytes)
    priv_b64 = os.getenv("RESULTS_SIGNING_PRIVKEY_B64")
    if priv_b64:
        raw = base64.b64decode(priv_b64)
        try:
            _PRIV = Ed25519PrivateKey.from_private_bytes(raw)
            return _PRIV
        except Exception:
            # fall through to create
            pass

    # Option B: create new (ephemeral) key
    _PRIV = Ed25519PrivateKey.generate()
    return _PRIV

def get_keypair() -> Tuple[Ed25519PrivateKey, Ed25519PublicKey]:
    priv = _load_or_create_key()
    pub = priv.public_key()
    return priv, pub

def get_public_key_b64() -> str:
    _, pub = get_keypair()
    pub_bytes = pub.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    return base64.b64encode(pub_bytes).decode("ascii")

def sign_detached_b64(message: bytes) -> str:
    priv, _ = get_keypair()
    sig = priv.sign(message)
    return base64.b64encode(sig).decode("ascii")

def get_pubkey_fingerprint() -> str:
    return hashlib.sha256(get_public_key_b64()).hexdigest()

def verify_detached_b64(message: bytes, signature_b64: str, public_key_b64: str) -> bool:
    try:
        sig = base64.b64decode(signature_b64)
        pub = base64.b64decode(public_key_b64)
        Ed25519PublicKey.from_public_bytes(pub).verify(sig, message)
        return True
    except Exception:
        return False