import logging
import threading
import uuid
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# Tiempo que se conserva un job terminado antes de olvidarlo.
_VENTANA_HORAS = 1


class Paso:
    def __init__(self, nombre: str):
        self.nombre = nombre
        self.estado = "pendiente"
        self.mensaje: Optional[str] = None

    def a_dict(self) -> dict:
        return {"nombre": self.nombre, "estado": self.estado, "mensaje": self.mensaje}


class JobRespaldo:
    """Estado de una operación larga (respaldo o restauración) que corre en
    segundo plano. La interfaz lo consulta mientras avanza."""

    def __init__(self, job_id: str, tipo: str, pasos: List[str], respaldo_id=None):
        self.job_id = job_id
        self.tipo = tipo
        self.estado = "en_proceso"
        self.paso_actual = ""
        self.pasos: List[Paso] = [Paso(nombre) for nombre in pasos]
        self.mensaje: Optional[str] = None
        self.respaldo_id = respaldo_id
        self.resultado: Optional[dict] = None
        self.inicio = datetime.utcnow()
        self.fin: Optional[datetime] = None
        self._lock = threading.Lock()

    def _buscar(self, nombre: str) -> Paso:
        for paso in self.pasos:
            if paso.nombre == nombre:
                return paso
        raise KeyError(f"El paso '{nombre}' no existe en el job {self.job_id}")

    @contextmanager
    def paso(self, nombre: str):
        """Marca un paso como en curso. Si algo falla dentro, deja el paso y el
        job en 'fallido' con el detalle y vuelve a lanzar el error."""
        paso = self._buscar(nombre)
        with self._lock:
            paso.estado = "en_proceso"
            paso.mensaje = None
            self.paso_actual = nombre
        try:
            yield
        except Exception as error:
            with self._lock:
                paso.estado = "fallido"
                paso.mensaje = str(error)
                self.estado = "fallido"
                self.mensaje = str(error)
            logger.warning("Fallo en el paso '%s' del job %s: %s", nombre, self.job_id, error)
            raise
        else:
            with self._lock:
                paso.estado = "completado"

    def terminar(self, resultado: Optional[dict] = None, mensaje: Optional[str] = None):
        with self._lock:
            if self.estado == "en_proceso":
                self.estado = "completado"
            self.mensaje = mensaje or self.mensaje
            self.resultado = resultado
            self.fin = datetime.utcnow()

    def fallar(self, mensaje: str):
        with self._lock:
            self.estado = "fallido"
            self.mensaje = mensaje
            if self.fin is None:
                self.fin = datetime.utcnow()

    def a_dict(self) -> dict:
        with self._lock:
            return {
                "job_id": self.job_id,
                "tipo": self.tipo,
                "estado": self.estado,
                "paso_actual": self.paso_actual,
                "pasos": [paso.a_dict() for paso in self.pasos],
                "mensaje": self.mensaje,
                "respaldo_id": self.respaldo_id,
                "resultado": self.resultado,
                "inicio": self.inicio,
                "fin": self.fin,
            }


_bloqueo = threading.Lock()
_jobs: Dict[str, JobRespaldo] = {}


def _podar():
    limite = datetime.utcnow() - timedelta(hours=_VENTANA_HORAS)
    vencidos = [clave for clave, job in _jobs.items() if job.fin and job.fin < limite]
    for clave in vencidos:
        _jobs.pop(clave, None)


def crear(tipo: str, pasos: List[str], respaldo_id=None) -> JobRespaldo:
    with _bloqueo:
        _podar()
        job = JobRespaldo(uuid.uuid4().hex[:16], tipo, pasos, respaldo_id)
        _jobs[job.job_id] = job
        return job


def obtener(job_id: str) -> Optional[JobRespaldo]:
    with _bloqueo:
        return _jobs.get(job_id)


def en_ejecucion() -> Optional[JobRespaldo]:
    with _bloqueo:
        for job in _jobs.values():
            if job.estado == "en_proceso":
                return job
    return None


def a_dict(job: Optional[JobRespaldo]) -> Optional[dict]:
    return job.a_dict() if job else None
