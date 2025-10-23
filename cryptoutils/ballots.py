# common/cryptoutils/ballots.py
from __future__ import annotations

import os
import json
import hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def _get_aes_key() -> bytes:
    """
    Reads BALLOT_AES_KEY (64 hex chars = 32 bytes) from env and returns raw bytes.
    Raises a clear error if it's missing or the wrong length.
    """
    key_hex = os.environ.get("BALLOT_AES_KEY", "")
    if len(key_hex) != 64:
        raise ValueError(
            "BALLOT_AES_KEY must be set to a 64-hex string (32-byte key). "
            f"Got length={len(key_hex)}"
        )
    try:
        return bytes.fromhex(key_hex)
    except ValueError:
        raise ValueError("BALLOT_AES_KEY must be valid hex.")


def canonical_prefs(prefs: list[int], election_id: str, ts: str) -> bytes:
    """
    Produces a stable, order-preserving representation of the ballot.
    DO NOT sort keys; keep separators tight to avoid whitespace differences.
    """
    return json.dumps(
        {"e": election_id, "t": ts, "p": prefs},
        separators=(",", ":"),
        sort_keys=False,
    ).encode("utf-8")


def receipt_hash(blob: bytes) -> str:
    """SHA-256 hex receipt over the exact canonical bytes."""
    return hashlib.sha256(blob).hexdigest()


def encrypt_ballot(blob: bytes) -> tuple[bytes, bytes]:
    """
    AES-GCM encryption (confidentiality + integrity).
    Returns (ciphertext, nonce).
    """
    key = _get_aes_key()
    nonce = os.urandom(12)
    ct = AESGCM(key).encrypt(nonce, blob, None)
    return ct, nonce


def hash_chain(prev_hash: bytes, ct: bytes, nonce: bytes) -> bytes:
    """Hash-chain step: H(prev || ct || nonce)."""
    return hashlib.sha256(prev_hash + ct + nonce).digest()
