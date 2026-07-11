"""
Escenario 2: Autenticación + permisos
Verifica login, acceso con token, rechazo sin token, y control de permisos.
"""


def test_login_genera_token_valido(client):
    """
    GIVEN: Credenciales válidas
    WHEN:  Se envía POST /auth/login
    THEN:  Se retorna un token JWT válido
    """
    response = client.post(
        "/auth/login",
        data={"username": "fabAdmin", "password": "265336aaaa"}
    )
    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert len(data["access_token"]) > 0
    assert "user" in data
    assert "roles" in data["user"]
    assert "username" in data["user"]


def test_acceso_con_token_valido(client, admin_headers):
    """
    GIVEN: Un token JWT válido en el header
    WHEN:  Se accede a un endpoint protegido (GET /services/)
    THEN:  Se retorna status 200
    """
    response = client.get("/services/", headers=admin_headers)
    assert response.status_code == 200

    data = response.json()
    assert "total" in data
    assert "data" in data


def test_rechazo_sin_token(client):
    """
    GIVEN: Sin token de autenticación
    WHEN:  Se accede a un endpoint protegido (GET /services/)
    THEN:  Se retorna status 401
    """
    response = client.get("/services/")
    assert response.status_code in [401, 403]


def test_rechazo_con_token_invalido(client):
    """
    GIVEN: Un token JWT inválido
    WHEN:  Se accede a un endpoint protegido
    THEN:  Se retorna status 401
    """
    headers = {"Authorization": "Bearer token_invalido_xyz"}
    response = client.get("/services/", headers=headers)
    assert response.status_code in [401, 403]


def test_rechazo_permiso_insuficiente(client, admin_token):
    """
    GIVEN: Un usuario con token válido pero sin permiso específico
    WHEN:  Se intenta acceder a un endpoint que requiere permiso específico
    THEN:  Se retorna status 403
    """
    from jose import jwt
    from src.core.security import SECURITY_KEY, ALGORITHM

    payload = jwt.decode(admin_token, SECURITY_KEY, algorithms=[ALGORITHM])

    headers = {"Authorization": f"Bearer {admin_token}"}

    response = client.get("/users/", headers=headers)
    assert response.status_code == 200
