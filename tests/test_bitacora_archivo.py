from datetime import date, datetime, timedelta

import pytest

from src.core import fechas
from src.services import bitacora_archivo_service


class FakeDrive:
    def __init__(self):
        self.FOLDER_ID = "raiz"
        self.autorizado = True
        self.archivos = []
        self.subidos = []
        self.eliminados = []
        self.secuencia = 0

    def verificar_estado(self):
        return {"autorizado": self.autorizado}

    def obtener_o_crear_carpeta(self, nombre, parent_id=None):
        assert nombre == "bitacora"
        assert parent_id is None
        return "carpeta-bitacora"

    def listar_contenido(self, carpeta_id, tipo):
        assert carpeta_id == "carpeta-bitacora"
        assert tipo == "archivos"
        return list(self.archivos)

    def subir_archivo(self, contenido, nombre, carpeta):
        assert contenido == b"x"
        assert carpeta == "bitacora"
        self.secuencia += 1
        archivo = {
            "id": f"archivo-{self.secuencia}",
            "name": nombre,
            "mimeType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "size": "1",
            "modifiedTime": "2026-11-08T12:00:00Z",
        }
        self.archivos.append(archivo)
        self.subidos.append(nombre)
        return {"file_id": archivo["id"], "filename": nombre}

    def eliminar_archivo(self, file_id):
        for archivo in self.archivos:
            if archivo["id"] == file_id:
                self.archivos.remove(archivo)
                self.eliminados.append(archivo["name"])
                return True
        return False


@pytest.fixture
def drive_falso(monkeypatch):
    drive = FakeDrive()
    monkeypatch.setattr(bitacora_archivo_service, "GoogleDriveService", lambda db: drive)
    monkeypatch.setattr(bitacora_archivo_service, "exportar_excel_dia", lambda db, dia: b"x")
    return drive


def test_carpeta_vacia_crea_los_30_dias_cerrados(drive_falso):
    resultado = bitacora_archivo_service.sincronizar(None, hoy=date(2026, 11, 8))
    esperados = [
        f"{(date(2026, 10, 9) + timedelta(days=indice)).isoformat()}.xlsx"
        for indice in range(30)
    ]

    assert resultado == {"estado": "ok", "creados": esperados, "eliminados": [], "total": 30}
    assert drive_falso.subidos == esperados
    assert [archivo["name"] for archivo in drive_falso.archivos] == esperados
    assert "2026-11-08.xlsx" not in drive_falso.subidos


def test_al_avanzar_un_dia_crea_el_ultimo_y_elimina_el_mas_antiguo(drive_falso):
    for indice in range(30):
        dia = date(2026, 10, 9) + timedelta(days=indice)
        drive_falso.subir_archivo(b"x", f"{dia.isoformat()}.xlsx", "bitacora")

    resultado = bitacora_archivo_service.sincronizar(None, hoy=date(2026, 11, 9))

    assert resultado == {
        "estado": "ok",
        "creados": ["2026-11-08.xlsx"],
        "eliminados": ["2026-10-09.xlsx"],
        "total": 30,
    }
    assert len(drive_falso.archivos) == 30
    assert drive_falso.eliminados == ["2026-10-09.xlsx"]
    assert "2026-10-09.xlsx" not in [archivo["name"] for archivo in drive_falso.archivos]


def test_sincronizar_dos_veces_el_mismo_dia_no_duplica(drive_falso):
    bitacora_archivo_service.sincronizar(None, hoy=date(2026, 11, 8))
    resultado = bitacora_archivo_service.sincronizar(None, hoy=date(2026, 11, 8))

    assert resultado == {"estado": "ok", "creados": [], "eliminados": [], "total": 30}
    assert len(drive_falso.subidos) == 30
    assert len(drive_falso.archivos) == 30
    assert drive_falso.eliminados == []


def test_archivos_ajenos_no_se_tocan(drive_falso):
    ajenos = [
        {"id": "notas", "name": "notas.txt"},
        {"id": "fecha-invalida", "name": "2026-11-31.xlsx"},
        {"id": "formato-ajeno", "name": "2026-1-01.xlsx"},
        {"id": "copia-ajena", "name": "2026-10-01.xlsx.bak"},
    ]
    drive_falso.archivos.extend(ajenos)

    resultado = bitacora_archivo_service.sincronizar(None, hoy=date(2026, 11, 8))

    assert resultado["estado"] == "ok"
    assert resultado["total"] == 30
    assert resultado["eliminados"] == []
    assert drive_falso.eliminados == []
    assert all(archivo in drive_falso.archivos for archivo in ajenos)


def test_drive_no_autorizado_omite_sin_excepcion(drive_falso):
    drive_falso.autorizado = False

    resultado = bitacora_archivo_service.sincronizar(None, hoy=date(2026, 11, 8))

    assert resultado["estado"] == "omitido"
    assert drive_falso.archivos == []
    assert drive_falso.subidos == []
    assert drive_falso.eliminados == []


def test_rango_utc_del_dia_local_con_offset_menos_cinco(monkeypatch):
    monkeypatch.setattr(fechas, "_OFFSET_HORA", -5)

    assert fechas.rango_utc_de_dia_local(date(2026, 11, 7)) == (
        datetime(2026, 11, 7, 5, 0),
        datetime(2026, 11, 8, 5, 0),
    )


def test_nombre_archivo_contiene_solo_fecha_y_extension():
    assert bitacora_archivo_service.nombre_archivo(date(2026, 11, 7)) == "2026-11-07.xlsx"
