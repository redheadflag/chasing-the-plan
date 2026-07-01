from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

import app.models  # noqa: F401  register models on Base.metadata
from app.config import settings
from app.database import Base, get_db
from app.main import app

TEST_DB = "chasing_the_plan_test"
_base_url = settings.database_url.rsplit("/", 1)[0]
TEST_DB_URL = f"{_base_url}/{TEST_DB}"


@pytest.fixture(scope="session")
def engine():
    # Create the test database if it doesn't exist.
    admin = create_engine(f"{_base_url}/postgres", isolation_level="AUTOCOMMIT")
    with admin.connect() as conn:
        exists = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :n"), {"n": TEST_DB}
        ).scalar()
        if not exists:
            conn.execute(text(f'CREATE DATABASE "{TEST_DB}"'))
    admin.dispose()

    eng = create_engine(TEST_DB_URL)
    Base.metadata.drop_all(eng)
    Base.metadata.create_all(eng)
    yield eng
    eng.dispose()


@pytest.fixture
def client(engine) -> Iterator[TestClient]:
    # Clean slate before each test.
    tables = ", ".join(t.name for t in Base.metadata.sorted_tables)
    with engine.begin() as conn:
        conn.execute(text(f"TRUNCATE {tables} RESTART IDENTITY CASCADE"))

    TestingSessionLocal = sessionmaker(
        bind=engine, autoflush=False, expire_on_commit=False
    )

    def override_get_db() -> Iterator[Session]:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def sample_catalog(client: TestClient) -> dict[str, int]:
    """Seed a few muscle groups + exercises; return name -> exercise id."""
    body = {
        "create_missing_groups": True,
        "items": [
            {"muscle_group": "CROSSFIT", "name": "TURKISH GETUP", "url": "https://ex/tg"},
            {"muscle_group": "CROSSFIT", "name": "TRX LOW ROW", "url": None},
            {"muscle_group": "КОР", "name": "FLUTTER KICK", "url": "https://ex/fk"},
        ],
    }
    client.post("/api/exercises/bulk", json=body).raise_for_status()
    return {e["name"]: e["id"] for e in client.get("/api/exercises").json()}
