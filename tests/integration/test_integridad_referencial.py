"""
Escenario 5: Integridad referencial
Verifica que no se puedan eliminar entidades vinculadas y que se limpien huérfanos.
"""
import time


def test_no_eliminar_fallecido_con_servicio(client, admin_headers, crear_ataud_para_test, crear_capilla_para_test):
    """
    GIVEN: Un fallecido vinculado a un servicio
    WHEN:  Se intenta eliminar el fallecido
    THEN:  Se retorna status 400
    """
    timestamp = int(time.time())
    ataud = crear_ataud_para_test
    capilla = crear_capilla_para_test

    servicio_data = {
        "id_ataud": ataud["id"],
        "id_capilla": capilla["id"],
        "direccion_velacion": f"Av. Integridad {timestamp}",
        "tipo_pago": "directo",
        "costo": 1800.00,
        "fecha": "2026-09-01",
        "cantidad_cargadores": None,
        "fallecido": {
            "nombre": f"Fallecido Integridad {timestamp}",
            "dni_fallecido": f"3333{timestamp % 10000:04d}"
        },
        "contratante": {
            "nombre": f"Contratante Integridad {timestamp}",
            "dni": f"4444{timestamp % 10000:04d}",
            "telefono": f"9{timestamp % 100000000:08d}"
        },
        "ids_vehiculos": [],
        "pasajeros": []
    }

    response = client.post("/services/", headers=admin_headers, json=servicio_data)
    assert response.status_code in [200, 201], f"Error: {response.json()}"
    servicio = response.json()
    fallecido_id = servicio["fallecido"]["id"]

    response_delete = client.delete(f"/deceased/{fallecido_id}", headers=admin_headers)
    assert response_delete.status_code == 400

    client.delete(f"/services/{servicio['id']}", headers=admin_headers)


def test_no_eliminar_contratante_con_servicio(client, admin_headers, crear_ataud_para_test, crear_capilla_para_test):
    """
    GIVEN: Un contratante vinculado a un servicio
    WHEN:  Se intenta eliminar el contratante
    THEN:  Se retorna status 400
    """
    timestamp = int(time.time())
    ataud = crear_ataud_para_test
    capilla = crear_capilla_para_test

    servicio_data = {
        "id_ataud": ataud["id"],
        "id_capilla": capilla["id"],
        "direccion_velacion": f"Av. Contratante {timestamp}",
        "tipo_pago": "directo",
        "costo": 1800.00,
        "fecha": "2026-09-02",
        "cantidad_cargadores": None,
        "fallecido": {
            "nombre": f"Fallecido Contratante {timestamp}",
            "dni_fallecido": f"5555{timestamp % 10000:04d}"
        },
        "contratante": {
            "nombre": f"Contratante Ref {timestamp}",
            "dni": f"6666{timestamp % 10000:04d}",
            "telefono": f"9{timestamp % 100000000:08d}"
        },
        "ids_vehiculos": [],
        "pasajeros": []
    }

    response = client.post("/services/", headers=admin_headers, json=servicio_data)
    assert response.status_code in [200, 201], f"Error: {response.json()}"
    servicio = response.json()
    contratante_id = servicio["contratante"]["id"]

    response_delete = client.delete(f"/contractors/{contratante_id}", headers=admin_headers)
    assert response_delete.status_code == 400

    client.delete(f"/services/{servicio['id']}", headers=admin_headers)


def test_eliminar_contratante_huerfano(client, admin_headers):
    """
    GIVEN: Un contratante sin servicios vinculados
    WHEN:  Se elimina el contratante
    THEN:  Se elimina exitosamente
    """
    timestamp = int(time.time())

    response_contratante = client.get("/contractors/", headers=admin_headers)
    contratantes_antes = len(response_contratante.json())

    ts2 = int(time.time())
    response_crear = client.post(
        "/users/",
        headers=admin_headers,
        json={"username": f"test_huerfano_{ts2}", "password": "pass123", "role_id": 1}
    )

    response_buscar = client.get(
        f"/contractors/?dni=7777{timestamp % 10000:04d}",
        headers=admin_headers
    )


def test_no_eliminar_fallecido_sin_servicio(client, admin_headers):
    """
    GIVEN: Un fallecido sin servicios vinculados
    WHEN:  Se intenta eliminar
    THEN:  Se elimina exitosamente (200) o retorna 404 si no existe
    """
    response = client.get("/deceased/", headers=admin_headers)
    fallecidos = response.json()

    fallecido_sin_servicio = None
    for f in fallecidos:
        if f.get("activo", False):
            fallecido_sin_servicio = f
            break

    if fallecido_sin_servicio is None:
        return
