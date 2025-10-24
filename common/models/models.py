# common/models/models.py
from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import ( # type: ignore
    Column,
    Integer,
    String,
    LargeBinary,
    DateTime,
    Boolean,
    ForeignKey,
    UniqueConstraint,
    Text,
    func,  # ✅ added this import for server_default=func.now()
)
from sqlalchemy.orm import Mapped, mapped_column # type: ignore

from common.db import Base
from common.models.roles import Role


# ---------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------
UTCNOW = lambda: datetime.now(timezone.utc)

# ---------------------------------------------------------------------
# Core Tables
# ---------------------------------------------------------------------

class Ballot(Base):
    """
    Stores encrypted ballots (ciphertext + nonce + receipt).
    Linked to BallotChain for append-only audit.
    """
    __tablename__ = "ballots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    election_id: Mapped[str] = mapped_column(String(64), index=True)
    ciphertext: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    nonce: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    receipt: Mapped[str] = mapped_column(String(64), index=True)  # SHA-256 hex of ciphertext
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=UTCNOW
    )


class BallotChain(Base):
    """
    Append-only blockchain-style chain linking ballots.
    Each record includes hash of the previous one for tamper-evidence.
    """
    __tablename__ = "ballot_chain"

    id = Column(Integer, primary_key=True, index=True)
    ballot_id = Column(Integer, ForeignKey("ballots.id"), nullable=False, index=True)
    prev_hash = Column(LargeBinary(32), nullable=False)
    curr_hash = Column(LargeBinary(32), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())  # ✅ fixed

# ---------------------------------------------------------------------
# Optional token + admin models
# ---------------------------------------------------------------------

class BallotToken(Base):
    """
    Tokens used to authorize ballot submissions.
    """
    __tablename__ = "ballot_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    token: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    voter_ref: Mapped[str] = mapped_column(String(128))
    exp_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    consumed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class AdminUser(Base):
    """
    Registered admin users with access to results and actions.
    Now includes role-based access control (SR-05).
    """
    __tablename__ = "admin_users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(254), unique=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # ✅ New field for RBAC
    role: Mapped[Role] = mapped_column(String(32), default=Role.AEC_STAFF.value)

    def has_role(self, required: Role) -> bool:
        """Check if user meets or exceeds the required role privilege."""
        hierarchy = [
            Role.OBSERVER,
            Role.AEC_STAFF,
            Role.COMMISSIONER_DELEGATE,
            Role.ADMIN,
        ]
        return hierarchy.index(self.role) >= hierarchy.index(required)



class ResultAction(Base):
    """
    Records actions (e.g., tally requests, approvals).
    """
    __tablename__ = "result_actions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type: Mapped[str] = mapped_column(String(64))
    payload: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32), default="PENDING")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=UTCNOW)


class Approval(Base):
    """
    Tracks admin approvals for result actions.
    """
    __tablename__ = "approvals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    action_id: Mapped[int] = mapped_column(ForeignKey("result_actions.id"), index=True)
    admin_id: Mapped[int] = mapped_column(ForeignKey("admin_users.id"), index=True)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=UTCNOW)

    __table_args__ = (
        UniqueConstraint("action_id", "admin_id", name="uq_action_admin"),
    )
