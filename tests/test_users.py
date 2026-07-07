"""
Escenarios de usuarios:
- Escenario 2: Obtener lista de usuarios
- Escenario 3: Crear un usuario nuevo
- Escenario 4: Cambiar estado de usuario
"""
import time


def test_obtener_lista_usuarios(client, admin_headers):
    """
    GIVEN: Un administrador autenticado
    WHEN: Se envía GET /users/
    THEN: Se retorna una lista de usuarios
    """
    response = client.get("/users/", headers=admin_headers)

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)

    assert len(data) > 0

    for usuario in data:
        assert "id" in usuario
        assert "username" in usuario
        assert "activo" in usuario
        assert "roles" in usuario


def test_crear_usuario_nuevo(client, admin_headers):
    """
    GIVEN: Un administrador autenticado con datos válidos
    WHEN: Se envía POST /users/ con username, password y role_id
    THEN: Se crea el usuario correctamente
    """
    unique_username = f"test_user_{int(time.time())}"

    response = client.post(
        "/users/",
        headers=admin_headers,
        json={
            "username": unique_username,
            "password": "pass123",
            "role_id": 1
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["username"] == unique_username
    assert "id" in data
    assert data["activo"] is True
    assert len(data["roles"]) > 0


def test_cambiar_estado_usuario(client, admin_headers, admin_user_id):
    """
    GIVEN: Un administrador autenticado
    WHEN: Se envía PATCH /users/{id}/status con activo: true
    THEN: Se retorna el usuario con el estado actualizado
    """
    response = client.get("/users/", headers=admin_headers)
    usuarios = response.json()

    usuario_test = None
    for u in usuarios:
        if u["id"] != admin_user_id:
            usuario_test = u
            break

    if usuario_test is None:
        unique_username = f"test_status_{int(time.time())}"
        create_response = client.post(
            "/users/",
            headers=admin_headers,
            json={
                "username": unique_username,
                "password": "pass123",
                "role_id": 1
            }
        )
        assert create_response.status_code == 200
        usuario_test = create_response.json()

    nuevo_estado = not usuario_test["activo"]
    response = client.patch(
        f"/users/{usuario_test['id']}/status",
        headers=admin_headers,
        json={"activo": nuevo_estado}
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == usuario_test["id"]
    assert data["activo"] == nuevo_estado
