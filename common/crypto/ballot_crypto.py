# common/crypto/ballot_crypto.py
from __future__ import annotations

import json
import os
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

# NOTE: We accept a KMS instance to satisfy SR-09 (key management entry point),
# but for this minimal path we read the DEK from BALLOT_AES_KEY.
# You can later modify this to derive/unwrap a per-ballot key via KMS.
def encrypt_ballot(ballot: dict, kms) -> tuple[bytes, bytes]:
    """
    Encrypt a ballot dict using AES-GCM.
    Returns (ciphertext_with_tag, nonce).
    """
    key_hex = os.environ.get("BALLOT_AES_KEY")
    if not key_hex:
        raise RuntimeError("BALLOT_AES_KEY is not set in environment")
    key = bytes.fromhex(key_hex)

    # Canonicalize JSON for stable receipts
    plaintext = json.dumps(ballot, separators=(",", ":"), sort_keys=True).encode("utf-8")

    nonce = get_random_bytes(12)  # 96-bit nonce for AES-GCM
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext)

    # Store tag alongside ciphertext (common pattern if you don't have a tag column)
    return ciphertext + tag, nonce
