"""
El detalle de la bitácora para archivos debe registrar el nombre
estandarizado (tipo_fallecido_dni.ext) que define archivo_service,
y no el nombre crudo con el que el usuario subió el archivo.
"""
import time


def _png():
    # No se valida el contenido, solo el mime type y el tamaño.
    return b"\x89PNG\r\n\x1a\n" + b"\x00" * 64


def test_subir_archivo_registra_nombre_estandarizado(
    client, admin_headers, crear_ataud_para_test, crear_capilla_para_test
):
    timestamp = int(time.time())
    servicio_data = {
        "id_ataud": crear_ataud_para_test["id"],
        "id_capilla": crear_capilla_para_test["id"],
        "direccion_velacion": f"Av. Bitacora {timestamp}",
        "tipo_pago": "directo",
        "costo": 1000.00,
        "fecha": "2026-08-15",
        "cantidad_cargadores": None,
        "fallecido": {
            "nombre": f"Ana Bitacora {timestamp}",
            "dni_fallecido": f"3333{timestamp % 10000:04d}",
        },
        "contratante": {
            "nombre": f"Luis Bitacora {timestamp}",
            "dni": f"4444{timestamp % 10000:04d}",
            "telefono": f"9{timestamp % 100000000:08d}",
        },
        "ids_vehiculos": [],
    }

    respuesta = client.post("/services/", headers=admin_headers, json=servicio_data)
    assert respuesta.status_code in [200, 201], respuesta.json()
    servicio_id = respuesta.json()["id"]
    dni_fallecido = servicio_data["fallecido"]["dni_fallecido"]
    nombre_cruudo = "MI documento PRIVADO #42.png"

    try:
        subida = client.post(
            f"/services/{servicio_id}/archivos",
            headers=admin_headers,
            data={"tipo": "acta"},
            files={"file": (nombre_cruudo, _png(), "image/png")},
        )
        assert subida.status_code == 201, subida.json()

        estandar = subida.json()["nombre_original"]
        assert estandar.startswith("acta_")
        assert estandar.endswith(".png")
        assert dni_fallecido in estandar
        assert "MI documento PRIVADO" not in estandar

        # La bitácora debe citar el nombre estandarizado, no el original.
        bitacora = client.get(
            "/bitacora/",
            headers=admin_headers,
            params={"modulo": "archivos", "accion": "crear", "limit": 5},
        )
        assert bitacora.status_code == 200
        detalles = [i["detalle"] or "" for i in bitacora.json()["items"]]
        entrada = next(
            (d for d in detalles if f"servicio #{servicio_id}" in d),
            None,
        )
        assert entrada is not None, f"No se registró la subida en la bitácora: {detalles}"
        assert estandar in entrada, entrada
        assert "MI documento PRIVADO" not in entrada, entrada
    finally:
        archivos = client.get(
            f"/services/{servicio_id}/archivos", headers=admin_headers
        )
        if archivos.status_code == 200:
            for item in archivos.json().get("archivos", []):
                client.delete(
                    f"/services/{servicio_id}/archivos/{item['id']}",
                    headers=admin_headers,
                )
        client.delete(f"/services/{servicio_id}", headers=admin_headers)


def test_reemplazar_archivo_tambien_usa_nombre_estandarizado(
    client, admin_headers, crear_ataud_para_test, crear_capilla_para_test
):
    timestamp = int(time.time())
    servicio_data = {
        "id_ataud": crear_ataud_para_test["id"],
        "id_capilla": crear_capilla_para_test["id"],
        "direccion_velacion": f"Av. Bitacora 2 {timestamp}",
        "tipo_pago": "directo",
        "costo": 1000.00,
        "fecha": "2026-08-15",
        "cantidad_cargadores": None,
        "fallecido": {
            "nombre": f"Rosa Bitacora {timestamp}",
            "dni_fallecido": f"5555{timestamp % 10000:04d}",
        },
        "contratante": {
            "nombre": f"Pedro Bitacora {timestamp}",
            "dni": f"6666{timestamp % 10000:04d}",
            "telefono": f"9{timestamp % 100000000:08d}",
        },
        "ids_vehiculos": [],
    }

    respuesta = client.post("/services/", headers=admin_headers, json=servicio_data)
    assert respuesta.status_code in [200, 201], respuesta.json()
    servicio_id = respuesta.json()["id"]

    try:
        subida = client.post(
            f"/services/{servicio_id}/archivos",
            headers=admin_headers,
            data={"tipo": "acta"},
            files={"file": ("primera_version.png", _png(), "image/png")},
        )
        assert subida.status_code == 201, subida.json()
        archivo_id = subida.json()["id"]

        reemplazo = client.put(
            f"/services/{servicio_id}/archivos/{archivo_id}",
            headers=admin_headers,
            files={"file": ("segunda_version.png", _png(), "image/png")},
        )
        assert reemplazo.status_code == 200, reemplazo.json()
        estandar = reemplazo.json()["nombre_original"]
        assert estandar.startswith("acta_")
        assert "segunda_version" not in estandar

        bitacora = client.get(
            "/bitacora/",
            headers=admin_headers,
            params={"modulo": "archivos", "accion": "actualizar", "limit": 5},
        )
        assert bitacora.status_code == 200
        detalles = [i["detalle"] or "" for i in bitacora.json()["items"]]
        entrada = next(
            (d for d in detalles if f"servicio #{servicio_id}" in d),
            None,
        )
        assert entrada is not None, f"No se registró el reemplazo en la bitácora: {detalles}"
        assert estandar in entrada, entrada
        assert "segunda_version" not in entrada, entrada
    finally:
        archivos = client.get(
            f"/services/{servicio_id}/archivos", headers=admin_headers
        )
        if archivos.status_code == 200:
            for item in archivos.json().get("archivos", []):
                client.delete(
                    f"/services/{servicio_id}/archivos/{item['id']}",
                    headers=admin_headers,
                )
        client.delete(f"/services/{servicio_id}", headers=admin_headers)
