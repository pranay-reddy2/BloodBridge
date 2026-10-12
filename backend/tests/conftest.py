import os

# Point the app at an isolated in-memory SQLite database *before* it is imported,
# so the test suite can never touch a real PostgreSQL instance.
os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
os.environ["ENVIRONMENT"] = "test"

from datetime import date, timedelta  # noqa: E402

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app import models  # noqa: E402,F401
from app.db import Base, SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(autouse=True)
def fresh_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def db_session():
    with SessionLocal() as session:
        yield session


@pytest.fixture
def make_donor(client):
    counter = {"n": 0}

    def _make(**overrides):
        counter["n"] += 1
        payload = {
            "full_name": f"Donor {counter['n']}",
            "blood_group": "O+",
            "email": f"donor{counter['n']}@example.org",
            "phone": "+91 98765 43210",
            "city": "Pune",
        }
        payload.update(overrides)
        response = client.post("/api/donors", json=payload)
        assert response.status_code == 201, response.text
        return response.json()

    return _make


@pytest.fixture
def stock(client, make_donor):
    """Create `count` available units of a group/component, one donor per unit."""

    def _stock(blood_group: str, count: int = 1, component: str = "RED_CELLS", collected_on: date | None = None):
        units = []
        for _ in range(count):
            donor = make_donor(blood_group=blood_group)
            body = {"component": component, "volume_ml": 300}
            if collected_on:
                body["collected_on"] = collected_on.isoformat()
            response = client.post(f"/api/donors/{donor['id']}/donations", json=body)
            assert response.status_code == 201, response.text
            units.append(response.json())
        return units

    return _stock


@pytest.fixture
def days_ago():
    return lambda n: date.today() - timedelta(days=n)
