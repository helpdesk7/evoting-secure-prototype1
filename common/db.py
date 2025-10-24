# common/db.py
from sqlalchemy import create_engine # type: ignore
from sqlalchemy.orm import sessionmaker, DeclarativeBase # type: ignore
import os
from sqlalchemy import create_engine # type: ignore
from sqlalchemy.orm import sessionmaker, DeclarativeBase # type: ignore
from dotenv import load_dotenv # type: ignore

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]


class Base(DeclarativeBase):
    pass

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
# Alias for FastAPI dependencies
get_db = get_session
