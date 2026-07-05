"""
Escenario 1: Login exitoso
Verifica que un usuario con credenciales válidas pueda iniciar sesión
y reciba un token JWT válido.
"""


def test_login_exitoso(client):
    """
    GIVEN: Un usuario registrado con credenciales correctas
    WHEN: Se envía POST /auth/login con username y password
    THEN: Se retorna un token de acceso válido
    """
    response = client.post(
        "/auth/login",
        data={"username": "fabAdmin", "password": "265336aaaa"}
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert "token_type" in data

    assert data["token_type"] == "bearer"

    assert len(data["access_token"]) > 0

    assert "user" in data
    assert "username" in data["user"]
    assert data["user"]["username"] == "fabAdmin"
    assert "roles" in data["user"]
