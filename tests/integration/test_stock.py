"""
Escenario 3: Gestión de stock con restricciones
Verifica que el stock se actualice correctamente y que no se permita stock negativo.
"""
import time


def test_actualizar_stock_positivo(client, admin_headers):
    """
    GIVEN: Un ataúd existente
    WHEN:  Se agrega stock positivo (+3)
    THEN:  El stock se incrementa correctamente
    """
    response = client.get("/coffins/", headers=admin_headers)
    ataudes = response.json()
    assert len(ataudes) > 0, "No hay ataúdes"

    ataud = ataudes[0]
    stock_inicial = ataud["stock"]

    response = client.patch(
        f"/coffins/{ataud['id']}/stock",
        headers=admin_headers,
        json={"cantidad": 3}
    )
    assert response.status_code == 200
    assert response.json()["stock"] == stock_inicial + 3

    # Restaurar stock original
    client.patch(
        f"/coffins/{ataud['id']}/stock",
        headers=admin_headers,
        json={"cantidad": -3}
    )


def test_no_permitir_stock_negativo(client, admin_headers):
    """
    GIVEN: Un ataúd con stock limitado
    WHEN:  Se intenta reducir el stock por debajo de 0
    THEN:  Se retorna status 400
    """
    ts = int(time.time())
    response_crear = client.post(
        "/coffins/",
        headers=admin_headers,
        json={"modelo": f"Test Stock {ts}", "color": "Rojo", "stock": 2}
    )
    assert response_crear.status_code in [200, 201]
    ataud_id = response_crear.json()["id"]

    response = client.patch(
        f"/coffins/{ataud_id}/stock",
        headers=admin_headers,
        json={"cantidad": -5}
    )
    assert response.status_code == 400

    # Limpiar
    client.delete(f"/coffins/{ataud_id}", headers=admin_headers)


def test_stock_en_capillas(client, admin_headers):
    """
    GIVEN: Una capilla existente
    WHEN:  Se actualiza su stock positiva y negativamente
    THEN:  El stock se modifica correctamente
    """
    ts = int(time.time())
    response_crear = client.post(
        "/chapels/",
        headers=admin_headers,
        json={"modelo": f"Test Capilla Stock {ts}", "stock": 10}
    )
    assert response_crear.status_code in [200, 201]
    capilla_id = response_crear.json()["id"]

    # Agregar stock
    response = client.patch(
        f"/chapels/{capilla_id}/stock",
        headers=admin_headers,
        json={"cantidad": 5}
    )
    assert response.status_code == 200
    assert response.json()["stock"] == 15

    # Reducir stock
    response = client.patch(
        f"/chapels/{capilla_id}/stock",
        headers=admin_headers,
        json={"cantidad": -7}
    )
    assert response.status_code == 200
    assert response.json()["stock"] == 8

    # Intentar reducir más de lo disponible
    response = client.patch(
        f"/chapels/{capilla_id}/stock",
        headers=admin_headers,
        json={"cantidad": -10}
    )
    assert response.status_code == 400

    # Verificar que el stock no cambió consultando de nuevo
    response_verificar = client.get("/chapels/", headers=admin_headers)
    capillas = response_verificar.json()
    capilla_actual = next((c for c in capillas if c["id"] == capilla_id), None)
    assert capilla_actual is not None
    assert capilla_actual["stock"] == 8

    # Limpiar
    client.delete(f"/chapels/{capilla_id}", headers=admin_headers)
