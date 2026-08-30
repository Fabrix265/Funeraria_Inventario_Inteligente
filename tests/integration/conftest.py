import time
import pytest
from fastapi.testclient import TestClient
from src.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def admin_token(client):
    response = client.post(
        "/auth/login",
        data={"username": "fabAdmin", "password": "265336aaaa"}
    )
    assert response.status_code == 200, f"Login failed: {response.json()}"
    return response.json()["access_token"]


@pytest.fixture(scope="module")
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture(scope="module")
def admin_user_id(admin_token):
    from jose import jwt
    from src.core.security import SECURITY_KEY, ALGORITHM
    payload = jwt.decode(admin_token, SECURITY_KEY, algorithms=[ALGORITHM])
    return int(payload.get("sub"))


@pytest.fixture(scope="module")
def crear_ataud_para_test(client, admin_headers):
    ts = int(time.time())
    response = client.post(
        "/coffins/",
        headers=admin_headers,
        json={"modelo": f"Test Int Ataud {ts}", "color": "Blanco", "stock": 5}
    )
    assert response.status_code in [200, 201]
    return response.json()


@pytest.fixture(scope="module")
def crear_capilla_para_test(client, admin_headers):
    ts = int(time.time())
    response = client.post(
        "/chapels/",
        headers=admin_headers,
        json={"modelo": f"Test Int Capilla {ts}", "stock": 5}
    )
    assert response.status_code in [200, 201]
    return response.json()


def ts():
    return int(time.time())
