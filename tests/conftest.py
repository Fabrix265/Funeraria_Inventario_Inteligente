import pytest
from fastapi.testclient import TestClient
from src.main import app


@pytest.fixture(scope="module")
def client():
    """Create a test client for the entire test module."""
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def admin_token(client):
    """Login as admin and return the access token."""
    response = client.post(
        "/auth/login",
        data={"username": "fabAdmin", "password": "265336aaaa"}
    )
    assert response.status_code == 200, f"Login failed: {response.json()}"
    return response.json()["access_token"]


@pytest.fixture(scope="module")
def admin_headers(admin_token):
    """Return authorization headers for admin user."""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture(scope="module")
def admin_user_id(admin_token):
    """Extract user ID from the admin token."""
    from jose import jwt
    from src.core.security import SECURITY_KEY, ALGORITHM
    payload = jwt.decode(admin_token, SECURITY_KEY, algorithms=[ALGORITHM])
    return int(payload.get("sub"))
