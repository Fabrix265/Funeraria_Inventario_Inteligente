"""
Escenarios de ataúdes:
- Escenario 5: Obtener lista de ataúdes
- Escenario 6: Crear un ataúd nuevo
- Escenario 7: Actualizar stock de ataúd
"""
import time


def test_obtener_lista_ataudes(client, admin_headers):
    """
    GIVEN: Un administrador autenticado
    WHEN: Se envía GET /coffins/
    THEN: Se retorna una lista de ataúdes
    """
    response = client.get("/coffins/", headers=admin_headers)

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)

    for ataud in data:
        assert "id" in ataud
        assert "modelo" in ataud
        assert "color" in ataud
        assert "stock" in ataud
        assert "activo" in ataud


def test_crear_ataud_nuevo(client, admin_headers):
    """
    GIVEN: Un administrador autenticado con datos válidos
    WHEN: Se envía POST /coffins/ con modelo, color y stock
    THEN: Se crea el ataúd correctamente
    """
    unique_modelo = f"Test Ataud {int(time.time())}"

    response = client.post(
        "/coffins/",
        headers=admin_headers,
        json={
            "modelo": unique_modelo,
            "color": "Blanco",
            "stock": 5
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["modelo"] == unique_modelo
    assert data["color"] == "Blanco"
    assert data["stock"] == 5
    assert data["activo"] is True
    assert "id" in data


def test_actualizar_stock_ataud(client, admin_headers):
    """
    GIVEN: Un administrador autenticado y un ataúd existente
    WHEN: Se envía PATCH /coffins/{id}/stock con cantidad positiva
    THEN: Se actualiza el stock correctamente
    """
    response = client.get("/coffins/", headers=admin_headers)
    ataudes = response.json()

    assert len(ataudes) > 0, "No hay ataúdes en la base de datos"

    ataud = ataudes[0]
    stock_inicial = ataud["stock"]

    response = client.patch(
        f"/coffins/{ataud['id']}/stock",
        headers=admin_headers,
        json={"cantidad": 3}
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == ataud["id"]
    assert data["stock"] == stock_inicial + 3
