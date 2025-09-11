from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
import logging
import os
from pathlib import Path
import uuid
from datetime import datetime

from services.extractor_simple import ExtractorSimple

logger = logging.getLogger(__name__)
router = APIRouter(tags=["extractor_simple"])

@router.post("/procesar")
async def procesar_extracto(
    archivo: UploadFile = File(...)
):
    """Procesa un extracto PDF y lo convierte a tabla"""
    try:
        # Validar archivo
        if not archivo.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF")
        
        # Guardar archivo temporal
        archivo_id = str(uuid.uuid4())
        archivo_path = f"data/temp/{archivo_id}_{archivo.filename}"
        
        Path(archivo_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(archivo_path, "wb") as buffer:
            content = await archivo.read()
            buffer.write(content)
        
        try:
            # Procesar con extractor simple
            extractor = ExtractorSimple()
            resultado = extractor.extraer_datos(archivo_path)
            
            if "error" in resultado:
                raise HTTPException(status_code=422, detail=resultado["error"])
            
            return {
                "success": True,
                "message": "Extracto procesado exitosamente",
                "resultado": resultado
            }
            
        finally:
            # Limpiar archivo temporal
            if os.path.exists(archivo_path):
                os.remove(archivo_path)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error procesando extracto: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")



