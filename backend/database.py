"""Database setup — sync SQLite for zero-config reliability."""

import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Auto-create DB directory if needed
_default_db = "sqlite:///./udara.db"
DB_PATH = os.environ.get("DATABASE_URL", _default_db)

_db_file = DB_PATH.replace("sqlite:///", "", 1) if DB_PATH.startswith("sqlite:///") else None
if _db_file:
    Path(_db_file).parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(DB_PATH, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def generate_uuid() -> str:
    return str(uuid.uuid4())


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def init_db():
    """Create all tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """FastAPI dependency — yields a session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
