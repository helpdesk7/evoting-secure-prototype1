# cryptoutils/encryption.py
"""
Unified encryption utilities for:
- SR-01: AES-256-GCM encryption of voter data
- SR-03: AES-256-CBC encryption of MFA secrets

Keys are read from environment as 64 hex chars (256-bit), with light normalization.
"""

import os
import re
from typing import Dict, Iterable, Any, Tuple
from binascii import unhexlify
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes


# -------------------------------------------------------------------------
# Helpers to load & validate 256-bit keys from env (hex)
# -------------------------------------------------------------------------
def _load_hex_key(varnames: Tuple[str, ...], display_name: str) -> bytes:
    """
    Load a 256-bit key from the first non-empty env var in `varnames`.
    Accepts hex with optional 0x prefix, spaces, or colons; normalizes to pure hex.
    Requires exactly 64 hex chars -> returns 32 raw bytes.
    """
    raw = None
    used_name = None
    for vn in varnames:
        v = os.getenv(vn)
        if v:
            raw = v
            used_name = vn
            break

    if not raw:
        raise RuntimeError(f"Missing {display_name}: set one of {', '.join(varnames)} in your environment")

    # normalize: strip, lower, remove 0x, spaces, colons
    s = raw.strip().lower()
    s = s.replace("0x", "").replace(" ", "").replace(":", "")

    if not re.fullmatch(r"[0-9a-f]{64}", s or ""):
        raise RuntimeError(
            f"{display_name} must be exactly 64 hex chars (256-bit). "
            f"Got length={len(s)} from {used_name}; original value={repr(raw)}"
        )

    try:
        return unhexlify(s)
    except Exception as e:
        raise RuntimeError(f"Failed to decode {display_name} from {used_name}: {e}")


# === Load the keys (supports both legacy & new names) ===
_AES_KEY = _load_hex_key(("AES_MASTER_KEY", "AES_MASTER_KEY_HEX"), "AES master key")
_MFA_KEY = _load_hex_key(("MFA_ENC_KEY_HEX", "MFA_ENC_KEY"), "MFA encryption key")


# -------------------------------------------------------------------------
# Shared helpers
# -------------------------------------------------------------------------
def _to_bytes(val: Any) -> bytes:
    if val is None:
        return b""
    if isinstance(val, bool):
        val = "true" if val else "false"
    if not isinstance(val, (bytes, bytearray)):
        val = str(val).encode("utf-8")
    return bytes(val)


# -------------------------------------------------------------------------
# 🟢 SR-01: AES-GCM Encryption for voter data
#   Output format: nonce(12) + tag(16) + ciphertext
# -------------------------------------------------------------------------
def encrypt(value: Any) -> bytes:
    pt = _to_bytes(value)
    nonce = get_random_bytes(12)
    cipher = AES.new(_AES_KEY, AES.MODE_GCM, nonce=nonce)
    ct, tag = cipher.encrypt_and_digest(pt)
    return nonce + tag + ct


def decrypt(blob: bytes) -> str:
    if not blob:
        return ""
    nonce, tag, ct = blob[:12], blob[12:28], blob[28:]
    cipher = AES.new(_AES_KEY, AES.MODE_GCM, nonce=nonce)
    pt = cipher.decrypt_and_verify(ct, tag)
    return pt.decode("utf-8")


def encrypt_selected_fields(data: Dict[str, Any], fields: Iterable[str]) -> Dict[str, bytes]:
    """Encrypt only selected fields from a dict; writes *_enc keys for DB storage."""
    out: Dict[str, bytes] = {}
    for f in fields:
        if f in data:
            out[f"{f}_enc"] = encrypt(data[f])
    return out


def encrypt_voter_data(data: Dict[str, Any]) -> Dict[str, bytes]:
    """Encrypt standard voter fields used by the Voter model."""
    return encrypt_selected_fields(data, ("name", "address", "dob", "eligibility"))


# -------------------------------------------------------------------------
# 🔵 SR-03: AES-CBC Encryption for MFA secrets (TOTP seeds, recovery codes)
#   Output format: iv(16) + ciphertext (PKCS#7 padded)
# -------------------------------------------------------------------------
def _pad(b: bytes) -> bytes:
    pad = 16 - (len(b) % 16)
    return b + bytes([pad]) * pad


def _unpad(b: bytes) -> bytes:
    if not b:
        raise ValueError("Invalid padding (empty)")
    pad = b[-1]
    if pad < 1 or pad > 16:
        raise ValueError("Invalid padding")
    return b[:-pad]


def encrypt_bytes(plain: bytes) -> bytes:
    iv = get_random_bytes(16)
    cipher = AES.new(_MFA_KEY, AES.MODE_CBC, iv)
    ct = cipher.encrypt(_pad(plain))
    return iv + ct


def decrypt_bytes(blob: bytes) -> bytes:
    if len(blob) < 32:
        raise ValueError("Ciphertext too short")
    iv, ct = blob[:16], blob[16:]
    cipher = AES.new(_MFA_KEY, AES.MODE_CBC, iv)
    pt = cipher.decrypt(ct)
    return _unpad(pt)