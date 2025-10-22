# common/crypto/signing.py
from __future__ import annotations
import os, pathlib
from typing import Tuple
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives import serialization

DEFAULT_KEY_DIR = os.getenv("RESULTS_SIGNING_KEY_DIR", "/app/keys")
DEFAULT_PRIV_PATH = os.getenv("RESULTS_SIGNING_PRIV", f"{DEFAULT_KEY_DIR}/ed25519_private.pem")

def _ensure_keypair(priv_path: str = DEFAULT_PRIV_PATH) -> Tuple[Ed25519PrivateKey, Ed25519PublicKey]:
    path = pathlib.Path(priv_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    if path.exists():
        data = path.read_bytes()
        priv = serialization.load_pem_private_key(data, password=None)
        if not isinstance(priv, Ed25519PrivateKey):
            raise ValueError("Loaded private key is not Ed25519")
    else:
        priv = Ed25519PrivateKey.generate()
        pem = priv.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        path.write_bytes(pem)

    pub = priv.public_key()
    return priv, pub

def get_public_key_pem() -> bytes:
    _, pub = _ensure_keypair()
    return pub.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

def sign_bytes(data: bytes) -> bytes:
    priv, _ = _ensure_keypair()
    return priv.sign(data)

def verify_bytes(data: bytes, signature: bytes) -> bool:
    _, pub = _ensure_keypair()
    try:
        pub.verify(signature, data)
        return True
    except Exception:
        return False