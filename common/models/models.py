# common/models/models.py
from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column  # type: ignore
from sqlalchemy import (  # type: ignore
    LargeBinary,
    Integer,
    String,
    TIMESTAMP,
    DateTime,
    Boolean,
    Column,
)
from sqlalchemy.sql import func  # type: ignore
from sqlalchemy.dialects.postgresql import UUID  # type: ignore
from passlib.hash import bcrypt  # type: ignore
import uuid

from cryptoutils.encryption import encrypt, decrypt  # SR-01 field helpers


# --------------------------------------------------------------------
# Base (import this from common.db and DO NOT redefine there)
# --------------------------------------------------------------------
class Base(DeclarativeBase):
    pass


# --------------------------------------------------------------------
# SR-01: Voter (encrypted fields at rest)
# --------------------------------------------------------------------
class Voter(Base):
    __tablename__ = "voters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # encrypted blobs in DB
    name_enc: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    address_enc: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    dob_enc: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    eligibility_enc: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)

    # not encrypted (example business field)
    region: Mapped[str] = mapped_column(String, nullable=False)

    created_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # ---- convenience accessors (decrypt on read / encrypt on write) ----
    @property
    def name(self) -> str:
        return decrypt(self.name_enc)

    @name.setter
    def name(self, v: str) -> None:
        self.name_enc = encrypt(v)

    @property
    def address(self) -> str:
        return decrypt(self.address_enc)

    @address.setter
    def address(self, v: str) -> None:
        self.address_enc = encrypt(v)

    @property
    def dob(self) -> str:
        return decrypt(self.dob_enc)

    @dob.setter
    def dob(self, v: str) -> None:
        self.dob_enc = encrypt(v)

    @property
    def eligibility(self) -> str:
        return decrypt(self.eligibility_enc)

    @eligibility.setter
    def eligibility(self, v: str) -> None:
        self.eligibility_enc = encrypt(v)


# --------------------------------------------------------------------
# SR-03: Auth models (UserAuth + optional LoginChallenge)
# --------------------------------------------------------------------
class UserAuth(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)  # used by routes_auth.py
    password_hash = Column(String(255), nullable=False)

    # MFA
    mfa_enabled = Column(Boolean, nullable=False, default=False)
    mfa_secret_enc = Column(LargeBinary, nullable=True)           # encrypted TOTP secret
    recovery_codes_hash = Column(String(2048), nullable=True)     # optional (hashed)

    # hygiene / lockout
    failed_logins = Column(Integer, nullable=False, default=0)
    locked_until = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # password helpers
    @staticmethod
    def hash_password(pw: str) -> str:
        return bcrypt.hash(pw)

    def verify_password(self, pw: str) -> bool:
        return bcrypt.verify(pw, self.password_hash)


class LoginChallenge(Base):
    __tablename__ = "login_challenges"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, nullable=False, index=True)
    jwt = Column(String(1024), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)