"""Conversión de las fechas guardadas en la BD a hora local.

Las columnas DateTime de este proyecto son "naive" y se escriben con
``datetime.utcnow()``, así que en las exportaciones salen 5 horas por
delante de la hora real de Perú (06:54 p. m. cuando son las 01:54 p. m.).

El corrimiento se controla con la variable ``TZ_OFFSET_HOURS`` del .env
(-5 por defecto, sin horario de verano en Perú).
"""

import os
from datetime import datetime, timedelta
from typing import Optional

_OFFSET_HORA = float(os.getenv("TZ_OFFSET_HOURS", "-5"))


def hora_local(valor: Optional[datetime]) -> Optional[datetime]:
    """Devuelve la misma fecha trasladada a la hora local. No modifica el original."""
    if valor is None:
        return None
    if valor.tzinfo is not None:
        return valor
    return valor + timedelta(hours=_OFFSET_HORA)


def hora_local_texto(valor: Optional[datetime], formato: str = "%d/%m/%Y %H:%M") -> str:
    """Fecha en hora local ya formateada. Cadena vacía si no hay valor."""
    local = hora_local(valor)
    return local.strftime(formato) if local else ""
