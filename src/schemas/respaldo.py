from datetime import datetime
from typing import List, Literal, Optional
from pydantic import BaseModel, Field

EstadoRespaldo = Literal["en_proceso", "completado", "fallido"]
TipoRespaldo = Literal["manual", "seguridad"]
Vigencia = Literal["nunca", "al_dia", "proximo", "vencido"]
EstadoPaso = Literal["pendiente", "en_proceso", "completado", "fallido"]


class RespaldoLeer(BaseModel):
    id: int
    etiqueta: str
    fecha: datetime
    nombre_archivo: str
    drive_file_url: Optional[str] = None
    tamano_bytes: int
    cantidad_archivos: int
    sha256: Optional[str] = None
    estado: EstadoRespaldo
    mensaje_error: Optional[str] = None
    tipo: TipoRespaldo
    observacion: Optional[str] = None
    usuario_nombre: Optional[str] = None

    class Config:
        from_attributes = True


class RespaldoCrear(BaseModel):
    observacion: Optional[str] = Field(default=None, max_length=255)


class RespaldoConfigLeer(BaseModel):
    frecuencia_dias: int
    dias_advertencia: int
    maximo_respaldos: int

    class Config:
        from_attributes = True


class RespaldoConfigActualizar(BaseModel):
    frecuencia_dias: Optional[int] = Field(default=None, ge=1, le=90)
    dias_advertencia: Optional[int] = Field(default=None, ge=1, le=90)
    maximo_respaldos: Optional[int] = Field(default=None, ge=2, le=200)


class PasoJob(BaseModel):
    nombre: str
    estado: EstadoPaso
    mensaje: Optional[str] = None


class RespaldoJobLeer(BaseModel):
    job_id: str
    tipo: str
    estado: Literal["en_proceso", "completado", "fallido"]
    paso_actual: str
    pasos: List[PasoJob] = []
    mensaje: Optional[str] = None
    respaldo_id: Optional[int] = None
    resultado: Optional[dict] = None
    inicio: datetime
    fin: Optional[datetime] = None


class RespaldoEstadoLeer(BaseModel):
    pg_dump_disponible: bool
    psql_disponible: bool
    pg_dump_ruta: Optional[str] = None
    psql_ruta: Optional[str] = None
    drive_conectado: bool
    drive_motivo: Optional[str] = None
    total_respaldos: int
    ultimo_respaldo: Optional[RespaldoLeer] = None
    dias_desde_ultimo: Optional[int] = None
    vigencia: Vigencia
    fecha_siguiente_recomendada: Optional[datetime] = None
    config: RespaldoConfigLeer
    carpeta_servicios_id: Optional[str] = None
    carpeta_base_datos_id: Optional[str] = None
    carpeta_archivos_id: Optional[str] = None
    carpeta_raiz_id: Optional[str] = None
    job_en_ejecucion: Optional[RespaldoJobLeer] = None
    maximo_alcanzado: bool = False


class TokenRestauracionLeer(BaseModel):
    token: str
    expira_en: datetime


class RestaurarRespaldo(BaseModel):
    confirmacion: str = Field(min_length=1, max_length=64)
    token: str = Field(min_length=10, max_length=200)
    restaurar_archivos: bool = True


class RecuperarArchivos(BaseModel):
    respaldo_id: int


class RespaldoListaResponse(BaseModel):
    items: List[RespaldoLeer] = []
    total: int = 0
