# cryptoutils/kms.py
from __future__ import annotations
import os, secrets, hashlib
from typing import Tuple
from Crypto.Cipher import AES

# We "wrap" data keys with a KEK using AES-GCM (nonce|ciphertext|tag)
# This simulates a KMS/HSM; production would call a real KMS instead.

def _b(hex_str: str) -> bytes:
    return bytes.fromhex(hex_str)

class LocalKMS:
    def __init__(self, kek_hex: str | None = None, key_id: str | None = None):
        self.key_id = (key_id or os.getenv("DATA_KEY_ID", "default-key")).encode("utf-8")
        kek_hex = kek_hex or os.getenv("KMS_KEK_HEX")
        if not kek_hex:
            raise RuntimeError("KMS_KEK_HEX not set")
        self.kek = _b(kek_hex)
        if len(self.kek) not in (16, 24, 32):
            raise RuntimeError("KMS_KEK_HEX must be 32/48/64 hex (128/192/256-bit)")

    def generate_data_key(self) -> Tuple[bytes, bytes]:
        """Return (plaintext_32B_DEK, wrapped_blob)"""
        dek = secrets.token_bytes(32)  # 256-bit DEK for AES-GCM
        nonce = secrets.token_bytes(12)
        cipher = AES.new(self.kek, AES.MODE_GCM, nonce=nonce)
        cipher.update(self.key_id)  # AAD = key_id
        ct, tag = cipher.encrypt_and_digest(dek)
        wrapped = nonce + ct + tag
        return dek, wrapped

    def decrypt_wrapped_key(self, wrapped: bytes) -> bytes:
        nonce, body = wrapped[:12], wrapped[12:]
        ct, tag = body[:-16], body[-16:]
        cipher = AES.new(self.kek, AES.MODE_GCM, nonce=nonce)
        cipher.update(self.key_id)
        return cipher.decrypt_and_verify(ct, tag)

def aad_hash(aad: bytes) -> bytes:
    return hashlib.sha256(aad).digest()