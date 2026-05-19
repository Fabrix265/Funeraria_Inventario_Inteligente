from fastapi import Query

def parametros_paginacion(
    offset: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(20, ge=1, le=100, description="Número de registros a traer")
):
    return {"offset": offset, "limit": limit}