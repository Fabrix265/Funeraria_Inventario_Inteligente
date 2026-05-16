from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from src.deps.role_check import get_current_user
from src.schemas.ia import TranscripcionContratoOut
from src.services.ia_service import IAService

ia_router = APIRouter()

@ia_router.post("/procesar-contrato", response_model=TranscripcionContratoOut, status_code=status.HTTP_200_OK)
async def procesar_contrato_con_ia(
    file: UploadFile = File(..., description="Archivo de imagen del contrato físico"),
    _ = Depends(get_current_user)
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Formato de archivo inválido ({file.content_type}). Debe subir una imagen (PNG, JPG, JPEG)."
        )
        
    try:
        imagen_bytes = await file.read()
        
        resultado_transcripcion = await IAService.procesar_imagen_contrato(imagen_bytes)
        return resultado_transcripcion
        
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocurrió un error inesperado al procesar el archivo: {str(e)}"
        )