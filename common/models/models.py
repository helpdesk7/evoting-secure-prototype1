# common/models/models.py
from __future__ import annotations
from datetime import datetime, timezone
from cryptoutils.encryption import encrypt_voter_data
from sqlalchemy import ( # type: ignore
    Column, Integer, String, LargeBinary, DateTime, Boolean,
    ForeignKey, UniqueConstraint, Text, func
)
from sqlalchemy.orm import Mapped, mapped_column # type: ignore
from common.db import Base  # <-- must import Base from common.db

UTCNOW = lambda: datetime.now(timezone.utc)

class Voter(Base):
    __tablename__ = "voters"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name_enc: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    address_enc: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    dob_enc: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    eligibility: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    region: Mapped[str] = mapped_column(String(64), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=UTCNOW)

# (include the rest of your models: Ballot, BallotChain, etc.)


    # convenience accessors (de/encrypt transparently)
    @property
    def name(self) -> str:
        return encrypt_voter_data(self.name_enc).decode()

    @name.setter
    def name(self, v: str) -> None:
        self.name_enc = encrypt_voter_data(v.encode())

    @property
    def address(self) -> str:
        return encrypt_voter_data(self.address_enc).decode()

    @address.setter
    def address(self, v: str) -> None:
        self.address_enc = encrypt_voter_data(v.encode())

    @property
    def dob(self) -> str:
        return encrypt_voter_data(self.dob_enc).decode()

    @dob.setter
    def dob(self, v: str) -> None:
        self.dob_enc = encrypt_voter_data(v.encode())

    @property
    def eligibility(self) -> str:
        return encrypt_voter_data(self.eligibility_enc).decode()

    @eligibility.setter
    def eligibility(self, v: str) -> None:
        self.eligibility_enc = encrypt_voter_data(v.encode())
