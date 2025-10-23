# services/registration/routes_auth.py
from __future__ import annotations

from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, status  # type: ignore
from pydantic import BaseModel, EmailStr  # type: ignore
from sqlalchemy.orm import Session  # type: ignore
from passlib.context import CryptContext  # type: ignore
import pyotp  # type: ignore
import time, os
import jwt  # type: ignore  # PyJWT

from common.db import get_session
from common.models.models import UserAuth
from cryptoutils.encryption import encrypt_bytes, decrypt_bytes

# --- Config ---
JWT_SECRET = os.environ.get("JWT_SECRET", "dev-secret")
JWT_ALG = "HS256"
pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(tags=["auth"])

# ---------- Schemas ----------
class RegisterIn(BaseModel):
    email: EmailStr
    password: str

class LoginIn(BaseModel):
    email: EmailStr
    password: str
    code: Optional[str] = None  # TOTP code if MFA enabled

class MFASetupOut(BaseModel):
    provisioning_uri: str  # use this in authenticator app (QR or manual)
    issuer: str
    account: EmailStr

class MFAVerifyIn(BaseModel):
    email: EmailStr
    code: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

# ---------- Helpers ----------
def _hash(pw: str) -> str:
    return pwd_ctx.hash(pw)

def _verify(pw: str, h: str) -> bool:
    return pwd_ctx.verify(pw, h)

def _make_jwt(sub: str) -> str:
    now = int(time.time())
    payload = {"sub": sub, "iat": now, "exp": now + 3600}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)

# ---------- Routes ----------
@router.post("/auth/register", status_code=status.HTTP_201_CREATED)
def register(body: RegisterIn, db: Session = Depends(get_session)):
    email = body.email.lower()
    # Check if email already taken
    if db.query(UserAuth).filter_by(email=email).first():
        raise HTTPException(status_code=409, detail="Email already registered")

    ua = UserAuth(email=email, password_hash=_hash(body.password))
    db.add(ua)
    db.commit()
    return {"ok": True}

@router.post("/auth/mfa/setup", response_model=MFASetupOut)
def mfa_setup(body: LoginIn, db: Session = Depends(get_session)):
    email = body.email.lower()
    ua = db.query(UserAuth).filter_by(email=email).first()
    if not ua or not _verify(body.password, ua.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Generate new TOTP secret (base32), encrypt at rest
    secret_b32 = pyotp.random_base32()
    ua.mfa_secret_enc = encrypt_bytes(secret_b32.encode("utf-8"))
    ua.mfa_enabled = False
    db.commit()

    issuer = "evote"
    uri = pyotp.TOTP(secret_b32).provisioning_uri(name=ua.email, issuer_name=issuer)
    return MFASetupOut(provisioning_uri=uri, issuer=issuer, account=ua.email)

@router.post("/auth/mfa/verify")
def mfa_verify(body: MFAVerifyIn, db: Session = Depends(get_session)):
    email = body.email.lower()
    ua = db.query(UserAuth).filter_by(email=email).first()
    if not ua or not ua.mfa_secret_enc:
        raise HTTPException(status_code=400, detail="MFA not initialized")

    secret_b32 = decrypt_bytes(ua.mfa_secret_enc).decode("utf-8")
    if not pyotp.TOTP(secret_b32).verify(body.code, valid_window=1):
        raise HTTPException(status_code=401, detail="Invalid TOTP code")

    ua.mfa_enabled = True
    db.commit()
    return {"ok": True}

@router.post("/auth/login", response_model=TokenOut)
def login(body: LoginIn, db: Session = Depends(get_session)):
    email = body.email.lower()
    ua = db.query(UserAuth).filter_by(email=email).first()
    if not ua or not _verify(body.password, ua.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if ua.mfa_enabled:
        if not body.code:
            raise HTTPException(status_code=401, detail="MFA code required")
        secret_b32 = decrypt_bytes(ua.mfa_secret_enc).decode("utf-8")
        if not pyotp.TOTP(secret_b32).verify(body.code, valid_window=1):
            raise HTTPException(status_code=401, detail="Invalid TOTP code")

    token = _make_jwt(str(ua.id))
    return TokenOut(access_token=token)