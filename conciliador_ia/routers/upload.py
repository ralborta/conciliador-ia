from fastapi import APIRouter, File, UploadFile
import shutil
from pathlib import Path
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/upload", tags=["upload"])

# Configuración simple
UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/extracto")
async def upload_extracto(file: UploadFile = File(...)):
    """Sube un archivo PDF de extracto bancario"""
    try:
        logger.info(f"Subida de extracto: {file.filename}")
        file_path = UPLOAD_DIR / file.filename
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logger.info(f"Extracto subido exitosamente: {file_path}")
        return {"status": "ok", "filename": file.filename, "file_path": str(file_path)}
    except Exception as e:
        logger.error(f"Error subiendo extracto: {e}")
        return {"status": "error", "message": str(e)}

@router.post("/comprobantes")
async def upload_comprobantes(file: UploadFile = File(...)):
    """Sube un archivo Excel o CSV de comprobantes de venta"""
    try:
        logger.info(f"Subida de comprobantes: {file.filename}")
        file_path = UPLOAD_DIR / file.filename
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logger.info(f"Comprobantes subidos exitosamente: {file_path}")
        return {"status": "ok", "filename": file.filename, "file_path": str(file_path)}
    except Exception as e:
        logger.error(f"Error subiendo comprobantes: {e}")
        return {"status": "error", "message": str(e)}

 