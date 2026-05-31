"""Test fixtures — sync SQLite for fast, isolated tests."""

import os
# Prevent static frontend mount during tests
os.environ.setdefault("STATIC_DIR", "/tmp/udara-test-nonexistent")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.database import Base, get_db
from backend.main import app

TEST_DB_URL = "sqlite:///./test_udara.db"
test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    """Create tables before each test, drop after."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client():
    """Sync HTTP test client."""
    return TestClient(app)


@pytest.fixture
def db():
    """Direct DB session for assertions."""
    db = TestSession()
    try:
        yield db
    finally:
        db.close()
