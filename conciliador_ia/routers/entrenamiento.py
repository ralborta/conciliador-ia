from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
import logging
import os
from pathlib import Path
from typing import Optional, Dict, Any, List
import uuid
from datetime import datetime

from services.patron_manager import PatronManager
from services.extractor_inteligente import ExtractorInteligente

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/entrenamiento", tags=["entrenamiento"])

# Verificación de servicios al inicio
def verificar_servicios():
    """Verifica disponibilidad de servicios críticos"""
    estado = {
        "patron_manager": False,
        "extractor_ia": False,
        "openai_configured": bool(os.getenv('OPENAI_API_KEY'))
    }
    
    try:
        global patron_manager
        patron_manager = PatronManager()
        estado["patron_manager"] = True
        logger.info("PatronManager inicializado correctamente")
    except Exception as e:
        logger.error(f"PatronManager no disponible: {e}")
        patron_manager = None
    
    try:
        if estado["openai_configured"]:
            global extractor_inteligente
            extractor_inteligente = ExtractorInteligente()
            estado["extractor_ia"] = True
            logger.info("Extractor Inteligente inicializado correctamente")
        else:
            logger.warning("OPENAI_API_KEY no configurada - funcionalidad de IA deshabilitada")
            extractor_inteligente = None
    except Exception as e:
        logger.error(f"ExtractorInteligente no disponible: {e}")
        extractor_inteligente = None
    
    return estado

# Ejecutar verificación
SERVICIOS_DISPONIBLES = verificar_servicios()
logger.info(f"Estado de servicios: {SERVICIOS_DISPONIBLES}")

@router.get("/bancos")
async def listar_bancos_entrenados():
    """Lista todos los bancos con patrones entrenados"""
    try:
        bancos = patron_manager.listar_bancos()
        estadisticas = patron_manager.obtener_estadisticas_globales()
        
        return {
            "success": True,
            "bancos": bancos,
            "estadisticas": estadisticas,
            "total_bancos": len(bancos)
        }
        
    except Exception as e:
        logger.error(f"Error listando bancos: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.get("/bancos/{banco_id}")
async def obtener_banco(banco_id: str):
    """Obtiene información detallada de un banco específico"""
    try:
        banco = patron_manager.obtener_banco(banco_id)
        if not banco:
            raise HTTPException(status_code=404, detail=f"Banco {banco_id} no encontrado")
        
        return {
            "success": True,
            "banco": banco
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo banco {banco_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.post("/entrenar")
async def entrenar_extracto(
    archivo: UploadFile = File(...),
    banco: Optional[str] = Form(None),
    forzar_ia: bool = Form(False)
):
    """Entrena un nuevo extracto bancario"""
    try:
        logger.info(f"=== INICIO ENTRENAMIENTO ===")
        logger.info(f"Archivo: {archivo.filename}")
        logger.info(f"Tamaño: {archivo.size}")
        logger.info(f"Banco: {banco}")
        logger.info(f"Forzar IA: {forzar_ia}")
        
        # Verificación temprana de servicios
        if not SERVICIOS_DISPONIBLES["patron_manager"]:
            raise HTTPException(
                status_code=503,
                detail="Servicio PatronManager no disponible"
            )
        
        if forzar_ia and not SERVICIOS_DISPONIBLES["extractor_ia"]:
            raise HTTPException(
                status_code=503,
                detail="Servicio de IA solicitado pero no disponible"
            )
        
        # Validar archivo básico
        if not archivo.filename:
            raise HTTPException(status_code=400, detail="No se proporcionó archivo")
            
        if not archivo.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF")
        
        # Verificar tamaño del archivo
        if hasattr(archivo, 'size') and archivo.size and archivo.size > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="El archivo es demasiado grande (máximo 10MB)")
        
        # Guardar archivo temporal
        archivo_id = str(uuid.uuid4())
        archivo_path = f"data/extractos_ejemplo/{archivo_id}_{archivo.filename}"
        
        # Crear directorio si no existe
        Path(archivo_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(archivo_path, "wb") as buffer:
            content = await archivo.read()
            buffer.write(content)
        
        logger.info(f"Archivo guardado: {archivo_path}")
        
        try:
            # Verificar si hay extractor disponible
            if not extractor_inteligente:
                raise HTTPException(
                    status_code=503, 
                    detail="Servicio de IA no disponible. Verifique la configuración de OPENAI_API_KEY."
                )
            
            # Extraer datos usando el extractor inteligente
            logger.info("Iniciando extracción con IA")
            resultado = extractor_inteligente.extraer_datos(archivo_path, banco)
            
            if not resultado:
                raise HTTPException(
                    status_code=422, 
                    detail="No se pudieron extraer datos del archivo PDF"
                )
            
            # Calcular precisión estimada
            total_movimientos = len(resultado["movimientos"])
            precision_estimada = resultado.get("precision_estimada", 0.9)
            
            # Actualizar estadísticas del banco
            banco_id = resultado.get("banco_id", "banco_test")
            patron_manager.actualizar_precision(banco_id, precision_estimada, True)
            
            return {
                "success": True,
                "message": "Extracto entrenado exitosamente",
                "resultado": {
                    "banco": resultado.get("banco"),
                    "banco_id": banco_id,
                    "metodo": resultado.get("metodo"),
                    "total_movimientos": total_movimientos,
                    "precision_estimada": precision_estimada,
                    "archivo": archivo.filename,
                    "archivo_id": archivo_id
                },
                "movimientos_muestra": resultado["movimientos"][:5]  # Primeros 5 movimientos
            }
            
        except Exception as e:
            # Limpiar archivo en caso de error
            if os.path.exists(archivo_path):
                os.remove(archivo_path)
            raise e
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error entrenando extracto: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.post("/entrenar/lote")
async def entrenar_lote_extractos(
    archivos: List[UploadFile] = File(...),
    banco: Optional[str] = Form(None)
):
    """Entrena múltiples extractos en lote"""
    try:
        if len(archivos) > 10:
            raise HTTPException(status_code=400, detail="Máximo 10 archivos por lote")
        
        resultados = []
        errores = []
        
        for i, archivo in enumerate(archivos):
            try:
                # Validar archivo
                if not archivo.filename.lower().endswith('.pdf'):
                    errores.append(f"Archivo {i+1}: Solo se permiten PDFs")
                    continue
                
                # Guardar archivo temporal
                archivo_id = str(uuid.uuid4())
                archivo_path = f"data/extractos_ejemplo/{archivo_id}_{archivo.filename}"
                
                Path(archivo_path).parent.mkdir(parents=True, exist_ok=True)
                
                with open(archivo_path, "wb") as buffer:
                    content = await archivo.read()
                    buffer.write(content)
                
                # Verificar si hay extractor disponible
                if not extractor_inteligente:
                    errores.append(f"Archivo {i+1}: Servicio de IA no disponible")
                    continue
                
                # Extraer datos
                resultado = extractor_inteligente.extraer_datos(archivo_path, banco)
                
                if resultado and resultado.get("movimientos"):
                    resultados.append({
                        "archivo": archivo.filename,
                        "banco": resultado.get("banco"),
                        "total_movimientos": len(resultado["movimientos"]),
                        "metodo": resultado.get("metodo"),
                        "precision": resultado.get("precision_estimada", 0.0)
                    })
                    
                    # Actualizar estadísticas
                    banco_id = resultado.get("banco_id", "banco_no_identificado")
                    patron_manager.actualizar_precision(banco_id, resultado.get("precision_estimada", 0.9), True)
                else:
                    errores.append(f"Archivo {i+1}: No se pudieron extraer movimientos")
                
                # Limpiar archivo temporal
                if os.path.exists(archivo_path):
                    os.remove(archivo_path)
                    
            except Exception as e:
                errores.append(f"Archivo {i+1}: {str(e)}")
                continue
        
        return {
            "success": True,
            "message": f"Procesados {len(archivos)} archivos",
            "resultados": resultados,
            "errores": errores,
            "total_exitosos": len(resultados),
            "total_errores": len(errores)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en entrenamiento por lote: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.put("/bancos/{banco_id}/patron")
async def actualizar_patron_banco(banco_id: str, patron_data: Dict[str, Any]):
    """Actualiza el patrón de un banco específico"""
    try:
        banco_actual = patron_manager.obtener_banco(banco_id)
        if not banco_actual:
            raise HTTPException(status_code=404, detail=f"Banco {banco_id} no encontrado")
        
        # Actualizar datos del banco
        banco_actual.update(patron_data)
        banco_actual["estadisticas"]["ultima_actualizacion"] = datetime.now().isoformat()
        
        patron_manager.guardar_banco(banco_id, banco_actual)
        
        return {
            "success": True,
            "message": f"Patrón del banco {banco_id} actualizado exitosamente",
            "banco": banco_actual
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error actualizando patrón del banco {banco_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.delete("/bancos/{banco_id}")
async def eliminar_banco(banco_id: str):
    """Elimina un banco del sistema de entrenamiento"""
    try:
        banco = patron_manager.obtener_banco(banco_id)
        if not banco:
            raise HTTPException(status_code=404, detail=f"Banco {banco_id} no encontrado")
        
        if patron_manager.eliminar_banco(banco_id):
            return {
                "success": True,
                "message": f"Banco {banco_id} eliminado exitosamente"
            }
        else:
            raise HTTPException(status_code=500, detail="Error eliminando banco")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error eliminando banco {banco_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.get("/monitor")
async def monitor_entrenamiento():
    """Endpoint de monitoreo para ver el estado del sistema"""
    try:
        # Verificar estado de servicios
        estado_servicios = {
            "patron_manager": "ok",
            "extractor_ia": "ok" if extractor_inteligente.client else "error",
            "openai_key": "ok" if os.getenv('OPENAI_API_KEY') else "error"
        }
        
        # Verificar directorios
        directorios = {
            "patrones_dir": str(patron_manager.patrones_dir),
            "patrones_exists": patron_manager.patrones_dir.exists(),
            "extractos_dir": str(patron_manager.extractos_dir),
            "extractos_exists": patron_manager.extractos_dir.exists()
        }
        
        # Estadísticas actuales
        estadisticas = patron_manager.obtener_estadisticas_globales()
        
        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "servicios": estado_servicios,
            "directorios": directorios,
            "estadisticas": estadisticas,
            "version": "1.0.0"
        }
        
    except Exception as e:
        logger.error(f"Error en monitor: {e}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/estadisticas")
async def obtener_estadisticas():
    """Obtiene estadísticas globales del sistema de entrenamiento"""
    try:
        estadisticas = patron_manager.obtener_estadisticas_globales()
        bancos = patron_manager.listar_bancos()
        
        # Estadísticas adicionales
        bancos_activos = len([b for b in bancos if b.get("activo", True)])
        precision_promedio = sum(b.get("precision", 0) for b in bancos) / len(bancos) if bancos else 0
        
        return {
            "success": True,
            "estadisticas": {
                **estadisticas,
                "bancos_activos": bancos_activos,
                "precision_promedio": round(precision_promedio, 3),
                "fecha_consulta": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.post("/exportar")
async def exportar_patrones(banco_id: Optional[str] = None):
    """Exporta patrones para backup"""
    try:
        patrones = patron_manager.exportar_patrones(banco_id)
        
        return {
            "success": True,
            "message": "Patrones exportados exitosamente",
            "patrones": patrones,
            "fecha_exportacion": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error exportando patrones: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.post("/importar")
async def importar_patrones(patrones_data: Dict[str, Any]):
    """Importa patrones desde un backup"""
    try:
        if patron_manager.importar_patrones(patrones_data):
            return {
                "success": True,
                "message": "Patrones importados exitosamente"
            }
        else:
            raise HTTPException(status_code=400, detail="Error importando patrones")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error importando patrones: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.post("/test-extractor")
async def test_extractor(
    archivo: UploadFile = File(...),
    banco: Optional[str] = Form(None)
):
    """Prueba el extractor sin guardar patrones"""
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
            # Verificar si hay extractor disponible
            if not extractor_inteligente:
                raise HTTPException(
                    status_code=503, 
                    detail="Servicio de IA no disponible. Verifique la configuración de OPENAI_API_KEY."
                )
            
            # Extraer datos
            resultado = extractor_inteligente.extraer_datos(archivo_path, banco)
            
            return {
                "success": True,
                "message": "Extracción de prueba completada",
                "resultado": resultado
            }
            
        finally:
            # Limpiar archivo temporal
            if os.path.exists(archivo_path):
                os.remove(archivo_path)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en test del extractor: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
