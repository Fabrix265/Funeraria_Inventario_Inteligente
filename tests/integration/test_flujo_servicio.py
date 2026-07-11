"""
Escenario 1: Flujo completo de servicio
Crea un servicio con todos sus componentes, lo obtiene, y lo elimina verificando cascade.
"""
import time


def test_flujo_completo_servicio(client, admin_headers, crear_ataud_para_test, crear_capilla_para_test):
    """
    GIVEN: Ataúd y capilla disponibles con stock
    WHEN:  Se crea un servicio completo, se obtiene, y se elimina
    THEN:  El servicio se crea con status 201, se obtiene con todas las relaciones,
           y al eliminar se restaura el stock
    """
    timestamp = int(time.time())
    ataud = crear_ataud_para_test
    capilla = crear_capilla_para_test

    stock_ataud_inicial = ataud["stock"]
    stock_capilla_inicial = capilla["stock"]

    servicio_data = {
        "id_ataud": ataud["id"],
        "id_capilla": capilla["id"],
        "direccion_velacion": f"Av. Integracion {timestamp}",
        "tipo_pago": "directo",
        "costo": 2500.00,
        "fecha": "2026-08-15",
        "cantidad_cargadores": None,
        "fallecido": {
            "nombre": f"Juan Integracion {timestamp}",
            "dni_fallecido": f"1111{timestamp % 10000:04d}"
        },
        "contratante": {
            "nombre": f"Maria Integracion {timestamp}",
            "dni": f"2222{timestamp % 10000:04d}",
            "telefono": f"9{timestamp % 100000000:08d}"
        },
        "ids_vehiculos": [],
        "pasajeros": []
    }

    # CREAR
    response_crear = client.post(
        "/services/",
        headers=admin_headers,
        json=servicio_data
    )
    assert response_crear.status_code in [200, 201], f"Error al crear: {response_crear.json()}"
    servicio_creado = response_crear.json()
    servicio_id = servicio_creado["id"]

    assert servicio_creado["direccion_velacion"] == f"Av. Integracion {timestamp}"
    assert servicio_creado["tipo_pago"] == "directo"
    assert float(servicio_creado["costo"]) == 2500.00
    assert "fallecido" in servicio_creado
    assert "contratante" in servicio_creado
    assert servicio_creado["fallecido"]["nombre"] == f"Juan Integracion {timestamp}"
    assert servicio_creado["contratante"]["dni"] == f"2222{timestamp % 10000:04d}"

    # Verificar stock a través de la lista
    response_ataudes = client.get("/coffins/", headers=admin_headers)
    assert response_ataudes.status_code == 200
    ataud_actual = next((a for a in response_ataudes.json() if a["id"] == ataud["id"]), None)
    assert ataud_actual is not None
    assert ataud_actual["stock"] == stock_ataud_inicial - 1

    response_capillas = client.get("/chapels/", headers=admin_headers)
    assert response_capillas.status_code == 200
    capilla_actual = next((c for c in response_capillas.json() if c["id"] == capilla["id"]), None)
    assert capilla_actual is not None
    assert capilla_actual["stock"] == stock_capilla_inicial - 1

    # OBTENER
    response_obtener = client.get(
        f"/services/{servicio_id}",
        headers=admin_headers
    )
    assert response_obtener.status_code == 200
    servicio_detalle = response_obtener.json()
    assert servicio_detalle["id"] == servicio_id
    assert "fallecido" in servicio_detalle
    assert "contratante" in servicio_detalle
    assert "capilla" in servicio_detalle

    # ELIMINAR
    response_eliminar = client.delete(
        f"/services/{servicio_id}",
        headers=admin_headers
    )
    assert response_eliminar.status_code == 200
    assert "message" in response_eliminar.json()

    # Verificar que el stock se restauró
    response_ataudes_final = client.get("/coffins/", headers=admin_headers)
    ataud_final = next((a for a in response_ataudes_final.json() if a["id"] == ataud["id"]), None)
    assert ataud_final is not None
    assert ataud_final["stock"] == stock_ataud_inicial

    response_capillas_final = client.get("/chapels/", headers=admin_headers)
    capilla_final = next((c for c in response_capillas_final.json() if c["id"] == capilla["id"]), None)
    assert capilla_final is not None
    assert capilla_final["stock"] == stock_capilla_inicial

    # Verificar que el servicio ya no existe
    response_verificar = client.get(
        f"/services/{servicio_id}",
        headers=admin_headers
    )
    assert response_verificar.status_code == 404
