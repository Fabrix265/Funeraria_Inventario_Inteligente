import traceback
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from src.deps.role_check import get_current_user
# Quitamos temporalmente TranscripcionContratoOut para diagnosticar
from src.services.ia_service import IAService

ia_router = APIRouter()

# 💡 TRUCO: Eliminamos 'response_model=TranscripcionContratoOut' para que FastAPI 
# no rompa la app si el JSON de la IA tiene algún campo nulo o inesperado.
@ia_router.post("/procesar-contrato", status_code=status.HTTP_200_OK)
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
        
        print("📸 [DIAGNÓSTICO] Imagen recibida en bytes con éxito. Enviando a la IA...")
        resultado_transcripcion = await IAService.procesar_imagen_contrato(imagen_bytes)
        
        print("🎉 [ÉXITO] La IA respondió esto en bruto:")
        print(resultado_transcripcion)
        
        return resultado_transcripcion
        
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        print("❌ [ERROR DEL ENRUTADOR] Detalles de la falla:")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocurrió un error inesperado al procesar el archivo: {str(e)}"
        )