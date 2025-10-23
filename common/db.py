# common/db.py
from sqlalchemy import create_engine  # type: ignore
from sqlalchemy.orm import sessionmaker, declarative_base  # type: ignore
import os
from dotenv import load_dotenv  # type: ignore

load_dotenv()

# ✅ Default to SQLite for dev if DATABASE_URL not set
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dev.db")

Base = declarative_base()

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_session():
    """Yield a database session for dependency injection."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Alias for FastAPI dependencies
get_db = get_session
