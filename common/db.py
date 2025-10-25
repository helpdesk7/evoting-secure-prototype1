from sqlalchemy import create_engine  # type: ignore
from sqlalchemy.orm import sessionmaker, DeclarativeBase  # type: ignore
from dotenv import load_dotenv  # type: ignore
import os

# Load environment variables
load_dotenv()

# ✅ Default to SQLite for local development if no DATABASE_URL provided
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dev.db")


class Base(DeclarativeBase):
    """Declarative base for SQLAlchemy models."""
    pass


# ✅ Create database engine with connection args for SQLite
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
)

# ✅ Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_session():
    """Yield a database session for FastAPI dependencies."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ✅ Alias for dependency injection
get_db = get_session
