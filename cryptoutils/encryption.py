"""
cryptoutils/encryption.py
Provides AES-256-GCM and AES-256-CBC helpers used in SR-01 and SR-03.
"""

import os
from typing import Dict, Iterable, Any
from binascii import unhexlify, Error as BinasciiError
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

# === Load keys from environment ===
AES_MASTER_KEY_HEX = os.getenv("AES_MASTER_KEY", "").strip()
MFA_ENC_KEY_HEX = os.getenv("MFA_ENC_KEY_HEX", "").strip()


def _load_key(hex_str: str, name: str) -> bytes:
    if not hex_str:
        raise RuntimeError(f"{name} missing from environment (.env)")
    try:
        key = unhexlify(hex_str)
    except BinasciiError:
        raise RuntimeError(f"{name} must be 64 hex chars (256-bit)")
    if len(key) != 32:
        raise RuntimeError(f"{name} must be exactly 32 bytes (256-bit)")
    return key


_KEY_VOTER = _load_key(AES_MASTER_KEY_HEX, "AES_MASTER_KEY")
_KEY_MFA = _load_key(MFA_ENC_KEY_HEX, "MFA_ENC_KEY_HEX")


# === Utility: safe to_bytes ===
def _to_bytes(val: Any) -> bytes:
    if val is None:
        return b""
    if isinstance(val, bool):
        val = "true" if val else "false"
    if not isinstance(val, (bytes, bytearray)):
        val = str(val).encode("utf-8")
    return bytes(val)


# ------------------------------------------------------------------
# SR-01: AES-GCM encryption for voter data
# ------------------------------------------------------------------
def encrypt(value: Any) -> bytes:
    pt = _to_bytes(value)
    nonce = get_random_bytes(12)
    cipher = AES.new(_KEY_VOTER, AES.MODE_GCM, nonce=nonce)
    ct, tag = cipher.encrypt_and_digest(pt)
    return nonce + tag + ct


def decrypt(blob: bytes) -> str:
    if not blob:
        return ""
    nonce, tag, ct = blob[:12], blob[12:28], blob[28:]
    cipher = AES.new(_KEY_VOTER, AES.MODE_GCM, nonce=nonce)
    pt = cipher.decrypt_and_verify(ct, tag)
    return pt.decode("utf-8")


# ------------------------------------------------------------------
# SR-03: AES-CBC encryption for MFA secrets
# ------------------------------------------------------------------
def _pad(b: bytes) -> bytes:
    pad = 16 - (len(b) % 16)
    return b + bytes([pad]) * pad


def _unpad(b: bytes) -> bytes:
    pad = b[-1]
    if pad < 1 or pad > 16:
        raise ValueError("Invalid padding")
    return b[:-pad]


def encrypt_bytes(plain: bytes) -> bytes:
    iv = get_random_bytes(16)
    cipher = AES.new(_KEY_MFA, AES.MODE_CBC, iv)
    ct = cipher.encrypt(_pad(plain))
    return iv + ct


def decrypt_bytes(blob: bytes) -> bytes:
    iv, ct = blob[:16], blob[16:]
    cipher = AES.new(_KEY_MFA, AES.MODE_CBC, iv)
    pt = cipher.decrypt(ct)
    return _unpad(pt)
