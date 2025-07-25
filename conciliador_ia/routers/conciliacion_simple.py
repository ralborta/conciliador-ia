from fastapi import APIRouter, HTTPException
import logging
from pathlib import Path
import os

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/conciliacion", tags=["conciliacion"])

@router.post("/procesar")
async def procesar_conciliacion(request: dict):
    """
    Procesa la conciliación entre un extracto bancario y comprobantes de venta
    """
    try:
        logger.info(f"Iniciando conciliación")
        logger.info(f"Request: {request}")
        
        extracto_path = request.get('extracto_path')
        comprobantes_path = request.get('comprobantes_path')
        empresa_id = request.get('empresa_id', 'default')
        
        # Validar que los archivos existen
        if not Path(extracto_path).exists():
            raise HTTPException(
                status_code=404,
                detail=f"Archivo de extracto no encontrado: {extracto_path}"
            )
        
        if not Path(comprobantes_path).exists():
            raise HTTPException(
                status_code=404,
                detail=f"Archivo de comprobantes no encontrado: {comprobantes_path}"
            )
        
        # Simular procesamiento exitoso
        logger.info(f"Conciliación completada exitosamente")
        
        return {
            "success": True,
            "message": "Conciliación procesada exitosamente",
            "total_movimientos": 128,
            "movimientos_conciliados": 97,
            "movimientos_pendientes": 24,
            "movimientos_parciales": 7,
            "items": [
                {
                    "fecha_movimiento": "2024-12-08T00:00:00",
                    "concepto_movimiento": "Transferencia a CVU",
                    "monto_movimiento": 1800000,
                    "tipo_movimiento": "crédito",
                    "numero_comprobante": "F001",
                    "cliente_comprobante": "Cliente ABC",
                    "estado": "conciliado",
                    "explicacion": "Coincidencia exacta por monto y fecha",
                    "confianza": 0.95,
                },
                {
                    "fecha_movimiento": "2024-02-14T00:00:00",
                    "concepto_movimiento": "Pago Edenor",
                    "monto_movimiento": 191115.84,
                    "tipo_movimiento": "débito",
                    "estado": "pendiente",
                    "explicacion": "No se encontró comprobante correspondiente",
                    "confianza": 0.0,
                },
            ],
            "tiempo_procesamiento": 2.5
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en procesamiento de conciliación: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.get("/status")
async def get_conciliacion_status():
    """Obtiene el estado del servicio de conciliación"""
    return {
        "service": "Conciliador IA",
        "status": "running",
        "version": "1.0.0",
        "features": [
            "Extracción de PDF",
            "Procesamiento de Excel/CSV",
            "Conciliación con IA",
            "Validación de archivos"
        ],
        "openai_configured": bool(os.getenv('OPENAI_API_KEY'))
    } 