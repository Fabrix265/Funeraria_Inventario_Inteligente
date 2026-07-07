"""
Escenarios de servicios:
- Escenario 8: Obtener lista de servicios
- Escenario 9: Obtener un servicio específico
- Escenario 10: Eliminar un servicio
"""
import time


def test_obtener_lista_servicios(client, admin_headers):
    """
    GIVEN: Un administrador autenticado
    WHEN: Se envía GET /services/
    THEN: Se retorna una lista paginada de servicios
    """
    response = client.get("/services/", headers=admin_headers)

    assert response.status_code == 200

    data = response.json()

    assert "total" in data
    assert "offset" in data
    assert "limit" in data
    assert "data" in data

    assert isinstance(data["data"], list)

    assert data["offset"] == 0
    assert data["limit"] == 20


def test_obtener_servicio_especifico(client, admin_headers):
    """
    GIVEN: Un administrador autenticado y servicios existentes
    WHEN: Se envía GET /services/{id} con un ID válido
    THEN: Se retorna el servicio completo con todos sus datos
    """
    response = client.get("/services/", headers=admin_headers)
    servicios = response.json()["data"]

    if len(servicios) == 0:
        return

    servicio = servicios[0]

    response = client.get(
        f"/services/{servicio['id']}",
        headers=admin_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == servicio["id"]
    assert "direccion_velacion" in data
    assert "tipo_pago" in data
    assert "costo" in data
    assert "fecha" in data

    assert "fallecido" in data
    assert "contratante" in data
    assert "capilla" in data


def test_eliminar_servicio(client, admin_headers):
    """
    GIVEN: Un administrador autenticado y un servicio existente
    WHEN: Se envía DELETE /services/{id} con un ID válido
    THEN: Se elimina el servicio correctamente
    """
    response = client.get("/services/", headers=admin_headers)
    servicios = response.json()["data"]

    if len(servicios) == 0:
        response_ataudes = client.get("/coffins/", headers=admin_headers)
        ataudes = response_ataudes.json()

        if len(ataudes) == 0:
            return 

        ataud_con_stock = None
        for at in ataudes:
            if at["stock"] > 0:
                ataud_con_stock = at
                break

        if ataud_con_stock is None:
            return 

        response_capillas = client.get("/chapels/", headers=admin_headers)
        capillas = response_capillas.json()

        capilla_con_stock = None
        for cap in capillas:
            if cap["stock"] > 0:
                capilla_con_stock = cap
                break

        if capilla_con_stock is None:
            return  

        timestamp = int(time.time())
        servicio_data = {
            "id_ataud": ataud_con_stock["id"],
            "id_capilla": capilla_con_stock["id"],
            "direccion_velacion": f"Av. Test {timestamp}",
            "tipo_pago": "efectivo",
            "costo": 1500.00,
            "fecha": "2026-07-04",
            "cantidad_cargadores": None,
            "fallecido": {
                "nombre": f"Juan Perez {timestamp}",
                "dni_fallecido": f"1234{timestamp % 10000:04d}"
            },
            "contratante": {
                "nombre": f"Maria Garcia {timestamp}",
                "dni": f"5678{timestamp % 10000:04d}",
                "telefono": f"9{timestamp % 10000000:07d}"
            },
            "ids_vehiculos": []
        }

        response = client.post(
            "/services/",
            headers=admin_headers,
            json=servicio_data
        )

        if response.status_code != 201:
            return  

        servicio = response.json()
        servicios = [servicio]

    servicio_a_eliminar = servicios[-1]
    servicio_id = servicio_a_eliminar["id"]

    response = client.delete(
        f"/services/{servicio_id}",
        headers=admin_headers
    )

    assert response.status_code == 200

    data = response.json()
    assert "message" in data
