# cryptoutils/encryption.py
from typing import Dict, Iterable, Any
from binascii import unhexlify
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

from common.config import AES_MASTER_KEY  # hex string from infra/.env

# master key must be 32 bytes (64 hex chars) for AES-256-GCM
_KEY = unhexlify(AES_MASTER_KEY.strip())

def _to_bytes(val: Any) -> bytes:
    if val is None:
        return b""
    if isinstance(val, bool):
        # normalize booleans to stable text form
        val = "true" if val else "false"
    if not isinstance(val, (bytes, bytearray)):
        val = str(val).encode("utf-8")
    return bytes(val)

def encrypt(value: Any) -> bytes:
    """Encrypt a single value using AES-256-GCM.
    Returns: nonce(12) + tag(16) + ciphertext
    """
    pt = _to_bytes(value)
    nonce = get_random_bytes(12)
    cipher = AES.new(_KEY, AES.MODE_GCM, nonce=nonce)
    ct, tag = cipher.encrypt_and_digest(pt)
    return nonce + tag + ct

def decrypt(blob: bytes) -> str:
    """Decrypt bytes produced by encrypt()."""
    if not blob:
        return ""
    nonce, tag, ct = blob[:12], blob[12:28], blob[28:]
    cipher = AES.new(_KEY, AES.MODE_GCM, nonce=nonce)
    pt = cipher.decrypt_and_verify(ct, tag)
    return pt.decode("utf-8")

def encrypt_selected_fields(data: Dict[str, Any], fields: Iterable[str]) -> Dict[str, bytes]:
    """Encrypt only the given fields from an input dict.
    Produces keys with *_enc suffix for DB storage.
    """
    out: Dict[str, bytes] = {}
    for f in fields:
        if f in data:
            out[f"{f}_enc"] = encrypt(data[f])
    return out

# Back-compat for existing imports in models.py
def encrypt_voter_data(data: Dict[str, Any]) -> Dict[str, bytes]:
    """Encrypt the standard voter fields."""
    return encrypt_selected_fields(data, ("name", "address", "dob", "eligibility"))
