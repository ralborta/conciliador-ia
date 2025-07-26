from fastapi import APIRouter, File, UploadFile, Form
import shutil
from pathlib import Path
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/upload", tags=["upload"])

# Configuración simple
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/extracto")
async def upload_extracto(file: UploadFile = File(...)):
    """Sube un archivo PDF de extracto bancario y lo procesa inmediatamente"""
    try:
        logger.info(f"Subida y procesamiento de extracto: {file.filename}")
        
        # Leer el contenido del archivo en memoria
        content = await file.read()
        
        # Sanitizar nombre del archivo
        import re
        safe_filename = re.sub(r'[^a-zA-Z0-9._-]', '_', file.filename)
        safe_filename = safe_filename.replace(' ', '_')
        
        # Guardar temporalmente para procesamiento
        temp_path = UPLOAD_DIR / safe_filename
        with temp_path.open("wb") as buffer:
            buffer.write(content)
        
        logger.info(f"Extracto guardado temporalmente: {temp_path}")
        return {"status": "ok", "filename": safe_filename, "file_path": str(temp_path)}
    except Exception as e:
        logger.error(f"Error subiendo extracto: {e}")
        return {"status": "error", "message": str(e)}

@router.post("/comprobantes")
async def upload_comprobantes(file: UploadFile = File(...)):
    """Sube un archivo Excel o CSV de comprobantes de venta"""
    try:
        logger.info(f"Subida de comprobantes: {file.filename}")
        
        # Leer el contenido del archivo en memoria
        content = await file.read()
        
        # Sanitizar nombre del archivo
        import re
        safe_filename = re.sub(r'[^a-zA-Z0-9._-]', '_', file.filename)
        safe_filename = safe_filename.replace(' ', '_')
        
        # Guardar temporalmente para procesamiento
        temp_path = UPLOAD_DIR / safe_filename
        with temp_path.open("wb") as buffer:
            buffer.write(content)
        
        logger.info(f"Comprobantes guardados temporalmente: {temp_path}")
        return {"status": "ok", "filename": safe_filename, "file_path": str(temp_path)}
    except Exception as e:
        logger.error(f"Error subiendo comprobantes: {e}")
        return {"status": "error", "message": str(e)}

 
@router.post("/procesar-inmediato")
async def procesar_archivos_inmediato(
    extracto: UploadFile = File(...),
    comprobantes: UploadFile = File(...),
    empresa_id: str = Form(...)
):
    """Procesa ambos archivos inmediatamente sin guardar a disco"""
    try:
        logger.info(f"Procesamiento inmediato iniciado para empresa: {empresa_id}")
        
        # Validar archivos
        if not extracto.filename or not comprobantes.filename:
            return {"status": "error", "message": "Ambos archivos son requeridos"}
        
        # Validar tipos de archivo
        if not extracto.filename.lower().endswith('.pdf'):
            return {"status": "error", "message": "El extracto debe ser un archivo PDF"}
        
        valid_comprobantes_extensions = ['.xlsx', '.xls', '.csv']
        if not any(comprobantes.filename.lower().endswith(ext) for ext in valid_comprobantes_extensions):
            return {"status": "error", "message": "Los comprobantes deben ser Excel (.xlsx, .xls) o CSV"}
        
        # Validar tamaño de archivos (máximo 10MB cada uno)
        max_size = 10 * 1024 * 1024  # 10MB
        extracto_content = await extracto.read()
        comprobantes_content = await comprobantes.read()
        
        if len(extracto_content) > max_size:
            return {"status": "error", "message": "El extracto es demasiado grande. Máximo 10MB permitido."}
        
        if len(comprobantes_content) > max_size:
            return {"status": "error", "message": "Los comprobantes son demasiado grandes. Máximo 10MB permitido."}
        
        # Crear archivos temporales únicos
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_extracto:
            temp_extracto.write(extracto_content)
            temp_extracto_path = temp_extracto.name
            
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_comprobantes:
            temp_comprobantes.write(comprobantes_content)
            temp_comprobantes_path = temp_comprobantes.name
        
        try:
            # Procesar con los archivos temporales
            from services.matchmaker import MatchmakerService
            matchmaker = MatchmakerService()
            
            logger.info("Iniciando procesamiento de conciliación...")
            response = matchmaker.procesar_conciliacion(
                extracto_path=temp_extracto_path,
                comprobantes_path=temp_comprobantes_path,
                empresa_id=empresa_id
            )
            
            logger.info("Procesamiento inmediato completado exitosamente")
            return response
            
        except Exception as processing_error:
            logger.error(f"Error en procesamiento: {processing_error}")
            return {
                "status": "error", 
                "message": f"Error en el procesamiento: {str(processing_error)}",
                "details": "Verifica que los archivos contengan datos válidos y no estén corruptos."
            }
        finally:
            # Limpiar archivos temporales
            try:
                os.unlink(temp_extracto_path)
                os.unlink(temp_comprobantes_path)
            except:
                pass
                
    except Exception as e:
        logger.error(f"Error en procesamiento inmediato: {e}")
        return {
            "status": "error", 
            "message": f"Error general: {str(e)}",
            "details": "Verifica la conexión y los archivos subidos."
        }

 