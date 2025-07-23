from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
import logging
from typing import Optional
import os

from ..utils.file_helpers import FileHelper
from ..models.schemas import UploadResponse, ErrorResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/upload", tags=["upload"])

# Configuración
MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 10485760))  # 10MB por defecto

def get_file_helper():
    """Dependency para obtener FileHelper"""
    return FileHelper()

@router.post("/extracto", response_model=UploadResponse)
async def upload_extracto(
    file: UploadFile = File(...),
    file_helper: FileHelper = Depends(get_file_helper)
):
    """
    Sube un archivo PDF de extracto bancario
    
    Args:
        file: Archivo PDF del extracto bancario
        
    Returns:
        Respuesta con información del archivo subido
    """
    try:
        logger.info(f"Subida de extracto: {file.filename}")
        
        # Validar tipo de archivo
        if not file_helper.validate_file_extension(file.filename, FileHelper.ALLOWED_EXTENSIONS['pdf']):
            raise HTTPException(
                status_code=400, 
                detail="Solo se permiten archivos PDF para extractos"
            )
        
        # Leer contenido del archivo
        file_content = await file.read()
        
        # Validar tamaño
        if not file_helper.validate_file_size(file_content, MAX_FILE_SIZE):
            raise HTTPException(
                status_code=400,
                detail=f"El archivo excede el tamaño máximo permitido ({MAX_FILE_SIZE / 1024 / 1024:.1f}MB)"
            )
        
        # Guardar archivo
        file_path = file_helper.save_uploaded_file(file_content, file.filename)
        if not file_path:
            raise HTTPException(
                status_code=500,
                detail="Error al guardar el archivo"
            )
        
        # Validar que es un PDF válido
        if not file_helper.is_valid_pdf(file_path):
            # Eliminar archivo inválido
            try:
                os.remove(file_path)
            except:
                pass
            raise HTTPException(
                status_code=400,
                detail="El archivo no es un PDF válido"
            )
        
        logger.info(f"Extracto subido exitosamente: {file_path}")
        
        return UploadResponse(
            success=True,
            message="Extracto subido exitosamente",
            file_path=file_path,
            file_name=file.filename
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error subiendo extracto: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor al subir el extracto"
        )

@router.post("/comprobantes", response_model=UploadResponse)
async def upload_comprobantes(
    file: UploadFile = File(...),
    file_helper: FileHelper = Depends(get_file_helper)
):
    """
    Sube un archivo Excel o CSV de comprobantes de venta
    
    Args:
        file: Archivo Excel (.xlsx, .xls) o CSV (.csv) con comprobantes
        
    Returns:
        Respuesta con información del archivo subido
    """
    try:
        logger.info(f"Subida de comprobantes: {file.filename}")
        
        # Validar tipo de archivo
        allowed_extensions = FileHelper.ALLOWED_EXTENSIONS['excel'] + FileHelper.ALLOWED_EXTENSIONS['csv']
        if not file_helper.validate_file_extension(file.filename, allowed_extensions):
            raise HTTPException(
                status_code=400,
                detail="Solo se permiten archivos Excel (.xlsx, .xls) o CSV (.csv) para comprobantes"
            )
        
        # Leer contenido del archivo
        file_content = await file.read()
        
        # Validar tamaño
        if not file_helper.validate_file_size(file_content, MAX_FILE_SIZE):
            raise HTTPException(
                status_code=400,
                detail=f"El archivo excede el tamaño máximo permitido ({MAX_FILE_SIZE / 1024 / 1024:.1f}MB)"
            )
        
        # Guardar archivo
        file_path = file_helper.save_uploaded_file(file_content, file.filename)
        if not file_path:
            raise HTTPException(
                status_code=500,
                detail="Error al guardar el archivo"
            )
        
        # Validar que es un archivo válido
        file_extension = file_helper.validate_file_extension(file.filename, ['.xlsx', '.xls'])
        if file_extension and not file_helper.is_valid_excel(file_path):
            try:
                os.remove(file_path)
            except:
                pass
            raise HTTPException(
                status_code=400,
                detail="El archivo no es un Excel válido"
            )
        
        file_extension = file_helper.validate_file_extension(file.filename, ['.csv'])
        if file_extension and not file_helper.is_valid_csv(file_path):
            try:
                os.remove(file_path)
            except:
                pass
            raise HTTPException(
                status_code=400,
                detail="El archivo no es un CSV válido"
            )
        
        logger.info(f"Comprobantes subidos exitosamente: {file_path}")
        
        return UploadResponse(
            success=True,
            message="Comprobantes subidos exitosamente",
            file_path=file_path,
            file_name=file.filename
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error subiendo comprobantes: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor al subir los comprobantes"
        )

@router.get("/files/{file_path:path}")
async def get_file_info(
    file_path: str,
    file_helper: FileHelper = Depends(get_file_helper)
):
    """
    Obtiene información de un archivo subido
    
    Args:
        file_path: Ruta del archivo
        
    Returns:
        Información del archivo
    """
    try:
        # Construir ruta completa
        full_path = os.path.join(file_helper.upload_dir, file_path)
        
        # Obtener información del archivo
        file_info = file_helper.get_file_info(full_path)
        
        if not file_info:
            raise HTTPException(
                status_code=404,
                detail="Archivo no encontrado"
            )
        
        return {
            "success": True,
            "file_info": file_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo información del archivo: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor"
        )

@router.delete("/files/{file_path:path}")
async def delete_file(
    file_path: str,
    file_helper: FileHelper = Depends(get_file_helper)
):
    """
    Elimina un archivo subido
    
    Args:
        file_path: Ruta del archivo a eliminar
        
    Returns:
        Confirmación de eliminación
    """
    try:
        # Construir ruta completa
        full_path = os.path.join(file_helper.upload_dir, file_path)
        
        # Verificar que el archivo existe
        if not os.path.exists(full_path):
            raise HTTPException(
                status_code=404,
                detail="Archivo no encontrado"
            )
        
        # Eliminar archivo
        os.remove(full_path)
        
        logger.info(f"Archivo eliminado: {full_path}")
        
        return {
            "success": True,
            "message": "Archivo eliminado exitosamente"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error eliminando archivo: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor al eliminar el archivo"
        )

@router.post("/cleanup")
async def cleanup_old_files(
    max_age_hours: int = 24,
    file_helper: FileHelper = Depends(get_file_helper)
):
    """
    Limpia archivos antiguos del directorio de uploads
    
    Args:
        max_age_hours: Edad máxima en horas para mantener archivos
        
    Returns:
        Resumen de la limpieza
    """
    try:
        deleted_count = file_helper.cleanup_old_files(max_age_hours)
        
        logger.info(f"Limpieza completada: {deleted_count} archivos eliminados")
        
        return {
            "success": True,
            "message": f"Limpieza completada",
            "archivos_eliminados": deleted_count,
            "max_age_hours": max_age_hours
        }
        
    except Exception as e:
        logger.error(f"Error en limpieza de archivos: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor durante la limpieza"
        ) 