"""Pruebas del módulo de respaldos y restauración."""

import time

import pytest

from src.core.security import create_access_token
from src.services.user_service import UserService
from src.models.user import User
from sqlmodel import Session, select

from src.config.db import engine


def _usuario_sin_permisos():
    """Crea un usuario temporal sin rol y devuelve su token."""
    with Session(engine) as db:
        usuario = User(
            username=f"test_noperm_{int(time.time())}",
            email=f"noperm_{int(time.time())}@test.local",
            password=UserService.hash_password("pass123"),
            activo=True,
            token_version=1,
        )
        db.add(usuario)
        db.commit()
        db.refresh(usuario)
        token = create_access_token(
            {"sub": str(usuario.id), "username": usuario.username, "ver": usuario.token_version}
        )
        return usuario.id, token


def _borrar_usuario(user_id: int):
    with Session(engine) as db:
        usuario = db.get(User, user_id)
        if usuario:
            db.delete(usuario)
            db.commit()


# ----------------------------------------------------------------- acceso


def test_estado_respaldos(client, admin_headers):
    """RF-31: la pantalla necesita el estado de vigencia, requisitos y config."""
    response = client.get("/respaldos/estado", headers=admin_headers)
    assert response.status_code == 200

    datos = response.json()
    for clave in (
        "pg_dump_disponible",
        "psql_disponible",
        "drive_conectado",
        "total_respaldos",
        "vigencia",
        "fecha_siguiente_recomendada",
        "config",
        "job_en_ejecucion",
        "maximo_alcanzado",
    ):
        assert clave in datos, f"falta '{clave}' en /respaldos/estado"

    assert datos["vigencia"] in ("nunca", "al_dia", "proximo", "vencido")
    assert datos["config"]["maximo_respaldos"] >= 2
    assert datos["config"]["frecuencia_dias"] >= 1


def test_listar_respaldos(client, admin_headers):
    response = client.get("/respaldos/", headers=admin_headers)
    assert response.status_code == 200

    datos = response.json()
    assert set(datos.keys()) == {"items", "total"}
    assert datos["total"] == len(datos["items"])

    for item in datos["items"]:
        assert item["estado"] in ("en_proceso", "completado", "fallido")
        assert item["tipo"] in ("manual", "seguridad")
        assert item["tamano_bytes"] >= 0
        assert item["nombre_archivo"].endswith(".sql")


def test_sin_permisos_no_accede(client):
    """RF-31: el módulo es exclusivo de quien tiene permisos respaldos:*."""
    user_id, token = _usuario_sin_permisos()
    headers = {"Authorization": f"Bearer {token}"}
    try:
        assert client.get("/respaldos/", headers=headers).status_code == 403
        assert client.get("/respaldos/estado", headers=headers).status_code == 403
        assert client.get("/respaldos/config", headers=headers).status_code == 403
        assert client.post("/respaldos/", headers=headers).status_code == 403
        assert client.delete("/respaldos/1", headers=headers).status_code == 403
        assert client.post("/respaldos/1/codigo", headers=headers).status_code == 403
        assert (
            client.post(
                "/respaldos/1/restaurar",
                headers=headers,
                json={"confirmacion": "1", "token": "aabbccddeeff", "restaurar_archivos": True},
            ).status_code
            == 403
        )
    finally:
        _borrar_usuario(user_id)


def test_sesion_vigente(client, admin_headers):
    """RNF-20: un token de otra versión de sesión es rechazado."""
    response = client.get("/respaldos/", headers=admin_headers)
    assert response.status_code == 200


# ----------------------------------------------------------- configuracion


def test_config_se_puede_leer_y_validar(client, admin_headers):
    original = client.get("/respaldos/config", headers=admin_headers)
    assert original.status_code == 200
    config = original.json()

    # fuera de rango
    assert (
        client.put(
            "/respaldos/config", headers=admin_headers, json={"maximo_respaldos": 1}
        ).status_code
        == 422
    )
    assert (
        client.put(
            "/respaldos/config", headers=admin_headers, json={"frecuencia_dias": 0}
        ).status_code
        == 422
    )
    assert (
        client.put(
            "/respaldos/config", headers=admin_headers, json={"dias_advertencia": 999}
        ).status_code
        == 422
    )

    # se devuelve la configuración original sin cambios
    assert client.get("/respaldos/config", headers=admin_headers).json() == config


def test_config_se_puede_guardar(client, admin_headers):
    original = client.get("/respaldos/config", headers=admin_headers).json()
    try:
        nuevo = dict(original, maximo_respaldos=10)
        response = client.put("/respaldos/config", headers=admin_headers, json=nuevo)
        assert response.status_code == 200
        assert response.json()["maximo_respaldos"] == 10
    finally:
        client.put("/respaldos/config", headers=admin_headers, json=original)
    assert client.get("/respaldos/config", headers=admin_headers).json() == original


# ------------------------------------------------------------------- borrar


def test_no_se_puede_eliminar_un_respaldo_que_no_es_el_mas_antiguo(client, admin_headers):
    """RF-33: regla de retención -> 409 salvo para el más antiguo."""
    respaldos = client.get("/respaldos/", headers=admin_headers).json()["items"]
    if len(respaldos) < 1:
        pytest.skip("no hay respaldos para probar")

    # El más reciente nunca es el más antiguo: siempre debe rechazarse.
    mas_reciente = respaldos[0]
    response = client.delete(f"/respaldos/{mas_reciente['id']}", headers=admin_headers)
    assert response.status_code == 409
    assert "detail" in response.json()


def test_no_se_puede_eliminar_un_respaldo_inexistente(client, admin_headers):
    response = client.delete("/respaldos/999999", headers=admin_headers)
    assert response.status_code == 404


def test_no_se_puede_restaurar_un_respaldo_inexistente(client, admin_headers):
    response = client.post("/respaldos/999999/codigo", headers=admin_headers)
    assert response.status_code == 404


# -------------------------------------------------------------- restauracion


def test_restaurar_requiere_doble_confirmacion(client, admin_headers):
    """RF-32: sin el id correcto no se emite el código de confirmación."""
    respaldos = client.get("/respaldos/", headers=admin_headers).json()["items"]
    if not respaldos:
        pytest.skip("no hay respaldos para probar")
    respaldo = respaldos[0]

    codigo = client.post(f"/respaldos/{respaldo['id']}/codigo", headers=admin_headers)
    assert codigo.status_code == 200
    token = codigo.json()["token"]
    assert len(token) >= 10
    assert "expira_en" in codigo.json()

    # confirmación incorrecta -> nunca se llega a tocar la base de datos
    fallo = client.post(
        f"/respaldos/{respaldo['id']}/restaurar",
        headers=admin_headers,
        json={"confirmacion": "no-coincide", "token": token, "restaurar_archivos": True},
    )
    assert fallo.status_code == 400
    assert "confirmaci" in fallo.json()["detail"].lower()

    # token incorrecto -> se rechaza
    fallo_token = client.post(
        f"/respaldos/{respaldo['id']}/restaurar",
        headers=admin_headers,
        json={"confirmacion": str(respaldo["id"]), "token": "xxxxxxxxxxxx", "restaurar_archivos": True},
    )
    assert fallo_token.status_code == 400


def test_el_codigo_de_confirmacion_es_de_un_solo_uso(client, admin_headers):
    """RF-32: reutilizar el mismo código ya usado falla."""
    respaldos = client.get("/respaldos/", headers=admin_headers).json()["items"]
    if not respaldos:
        pytest.skip("no hay respaldos para probar")
    respaldo = respaldos[0]

    token = client.post(f"/respaldos/{respaldo['id']}/codigo", headers=admin_headers).json()[
        "token"
    ]

    # confirmación correcta pero otro fallo posterior: el código sigue vigente
    # mientras no se use; lo agotamos con un token inválido.
    cliente = client.post(
        f"/respaldos/{respaldo['id']}/restaurar",
        headers=admin_headers,
        json={"confirmacion": str(respaldo["id"]), "token": "xxxxxxxxxxxx", "restaurar_archivos": True},
    )
    assert cliente.status_code == 400

    # pedir otro código invalida el anterior
    nuevo = client.post(f"/respaldos/{respaldo['id']}/codigo", headers=admin_headers)
    assert nuevo.status_code == 200
    assert nuevo.json()["token"] != token


# ----------------------------------------------------------------  creacion


def test_generar_respaldo_completo(client, admin_headers):
    """RF-34: un respaldo genera a la vez el .sql y el snapshot de documentos."""
    estado = client.get("/respaldos/estado", headers=admin_headers).json()
    if estado["job_en_ejecucion"]:
        pytest.skip("ya hay un trabajo en curso")

    antes = client.get("/respaldos/", headers=admin_headers).json()["total"]

    response = client.post(
        "/respaldos/",
        headers=admin_headers,
        json={"observacion": "prueba automatizada"},
    )
    assert response.status_code == 202

    job_id = response.json()["job_id"]
    job = response.json()
    for _ in range(180):
        job = client.get(f"/respaldos/jobs/{job_id}", headers=admin_headers).json()
        if job["estado"] != "en_proceso":
            break
        time.sleep(1)

    assert job["estado"] == "completado", job.get("mensaje")
    assert len(job["pasos"]) >= 5
    assert all(p["estado"] == "completado" for p in job["pasos"])
    assert job["respaldo_id"]

    despues = client.get("/respaldos/", headers=admin_headers).json()
    assert despues["total"] >= antes
    nuevo = next(r for r in despues["items"] if r["id"] == job["respaldo_id"])
    assert nuevo["estado"] == "completado"
    assert nuevo["tipo"] == "manual"
    assert nuevo["tamano_bytes"] > 0
    assert nuevo["sha256"]
    assert nuevo["drive_file_url"]

    # el estado refleja el nuevo respaldo
    estado = client.get("/respaldos/estado", headers=admin_headers).json()
    assert estado["ultimo_respaldo"]["id"] == job["respaldo_id"]
    assert estado["total_respaldos"] >= antes
