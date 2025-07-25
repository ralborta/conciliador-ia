from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
import logging
from typing import Optional
import os
from pathlib import Path

from services.matchmaker import MatchmakerService
from models.schemas import ConciliacionRequest, ConciliacionResponse, ErrorResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/conciliacion", tags=["conciliacion"])

def get_matchmaker_service():
    """Dependency para obtener MatchmakerService"""
    return MatchmakerService()

@router.post("/procesar", response_model=ConciliacionResponse)
async def procesar_conciliacion(
    request: ConciliacionRequest,
    matchmaker: MatchmakerService = Depends(get_matchmaker_service)
):
    """
    Procesa la conciliación entre un extracto bancario y comprobantes de venta
    
    Args:
        request: Request con las rutas de los archivos y empresa_id opcional
        
    Returns:
        Resultado de la conciliación estructurado
    """
    try:
        logger.info(f"🚀 Starting conciliation process...")
        logger.info(f"📄 Request received: {request}")
        logger.info(f"📁 Extracto: {request.extracto_path}")
        logger.info(f"📁 Comprobantes: {request.comprobantes_path}")
        logger.info(f"🏢 Empresa ID: {request.empresa_id}")
        
        # Validar que los archivos existen
        extracto_full_path = Path("uploads") / Path(request.extracto_path).name
        comprobantes_full_path = Path("uploads") / Path(request.comprobantes_path).name
        
        if not extracto_full_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Archivo de extracto no encontrado: {extracto_full_path}"
            )
        
        if not comprobantes_full_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Archivo de comprobantes no encontrado: {comprobantes_full_path}"
            )
        
        # Procesar conciliación
        response = matchmaker.procesar_conciliacion(
            extracto_path=request.extracto_path,
            comprobantes_path=request.comprobantes_path,
            empresa_id=request.empresa_id
        )
        
        logger.info(f"Conciliación completada exitosamente")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Process failed: {e}")
        logger.error(f"❌ Stack trace: {e.__class__.__name__}: {str(e)}")
        import traceback
        logger.error(f"❌ Full traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.get("/status")
async def get_conciliacion_status():
    """
    Obtiene el estado del servicio de conciliación
    
    Returns:
        Estado del servicio
    """
    try:
        # Verificar que las dependencias estén disponibles
        status = {
            "service": "Conciliador IA",
            "status": "running",
            "version": "1.0.0",
            "features": [
                "Extracción de PDF",
                "Procesamiento de Excel/CSV",
                "Conciliación con IA",
                "Validación de archivos"
            ]
        }
        
        # Verificar OpenAI API key
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key:
            status["openai_configured"] = True
        else:
            status["openai_configured"] = False
            status["warnings"] = ["OpenAI API key no configurada"]
        
        return status
        
    except Exception as e:
        logger.error(f"Error obteniendo estado del servicio: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor"
        )

@router.post("/test")
async def test_conciliacion():
    """
    Endpoint de prueba para verificar el funcionamiento del servicio
    
    Returns:
        Resultado de la prueba
    """
    try:
        # Crear datos de prueba
        import pandas as pd
        from datetime import datetime, timedelta
        
        # Datos de prueba para movimientos
        movimientos_data = {
            'fecha': [
                datetime.now() - timedelta(days=1),
                datetime.now() - timedelta(days=2),
                datetime.now() - timedelta(days=3)
            ],
            'concepto': [
                'Pago cliente ABC',
                'Transferencia recibida',
                'Depósito en efectivo'
            ],
            'importe': [1500.00, 2500.00, 800.00],
            'tipo': ['crédito', 'crédito', 'crédito']
        }
        
        # Datos de prueba para comprobantes
        comprobantes_data = {
            'fecha': [
                datetime.now() - timedelta(days=1),
                datetime.now() - timedelta(days=2),
                datetime.now() - timedelta(days=3)
            ],
            'cliente': ['Cliente ABC', 'Cliente XYZ', 'Cliente DEF'],
            'concepto': [
                'Factura 001 - Servicios',
                'Factura 002 - Productos',
                'Factura 003 - Consultoría'
            ],
            'monto': [1500.00, 2500.00, 800.00],
            'numero_comprobante': ['F001', 'F002', 'F003']
        }
        
        df_movimientos = pd.DataFrame(movimientos_data)
        df_comprobantes = pd.DataFrame(comprobantes_data)
        
        # Probar conciliación
        matchmaker = MatchmakerService()
        items_conciliados = matchmaker.conciliador.conciliar_movimientos(
            df_movimientos, df_comprobantes, "test_empresa"
        )
        
        return {
            "success": True,
            "message": "Prueba de conciliación completada",
            "movimientos_procesados": len(df_movimientos),
            "comprobantes_procesados": len(df_comprobantes),
            "items_conciliados": len(items_conciliados),
            "test_data": {
                "movimientos": movimientos_data,
                "comprobantes": comprobantes_data
            }
        }
        
    except Exception as e:
        logger.error(f"Error en prueba de conciliación: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Error en prueba de conciliación"
        }

@router.get("/stats")
async def get_conciliacion_stats():
    """
    Obtiene estadísticas del servicio de conciliación
    
    Returns:
        Estadísticas del servicio
    """
    try:
        # Aquí podrías agregar estadísticas reales del servicio
        # Por ahora retornamos datos de ejemplo
        stats = {
            "total_conciliaciones": 0,
            "conciliaciones_exitosas": 0,
            "tasa_exito": 0.0,
            "tiempo_promedio_procesamiento": 0.0,
            "archivos_procesados": {
                "pdf": 0,
                "excel": 0,
                "csv": 0
            },
            "movimientos_procesados": 0,
            "comprobantes_procesados": 0
        }
        
        return stats
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor"
        )

@router.post("/validate-files")
async def validate_files(
    extracto_path: str,
    comprobantes_path: str
):
    """
    Valida que los archivos estén en el formato correcto
    
    Args:
        extracto_path: Ruta al archivo de extracto
        comprobantes_path: Ruta al archivo de comprobantes
        
    Returns:
        Resultado de la validación
    """
    try:
        validation_result = {
            "success": True,
            "extracto": {},
            "comprobantes": {},
            "errors": []
        }
        
        # Validar archivo de extracto
        if not Path(extracto_path).exists():
            validation_result["errors"].append(f"Archivo de extracto no encontrado: {extracto_path}")
            validation_result["success"] = False
        else:
            # Aquí podrías agregar validaciones específicas del PDF
            validation_result["extracto"] = {
                "exists": True,
                "size": Path(extracto_path).stat().st_size,
                "extension": Path(extracto_path).suffix
            }
        
        # Validar archivo de comprobantes
        if not Path(comprobantes_path).exists():
            validation_result["errors"].append(f"Archivo de comprobantes no encontrado: {comprobantes_path}")
            validation_result["success"] = False
        else:
            # Aquí podrías agregar validaciones específicas del Excel/CSV
            validation_result["comprobantes"] = {
                "exists": True,
                "size": Path(comprobantes_path).stat().st_size,
                "extension": Path(comprobantes_path).suffix
            }
        
        return validation_result
        
    except Exception as e:
        logger.error(f"Error validando archivos: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor durante la validación"
        ) 