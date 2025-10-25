import os
import time
from typing import Optional, Tuple
from itsdangerous import TimestampSigner, BadSignature, SignatureExpired

SESSION_COOKIE = "evote_sess"
CSRF_HEADER   = "X-CSRF-Token"

def _get_secret() -> bytes:
    key = os.getenv("RESULTS_SESSION_SECRET", "")
    if len(key) != 64:
        # 32 bytes hex-encoded = 64 chars
        raise RuntimeError("RESULTS_SESSION_SECRET must be 64 hex chars")
    return bytes.fromhex(key)

def _get_ttl() -> int:
    try:
        return int(os.getenv("RESULTS_SESSION_TTL_MIN", "30")) * 60
    except:
        return 1800

def sign_session(username: str, roles: list[str], csrf: str) -> str:
    """Create signed session payload: user|iat|csrf|roles_json"""
    iat = int(time.time())
    payload = f"{username}|{iat}|{csrf}|{','.join(roles)}"
    signer = TimestampSigner(_get_secret())
    return signer.sign(payload.encode("utf-8")).decode("utf-8")

def verify_session(token: str) -> Tuple[str, int, str, list[str]]:
    """Return (username, iat, csrf, roles) or raise."""
    signer = TimestampSigner(_get_secret())
    # Enforce absolute TTL
    max_age = _get_ttl()
    try:
        raw = signer.unsign(token, max_age=max_age).decode("utf-8")
    except SignatureExpired as e:
        raise ValueError("expired") from e
    except BadSignature as e:
        raise ValueError("bad") from e

    parts = raw.split("|", 3)
    if len(parts) != 4:
        raise ValueError("bad")
    username, iat_s, csrf, roles_csv = parts
    iat = int(iat_s)
    roles = [r for r in roles_csv.split(",") if r]
    return username, iat, csrf, roles
