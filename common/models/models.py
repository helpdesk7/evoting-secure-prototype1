from cryptoutils.encryption import encrypt_voter_data
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column # type: ignore
from sqlalchemy import LargeBinary, Integer, String, TIMESTAMP, func # type: ignore

class Base(DeclarativeBase):
    pass

class Voter(Base):
    __tablename__ = "voters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name_enc: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    address_enc: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    dob_enc: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    # ➜ ADD THIS (it’s missing)
    eligibility_enc: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)

    region: Mapped[str] = mapped_column(String, nullable=False)

    created_at: Mapped[str] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[str] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


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
