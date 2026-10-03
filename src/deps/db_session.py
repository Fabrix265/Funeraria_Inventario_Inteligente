from typing import Annotated, Generator
from fastapi import Depends
from sqlmodel import Session
from src.config.db import engine

def get_db() -> Generator[Session, None, None]:
    session = Session(engine)
    try:
        yield session
    finally:
        try:
            session.close()
        except Exception:
            # La conexión pudo ser cerrada por el servidor mientras corría
            # una restauración en segundo plano. No debe tumbar la respuesta:
            # se descartan las conexiones del pool y se sigue.
            engine.dispose()

SessionDep = Annotated[Session, Depends(get_db)]

#ay mi admin
