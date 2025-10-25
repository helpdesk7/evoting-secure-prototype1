from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

ALGO = "HS256"
SECRET = "dev-secret-change-me"      # TODO: move to env
ACCESS_TTL_MIN = 15                  # minutes
ABSOLUTE_TTL_HOURS = 8

bearer = HTTPBearer(auto_error=True)

def issue_access_token(sub: str, role: str = "guest", ttl_min: int = ACCESS_TTL_MIN) -> str:
    """
    Issue a signed JWT with user identity and role claim.
    Args:
        sub: Subject identifier (e.g., email or user_id)
        role: User's role (e.g., 'admin', 'aec_staff', etc.)
        ttl_min: Time-to-live for the access token
    """
    now = datetime.now(timezone.utc)
    payload = {
        "sub": sub,
        "role": role,  # ✅ Included role for RBAC enforcement
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=ttl_min)).timestamp()),
        "abs": int((now + timedelta(hours=ABSOLUTE_TTL_HOURS)).timestamp()),
    }
    return jwt.encode(payload, SECRET, algorithm=ALGO)


def verify_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGO])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"code":"invalid_token","detail":"Invalid or expired token"})
    now = int(datetime.now(timezone.utc).timestamp())
    if now > int(payload.get("abs", 0)):
        raise HTTPException(status_code=401, detail={"code":"session_expired","detail":"Absolute session expired"})
    return payload

# Alias for backward compatibility
decode_jwt_token = verify_access_token

def auth_dep(creds: HTTPAuthorizationCredentials = Depends(bearer)) -> dict:
    return verify_access_token(creds.credentials)
