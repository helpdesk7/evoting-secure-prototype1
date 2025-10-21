# common/models/models.py (excerpt)
from sqlalchemy import Column, Integer, String, LargeBinary, DateTime, Boolean, ForeignKey, UniqueConstraint, Text # type: ignore
from sqlalchemy.orm import Mapped, mapped_column # type: ignore
from datetime import datetime, timezone
from common.db import Base

UTCNOW = lambda: datetime.now(timezone.utc)

class Ballot(Base):
    __tablename__ = "ballots"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    election_id: Mapped[str] = mapped_column(String(64), index=True)
    ciphertext: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    nonce: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    receipt: Mapped[str] = mapped_column(String(64), index=True)  # SHA-256 hex
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=UTCNOW)

class BallotChain(Base):
    __tablename__ = "ballot_chain"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ballot_id: Mapped[int] = mapped_column(ForeignKey("ballots.id"), index=True)
    prev_hash: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    curr_hash: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=UTCNOW)

class BallotToken(Base):
    __tablename__ = "ballot_tokens"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    token: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    voter_ref: Mapped[str] = mapped_column(String(128))
    exp_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

class AdminUser(Base):
    __tablename__ = "admin_users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(254), unique=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

class ResultAction(Base):
    __tablename__ = "result_actions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type: Mapped[str] = mapped_column(String(64))
    payload: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32), default="PENDING")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=UTCNOW)

class Approval(Base):
    __tablename__ = "approvals"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    action_id: Mapped[int] = mapped_column(ForeignKey("result_actions.id"), index=True)
    admin_id: Mapped[int] = mapped_column(ForeignKey("admin_users.id"), index=True)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=UTCNOW)
    __table_args__ = (UniqueConstraint("action_id", "admin_id", name="uq_action_admin"),)