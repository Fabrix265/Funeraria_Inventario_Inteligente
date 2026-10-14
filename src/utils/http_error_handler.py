import logging
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette import status

logger = logging.getLogger(__name__)


async def http_error_handler(request: Request, call_next):
    try:
        return await call_next(request)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error no manejado en {request.method} {request.url.path}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Error interno del servidor"}
        )