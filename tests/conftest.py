"""
Shared pytest fixtures.

Each test gets a FRESH in-memory database via the db_reset fixture,
so tests are fully isolated from each other.
"""
import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings, Settings
from app.main import create_app
from app.models.domain import PLANTS_DB, USERS_DB, USERNAME_INDEX, UserInDB
from app.core.security import hash_password


# ── Test Settings override ─────────────────────────────────────────────────────

@pytest.fixture(scope="session", autouse=True)
def override_settings():
    """Use a known secret key in tests — avoids env file dependency."""
    import os
    import app.core.config as cfg_module

    # Set environment variables before Settings is loaded
    os.environ["SECRET_KEY"] = "test-secret-key-that-is-long-enough-32chars"
    os.environ["ENVIRONMENT"] = "development"
    os.environ["DEBUG"] = "True"
    os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"
    os.environ["RATE_LIMIT_REQUESTS"] = "1000"

    # Clear the cache so next call loads fresh settings with new env vars
    cfg_module.get_settings.cache_clear()

    # Call get_settings to load and cache the test settings
    test_settings = cfg_module.get_settings()
    
    # Verify settings were loaded correctly
    assert test_settings.secret_key == "test-secret-key-that-is-long-enough-32chars", \
        f"Secret key mismatch: {test_settings.secret_key}"

    yield test_settings


# ── DB isolation ───────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def db_reset():
    """
    Reset the in-memory DBs before every test.
    Seeds three standard users so auth tests work out of the box.
    """
    PLANTS_DB.clear()
    USERS_DB.clear()
    USERNAME_INDEX.clear()

    # Seed test users
    test_users = [
        UserInDB(id="user-admin-id", username="admin",
                 email="admin@test.com", hashed_password=hash_password("Admin@123"),
                 role="admin"),
        UserInDB(id="user-operator-id", username="operator",
                 email="operator@test.com", hashed_password=hash_password("Operator@123"),
                 role="operator"),
        UserInDB(id="user-viewer-id", username="viewer",
                 email="viewer@test.com", hashed_password=hash_password("Viewer@123"),
                 role="viewer"),
    ]
    for u in test_users:
        USERS_DB[u.id] = u
        USERNAME_INDEX[u.username] = u.id

    yield

    PLANTS_DB.clear()


# ── Test client ────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def app():
    return create_app()


@pytest.fixture
def client(app):
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


# ── Auth helper fixtures ───────────────────────────────────────────────────────

def _login(client, username: str, password: str) -> dict:
    resp = client.post("/api/v1/auth/login", json={"username": username, "password": password})
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    return resp.json()


@pytest.fixture
def admin_token(client) -> str:
    return _login(client, "admin", "Admin@123")["access_token"]


@pytest.fixture
def operator_token(client) -> str:
    return _login(client, "operator", "Operator@123")["access_token"]


@pytest.fixture
def viewer_token(client) -> str:
    return _login(client, "viewer", "Viewer@123")["access_token"]


@pytest.fixture
def admin_headers(admin_token) -> dict:
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def operator_headers(operator_token) -> dict:
    return {"Authorization": f"Bearer {operator_token}"}


@pytest.fixture
def viewer_headers(viewer_token) -> dict:
    return {"Authorization": f"Bearer {viewer_token}"}


# ── Plant factory ──────────────────────────────────────────────────────────────

VALID_PLANT = {
    "name": "Test Plant Alpha",
    "location": "Bangalore, India",
    "status": "operational",
    "capacity_kw": 5000.0,
    "uptime_percent": 98.5,
}
