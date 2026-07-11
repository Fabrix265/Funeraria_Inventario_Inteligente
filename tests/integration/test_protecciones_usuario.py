"""
Escenario 4: Protecciones de usuario
Verifica que no se pueda desactivar a uno mismo ni al último admin.
"""
import time


def test_no_puede_desactivar_su_propia_cuenta(client, admin_headers, admin_user_id):
    """
    GIVEN: Un administrador autenticado
    WHEN:  Intenta desactivar su propia cuenta
    THEN:  Se retorna status 400
    """
    response = client.patch(
        f"/users/{admin_user_id}/status",
        headers=admin_headers,
        json={"activo": False}
    )
    assert response.status_code == 400


def test_no_puede_desactivar_ultimo_admin(client, admin_headers, admin_user_id):
    """
    GIVEN: Solo hay un administrador activo
    WHEN:  Se intenta desactivar al único admin
    THEN:  Se retorna status 400
    """
    response = client.get("/users/", headers=admin_headers)
    usuarios = response.json()

    admins_activos = [
        u for u in usuarios
        if any(r.get("nombre", "").lower() == "administrador" for r in u.get("roles", []))
        and u["activo"]
    ]

    if len(admins_activos) > 1:
        return

    response = client.patch(
        f"/users/{admin_user_id}/status",
        headers=admin_headers,
        json={"activo": False}
    )
    assert response.status_code == 400


def test_crear_usuario_username_unico(client, admin_headers):
    """
    GIVEN: Un administrador autenticado
    WHEN:  Intenta crear un usuario con un username ya existente
    THEN:  Se retorna status 400
    """
    ts = int(time.time())
    username = f"test_int_{ts}"

    response1 = client.post(
        "/users/",
        headers=admin_headers,
        json={"username": username, "password": "pass123", "role_id": 1}
    )
    assert response1.status_code == 200
    user_id = response1.json()["id"]

    response2 = client.post(
        "/users/",
        headers=admin_headers,
        json={"username": username, "password": "pass456", "role_id": 1}
    )
    assert response2.status_code == 400

    # Limpiar
    client.delete(f"/users/{user_id}", headers=admin_headers)


def test_crear_usuario_con_rol_inexistente(client, admin_headers):
    """
    GIVEN: Un administrador autenticado
    WHEN:  Intenta crear un usuario con role_id inexistente
    THEN:  Se retorna status 404
    """
    ts = int(time.time())
    response = client.post(
        "/users/",
        headers=admin_headers,
        json={"username": f"test_no_rol_{ts}", "password": "pass123", "role_id": 99999}
    )
    assert response.status_code == 404
